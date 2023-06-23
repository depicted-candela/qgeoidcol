#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 20:59:57 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from .string_tools import split_text_in_equal_lines as stiql

import matplotlib.pyplot as plt
import numpy as np
import copy

## Código implementado con ayuda de ChatGPT-4: openai

# Gráfico de todas las líneas
def values_per_lines(proj, var_name):
    
    df = proj.df
    aggr = proj.aggregator
    
    grpd_data = df.groupby(aggr)[var_name].apply(list).to_dict()
    
    # Plotting the graph
    for key, values in grpd_data.items():
        plt.plot(values, label=key)
    
    # Customize the plot
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Graph with Dictionary Values')
    plt.legend()
    
    # Display the plot
    plt.show()


# Gráfico de diez líneas
def values_per_lines_limited(project, var_name, start_line, end_line):
    
    df = project.df
    aggr = project.aggregator
    
    grpd_data = df.groupby(aggr)[var_name].apply(list).to_dict()
    keys = list(grpd_data.keys())[start_line: end_line]
    subset_dict = {key: grpd_data[key] for key in keys if key in grpd_data}
    
    # Plotting the graph
    for key, values in subset_dict.items():
        plt.plot(values, label=key)
    
    # Customize the plot
    plt.xlabel('observaciones')
    plt.ylabel('metros')
    plt.title('Altimetría de radar por línea')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Display the plot
    plt.show()


## Para atípicos de una variable anormal
def anormal_histogram_outlier(prj, var):
    
    subdf = prj.df[[var, 'GEOM']]
    valuesdf = prj.df[var]
    
    ## Extracción de valores del dataframe
    x = copy.deepcopy(np.array(subdf['GEOM'].apply(lambda point: point.x)))
    y = copy.deepcopy(np.array(subdf['GEOM'].apply(lambda point: point.y)))
    
    subdf.loc[:,'x'] = x
    subdf.loc[:,'y'] = y

    del subdf['GEOM']
    
    array3d = np.array(subdf)
    array = np.array(valuesdf).reshape(-1, 1)
    
    # Paquete para One-class SVM detector
    from pyod.models.ocsvm import OCSVM
    
    model = OCSVM(kernel='rbf', nu=0.5)
    model.fit(array3d)
    
    labels = model.predict(array3d)
    positions = np.where(labels==1)[0]
    
    # Si hay valores atípicos
    if 1 in labels:
        
        # Para acceder a posiciones y valores atípicos
        positions = np.where(labels==1)[0]
        values = np.take(array, positions)
        
        print(f'Hay {len(values)} valores atípicos')
        
        # Histograma con todos los datos
        plt.hist(array, bins=30, alpha=0.5)
        
        # Líneas límite
        for out in values:
            plt.axvline(x=out, color='red', linestyle='--')
        
        # Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma con detetección de outliers para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        plt.show()
        
        return values
    
    else:
        
        ## Histograma sin valores atípicos
        plt.hist(array, bins=30, alpha=0.5)
        
        # Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma con detetección de outliers para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        plt.show()
        
        print("No hay valores atípicos")
        
        return None


## Para atípicos de una variable normal
def normal_histogram_outlier(array, umbral, var):
    
    from scipy import stats
    
    ## Cálculo de outliers
    z_scores = stats.zscore(array)
    outliers_pos = np.where(np.abs(z_scores) > umbral)
    outliers = array[outliers_pos]
    
    ## Si no hay outliers, terminar
    if len(outliers) == 0:
        
        ## Histograma de variable normal sin atípicos
        plt.hist(array, bins=30, alpha=0.5)
        
        ## Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        
        ## Mostrar gráfico
        plt.show()
        
        ## Mensaje explicativo
        mensaje = f"Con un umbral de {umbral} no hay atípicos, "
        mensaje += "para subir el detalle de detección baje el"
        mensaje += "valor de 'umbral'"
        stiql(mensaje, 60)
        
        print(mensaje)
        
        return None
    
    # Cuando hay outliers
    else:
        
        from .cluster import simpleKMeans
        
        print(f'Hay {len(outliers)} valores atípicos')
        
        ## Determina límites
        limits = simpleKMeans(outliers, 'limits-outliers')
        
        plt.figure(1)
        plt.hist(array, bins=30, alpha=0.5)
        
        for limit in limits:
            plt.axvline(x=limit, color='red', linestyle='--')
        
        ## Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma con detetección de outliers para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        
        ## Mostrar gráfico
        plt.show()
        
        return outliers