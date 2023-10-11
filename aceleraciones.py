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
    
    def acelerar(self, prj, metodo, pos='GEOM', time='TIME'):
        
        acelerador = get_aceleraciones(prj)
        df_con_acc = acelerador(prj, metodo, pos, time)
        
        return prj.set_df_file_tipo(df_con_acc, prj.file, prj.tipo)


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
    
    if isinstance(prj, AeroRawProject) or str(type(prj)) == str(AeroRawProject):
        return _aceleracion_aerogravimetria
    
    else:
        raise ValueError("Tipo de proyecto no soportado")

def _aceleracion_aerogravimetria(prj, metodo, pos, time):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    prj : qgeoidcol.models.RawProject
        PROYECTO A CALCULAR.
    metodo : string
        YA SEA PARA horizontal O verticales.
    pos : string
        VARIABLE CON POSICION DE VUELO.
    time : string
        NOMBRE DE LA VARIABLE TEMPORAL.

    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR MÉTODO DE ACELERACIÓN DESCONOCIDO.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    try:
        
        groups = prj.groups
        aggr = prj.aggregator
        groups = prj.groups
        
    except:
        
        mensaje = "El objecto {prj} del archivo {prj.file} debe ser"
        mensaje += "agregado por líneas, por ejemplo:   "
        mensaje += "caguan_grav_hi.aggregator_group('LINE')"
        mensaje = stiql(mensaje, 52)
        
        raise ValueError(mensaje)
    
    ## Para variar el comportamiento según el método
    ## Aceleración vertical
    if metodo == 'vertical':
    
        return __aceleracion(prj.df, pos, time, groups, aggr, 'ACC_VERT')
    
    ## Aceleración horizontal
    elif metodo == 'horizontal_x':
        
        return __aceleracion(prj.df, pos, time, groups, aggr, 'ACC_HOR_X')
    
    ## Aceleraciones horizontales
    elif metodo == 'horizontal_y':
        
        return __aceleracion(prj.df, pos, time, groups, aggr, 'ACC_HOR_Y')
    
    elif metodo == 'horizontal':

        return __aceleracion_h(prj.df, 'ACC_HOR')
    
    elif metodo == 'total':

        return __aceleracion_c(prj.df, 'ACC_TOT')
    
    ## Si método mal proporcionado
    else:
        
        raise ValueError(f"No hay métodos para aceleracion {metodo}")


def __aceleracion_c(df, acc):

    """
    PARA CALCULAR LA ACELERACIÓN HORIZONTAL DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.
    acc : string
        NOMBRE DE VARIABLE DE NUEVA VARIABLE DE ACELERACIÓN

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA
        
    """

    array_list = []

    try:
        acc_x = np.array(df['ACC_HOR_X'])
        acc_y = np.array(df['ACC_HOR_Y'])
        if 'RAW_VERTACC' not in df.columns:
            c = False
            while not c:
                acc_z_name = input("Ingrese el nombre de la variable de aceleración vertical: ")
                if acc_z_name in df.columns:
                    acc_z = np.array(df[acc_z_name])
                    c = True
                else:
                    print(f"La variable {acc_z_name} no existe en el data frame, las variables que existen son: {df.columns}")
        else:
            acc_z = np.array(df['RAW_VERTACC'])
    except:
        raise ValueError('Debe primero calcular las aceleraciones horizontales x y y')

    df_array = np.array(df)
    acc_t = np.sqrt(list(acc_x**2 + acc_y**2 + acc_z**2))

    ## Concatena arrays
    acc_array_t = np.array(acc_t)
    acc_array_t = acc_array_t.reshape(-1, 1)
    df_array = np.hstack((df_array, acc_array_t))

    ## Almacena arrays en lista
    array_list.append(df_array)

    # Concatenate arrays vertically
    result_array = np.vstack(array_list)
    
    ## Crea el nuevo data frame con aceleración vertical
    columns = df.columns.to_list()
    columns.append(acc)
    acc_t_df = pd.DataFrame(result_array, columns=columns)
    
    return acc_t_df


