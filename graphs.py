#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 20:59:57 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

import matplotlib.pyplot as plt
import numpy as np

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
def anormal_histogram_outlier(array, var):
    
    # Paquetes para Median Absolute Deviation
    from pyod.models.mad import MAD
    
    array_2d = array.reshape(-1, 1)
    mad = MAD().fit(array_2d)
    labels = mad.labels_
    
    # Si hay valores atípicos
    if 1 in labels:
        
        from .cluster import simpleKMeans
        
        # Para acceder a posiciones y valores atípicos
        positions = np.where(labels==1)[0]
        values = np.take(array, positions)
        
        print(f'Hay {len(values)} valores atípicos, son:\n{values}')
        
        limits = simpleKMeans(values, 'limits-outliers')
        
        # Histograma con todos los datos
        plt.hist(values, bins=30, alpha=0.5)
        
        # Líneas límite
        for limit in limits:
            plt.axvline(x=limit, color='red', linestyle='--')
        
        # Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        plt.title(f'Histograma con detetección de outliers\npara: {var}')
        
        return values
    
    else:
        
        print("No hay valores atípicos")


## Para atípicos de una variable normal
def normal_histogram_outlier(array, umbral, var):
    
    from scipy import stats
    
    ## Cálculo de outliers
    z_scores = stats.zscore(array)
    outliers_pos = np.where(np.abs(z_scores) > umbral)
    outliers = array[outliers_pos]
    
    ## Si no hay outliers, terminar
    if len(outliers) == 0:
        mensaje = f"Con un umbral de {umbral} no hay atípicos,\n"
        mensaje += "para subir el detalle de detección baje el\n"
        mensaje += "valor de 'umbral'"
        
        print(mensaje)
    
    # Cuando hay outliers
    else:
        
        from .cluster import simpleKMeans
        
        print(f'Hay {len(outliers)} valores atípicos, son:\n{outliers}')
        
        ## Determina límites
        limits = simpleKMeans(outliers, 'limits-outliers')
        
        plt.figure(1)
        plt.hist(outliers, bins=30, alpha=0.5)
        
        for limit in limits:
            plt.axvline(x=limit, color='red', linestyle='--')
            
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        plt.title(f'Histograma con detetección de outliers\npara: {var}')
        
        plt.show()
        
        return outliers