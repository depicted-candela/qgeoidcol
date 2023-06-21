#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 18:03:13 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

import numpy as np
import matplotlib.pyplot as plt


# Distribución empírica y acumulada de una variable agregada
def empirica_acumulada(project, var_name, breaks):
    
    var = project.df
    var = var[var_name].tolist()
    
    hist, bins = np.histogram(var, bins=breaks, range=(min(var), max(var)))
    
    # Calculate cumulative distribution
    cumulative = np.cumsum(hist) / len(var)
    
    # Create figure and axes
    fig, ax1 = plt.subplots()
    
    # Plot histogram
    ax1.hist(var, bins=bins, range=(min(var), max(var)), edgecolor='black',
             alpha=0.5, label='Empírica')
    
    # Set labels and title for histogram
    ax1.set_xlabel('Valor')
    ax1.set_ylabel('Frecuencia')
    title = 'Distribuciones Empirica y Acumulada de ' + var_name
    ax1.set_title(title)
    ax1.legend(loc='upper left')
    
    # Create secondary y-axis for cumulative distribution
    ax2 = ax1.twinx()
    
    # Plot cumulative distribution
    ax2.plot(bins[:-1], cumulative, 'r-', marker='o', markersize=4,
             label='Acumulada')
    
    # Set labels and title for cumulative distribution
    ax2.set_ylabel('Probabilidad Acumulada')
    ax2.legend(loc='upper right')
    
    # Show the plot
    return plt.show()
    

# Distribución empírica y acumulada de una variable por línea
def empirica_acumulada_linea(project, var_name, breaks, start_line, end_line):
    
    # Agrupa los datos
    grouped_data = project.df
    aggr = project.aggregator
    grpd_data = grouped_data.groupby(aggr)[var_name].apply(list).to_dict()
    
    if end_line - start_line == 10:
        lines = project.groups[start_line:end_line]
    elif end_line - start_line < 0:
        return 'No ha seleccionado líneas'
    elif start_line < 0:
        return 'No ha seleccionado líneas'
    elif len(project.groups) > start_line:
        return 'No existen tales líneas'
    else:
        return 'Intente no analizar tantos grupos al tiempo'
    
    plotlines = 1
    for l in lines:
        
        # Massive plots
        plt.figure(l+1)
        
        # Datos de la variable
        var = grpd_data[l]
        hist, bins = np.histogram(var, bins=breaks, range=(min(var), max(var)))
        
        # Calculate cumulative distribution
        cumulative = np.cumsum(hist) / len(var)
        
        # Create figure and axes
        fig, ax1 = plt.subplots()
        
        # Plot histogram
        ax1.hist(var, bins=bins, range=(min(var), max(var)), edgecolor='black',
                 alpha=0.5, label='Empírica')
        
        # Set labels and title for histogram
        ax1.set_xlabel('Valor')
        ax1.set_ylabel('Frecuencia')
        title = 'Distribuciones Empirica y Acumulada de ' + var_name + '\n'
        title = title + 'grupo ' + str(l)
        ax1.set_title(title)
        ax1.legend(loc='upper left')
        
        # Create secondary y-axis for cumulative distribution
        ax2 = ax1.twinx()
        
        # Plot cumulative distribution
        ax2.plot(bins[:-1], cumulative, 'r-', marker='o', markersize=4,
                 label='Acumulada')
        
        # Set labels and title for cumulative distribution
        ax2.set_ylabel('Probabilidad Acumulada')
        ax2.legend(loc='upper right')
        
        plotlines+=1
        
    # Show the plot
    plt.show()