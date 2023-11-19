#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:06:37 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from boule import GRS80, WGS84

class WGS_84:
    
    def __init__(self):
        
        print(f'Inicializando instancia para Elipsoide {self}')
        
        self._A     = WGS84.semimajor_axis
        self._B     = WGS84.semiminor_axis
        self._F     = WGS84.flattening
        self._M     = ((WGS84.angular_velocity**2)*(self.A**2)*(self.B))/(WGS84.geocentric_grav_const)
        self._GE    = WGS84.gravity_equator
        self._GP    = WGS84.gravity_pole
        self._W     = WGS84.angular_velocity
        self._GM    = WGS84.geocentric_grav_const

    @property
    def GM(self):
        return self._GM

    @property
    def W(self):
        return self._W

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

class GRS_80:
    
    def __init__(self):
        
        print(f'Inicializando instancia para Elipsoide {self}')
        
        self._A = GRS80.semimajor_axis
        self._B = GRS80.semiminor_axis
        self._F = GRS80.flattening
        self._M = ((GRS80.angular_velocity**2)*(self.A**2)*(self.B))/(GRS80.geocentric_grav_const)
        self._GE = GRS80.gravity_equator
        self._GP = GRS80.gravity_pole
        self._W = GRS80.angular_velocity
        self._GM = GRS80.geocentric_grav_const

    @property
    def GM(self):
        return self._GM

    @property
    def W(self):
        return self._W

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