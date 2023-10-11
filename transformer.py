#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:12:01 2023

@author: nicalcoca
"""

import os
import pandas as pd


# Para limpiar ruido de una variable
def transforming_var(wd, file, var, output):
    
    os.chdir(wd)
    
    df = pd.read_csv(os.path.join(wd, file), delimiter=',')
    
    column_data = df.loc[:, var]
    
    # condicionales para transformar variables según sea el caso
    if var == 'RADAR_Feet':
        
        radar_meters = feet_meters(column_data)
        df['RADAR_Meters'] = radar_meters.tolist()
        df.to_csv(output, sep=',')
    
        return f'Save to {wd}/{output}'
        
    else:
        
        return 'No existe la variable ingresada'


# De pies a metros
def feet_meters(feet):
    
    return feet/3.2808

# if __name__ == '__main__':
    
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--dt', type=str, help='Directorio de trabajo')
    
#     parser.add_argument('--ai', type=str, help='Archivo de entrada')
    
#     parser.add_argument('--v', type=str, help='Variable a limpiar')
    
#     help_ao='Archivo de salida dentro del directorio de trabajo'
#     parser.add_argument('--ao', type=str, help=help_ao)
    
#     args = parser.parse_args()
#     result = transforming(args.dt, args.ai, args.v, args.ao)
    
#     print(result)
    
    