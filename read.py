#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 20:45:18 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from .models import Project, AeroRawProject, TerrainRawProject, Correctores

import pandas as pd
import geopandas as gpd
import numpy as np

import os

class Lector:

    """
    Clase lectora de archivos para el modelo geoidal
    """
    def leer(self, wd, file, metodo='proyecto_gravedad', **kwargs):

        lector = get_lector(metodo)

        return lector(wd, file, **kwargs)


## Lector para archivos
def get_lector(metodo):

    if metodo == 'proyecto_gravedad':

        return _reader_prj
    
    elif metodo == 'deriva':

        return _reader_deriva

    else:

        raise ValueError("Método desconocido")

## Lector de archivos de deriva
def _reader_deriva(wd, file, **kwargs):

    try:
        empresa = kwargs['empresa']
    except:
        raise ValueError("Debe proporcionar el 'delimitador' y la 'empresa")
    
    if empresa == 'carson':
        return __deriva_carson(file, **kwargs)
    
    else:
        raise ValueError("Empresa desconocida")

## Para calcular deriva desde archivos de Carson
def __deriva_carson(file, **kwargs):

    try:
        concat = kwargs['concatenador']
        delimiter = kwargs['delimitador']
    except:
        raise ValueError("Si el proyecto es de Carson debe utilizar un 'concatenador' y 'delimitador'")
    
    df = pd.read_csv(file, delimiter=delimiter)
    concat = Correctores.read_csv(concat, empresa='carson', delimiter=delimiter)
    
    ## Para concatenar
    subdf = df[['FlightNumber', 'BeforeFlight', 'AfterFlight']]
    subdf.columns = ['Flt', 'BeforeFlight', 'AfterFlight']
    subdf['Flt'].apply(int)
    df = concat.data.merge(subdf, on='Flt')

    ## Concatena la línea de vuelo
    dir = df['Dir'].apply(str)
    flt = df['Flt'].apply(lambda x: '0' + str(x) if x < 10 else str(x))
    line = df['LineID#'].apply(str)
    df['LINE'] = dir + flt + line
    df['LINE'] = df['LINE'].apply(float)
    concat.set_data(df)

    return concat

## Lector de archivos de gravimetría y altimetría
def _reader_prj(wd, file, **kwargs):

    try:
        tipo = kwargs['tipo']
    except:
        raise ValueError("Debe proporcionar el 'tipo' de objeto si quiere subir un archivo gravimétrico")
    
    file_name, file_ext = os.path.splitext(file)
    
    os.chdir(wd)
    
    ## Archivos .csv
    if file_ext == '.csv':
        
        df = pd.read_csv(file, delimiter=',')

        if 'geometry' in df.columns:
            df = df.rename(columns={'geometry': 'GEOM'})
        elif 'geom' in df.columns:
            df = df.rename(columns={'geometry': 'GEOM'})
        else:
            pass
    
    ## Archivos .shp
    elif file_ext == '.shp' or file_ext == '.gpkg':
        
        gdf = gpd.read_file(file)
        df = pd.DataFrame(gdf)

        if 'geometry' in df.columns:
            df = df.rename(columns={'geometry': 'GEOM'})
        elif 'geom' in df.columns:
            df = df.rename(columns={'geometry': 'GEOM'})
        else:
            pass
        
    ## El resto de archivos
    else:
        
        return 'Formato no soportado'
    
    match tipo:
        
        ## Para objetos de clase Proyecto
        case 'nivelacion'|'gravedad-absoluta'|'gravedad-relativa'|'gravedades':
            return Project(file, df, tipo)
    
        ## Para objetos de clase RawProject
        case 'crudo-aereo':

            prj = AeroRawProject(file, df, tipo)

            if 'long' in kwargs.keys() and 'lat' in kwargs.keys():

                prj.spatialize_vars(kwargs['long'], kwargs['lat'])

            return prj
        
        case 'crudo-terreno':
            return TerrainRawProject(file, df, tipo)
    
