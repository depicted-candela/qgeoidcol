#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 20:59:57 2023

@author: nicalcoca
"""

import matplotlib.pyplot as plt


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





