#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 09:01:57 2023

@author: nicalcoca
"""

from .string_tools import split_text_in_equal_lines as stiql
from .models import AeroRawProject

import pandas as pd
import numpy as np


class Aceleraciones:
    
    """
    Clase calculadora de aceleraciones
    """
    
    def calcular_aceleraciones(self, df, prj, tipo, alt='ADJ_ALT',
                               vertacc='RAW_VERTACC', time='TIME'):
        
        acelerador = get_aceleraciones(prj)
        df_con_acc = acelerador(prj, prj.df, prj.tipo, kwargs['alt'],
                                kwargs['vertacc'], kwargs['time'])
    #### Terminar

def get_aceleraciones(prj):
    
    """
    TRAE LAS ACELERACIONES.

    Parameters
    ----------
    prj : qgeoidcol.models.RawProject
        PROYECTO A CALCULAR.

    Returns
    -------
    pandas.core.frame.DataFrame
        DATA FRAME DEL PROYECTO MÁS CORRECCIONES.

    """
    
    if isinstance(prj, AeroRawProject):
        return _aceleraciones_aerogravimetria
    
    else:
        raise ValueError("Tipo de proyecto no soportado")


def _aceleraciones_aerogravimetria(prj, df, tipo, alt, vertacc, time):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.

    Returns
    -------
    pandas.core.frame.DataFrame

    """
    
    ## Para variar el comportamiento según el método
    if tipo == 'vertical':
        
        try:
            groups = prj.groups
        except:
            
            mensaje = "El objecto {prj} del archivo {prj.file} debe ser"
            mensaje += "agregado por líneas, por ejemplo:   "
            mensaje += "caguan_grav_hi.aggregator_group('LINE')"
            mensaje = stiql(mensaje, 52)
            
            raise ValueError(mensaje)
        
        aggr = prj.aggregator
        subdf = df[time, alt, vertacc]
        
        acc_df = __aceleracion_aerogravimetria(subdf, alt, time, groups, aggr)
        
        return acc_df

    
def __aceleracion_aerogravimetria(subdf, alt, time, groups, aggr):
    
    """
    PARA CALCULAR VELOCIDADES DE PROYECTOS AÉREOS

    Parameters
    ----------
    subdf : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.
    alt : string
        NOMBRE DE LA VARIABLE PARA ALTURA.
    time : string
        NOMBRE DE LA VARIABLE PARA TIEMPO.
    groups : lista de floats

    Returns
    -------
    None.

    """
    
    ## Itera sobre grupos para extraer variables
    for g in groups:
        
        cols = subdf.columns
        
        
        group_df = subdf[subdf[aggr] == g]
        sex_time = group_df[time]
        df_alt = group_df[alt]
        
        sec_time = __tiempo_utc_segundos(sex_time)
        
        e3 = group_df[alt].shift(periods=2)
        e2 = group_df[alt].shift(periods=1)
        e1 = group_df[alt]
        
        dt1 = group_df[time].shift(periods=1) - group_df[time]
        dt2 = group_df[time].shift(periods=2) - group_df[time].shift(periods=1)
        
        acc = ((e3 - e2) - (e2 - e1))/(dt1 * dt2)


def __aceleracion_aerogravimetria(subdf, alt, time, groups, aggr):
    
    """
    PARA CALCULAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    subdf : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.
    alt : string
        NOMBRE DE LA VARIABLE PARA ALTURA.
    time : string
        NOMBRE DE LA VARIABLE PARA TIEMPO.
    groups : lista de floats

    Returns
    -------
    None.

    """
    
    array_list = []
    
    ## Itera sobre grupos para extraer variables
    for g in groups:
    
        group_df = subdf[subdf[aggr] == g]
        group_array = np.array(group_df)
    
        ## Calcula aceleraciones
        e3 = newdf[alt].shift(periods=2)
        e2 = newdf[alt].shift(periods=1)
        e1 = newdf[alt]
        
        dt1 = newdf[time].shift(periods=1) - newdf[time]
        dt2 = newdf[time].shift(periods=2) - newdf[time].shift(periods=1)

        acc = ((e3 - e2) - (e2 - e1))/(dt1 * dt2)
        
        ## Concatena arrays
        acc =  np.array(acc)
        group_array = np.hstack((group_array, acc))
        
        ## Almacena arrays en lista
        array_list.append(group_array)
    
    # Concatenate arrays vertically
    result_array = np.vstack(array_list)
    
    ## Crea el nuevo data frame con aceleración vertical
    columns = subdf.columns.to_list()
    columns.append('ACC_VERT')
    acc_df = pd.DataFrame(result_array, columns=columns)
    
    return acc_df


def __tiempo_utc_segundos(tiempo):
    
    """
    Convierte tiempo sexagecimal a contador de segundos

    Parameters
    ----------
    tiempo : pandas.core.series.Series
        VARIABLE TEMPORAL EN ESCALA SEXAGECIMAL.

    Returns
    -------
    asfd.

    """
    
    s_time = list()
    
    ## Itera para transformar valores UTC a segundos
    for i in range(len(tiempo)):
        
        value = tiempo.iloc[i]
        secs = float(str(value)[4:])
        secs += float(str(value)[2:4]) * 60
        secs += float(str(value)[0:2]) * 3600
        s_time.append(secs)
    
    ## retorna pandas.core.series.Series
    return s_time



    
linedf = subdf[subdf['LINE'] == caguan_grav_hi.groups[0]]
linedf = linedf[['TIME', 'ADJ_ALT', 'RAW_VERTACC']]

sec_time = __tiempo_utc_segundos(timedf)
adj_alt = linedf['ADJ_ALT']
raw_acc = linedf['RAW_VERTACC']



newdf = pd.DataFrame({'TIME': sec_time, 'ADJ_ALT': adj_alt, 'RAW_VERTACC': raw_acc})

e3 = newdf['ADJ_ALT'].shift(periods=2)
e2 = newdf['ADJ_ALT'].shift(periods=1)
e1 = newdf['ADJ_ALT']

dt1 = newdf['TIME'].shift(periods=1) - newdf['TIME']
dt2 = newdf['TIME'].shift(periods=2) - newdf['TIME'].shift(periods=1)

acc = ((e3 - e2) - (e2 - e1))/(dt1 * dt2)





