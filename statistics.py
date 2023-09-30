#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 15:14:48 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

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


def calculate_statistics(group):

    from scipy.stats import kurtosis, skew, entropy
    import pandas as pd
    import numpy as np

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