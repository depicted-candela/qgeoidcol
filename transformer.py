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
    