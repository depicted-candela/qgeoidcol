#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 11:39:07 2023

@author: nicalcoca
"""

from .models import GrvLvlProject, GrvLvlCorrProject, AeroRawProject, AeroCorrectProject, TerrainRawProject, TerrainCorrectProject
from .elipsoides import GRS_80, WGS_84
from .alturas import Alturas

import math as mt
import numpy as np
import pandas as pd

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

        prj = GrvLvlCorrProject(prj.file,
                                 _correccion_proyectos_terrestres(prj, **kwargs),
                                 'nivelacion-gravedades-intersectado-correcciones',
                                 prj.metodo,
                                 empresa=None)

        return prj
    
    if isinstance(prj, TerrainRawProject):
        
        prj = TerrainCorrectProject(prj.file,
                                     _correccion_proyectos_terrestres(prj, **kwargs),
                                     'aire-libre-terreno',
                                     empresa=None)

        return prj
    
    elif isinstance(prj, AeroRawProject):

        ## Start the JVM with the directory containing class file

        prj = AeroCorrectProject(prj.file,
                           _correccion_proyectos_aereos(prj, **kwargs),
                           'aire-libre-aereo',
                           empresa='carson')
        
        return prj
    
    else:
        raise ValueError("El tipo de proyecto no es adecuado")


def __validadores_correccion_proyectos_aereos(**kwargs):
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
    ellip = __metadata_ellipsoid(**kwargs)

    ## Arreglo de variables necesarias para calcular
    ## ondulación geoidal y gravedad normal
    lambd   = np.array(prj.df['GEOM'].apply(lambda x:___geom_lambda(x)))
    phi     = np.array(prj.df['GEOM'].apply(lambda x:___geom_phi(x)))
    fly_h   = np.array(prj.df[kwargs['fly_height']])
    grav    = np.array(prj.df[kwargs['grav']])
    subarr  = np.array([lambd, phi, fly_h, grav])

    from pyshtools.gravmag import NormalGravity as ng

    ## Gravedad normal con elipsoide GRS80
    normalgrav = ng(subarr[1],
                    ellip.GM, ellip.W,
                    ellip.A, ellip.B) * 100000

    ## Cálculo de altura anómala interpolando
    ## con el paquete de Tinfour de Java
    altura      = Alturas()
    altura.calcular_altura(prj, 'altura_anomala', modelo='eigen_6c4')

    ## Cálculo de anomalía de Aire Libre
    H_Q = subarr[2] - prj.df["Xi"]
    subdf = prj.df
    subdf['A_AIRE_LIBRE'] = __aly_aire_libre(H_Q,
                                        subarr[3],
                                        normalgrav,
                                        subarr[0],
                                        ellip)

    return subdf

def __aly_aire_libre(cota, grav, normalgrav, phi, ellip):

    ## Para segundo y último término interno de aire libre
    seg_ult = cota/ellip.A
    
    ## Grados a radianes
    radphi = grados_radianes(phi)

    ## Segundo término interno de aire libre
    sin_phi_squared = np.array([mt.pow(num, 2) for num in list(map(mt.sin, radphi))])
    term2 = 2 * (1 + ellip.F + ellip.M - 2 * ellip.F * sin_phi_squared) * seg_ult

    ## Último término interno de aire libre
    term3 = 3 * seg_ult ** 2

    normal_telluroid = normalgrav * (1 - term2 + term3)
    
    ## Anomalía de Aire Libre
    aly_aire_libre = grav - normal_telluroid
    
    return aly_aire_libre

def _tinfour_natural_neighbor(array, jpype):

    """
    INTERPOLA ONDULACIONES GEOIDALES CON LIBRERÍA TINFOUR DE JAVA
    https://github.com/gwlucastrig/Tinfour (INFORMACIÓN RELACIONADA
    EN https://gwlucastrig.github.io/TinfourDocs/). FUE UTILIZADO UN
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

    ## Initiliaze the NaturalNeighbor class
    NaturalNeighbor = jpype.JClass('interpolations.NaturalNeighbor')

    ## Uses the NaturalNeighnor constructor
    nni = NaturalNeighbor(array[0, :].tolist(), array[1, :].tolist())

    ## Interpolates all the points with NaturalNeighbor
    values = nni.getInterps()

    ## Java instance to array
    values_array = np.array(list(values))

    return values_array


def __validadores_correccion_proyectos_terrestres(**kwargs):

    if 'grav' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene la gravedad de los puntos")
    if 'altura' not in kwargs.keys():
        raise ValueError("Debe proporcionar el nombre de la variable que contiene la altura de los puntos")

## Metadato del elipsoide
def __metadata_ellipsoid(**kwargs):
    if 'ellipsoid' not in kwargs.keys() or kwargs['ellipsoid'] == 'grs80':
        return GRS_80()
    elif kwargs['ellipsoid'] == 'wgs84':
        return WGS_84()
    else: raise ValueError("El elipsoide de referencia no ha sido establecido aquí")

