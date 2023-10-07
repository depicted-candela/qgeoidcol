#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:14:48 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from string_tools import split_text_in_equal_lines as stiql

## Grafica coecientes entre estadísticos de dos proyectos
class Cocientes():

    """
    Clase graficadora de cocientes
    """
    
    def comparar(self, self_p, other_prj, *args, **kwargs):
        
        comparador = get_comparaciones(args, kwargs, self_p, other_prj)
        comparaciones = comparador(args)
        
        return prj.set_df_file_tipo(df_con_acc, prj.file, prj.tipo)

def get_comparaciones(args, kwargs, self_p, other_p):
    
    """
    TRAE LAS COMPARACIONES.

    Parameters
    ----------
    args : tuple
        VARIABLES A COMPARAR PARA DETERMINAR CONFIGURACIÓN.
    kwargs : dictionaty of lists
        LÍNEAS A COMPARAR CON LA CONFIGURACIÓN
    self_p : qgeoidcol.models.RawProject
        PROYECTO A COMPARAR
    other_prj : qgeoidcol.models.RawProject
        PROYECTO PARA COMPARAR

    Returns
    -------
    pandas.core.frame.DataFrame
        COMPARACIONES POR LÍNEA.

    """
    
    if len([kk for kk in kwargs.keys() if kk not in ['comparar', 'base']]) != 0:

        raise ValueError("Debes especificar líneas a comparar en el argumento 'comparar' y para comparar en el argumento 'base'")

    largs = len(args)

    if largs == 1:
        
        if 'GRAV_REL_zcore' not in args:

            return ValueError(f'La variable debe ser GRAV_REL_zcore')

        return _comparacion_statistics
    
    elif largs == 2:

        possible_vars = ['ACC_HOR', 'ACC_TOT']

        if len([k for k in kwargs.keys() if k not in possible_vars]) != 0:

            raise ValueError(f"Las valores deben ser {possible_vars}")
        
        return _comparacion_statistics
    
    else:
        raise ValueError("Proporciene suficientes variables (1 o 2)")


def _comparacion_statistics(own_prj, com_prj, kwargs, args):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    own_prj : qgeoidcol.models.RawProject
        PROYECTO A CALCULAR.
    com_prj : string
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
        
        own_prj.groups
        com_prj.groups
        
    except:
        
        mensaje = "El objecto {prj} del archivo {prj.file} debe ser"
        mensaje += "agregado por líneas, por ejemplo:   "
        mensaje += "caguan_grav_hi.aggregator_group('LINE')"
        mensaje = stiql(mensaje, 52)
        
        raise ValueError(mensaje)
    
    ## Para variar el comportamiento según el método
    ## Aceleración vertical
    vars = ['ACC_HOR', 'ACC_TOT']
    stats_name = ['mean', 'entropy']
    known = [228108.1, 202117.0 , 238109.1]

    entropy = pd.DataFrame(columns=['unknown', 'known', 'coef'])
    mean = pd.DataFrame(columns=['unknown', 'known', 'coef'])

    import math
    cc = 0
    c_ = 0
    ll = len(vars)*len(known)*len(grav_north_low.groups)*len(stats_name)
    for v in vars:
        for u in grav_north_low.groups:
            unk = grav_north_low.grouped_statistics(var=v, id='FID')[u]
            for k in known:
                kn = caguan_2006.grouped_statistics(var=v, id='FID')[k]
                for i, s in enumerate(stats_name):
                    c = unk[s] / kn[s]
                    if c >=2 and math.isfinite(c):
                        # print(v)
                        # print(s)
                        # print(u)
                        # print(unk[s])
                        # print(k)
                        # print(kn[s])
                        # print(c)
                        if s == 'entropy':
                            entropy = entropy._append({'unknown': str(u), 'known': str(k), 'coef': c}, ignore_index=True)
                        else:
                            mean = mean._append({'unknown': str(u), 'known': str(k), 'coef': c}, ignore_index=True)
                        # grav_north_low.values_compared_per_group(caguan_2006, v, u, k)
                    if c >= c_ and math.isfinite(c):
                        c_ = c
                    cc+=1
                    if cc % 10 == 0:
                        print(cc/ll)

    len(list(set(mean['unknown']))) + len(list(set(entropy['known'])))
    len(list(set(grav_north_low.df['LINE'])))


## Para detectar normalidad
def normality(array):

    ## Para listas pequeñas
    if len(array) < 5000:

        from scipy import stats
        
        # Estadístico de Shapiro
        statistic, p_value = stats.shapiro(array)
        
        if p_value > 0.05:
            
            print("Los datos siguen una distribución normal")
            return True
        
        else:
            
            print("Los datos no siguen una distribución normal")
            return False
    
    ## Para listas grandes
    else:
        
        # Estadístico de Anderson
        result = stats.anderson(array)

        # Extrae valores críticos y estadísticos
        critical_values = result.critical_values
        statistic = result.statistic
        
        # Si el valor crítico al 5% de significancia es mayor
        # que el estadístico, es normal la variable
        is_normal = statistic < critical_values[2]  # Usando el nivelde significancia 5%
        
        # Print the result
        if is_normal:
            
            print("Los datos siguen una distribución normal")
            return True
        else:
            
            print("Los datos no siguen una distribución normal")
            return False


## Derminador de estadísticos para agregaciones o variables agregadas
def calculate_statistics(group):

    from scipy.stats import kurtosis, skew, entropy
    import pandas as pd
    import numpy as np

    group = pd.to_numeric(group, errors='coerce')

    return pd.Series({
        'variance': group.var(),
        'entropy': entropy(np.histogram(group, bins=len(set(group)))[0]),
        'mean': group.mean(),
        'median': group.median(),
        'kurtosis': kurtosis(group),
        'skewness': skew(group),
        'std': group.std(),
        'max': group.max(),
        'min': group.min(),
        '25th_percentile': group.quantile(0.25),
        '50th_percentile': group.quantile(0.50),
        '75th_percentile': group.quantile(0.75)
    })

