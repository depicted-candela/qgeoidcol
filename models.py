#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:43:42 2023

@author: nicalcoca
"""

import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame as pdf

## Clase para estandarizar objetos de proyectos de nivelación
## y gravimétricos
class Project:
    
    """ Tipos válidos para proyectos geoidales:
    
        - el tipo 'gravedades' se refiere a un dataframe con gravedades
    absolutas y relativas
        - el tipo 'nivelacion-gravedades' se refiere a un dataframe con
    gravedades absolutas y relativas intersecadas 
    """
    VALID_TYPES = ['nivelacion', 'gravedad-absoluta', 'gravedad-relativa',
                   'gravedades']
    
    
    ## Valores inicializadores
    def __init__(self, file, df, tipo):
        
        # Para validar tipos de formato de objetos de entrada
        if type(file) == str and type(df) == pdf and type(tipo) == str:
            self.__file = file
            self.__df = df
        
        ## Para validar tipo de proyecto
        if tipo in self.VALID_TYPES:
            print(f"Inicializando objeto de {tipo}")
            self.__tipo = tipo
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.VALID_TYPES)}")
        
        ## Para crear grupos basados en el agregador
        self.__aggregator = None
        self.__groups = None
    
    
    ## Define el agregador como propiedad del objeto
    @property
    def aggregator(self):
        return self.__aggregator
    
    ## Define groups como propiedad del objeto
    @property
    def groups(self):
        return self.__groups
        
    
    ## Determinador de agrupaciones
    def aggregator_group(self, agg):
        
        ## Si la variable está en el data frame
        if agg in list(self.df.columns):
            
            def aggregator(self, value):
                self.__aggregator = value
            
            aggregator(self, agg)
            grs = list(set(list(self.df[agg])))

            def groups(self, value):
                self.__groups = value
            
            groups(self, grs)
            
        else:
            raise ValueError(f"La variable {aggregator} no existe")
            
    
    ## Define el agregador como propiedad del objeto
    @property
    def df(self):
        return self.__df
    
    ## Define archivo como propiedad del objeto
    @property
    def file(self):
        return self.__file
    
    # Define el tipo como propiedad del objecto
    @property
    def tipo(self):
        return self.__tipo
    

    ## Reglas para tipo de dato
    def set_df_file_tipo(self, df, file, tipo):
        
        # Para validar tipos de formato de objetos de entrada
        if type(file) == str and type(df) == pdf and type(tipo) == str:
            self.__file = file
            self.__df = df
        else:
            raise TypeError(f"Los valores de entrada {(df, file, tipo)} no son del tipo indicado")
        
        ## Para validar tipo de proyecto
        if tipo in self.VALID_TYPES:
            self.__tipo = tipo
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.VALID_TYPES)}")

    
    # Resultado para la función print
    def __str__(self):
        return f"{self.file}"
    
    
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
        
        clean_df = self.__df
        
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
        
        self.__df = clean_df
    
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
    
    
    ## Para limpiar variables no necesarias
    def cleaning_var(self, *args):
        
        ## Extrae argumentos
        _args = list(args)
        
        ## Comprueba validez de parámetros
        if (len(_args) != 3):
            
            error = """La lista de argumentos proveídos en la función
            y en el dataframe deben seguir el orden:
            - nivelación: nomenclatura (id), geometria,
            altura_sobre_el_nivel_del_mar
            - gravedades absolutas o relativas: nomenclatura (id),
            geometria, gravedad (mGals)
            """
            raise ValueError(error)
        
        ## Para extraer argumentos
        _id = _args[0]
        geom = _args[1]
        var = _args[2]
        
        ## Variable para utilizar función para gravedad o nivelación
        tipo = self.tipo
        
        if tipo == 'nivelacion':
            
            df = self.cleaning_levelling(self, _id, geom,  var)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedad-absoluta' or tipo == 'gravedad-relativa':
            
            df = self.cleaning_absolute_relative_gravity(self, _id, geom,  var)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedades':
            
            raise ValueError(f'Aún no se establece rutina para limpiar archivo de tipo {tipo}')
        
        else:
            
            raise ValueError('No han sido proporcionados tipos de datos válidos')


class GrvLvlProject(Project):
    
    
    VALID_TYPES = ['nivelacion-gravedades-intersectado']
    
    def cleaning_var():
        pass
    def cleaning_absolute_relative_gravity():
        pass
    def cleaning_levelling():
        pass
    