def __aceleracion_h(df, acc):

    """
    PARA CALCULAR LA ACELERACIÓN HORIZONTAL DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.
    groups : lista
        AGRUPACIONES
    aggr : string
        VARIABLE AGREGADORA
    acc : string
        NOMBRE DE VARIABLE DE NUEVA VARIABLE DE ACELERACIÓN

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA
        
    """

    array_list = []

    try:
        df['ACC_HOR_X']
        df['ACC_HOR_Y']
    except:
        raise ValueError('Debe primero calcular las aceleraciones horizontales x y y')

    df_array = np.array(df)
    acc_x = np.array(df['ACC_HOR_X'])
    acc_y = np.array(df['ACC_HOR_Y'])
    acc_h = np.sqrt(list(acc_x**2 + acc_y**2))

    ## Concatena arrays
    acc_array_h = np.array(acc_h)
    acc_array_h = acc_array_h.reshape(-1, 1)
    df_array = np.hstack((df_array, acc_array_h))

    ## Almacena arrays en lista
    array_list.append(df_array)

    # Concatenate arrays vertically
    result_array = np.vstack(array_list)
    
    ## Crea el nuevo data frame con aceleración vertical
    columns = df.columns.to_list()
    columns.append(acc)
    acc_h_df = pd.DataFrame(result_array, columns=columns)
    
    return acc_h_df


def __aceleracion(df, pos, time, groups, aggr, acc):
    
    """
    PARA CALCULAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        DATA FRAME CON VARIABLES PARA ACELERACIONES CALCULAR.
    pos : string
        NOMBRE DE LA VARIABLE DE POSICION.
    time : string
        NOMBRE DE LA VARIABLE TEMPORAL.
    groups : lista de floats
        AGRUPACIONES
    aggr : string
        VARIABLE AGREGADORA
    acc : string
        NOMBRE DE VARIABLE DE NUEVA VARIABLE DE ACELERACIÓN

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA
        
    """
    
    array_list = []
    
    ## Itera sobre grupos para extraer variables
    for g in groups:
        
        ## Segmenta por grupo
        group_df = df[df[aggr] == g]
        group_array = np.array(group_df)
        
        ## Calcula geometrías
        if acc == 'ACC_HOR_X':
            geom = pd.Series([g.x for g in group_df['GEOM']])
        elif acc == 'ACC_HOR_Y':
            geom = pd.Series([g.y for g in group_df['GEOM']])
        elif acc == 'ACC_VERT':
            geom = group_df[pos]
        else:
            raise ValueError("Posición no disponible")
        
        ## Calcula diferencia de posición
        e3 = np.array(geom.shift(periods=2))
        e2 = np.array(geom.shift(periods=1))
        e1 = np.array(geom)
        
        ## Tiempo sexagecimal UTM a contador de segundos en decimales
        dec_time = __tiempo_utc_segundos(group_df[time])
        
        ## Diferencia en segundos
        dt1 = np.array(dec_time.shift(periods=1) - dec_time)
        dt2 = np.array(dec_time.shift(periods=2) - dec_time.shift(periods=1))
        
        ## Aceleración en miligales
        acc_array = (((e3 - e2) - (e2 - e1))/(dt1 * dt2)) * 100000
        
        ## Concatena arrays
        acc_array = np.array(acc_array)
        acc_array = acc_array.reshape(-1, 1)
        group_array = np.hstack((group_array, acc_array))
        
        ## Almacena arrays en lista
        array_list.append(group_array)
    
    # Concatenate arrays vertically
    result_array = np.vstack(array_list)
    
    ## Crea el nuevo data frame con aceleración vertical
    columns = df.columns.to_list()
    columns.append(acc)
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
    pandas.core.series.Series
        SERIES CON TIEMPO EN CONTADOR DE SEGUNDOS

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
    s_time = pd.Series(s_time)
    return s_time
