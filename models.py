#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:43:42 2023

@author: nicalcoca
"""

import matplotlib.pyplot as plt
import pandas as pd


## Clase para estandarizar objetos de proyectos de nivelación
## y gravimétricos
class Project:
    
    """ Tipos válidos para proyectos geoidales:
    
        - el tipo 'gravedades' se refiere a un dataframe con gravedades
    absolutas y relativas
        - el tipo 'nivelacion-gravedades' se refiere a un dataframe con
    gravedades absolutas y relativas intersecadas 
    """
    valid_types = ['nivelacion', 'gravedad-absoluta', 'gravedad-relativa',
                   'gravedades']
    
    
    ## Valores inicializadores
    def __init__(self, file, df, groups, tipo, aggregator=None):
        
        self.file = file
        self.df = df
        self.groups = groups
        self.aggregator = aggregator
        
        if tipo in Project.valid_types:
            self.tipo = tipo
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.valid_types)}")
    
    
    # Define el tipo como propiedad del objecto
    @property
    def _tipo(self):
        return self.tipo
    
    
    ## Reglas para tipo de dato
    @_tipo.setter
    def _tipo(self, value):
        
        if value in Project.valid_types:
            self.tipo = value
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.valid_types)}")
    
    # Resultado para la función print
    def __str__(self):
        return f"{self.file}"
    
    ## Llama el nombre del archivo
    def self_file(self):
        return self.file
    
    ## Gráfico para observar coordenadas
    def plot_coordinates(self):
        
        coords = self.df.GEOM.to_list()
        
        x = [coord.x for coord in coords]
        y = [coord.y for coord in coords]

        plt.scatter(x, y)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(f"Coordenadas para\n{self.file}")
        plt.show()


    # Para limpiar ruido de un proyecto por una variable
    def cleaning(self, var, minor=None, major=None, avoid=None, select=None):
        
        clean_df = self.df
        
        if minor != None:
                    
            clean_df = clean_df[clean_df[var] > minor]
            
        if major != None:
            
            clean_df = clean_df[clean_df[var] < major]
        
        if avoid != None:
            
            clean_df = clean_df[(clean_df[var] != avoid)]
            
        elif select != None:
                
            clean_df = clean_df[(clean_df[var] == select)]
        
        elif avoid != None and avoid != None:
            
            raise ValueError("No puede seleccionar solo un valor de atributo y evitar otro únicamente")
        
        else:
            
            pass
        
        self.df = clean_df
    
    ## Para estandarizar nivelación
    @classmethod
    def cleaning_levelling(cls, instance, _id, geom, var):

        clean_df = instance.df.rename(columns={_id: 'ID',
                                               geom: 'GEOM',
                                               var: 'ALTURA_M_S'})
        clean_df = clean_df[['ID', 'GEOM', 'ALTURA_M_S']]
        
        return clean_df
    
    
    ## Para estandarizar gravimetría absoluta o 
    @classmethod
    def cleaning_absolute_relative_gravity(cls, instance, _id, geom, var):
        
        clean_df = instance.df.rename(columns={_id: 'ID',
                                               geom: 'GEOM',
                                               var: 'GRAV'})
        clean_df = clean_df[['ID', 'GEOM', 'GRAV']]
        
        return clean_df
    
    
    # Para limpiar variables no necesarias
    def cleaning_var(self, *args):
        
        # Extrae argumentos
        _args = list(args)
        if (len(_args) != 3):
            
            error = """La lista de argumentos proveídos en la función
            y en el dataframe deben seguir el orden:
            - nivelación: nomenclatura (id), geometria,
            altura_sobre_el_nivel_del_mar
            - gravedades absolutas o relativas: nomenclatura (id),
            geometria, gravedad (mGals)
        """
            raise ValueError(error)
        
        _id = _args[0]
        geom = _args[1]
        var = _args[2]
        
        # Variables que del proyecto se seleccionarán
        tipo = self.tipo
        
        if tipo == 'nivelacion':
            
            self.df = Project.cleaning_levelling(self, _id, geom,
                                                 var)
        
        elif tipo == 'gravedad-absoluta' or tipo == 'gravedad-relativa':
            
            self.df = Project.cleaning_absolute_relative_gravity(self,
                                                                 _id, geom,
                                                                 var)
            
        else:
            
            return 'No han sido proporcionados tipos de datos válidos'


class var:
    def __init__(self, file, df, groups, aggregator):
        self.file = file
        self.df = df
        self.groups = groups
        self.aggregator = aggregator
    
    def __str__(self):
        return f"{self.file}"