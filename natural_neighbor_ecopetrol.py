#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:16:51 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

import numpy as np
import metpy.interpolate as interp
import pandas as pd
import os, argparse
import matplotlib.pyplot as plt

## Rutina implementada con ayuda de ChatGPT-4: openai

def natural_neighbor_user(wd, file, variable, output, avoid=None):

    os.chdir(wd)
    
    df = pd.read_csv(file, delimiter=',')
    
    not_null_variable = df[df[variable] != avoid]
    clean_variable = not_null_variable[['LAT', 'LONG', variable]]
    
    # Create sample data with unevenly spaced points
    LAT = clean_variable[['LAT']]
    LAT = np.array([i[0] for i in LAT.values])
    LONG = clean_variable[['LONG']]
    LONG = np.array([i[0] for i in LONG.values])
    variable_num = clean_variable[[variable]]
    variable_num = np.array([i[0] for i in variable_num.values])
    
    # Define the grid to interpolate onto
    LATi = np.linspace(min(LAT), max(LAT), 100)
    LONGi = np.linspace(min(LONG), max(LONG), 100)
    LONGi, LATi = np.meshgrid(LONGi, LATi)
    
    
    # Interpolate data onto the grid using Natural Neighbor interpolation
    variable_intplt = interp.natural_neighbor_to_grid(LONG,
                                                      LAT,
                                                      variable_num,
                                                      LONGi,
                                                      LATi)
    
    # Create a plot
    fig, ax = plt.subplots()
    im = ax.imshow(variable_intplt, extent=[min(LONG), max(LONG), min(LAT), max(LAT)],
                  origin='lower', cmap='viridis')
    
    # Set the scales of the x and y axes to be the same
    ax.set_xlim([min(LONG), max(LONG)])
    ax.set_ylim([min(LAT), max(LAT)])
    
    # Add a colorbar
    cbar = plt.colorbar(im)
    
    # Add a title
    ax.set_title(f'Interpolación de {variable} con Vecinos Naturales')
    
    # Show the plot
    plt.show()
    
    # Save the plot as an image
    plt.savefig(os.path.join(wd,output))
    
    return f'Save to {wd}/{output}'


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dt', type=str, help='Directorio de trabajo')
    parser.add_argument('--ai', type=str, help='Archivo de entrada')
    parser.add_argument('--v', type=str, help='Variable')
    parser.add_argument('--ao', type=str, help='Archivo de salida dentro del directorio de trabajo')
    parser.add_argument('--av', help="Valor a evitar")
    
    args = parser.parse_args()
    result = natural_neighbor_user(args.dt, args.ai, args.v, args.ao, args.av)
    
    print(result)
