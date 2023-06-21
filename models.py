#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:43:42 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from pandas.core.frame import DataFrame as pdf

from .graphs import anormal_histogram_outlier, normal_histogram_outlier
from .statistics import normality

import matplotlib.pyplot as plt
import numpy as np


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
    def plot_coordinates(self, *args):
        """
        

        Parametros
        ----------
        *args : no ingresar si utiliza la función directamente
            (con la forma instance.plot_coordinates()), estos
            parámetros se utilizan internamente en la función
            histogram_outlier(var='---------')

        Returns
        -------
        None.

        """
        
        
        coords = self.df.GEOM.to_list()
        
        x = [coord.x for coord in coords]
        y = [coord.y for coord in coords]
        
        plt.figure(2)
        plt.scatter(x, y, s=0.1)
        plt.xlabel('X')
        plt.ylabel('Y')
        
        ## Si se invoca la función desde instance.histogram_outlier
        ## to plot the coordinates with outliers
        if len(args) > 1:
            
            outs = list(args[1]) 
            var = args[2]
            
            ## Extrae coordenadas que tengas los valores atípicos
            ## de la variable dada
            out_coords = self.df[self.df[var].isin(outs)].GEOM.to_list()
            out_x = [coord.x for coord in out_coords]
            out_y = [coord.y for coord in out_coords]
            
            plt.scatter(out_x, out_y, s=1, c='red')
            plt.title(f"Coordenadas con outliers\npara {var} de {self.file}")
        
        else:
            
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
    def __cleaning_levelling(cls, instance, _id, geom, var):

        clean_df = instance.df.rename(columns={_id: 'ID',
                                               geom: 'GEOM',
                                               var: 'ALTURA_M_S'})
        clean_df = clean_df[['ID', 'GEOM', 'ALTURA_M_S']]
        
        return clean_df
    
    
    ## Para estandarizar gravimetría absoluta o 
    @classmethod
    def __cleaning_absolute_relative_gravity(cls, instance, _id, geom, var):
        
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
            
            df = self.__cleaning_levelling(self, _id, geom,  var)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedad-absoluta' or tipo == 'gravedad-relativa':
            
            df = self.__cleaning_absolute_relative_gravity(self, _id, geom,  var)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedades':
            
            raise ValueError(f'Aún no se establece rutina para limpiar archivo de tipo {tipo}')
        
        else:
            
            raise ValueError('No han sido proporcionados tipos de datos válidos')
    
    
    ## Condiciones para funciones de detección de outliers
    def __cond_outlier(self, **kwargs):
        
        pargs = kwargs['pargs']
        _kwargs = kwargs['kwargs']
        obg = kwargs['obg']
        opt = kwargs['opt']
        method = kwargs['method']
        
        ## Parámetros permitidos
        invalid_keys = len([a for a in _kwargs.keys() if a not in pargs])
        
        ## Variables del objeto
        invalid_var = list(_kwargs.values())[0] not in self.df.columns
        
        ## Mensaje de ayuda
        h = f"Escriba en consola help(models.Project.{method})\n"
        h += "para más información"        
        
        ## Validez de kwargs
        l_kwargs = len(_kwargs)
        if l_kwargs not in [obg, obg+opt] or invalid_keys != 0 or invalid_var:
            
            raise ValueError(h)
        
        else:
            return l_kwargs

    
    ## Para detectar outliers dada una variable y un dataframe base
    def histogram_outlier(self, **kwargs):
        """
        Utilice este método tal que:
            
            - Con umbral de detección de outliers predeterminado (3):
            instance.histogram_outlier(var='variable')
            
            - Con umbral de detección de outliers personalizado:
            instance.histogram_outlier(var='variable', umbral=2)
        """
        
        ## Parámetros permitidos
        PARGS = ['var', 'umbral']
        
        ## Estandarización de parámetros
        lkwargs = self.__cond_outlier(pargs=PARGS, kwargs=kwargs, obg=1, opt=1,
                                    method='histogram_outlier')
        
        ## Extracción de kwargs
        var = kwargs['var']
        umbral = 3
        
        if lkwargs == 2:
            umbral  = kwargs['umbral']
        
        ## Extracción de valores del dataframe
        array = np.array(self.df[var])
        
        ## Para detectar outliers con media o SVM
        # Media
        if normality(array):
            outliers = normal_histogram_outlier(array, umbral, var)
            
        # SVM
        else:
            
            # Detecta outliers de una variable anormal
            outliers = anormal_histogram_outlier(self, var)
            
            # Si no hay outliers
            if outliers is None:
                
                self.plot_coordinates(self)
            
            else:
                
                self.plot_coordinates(self, outliers, var)
            
            return outliers
    
    ## Para detectar outliers dada una variable y un dataframe base
    def boxcox_outlier(self, **kwargs):
        
        """
        Utilice este método tal que:
            
            - instance.simple_outlier(var='variable')
        """
        
        import seaborn as sns
        
        ## Parámetros permitidos
        PARGS = ['var']
        
        self.__cond_outlier(pargs=PARGS, kwargs=kwargs, obg=1, opt=0,
                            method='boxcox_outlier')
        
        ## Extracción de kwargs
        var = kwargs['var']
        
        ## Extracción de valores del dataframe
        array = np.array(self.df[var])
        
        ## Gráfico box plot
        sns.boxplot(data=array)
        
        ## Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        plt.title(f'Box-Cox para: {var}')
        plt.show()
    
    
    ## Para mostrar espacialmente los outliers
    
    
class GrvLvlProject(Project):
    
    
    VALID_TYPES = ['nivelacion-gravedades-intersectado']
    METODO_CALCULO = ['nomenclatura', 'coordenadas']
    
    ## Valores inicializadores
    def __init__(self, file, df, tipo, metodo):
        
        # Para validar tipos de formato de objetos de entrada
        cond1 = type(file) == str
        cond2 = type(df) == pdf
        cond3 = type(tipo) == str
        cond4 = type(metodo) == str
        
        if cond1 and cond2 and cond3 and cond4:
            self.__file = file
            self.__df = df
        
        ## Para validar tipo de proyecto
        if tipo in self.VALID_TYPES:
            self.__tipo = tipo
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.VALID_TYPES)}")
            
        ## Para validar tipo de proyecto
        if metodo in self.METODO_CALCULO:
            print(f"Inicializando objeto de {tipo}")
            self.__tipo = tipo
            
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.METODO_CALCULO)}")
        
        ## Para crear grupos basados en el agregador
        self.__aggregator = None
        self.__groups = None
    
    
    ## Define el agregador como propiedad del objeto
    @property
    def df(self):
        return self._GrvLvlProject__df
    
    ## Define archivo como propiedad del objeto
    @property
    def file(self):
        return self._GrvLvlProject__file
    
    # Define el tipo como propiedad del objecto
    @property
    def tipo(self):
        return self._GrvLvlProject__tipo
    
    
    def cleaning_var():
        pass
    def __cleaning_absolute_relative_gravity():
        pass
    def __cleaning_levelling():
        pass
    