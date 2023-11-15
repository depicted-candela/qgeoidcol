#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 11:39:07 2023

@author: nicalcoca
"""

from .models import GrvLvlProject, GrvLvlCorrProject, AeroRawProject, AeroCorrectProject
from .elipsoides import GRS_80

import math as mt
import numpy as np
import pandas as pd
import jpype


def _data_elip_terreno():
    
    grs80 = GRS_80()
    
    param = [grs80.A]
    param.append(grs80.B)
    param.append(grs80.M)
    param.append(grs80.GE)
    param.append(grs80.GP)
    param.append(grs80.F)
    
    return param


class Correcciones:

    """
    Clase calculadora de correcciones de gravedad
    """
    
    def corregir(self, prj, **kwargs):
        
        corrector = get_corrector(prj, **kwargs)

        return corrector


def get_corrector(prj, **kwargs):
    
    """
    TRAE LAS CORRECCIONES

    Parameters
    ----------
    prj : GrvLvlProject
        PROYECTO A CALCULAR.

    Returns
    -------
    pandas.core.frame.DataFrame
        DATA FRAME DEL PROYECTO TERRESTRE MÁS CORRECCIONES.

    """
    
    if isinstance(prj, GrvLvlProject):
        # return GrvLvlCorrProject(prj.file,
        #                          _correccion_proyectos_terrestres,
        #                          'nivelacion-gravedades-intersectado-correcciones',
        #                          prj.metodo,
        #                          empresa='carson')
        return _correccion_proyectos_terrestres
    
    elif isinstance(prj, AeroRawProject):
        
        return AeroCorrectProject(prj.file,
                           _correccion_proyectos_aereos(prj, **kwargs),
                           'aire-libre-aereo',
                           empresa='carson')
    
    else:
        raise ValueError("El tipo de proyecto no es adecuado")


def __validadores_correccion_proyectos_aereos(**kwargs):

    if 'lat' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene las latitudes de los puntos")
    if 'long' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene las longitudes de los puntos")
    if 'fly_height' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene las altitudes de vuelo")
    if 'grav' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene las latitudes de los puntos")
    

def _correccion_proyectos_aereos(prj, **kwargs):
    
    """
    PARA CALCULAR ANOMALÍAS DE PROYECTOS AÉREOS.

    Parameters
    ----------
    prj : AeroRawProject
        PROYECTO AÉREO.

    Returns
    -------
    pandas dataframe
        DATA FRAME DEL PROYECTO TERRESTRE MÁS ANOMALÍA DE AIRE LIBRE.

    """

    ## Valida argumentos
    __validadores_correccion_proyectos_aereos(**kwargs)

    ## Agrega valores de argumentos
    args_agg = [kwargs['lat'], kwargs['long'], kwargs['fly_height'], kwargs['grav']]

    from pyshtools.gravmag import NormalGravity as ng
    from qgeoidcol.elipsoides import GRS_80

    ## Metadato del GRS80
    grs80 = GRS_80()

    ## Arreglo de variables necesarias para calcular
    ## ondulación geoidal y gravedad normal
    subarray = np.array(prj.df[args_agg]).T

    ## Gravedad normal con elipsoide GRS80
    normalgrav = ng(subarray[1],
                    grs80.GM, grs80.W,
                    grs80.A, grs80.B) * 100000
    
    ## Gravedad observada menos gravedad normal
    term1 = np.array(subarray[3]) - normalgrav

    ## Cálculo de ondulación geoidal interpolando
    ## con el paquete de Tinfour de Java
    N = _tinfour_natural_neighbor(subarray[:3])
    N = np.array(N)

    ## Cálculo de anomalía de Aire Libre
    free_air = term1 + 0.3086 * (subarray[2] - N)

    ## Finished the connection to the java class
    jpype.shutdownJVM()

    ## Almacena anomalía de Aire Libre
    subdf = prj.df
    subdf['FREE_AIR'] = free_air

    return subdf

def _tinfour_natural_neighbor(array):

    """
    INTERPOLA ONDULACIONES GEOIDALES CON LIBRERÍA TINFOUR DE JAVA
    https://github.com/gwlucastrig/Tinfour (INFORMACIÓN RELACIONADA
    en https://gwlucastrig.github.io/TinfourDocs/). FUE UTILIZADO UN
    MODELO GEOIDAL GLOBAL DESCARGADO DE http://icgem.gfz-potsdam.de/home
    PARA EL PAQUETE DE JAVA.

    Parameters
    ----------
    array : numpy.ndarray

    Returns
    -------
    numpy.ndarray
        ARREGLO DE ONDULACIONES GEOIDALES

    """

    ## Start the JVM with the directory containing class file
    jpype.startJVM(classpath=['/home/nicalcoca/eclipse-workspace/JToolsQgeoid/bin/',
                            '/home/nicalcoca/eclipse-workspace/jars/TinfourCore-2.1.7.jar'])
    
    ## Initiliaze the NaturalNeighbor class
    NaturalNeighbor = jpype.JClass('interpolations.NaturalNeighbor')

    ## Uses the NaturalNeighnor constructor
    nni = NaturalNeighbor(array[1, :].tolist(), array[0, :].tolist())

    ## Interpolates all the points with NaturalNeighbor
    values = nni.getInterps()

    ## Java instance to array
    values_array = np.array(list(values))

    return values_array

def _correccion_proyectos_terrestres(prj, **kwargs):
    
    """
    PARA CALCULAR ANOMALÍAS DE PROYECTOS TERRESTRES.

    Parameters
    ----------
    df : pandas dataframe
        DATA FRAME DEL PROYECTO TERRESTRE.

    Returns
    -------
    pandas dataframe
        DATA FRAME DEL PROYECTO TERRESTRE MÁS CORRECCIONES.

    """
    
    _vars = _data_elip_terreno()
    
    A = _vars[0]
    B = _vars[1]
    M = _vars[2]
    GE = _vars[3]
    GP = _vars[4]
    F = _vars[5]
    geom = prj.df['GEOM']
    
    som = _somigliana(A, B, M, GE, GP, geom)
    
    grav = prj.df['GRAV']
    H = prj.df['ALTURA_M_S']
    F = _vars[5]
    
    aire = _aire_libre(A, M, F, som, geom, grav, H)
    bouguer = _corr_bouguer(B, H)
    
    df_c = pd.DataFrame({'AIRE_LIBRE': aire, 'BOUGUER': bouguer})
    
    return pd.concat([prj.df, df_c], axis=1)
    

def geom_phi(geom):
    
    """
    Para pasar de Point a latitud

    Parameters
    ----------
    geom : lista de shapely.geometry.point.Point
        GEOMETRÍA DEL PUNTO DE OBSERVACIÓN.

    Returns
    -------
    Lista de latitudes.

    """
    
    return [c.y for c in geom]


def grados_radianes(lat):
    
    """
    De grados a radianes

    Parameters
    ----------
    lat : lista de numpy.float64
        LATITUD DE PUNTOS DE OBSERVACIÓN

    Returns
    -------
    Lista de latitudes en radianes

    """
    
    return list(map(mt.radians, lat)) 


def somigliana_numerador(radphi, gp, a, b, ge):
    
    """
    Numerador de ecuación Somigliana

    Parameters
    ----------
    radphi : lista de floats
        LATITIUD EN RADIANES.
    gp : float
        GRAVEDAD EN EL POLO.
    a : int
        EJE SEMIMENOR.
    b : TYPE
        EJE SEMIMAYOR.
    ge : float
        GRAVEDAD EN EL ECUADOR.

    Returns
    -------
    Lista de floats.

    """
    
    sumando1 = a * ge * np.array([mt.pow(num,
                                          2) for num in list(map(mt.cos,
                                                                radphi))])
    sumando2 = b * gp * np.array([mt.pow(num,
                                          2) for num in list(map(mt.sin,
                                                                radphi))])
    
    sumandos = sumando1 + sumando2
    
    return sumandos


def somigliana_denominador(radphi, a, b):
    """
    Denominador de ecuación Somigliana

    Parameters
    ----------
    radphi : lista de floats
        LATITIUD EN RADIANES.
    a : int
        EJE SEMIMAYOR.
    b : float
        EJE SEMIMENOR.

    Returns
    -------
    Lista de floats.

    """
    
    sumando1 = a ** 2 * np.array([mt.pow(num,
                                          2) for num in list(map(mt.cos,
                                                                radphi))])
    sumando2 = b ** 2 * np.array([mt.pow(num,
                                          2) for num in list(map(mt.sin,
                                                                radphi))])
    raiz = list(map(mt.sqrt, sumando1 + sumando2))
    
    return raiz


def _somigliana(A, B, M, GE, GP, geom):
    """
    La funcion recibe parametros del elipsoide y datos de observaciones y
    calcula la altura normal somigliana correspondiente.

    Parameters
    ----------
    A : int
        EJE SEMIMAYOR.
    M : float
        PARÁMETRO FÍSICO.
    GE : float
        GRAVEDAD EN EL ECUADOR.
    GP : float
        GRAVEDAD EN EL POLO.
    geom : lista de shapely.geometry.point.Point
        GEOMETRÍA EN LONGITUD Y LATITUD.

    Returns
    -------
    Lista de cálculos de Somigliana.

    """
    
    gphi = geom_phi(geom)
    radphi = grados_radianes(gphi)
    
    som_num = somigliana_numerador(radphi, GP, A, B, GE)
    som_den = somigliana_denominador(radphi, A, B)

    som = som_num/som_den

    return som


def _aire_libre(A, M, F, somi, geom, grav, H):
    """
    La funcion recibe parametros del elipsoide y calcula la
    corrección de aire libre.

    Parameters
    ----------
    A : int
        EJE SEMIMAYOR.
    M : float
        PARÁMETRO FÍSICO.
    F : float
        APLANAMIENTO.
    somi : lista de floats
        CÁLCULO DE SOMIGLIANA.
    geom : lista de shapely.geometry.point.Point
        GEOMETRÍA EN LONGITUD Y LATITUD.
    grav: lista de floats
        GRAVEDAD OBSERVADA.
    H : lista de floats
        ALTURAS SOBRE EL NIVEL DEL MAR.

    Returns
    -------
    aly_aire_libre : TYPE
        ANOMALÍA DE AIRE LIBRE.

    """
    
    
    ## Último término de aire libre
    normal = H/A
    
    ## Grados a radianes
    gphi = geom_phi(geom)
    radphi = grados_radianes(gphi)
    
    ## Cálculos
    sumando1 = 1 + M + F - 2 * F * np.array([mt.pow(num,
                                                    2) for num in list(map(mt.sin,
                                                                           radphi))])
    sumando2 = np.array([mt.pow(num, 2) for num in normal])
    
    ## Corrección de Aire Libre
    corr_aire_libre = 1 - 2 * (sumando1 * normal) + sumando2
    
    ## Anomalía de Aire Libre
    aly_aire_libre = grav - somi * corr_aire_libre
    
    return aly_aire_libre


def _corr_bouguer(B, H):
    """
    La funcion recibe parametros y datos de observaciones y calcula la
    anomalia de Bouguer correspondiente. Den se refiere a la densidad media

    Parameters
    ----------
    B : float
        EJE SEMIMAYOR.
    H : TYPE
        DESCRIPTION.

    Returns
    -------
    Boug : lista de floats
        CORRECCIÓN DE BOUGUER.

    """
    
    ## Densidad promedio de la tierra
    DEN = 2.67
    boug = DEN * B * H
    
    return boug
