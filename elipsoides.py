#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:06:37 2023

@author: nicalcoca
"""

from boule import GRS80

class GRS80:
    
    _dict = dict()
    
    def __new__(cls):
        
        if 'key' in GRS80._dict:
            
            print(f'Existan ya parámetros para el Elipsoide {cls}')
        
        else:
            
            print(f'Nueva instancia para Elipsoide {cls}')
            return super(GRS80, cls).__new__(cls)
            
    def __init__(self):
        
        print(f'Inicializando instancia para Elipsoide {self}')
        
        A = GRS80.semimajor_axis
        B = GRS80.semiminor_axis
        F = GRS80.flattening
        M = ((GRS80.angular_velocity**2)*(A**2)*(B))/(GRS80.geocentric_grav_const)
        
        GRS80._dict['key'] = self
        print("")