def _correccion_proyectos_terrestres(prj, **kwargs):
    
    """
    PARA CALCULAR ANOMALÍAS DE PROYECTOS TERRESTRES.

    Parameters
    ----------
    df : pandas dataframe
        DATA FRAME DEL PROYECTO TERRESTRE.
    kwargs : dictionary
        DEBE PROVEER EN LAS variables grav='NOMBREVARIABLEGRAVEDAD' Y altura='NOMBREVARIABLEALTURA'

    Returns
    -------
    pandas dataframe
        DATA FRAME DEL PROYECTO TERRESTRE MÁS CORRECCIONES.

    """

    __validadores_correccion_proyectos_terrestres(**kwargs)
    ellip = __metadata_ellipsoid(**kwargs)
    
    from pyshtools.gravmag import NormalGravity as ng

    ## Extracción de variables necesarias
    grav = prj.df[kwargs['grav']]
    H = prj.df[kwargs['altura']]
    phi = np.array(prj.df['GEOM'].apply(lambda x:___geom_phi(x)))

    ## Gravedad normal con elipsoide GRS80
    normalgrav = ng(phi,
                    ellip.GM, ellip.W,
                    ellip.A, ellip.B) * 100000
    
    ## Cálculo de anomalía de Aire LIbre
    subdf = prj.df
    subdf['A_AIRE_LIBRE'] = __aly_aire_libre(H, grav, normalgrav, phi, ellip)
    
    return subdf
    

def ___geom_phi(geom):
    
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
    
    return geom.y

def ___geom_lambda(geom):
    
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
    
    return geom.x


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


# def somigliana_numerador(radphi, gp, a, b, ge):
    
#     """
#     Numerador de ecuación Somigliana

#     Parameters
#     ----------
#     radphi : lista de floats
#         LATITIUD EN RADIANES.
#     gp : float
#         GRAVEDAD EN EL POLO.
#     a : int
#         EJE SEMIMENOR.
#     b : TYPE
#         EJE SEMIMAYOR.
#     ge : float
#         GRAVEDAD EN EL ECUADOR.

#     Returns
#     -------
#     Lista de floats.

#     """
    
#     sumando1 = a * ge * np.array([mt.pow(num,
#                                           2) for num in list(map(mt.cos,
#                                                                 radphi))])
#     sumando2 = b * gp * np.array([mt.pow(num,
#                                           2) for num in list(map(mt.sin,
#                                                                 radphi))])
    
#     sumandos = sumando1 + sumando2
    
#     return sumandos


# def somigliana_denominador(radphi, a, b):
#     """
#     Denominador de ecuación Somigliana

#     Parameters
#     ----------
#     radphi : lista de floats
#         LATITIUD EN RADIANES.
#     a : int
#         EJE SEMIMAYOR.
#     b : float
#         EJE SEMIMENOR.

#     Returns
#     -------
#     Lista de floats.

#     """
    
#     sumando1 = a ** 2 * np.array([mt.pow(num,
#                                           2) for num in list(map(mt.cos,
#                                                                 radphi))])
#     sumando2 = b ** 2 * np.array([mt.pow(num,
#                                           2) for num in list(map(mt.sin,
#                                                                 radphi))])
#     raiz = list(map(mt.sqrt, sumando1 + sumando2))
    
#     return raiz


# def _somigliana(A, B, M, GE, GP, geom):
#     """
#     La funcion recibe parametros del elipsoide y datos de observaciones y
#     calcula la altura normal somigliana correspondiente.

#     Parameters
#     ----------
#     A : int
#         EJE SEMIMAYOR.
#     M : float
#         PARÁMETRO FÍSICO.
#     GE : float
#         GRAVEDAD EN EL ECUADOR.
#     GP : float
#         GRAVEDAD EN EL POLO.
#     geom : lista de shapely.geometry.point.Point
#         GEOMETRÍA EN LONGITUD Y LATITUD.

#     Returns
#     -------
#     Lista de cálculos de Somigliana.

#     """
    
#     gphi =___geom_phi(geom)
#     radphi = grados_radianes(gphi)
    
#     som_num = somigliana_numerador(radphi, GP, A, B, GE)
#     som_den = somigliana_denominador(radphi, A, B)

#     som = som_num/som_den

#     return som


# def _aire_libre(A, M, F, somi, geom, grav, H):
#     """
#     La funcion recibe parametros del elipsoide y calcula la
#     corrección de aire libre.

#     Parameters
#     ----------
#     A : int
#         EJE SEMIMAYOR.
#     M : float
#         PARÁMETRO FÍSICO.
#     F : float
#         APLANAMIENTO.
#     somi : lista de floats
#         CÁLCULO DE SOMIGLIANA.
#     geom : lista de shapely.geometry.point.Point
#         GEOMETRÍA EN LONGITUD Y LATITUD.
#     grav: lista de floats
#         GRAVEDAD OBSERVADA.
#     H : lista de floats
#         ALTURAS SOBRE EL NIVEL DEL MAR.

#     Returns
#     -------
#     aly_aire_libre : TYPE
#         ANOMALÍA DE AIRE LIBRE.

#     """
    
    
#     ## Último término de aire libre
#     normal = H/A
    
#     ## Grados a radianes
#     gphi =___geom_phi(geom)
#     radphi = grados_radianes(gphi)
    
#     ## Cálculos
#     sumando1 = 1 + M + F - 2 * F * np.array([mt.pow(num,
#                                                     2) for num in list(map(mt.sin,
#                                                                            radphi))])
#     sumando2 = np.array([mt.pow(num, 2) for num in normal])
    
#     ## Corrección de Aire Libre
#     corr_aire_libre = 1 - 2 * (sumando1 * normal) + sumando2
    
#     ## Anomalía de Aire Libre
#     aly_aire_libre = grav - somi * corr_aire_libre
    
#     return aly_aire_libre


# def _corr_bouguer(B, H):
#     """
#     La funcion recibe parametros y datos de observaciones y calcula la
#     anomalia de Bouguer correspondiente. Den se refiere a la densidad media

#     Parameters
#     ----------
#     B : float
#         EJE SEMIMAYOR.
#     H : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     Boug : lista de floats
#         CORRECCIÓN DE BOUGUER.

#     """
    
#     ## Densidad promedio de la tierra
#     DEN = 2.67
#     boug = DEN * B * H
    
#     return boug
