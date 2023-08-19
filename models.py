#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:43:42 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from pandas.core.frame import DataFrame as pdf

from .string_tools import split_text_in_equal_lines as stiql

from .graphs import anormal_histogram_outlier, normal_histogram_outlier
from .statistics import normality

from metpy import interpolate as interp
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
    
    ## Retorna un dataframe por grupos
    def return_subdf(self, g):
        return self.df[self.df[self.aggregator] == g]
        
    
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
    
    
    ## Interpolación rápida, vecinos naturales
    def natural_neighbor(self, **kwargs):
        
        variable = kwargs['var']
        try:
            avoid = kwargs['avoid']
        except:
            avoid = None
        
        df = self.df
        
        not_null_variable = df[df[variable] != avoid]
        clean_variable = not_null_variable[['GEOM', variable]]
        
        ## Extracción de valores del dataframe
        LAT = np.array(df['GEOM'].apply(lambda point: point.y))
        LONG = np.array(df['GEOM'].apply(lambda point: point.x))
        
        variable_num = clean_variable[[variable]]
        variable_num = np.array([i[0] for i in variable_num.values])
        
        # Define the grid to interpolate Into
        LATi = np.linspace(min(LAT), max(LAT), 100)
        LONGi = np.linspace(min(LONG), max(LONG), 100)
        LONGi, LATi = np.meshgrid(LONGi, LATi)
        
        
        # Interpolate data onto the grid using Natural Neighbor interpolation
        variable_intplt = interp.natural_neighbor_to_grid(LONG,
                                                          LAT,
                                                          variable_num,
                                                          LONGi,
                                                          LATi)
        ## A float
        variable_intplt = np.array(variable_intplt, dtype=float)
        
        # Create a plot
        fig, ax = plt.subplots()
        im = ax.imshow(variable_intplt, extent=[min(LONG), max(LONG), min(LAT),
                                           max(LAT)],
                  origin='lower', cmap='viridis')
        
        # Set the scales of the x and y axes to be the same
        ax.set_xlim([min(LONG), max(LONG)])
        ax.set_ylim([min(LAT), max(LAT)])
        plt.axis('equal')
        plt.colorbar(im, extend='both')
        
        # Add a title
        ax.set_title(f'Interpolación de {variable} con Vecinos Naturales')
        
        # Show the plot
        plt.show()
    
    
    ## Gráfico para observar coordenadas
    def plot_coordinates(self, *args):
        """f
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
        
        fig, ax = plt.subplots()
        plt.scatter(x, y, s=0.1)
        plt.axis('equal')
        plt.xlabel('X')
        plt.ylabel('Y')
        
        ## Si se invoca la función desde instance.histogram_outlier
        ## to plot the coordinates with outliers
        if len(args) > 1:
            
            outs = list(args[1]['id'])
            var = args[2]
            
            ## Extrae coordenadas que tengan los valores atípicos
            ## de la variable dada
            out_coords = self.df.iloc[outs].GEOM.to_list()
            # out_coords = self.df[self.df[var].isin(outs)].GEOM.to_list()
            out_x = [coord.x for coord in out_coords]
            out_y = [coord.y for coord in out_coords]
            
            plt.scatter(out_x, out_y, s=10, c='red')
            title = f"Coordenadas con outliers para {var} de {self.file}"
            title = stiql(title, 52)
            plt.title(title)
        
        else:
            
            ## Si no hay outliers, el mapa lo confirma
            title = f"Coordenadas para {self.file}"
            title = stiql(title, 52)
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
    
    
    ## geometria puntual de variables
    def __pointed_lev(instance, _vars):
        
        from shapely.geometry import Point
        import pandas as pd
        
        ## Selecciona columnas x y y
        geom_array = np.array(instance.df[list(_vars[1:3])])
        
        ## Transforma valores x y y a coordenadas
        points = [Point(ga[0], ga[1]) for ga in geom_array]
        _id = instance.df[_vars[0]]
        var = instance.df[_vars[-1]]
        
        ## Data frame limpio
        points_df = pd.DataFrame({'ID': _id, 'GEOM': points,
                                  'ALTURA_M_S': var})
        
        return points_df
    
    
    ## geometría puntual de shapefile
    def __geometred_lev(instance, _vars):
        
        clean_df = instance.df.rename(columns={_vars[0]: 'ID',
                                               _vars[1]: 'GEOM',
                                               _vars[2]: 'ALTURA_M_S'})
        clean_df = clean_df[['ID', 'GEOM', 'ALTURA_M_S']]
        
        return clean_df
    
    
    ## geometria puntual de variables
    def __pointed_grv(instance, _vars):
        
        from shapely.geometry import Point
        import pandas as pd
        
        ## Selecciona columnas x y y
        geom_array = np.array(instance.df[list(_vars[1:3])])
        
        ## Transforma valores x y y a coordenadas
        points = [Point(ga[0], ga[1]) for ga in geom_array]
        _id = instance.df[_vars[0]]
        var = instance.df[_vars[-1]]
        
        ## Data frame limpio
        points_df = pd.DataFrame({'ID': _id, 'GEOM': points,
                                  'GRAV': var})
        
        return points_df
    
    
    ## geometría puntual de shapefile
    def __geometred_grv(instance, _vars):
        
        clean_df = instance.df.rename(columns={_vars[0]: 'ID',
                                               _vars[1]: 'GEOM',
                                               _vars[2]: 'GRAV'})
        clean_df = clean_df[['ID', 'GEOM', 'GRAV']]
        
        return clean_df
    
    
    ## Para estandarizar nivelación
    @classmethod
    def __cleaning_levelling(cls, instance, _vars):
        
        lvars = len(_vars)
        
        if lvars == 3:
            
            return cls.__geometred_lev(instance, _vars)
        
        elif lvars == 4:

            return cls.__pointed_lev(instance, _vars)
    
    
    ## Para estandarizar gravimetría absoluta o 
    @classmethod
    def __cleaning_absolute_relative_gravity(cls, instance, _vars):
        
        lvars = len(_vars)
        
        if lvars == 3:
            
            return cls.__geometred_grv(instance, _vars)
        
        elif lvars == 4:
            
            return cls.__pointed_grv(instance, _vars)

    
    ## Para limpiar variables no necesarias
    def cleaning_var(self, *args):
        
        ## Extrae argumentos
        _args = list(args)
        
        ## Comprueba validez de parámetros
        toclean_vars = self.df_vars(_args)
        
        ## Variable para utilizar función para gravedad o nivelación
        tipo = self.tipo
        
        if tipo == 'nivelacion':
            
            df = self.__cleaning_levelling(self, toclean_vars)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedad-absoluta' or tipo == 'gravedad-relativa':
            
            df = self.__cleaning_absolute_relative_gravity(self, toclean_vars)
            self.set_df_file_tipo(df, self.file, self.tipo)
        
        elif tipo == 'gravedades':
            
            raise ValueError(f'Aún no se establece rutina para limpiar por variable archivo de tipo {tipo}')
        
        else:
            
            raise ValueError('No han sido proporcionados tipos de datos válidos')
    
    ## Mensage de ilustrativo
    def df_vars_message():
        
        """
        
        
        Returns
        -------
        Mensaje.

        """
        
        
        return """La lista de argumentos proveídos en la función
        y en el dataframe deben seguir el orden:
            
        i. Si las coordenadas provienen de la geometría de un shapefile o
        geopackage
            - nivelación: nomenclatura (id), geometria,
            altura_sobre_el_nivel_del_mar (m)
            - gravedades absolutas o relativas: nomenclatura (id),
            geometria, gravedad (mGals)
        ii. Si las coordenadas provienen de variables de shapefile,
        geopackage o csv
            - nivelación: nomenclatura (id), x, y,
            altura_sobre_el_nivel_del_mar (m)
            - gravedades absolutas o relativas: nomenclatura (id), x, y
            gravedad (mGals)
            """
    
    ## Par de coordenadas a puntos
    def pointed(self, args):
        
        _id = args[0]
        x = args[1]
        y = args[2]
        var = args[3]
        
        return _id, x, y, var
    
    ## Punto geometrizado
    def geometred(self, args):
        
        _id = args[0]
        geom = args[1]
        var = args[2]
        
        return _id, geom, var
    
    
    ## Creador de variables
    def df_vars(self, args):
        
        _args = list(args)
        _largs = len(_args)
        
        ## Comprueba validez de parámetros
        if _largs not in [3, 4]:
            
            ## Mensaje ilustrativo
            self.df_vars_message()
        
        ## Geometría desde shapefile
        elif _largs == 3:
            
            return self.geometred(_args)
        
        ## Geometría desde par de variables
        else:
            
            return self.pointed(_args)
    
    
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
        
        result_list = list(range(obg, obg+opt + 1, 1))
        
        if l_kwargs not in result_list or invalid_keys != 0 or invalid_var:
            
            raise ValueError(h)
        
        else:
            return l_kwargs
    
    
    ## Para reducir tamaño de histogram_outlier
    def histogram_xy_plot(self, outliers, var):
        
        # Si no hay outliers
        if outliers is None:
            
            self.plot_coordinates(self)
            
            return None
        
        else:
            
            self.plot_coordinates(self, outliers, var)
        
            return outliers
    
    
    ## Para detectar outliers dada una variable y un dataframe base
    def histogram_outlier(self, **kwargs):
        """
        Utilice este método tal que:
            
            - Con umbral de detección de outliers predeterminado (3):
            instance.histogram_outlier(var='variable')
            
            - Con umbral de detección de outliers personalizado:
            instance.histogram_outlier(var='variable', umbral=2)
            
            - Con umbral de detección de outliers no normal personalizado:
            instance.histogram_outlier(var='variable', cont=0.1, est='nombre')
        """
        
        ## Parámetros permitidos
        PARGS = ['var', 'umbral', 'cont', 'est']
        
        ## Estandarización de parámetros
        lkwargs = self.__cond_outlier(pargs=PARGS, kwargs=kwargs, obg=1, opt=3,
                                    method='histogram_outlier')
        
        ## Extracción de kwargs
        var = kwargs['var']
        
        ## Extracción de valores del dataframe
        array = np.array(self.df[var])
        
        ## Para detectar outliers con media o SVM
        # Media
        if normality(array):
            
            umbral = 3
            
            if lkwargs == 2:
                umbral = kwargs['umbral']
            
            # Detecta outliers de una variable normal
            outliers = normal_histogram_outlier(array, umbral, var)
            
            return self.histogram_xy_plot(outliers, var)
            
        # SVM
        else:
            
            contamination = kwargs['cont']
            estacion = kwargs['est']
            
            # Detecta outliers de una variable anormal
            outliers = anormal_histogram_outlier(self, var, contamination, estacion)
            
            return self.histogram_xy_plot(outliers, var)
        
        
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


class RawProject(Project):
    
    ## Tipos válidos
    VALID_TYPES = ['crudo']
    
    ## Define el agregador como propiedad del objeto
    @property
    def df(self):
        return self._Project__df
    
    ## Define archivo como propiedad del objeto
    @property
    def file(self):
        return self._Project__file
    
    # Define el tipo como propiedad del objecto
    @property
    def tipo(self):
        return self._Project__tipo
    
    ## Methods to avoid
    def cleaning_var():
        pass
    def __cleaning_absolute_relative_gravity():
        pass
    def __cleaning_levelling():
        pass
    
    # Gráfico de todas las líneas
    def values_per_group(self, var_name):
        
        df = self.df
        aggr = self.aggregator
        
        ## Para determinar agregador
        if aggr in df.columns:
            grpd_data = df.groupby([aggr])[var_name].apply(list).to_dict()
        else:
            raise ValueError("Primero determine la variable agregadora con instance.aggregator_group('variable agregadora')")
        
        # Plotting the graph
        for key, values in grpd_data.items():
            plt.plot(values, label=key)
        
        # Customize the plot
        plt.xlabel('X')
        plt.ylabel(f'{var_name}')
        plt.title('Todos los grupos')
        plt.legend()
        
        # Display the plot
        plt.show()
    
    # Gráfico de diez líneas
    def values_per_group_limited(self, var_name, start, end):
        
        df = self.df
        aggr = self.aggregator
        grps = self.groups
        
        ## Para confirmar agregador
        if aggr in df.columns:
            grpd_data = df.groupby([aggr])[var_name].apply(list).to_dict()
        else:
            raise ValueError("Primero determine la variable agregadora con instance.aggregator_group('variable agregadora')")
            
        keys = list(grpd_data.keys())[start: end]
        subset_dict = {key: grpd_data[key] for key in keys if key in grpd_data}
        
        # Plotting the graph
        for key, values in subset_dict.items():
            plt.plot(values, label=key)
        
        # Customize the plot
        plt.xlabel('obs')
        plt.ylabel(f'{var_name}')
        plt.title(f'Grupos desde {start} hasta {end} de {len(grps)}')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
        # Display the plot
        plt.show()
    

class AeroRawProject(RawProject):
    
    """Clase para proyectos crudos de aerogravimetría"""
    
    ## Tipos válidos
    VALID_TYPES = ['crudo-aereo']
    

class TerrainRawProject(RawProject):
    
    """Clase para proyectos crudos de aerogravimetría"""
    
    ## Tipos válidos
    VALID_TYPES = ['crudo-terreno']
    


class GrvLvlProject(Project):
    
    ## Tipos válidos
    VALID_TYPES = ['nivelacion-gravedades-intersectado']
    
    ## Métodos válidos
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
            print(f"Inicializando objeto de {tipo} con metodo {metodo}")
            self.__metodo = metodo
            
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
    
    # Define el método como propiedad del objecto
    @property
    def metodo(self):
        return self._GrvLvlProject__metodo
    
    ## Methods to avoid
    def cleaning_var():
        pass
    def __cleaning_absolute_relative_gravity():
        pass
    def __cleaning_levelling():
        pass


class GrvLvlCorrProject(Project):
    
    ## Tipos válidos
    VALID_TYPES = ['nivelacion-gravedades-intersectado-correcciones']
    
    ## Métodos válidos
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
            print(f"Inicializando objeto de {tipo} con metodo {metodo}")
            self.__metodo = metodo
            
        else:
            raise ValueError(f"Valores válidos para tipo son: {', '.join(self.METODO_CALCULO)}")
        
        ## Para crear grupos basados en el agregador
        self.__aggregator = None
        self.__groups = None
    
    ## Define el agregador como propiedad del objeto
    @property
    def df(self):
        return self._GrvLvlCorrProject__df
    
    ## Define archivo como propiedad del objeto
    @property
    def file(self):
        return self._GrvLvlCorrProject__file
    
    # Define el tipo como propiedad del objecto
    @property
    def tipo(self):
        return self._GrvLvlCorrProject__tipo
    
    # Define el método como propiedad del objecto
    @property
    def metodo(self):
        return self._GrvLvlCorrProject__metodo
    
    ## Methods to avoid
    def cleaning_var():
        pass
    def __cleaning_absolute_relative_gravity():
        pass
    def __cleaning_levelling():
        pass
