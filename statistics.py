#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:14:48 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from .string_tools import split_text_in_equal_lines as stiql

## Grafica coecientes entre estadísticos de dos proyectos
class Cocientes():

    """
    Clase graficadora de cocientes
    """
    
    def comparar(self, self_p, other_prj, *args, **kwargs):
        
        comparador = get_comparaciones(self_p, other_prj, args[0], kwargs)
        comparaciones = comparador
        
        return comparaciones

def get_comparaciones(self_p, other_p, args, kwargs):
    
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
    
    ## Para contrastar variables bien ingresadas
    try:
    
        sg = self_p.groups
        og = other_p.groups
        
    except:
        
        mensaje = "El objecto {prj} del archivo {prj.file} debe ser"
        mensaje += "agregado por líneas, por ejemplo:   "
        mensaje += "caguan_grav_hi.aggregator_group('LINE')"
        mensaje = stiql(mensaje, 52)
        
        raise ValueError(mensaje)
    
    ## Tamaño de argumentos por tuplas
    largs = len(args)

    ## Para variar la configuración
    if largs == 1:
        
        if 'GRAV_REL_zcore' not in args: return ValueError(f'La variable debe ser GRAV_REL_zcore')

        return _comparacion_statistics(self_p, other_p, ['entropy'], args, kwargs)
    
    elif largs == 2:

        possible_vars = ['ACC_HOR', 'ACC_TOT']
        if len([k for k in args if k not in possible_vars]) != 0: raise ValueError(f"Las valores deben ser {possible_vars}")
        
        return _comparacion_statistics(self_p, other_p, ['entropy', 'mean'], possible_vars, kwargs)
    
    else:
        raise ValueError("Proporciene suficientes variables (1 o 2)")


def _comparacion_statistics(own_prj, com_prj, stats_name, args, kwargs):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    own_prj : qgeoidcol.models.RawProject
        PROYECTO A COMPARAR.
    com_prj : string
        PROYECTO A COMPARAR.
    stats : list of strings
        ESTADÍSTICOS PARA COMPARAR.
    args : tuple
        VARIABLES A COMPARAR CON LA CONFIGURACIÓN.
    kwargs : string
        LÍNEAS A COMPARAR CON LA CONFIGURACIÓN.

    Raises
    ------
    ValueError
        MENSAJES DE ERROR.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON COMPARACIONES SEGÚN CONFIGURACIÓN.

    """
    
    import pandas as pd
    import math
    import copy

    ## Estructura de datos para guardar información
    info = {sn: pd.DataFrame(columns=['unknown', 'known', 'coef', 'mGals', 'var']) for sn in stats_name}
    info['own'] = own_prj.file
    info['comp'] = com_prj.file

    c_ = 0  ## Máximo valor de coeficiente para considerar si graficar
    cc = 0  ## Contador para mostrar
    linea = None
    vars = list(args)

    ll = len(vars)*len(kwargs['base'])*len(kwargs['comparar'])*len(stats_name)
            ## Cuenta los pasos para crear porcentaje

    ## Itera sobre líneas de ambos proyectos para comparar estadísticos
    for v in vars:                  ## Itera sobre variables
        for u in kwargs['comparar']: ## Itera sobre líneas a comparar
            unk = own_prj.grouped_statistics(var=v, id='GEOM')[u]
            for k in kwargs['base']: ## Itera sobre líneas para comparar
                try:
                    kn = com_prj.grouped_statistics(var=v, id='GEOM')[k]
                except:
                    raise ValueError("Ingrese correctamente el proyecto o líneas a comparar")
                for i, s in enumerate(stats_name):
                    c = unk[s] / kn[s]
                    if c >=2 and math.isfinite(c):
                        info[s] = info[s]._append({'unknown': str(u),
                                                   'known': str(k),
                                                   'coef': c,
                                                   'mGals': c / 2,
                                                   'var': v},
                                                   ignore_index=True)
                    ## Si es un coeficiente mayor y no infinito
                    if c >= c_ and math.isfinite(c):
                        c_ = c
                        linea = u
                        ulinea = k
                        max_var = v
                        max_s = s
                    ## Cuenta pasos
                    cc+=1
                    ## Imprime avance
                    if cc % 10 == 0:
                        print(f"Percentage of advance: {cc/ll*100:.2f}%", end='\r')
    
    print(f"El mayor valor del coeficiente es {c_} ({c_ / 2} mGals) para la variable {max_var} con el estadístico {max_s} en la línea {linea} del proyecto {own_prj.file} comparada con la {ulinea} del proyecto {com_prj.file}.")

    tempdfinfo = copy.deepcopy(info)

    ## Información final de comparaciones
    for k, v in tempdfinfo.items():
        if isinstance(v, pd.core.frame.DataFrame) and len(v) > 0:
            ## Guarda máximo cociente en diccionario
            info[k + '_max'] = v['coef'].max()
            print(f"Existen {len(list(set(v['unknown'])))} líneas con coeficiente mayor a dos para {k}")
    
    return info


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

