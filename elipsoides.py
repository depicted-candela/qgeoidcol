#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:06:37 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from boule import GRS80

class GRS_80:
    
    # _dict = dict()
    
    # def __new__(cls):
        
    #     if 'grs80' in GRS_80._dict:
            
    #         print(f'Existan ya parámetros para el Elipsoide {cls}')
        
    #     else:
            
    #         print(f'Nueva instancia para Elipsoide {cls}')
    #         return super(GRS_80, cls).__new__(cls)
    
    def __init__(self):
        
        print(f'Inicializando instancia para Elipsoide {self}')
        
        self._A = GRS80.semimajor_axis
        self._B = GRS80.semiminor_axis
        self._F = GRS80.flattening
        self._M = ((GRS80.angular_velocity**2)*(self.A**2)*(self.B))/(GRS80.geocentric_grav_const)
        self._GE = GRS80.gravity_equator
        self._GP = GRS80.gravity_pole
        
        # GRS_80._dict['grs80'] = self

    @property
    def A(self):
        return self._A
    
    @property
    def B(self):
        return self._B
    
    @property
    def F(self):
        return self._F
    
    @property
    def M(self):
        return self._M
    
    @property
    def GE(self):
        return self._GE
    
    @property
    def GP(self):
        return self._GP