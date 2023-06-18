#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:16:51 2023

@author: nicalcoca
"""

import os, argparse
import pandas as pd

from .models import Project
from .read import _aggregator


# Para limpiar ruido de una variable de un archivo csv
def cleaning_csv(wd, file, var, output=None, minor=None, major=None,
                 avoid=None, save = None):
    
    os.chdir(wd)
    
    clean_df = pd.read_csv(file, delimiter=',')
    
    if minor != None:
                
        clean_df = clean_df[clean_df[var] > minor]
        
    if major != None:
        
        clean_df = clean_df[clean_df[var] < major]
    
    if avoid != None:
        
        clean_df = clean_df[(clean_df[var] != avoid)]
        
    if save != None:
        
        clean_df.to_csv(output, sep=',')
    
    else:
        
        return clean_df
    
    return f'Save to {wd}/{output}'


# # Para limpiar ruido de una variable de un proyecto
# def cleaning_prj(proj, var, minor=None, major=None, avoid=None, select=None):
    
#     clean_df = proj.df
    
#     if minor != None:
                
#         clean_df = clean_df[clean_df[var] > minor]
        
#     if major != None:
        
#         clean_df = clean_df[clean_df[var] < major]
    
#     if avoid != None:
        
#         clean_df = clean_df[(clean_df[var] != avoid)]
        
#     elif select != None:
            
#         clean_df = clean_df[(clean_df[var] == select)]
    
#     elif avoid != None and avoid != None:
        
#         raise ValueError("No puede seleccionar solo un valor de atributo y evitar otro únicamente")
    
#     else:
        
#         pass
    
#     proj.df = clean_df
    
#     return proj


# # Para limpiar variables no necesarias
# def cleaning_var(prj, *args):
    
#     """La lista de argumentos proveídos en la función
#     y en el dataframe deben seguir el orden:
#         - nivelación: nomenclatura (id), geometria,
#         altura_sobre_el_nivel_del_mar
#         - gravedades absolutas o relativas: nomenclatura (id),
#         geometria, gravedad (mGals)
#     """
    
#     # Variables que del proyecto se seleccionarán
#     useful_ordered_vars = list(args)
    
#     clean_df = prj.df
#     tipo = prj.tipo
    
#     if tipo == 'nivelacion':
        
#         prj.df = cleaning_levelling(clean_df, useful_ordered_vars)
    
#     elif tipo == 'gravedad absoluta' or tipo == 'gravedad relativa':
        
#         prj.df = cleaning_absolute_relative_gravity(clean_df, useful_ordered_vars)
        
#     else:
#         return None
    
#     return prj


# ## Para estandarizar nivelación
# def cleaning_levelling(clean_df, useful_ordered_vars):

#     clean_df = clean_df.rename(columns={useful_ordered_vars[0]: 'ID',
#                                         useful_ordered_vars[1]: 'GEOM',
#                                         useful_ordered_vars[2]: 'ALTURA_M_S'})
#     clean_df = clean_df[['ID', 'GEOM', 'ALTURA_M_S']]
    
#     return clean_df


# ## Para estandarizar gravimetría absoluta o relativa
# def cleaning_absolute_relative_gravity(clean_df, useful_ordered_vars):
    
#     clean_df = clean_df.rename(columns={useful_ordered_vars[0]: 'ID',
#                                         useful_ordered_vars[1]: 'GEOM',
#                                         useful_ordered_vars[2]: 'GRAV'})
#     clean_df = clean_df[['ID', 'GEOM', 'GRAV']]
    
#     return clean_df


## Unir gravedad absoluta y relativa
def join_gravities(*args):
    
    
    data = pd.DataFrame({'ID': [], 'GEOM': [], 'GRAV': []})
    
    if check_class(args):
        
        #Para trazar los archivos unidos"
        files = ''
        
        #Une los dataframes estructurados"
        for a in args:
            
            _data = a.df
            
            if list(a.df.columns) == ['ID', 'GEOM', 'GRAV']:
            
                data = pd.concat([data, _data], axis=0)
                
            files += a.file + ' '
        
        groups = _aggregator(data)
        
        """Crea el objeto Project de gravedades absolutas
        y relativas unidas"""
        
        joined_gravs = Project(files, data, groups, 'gravedades')
        
        return joined_gravs
    

## Para verificar que objetos sean de la clase Project
def check_class(*args):
    _args = list(args[0])
    
    for a in _args:
        
        if str(type(a)) == str(Project):
            continue
            
        else:
            raise ValueError(f"El objeto {a} no es de la clase {Project}")
    
    return True


## Para intersecar por coordenadas o nomenclatura
def intersects(*args):
    
    _args = list(args)
    tipo = _args[0].tipo
    
    ## Extrae objetos del argumento
    arg1 = _args[0]
    arg2 = _args[1]
    arg3 = _args[2]
    
    
    ## Detecta coincidencias por coordenadas para nivelación
    if len(_args) == 4 and tipo == 'nivelacion' and arg3 == True:
        
        arg4 = _args[3]
        common = arg1.df[arg1.df['GEOM'].apply(lambda point: any(point.distance(other) <= arg4 for other in arg2.df['GEOM']))]
        del common['GEOM_y']
        
        return common.rename(columns={'GEOM_x': 'GEOM'})
            
    ## Detecta coincidencias por nomenclaturas para nivelación
    elif len(_args) == 3 and tipo == 'nivelacion' and arg3 == False:
        
        common = pd.merge(arg1.df, arg2.df, left_on='ID', right_on='ID')
        del common['GEOM_y']
        
        return common.rename(columns={'GEOM_x': 'GEOM'})
    
    ## Detecta coincidencias por coordenadas para gravimetría
    elif len(_args) == 4 and tipo in Project.valid_types[1:len(Project.valid_types)] and arg3 == True:
        
        arg4 = _args[3]
        common = arg2.df[arg2.df['GEOM'].apply(lambda point: any(point.distance(other) <= arg4 for other in arg1.df['GEOM']))]
        del common['GEOM_y']
        
        return common.rename(columns={'GEOM_x': 'GEOM'})
    
    ## Detecta coincidencias por nomenclatura para nivelación
    elif len(_args) == 3 and tipo in Project.valid_types[1:len(Project.valid_types)] and arg3 == False:
        
        common = pd.merge(arg2.df, arg1.df, left_on='ID', right_on='ID')
        del common['GEOM_y']
        
        return common.rename(columns={'GEOM_x': 'GEOM'})

    else:
        
        raise ValueError("Escriba help(levelling_gravity_intersect) para entender cómo utilizar la función")


# Para organizar y depurar conjuntamente nivelación y gravedad.

def levelling_gravity_intersect(**kwargs):

    """
    Los parámetros de este método deben de modo que

    nivelacion: objeto de nivelación
    gravimetria: objeto de gravimetría
    coordenadas: True si el metodo para intersectar es por coordenadas, si no, False para utilizar nomenclaturas
    umbral: si coordenadas es True numérico, si no, omitir
    """
    
    
    niv = kwargs['nivelacion']
    grv = kwargs['gravimetria']
    coords = kwargs['coordenadas']
    
    print(niv.file, grv.file)
    
    ## Para verificar que el objeto base sea correcto
    if niv.file == grv.file:
        raise ValueError("Está utilizando el mismo objeto")
    else:
        pass
        
    ## Para verificar que objetos sean de la clase Project
    if type(niv) == type(grv) == Project:
        pass
    else:
        raise ValueError(f"Objetos no son de la clase: {Project}")
    
    ## Para segmentar las funcionalidades de la función por método
    largs = len(kwargs)
    if largs == 4 and coords == True:

        umbral = kwargs['coordenadas']
        
        # Para objetos de nivelación
        if niv.tipo == 'nivelacion':
            return Project.intersects(niv, grv, coords, umbral)
        
        ## Para objetos de gravimetría
        elif grv.tipo in Project.valid_types[1:len(Project.valid_types)]:
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            return Project.intersects(niv, grv, coords, umbral)
    
    elif largs == 3 and coords == False:
        
        # Para objetos de nivelación
        if niv.tipo == 'nivelacion':
            return intersects(niv, grv, coords)
        
        ## Para objetos de gravimetría
        elif grv.tipo in Project.valid_types[1:len(Project.valid_types)]:
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            return intersects(niv, grv, coords)
        
    else:
        
        raise ValueError("Escriba help(levelling_gravity_intersect) para entender cómo utilizar la función")

     

# Desde el terminal
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dt', type=str, help='Directorio de trabajo')
    
    parser.add_argument('--ai', type=str, help='Archivo de entrada')
    
    parser.add_argument('--v', type=str, help='Variable a limpiar')
    
    help_ao='Archivo de salida dentro del directorio de trabajo'
    parser.add_argument('--ao', type=str, help=help_ao)
    
    help_miv='Valores menores a este se evitan'
    parser.add_argument('--miv', help=help_miv)
    
    help_mav='Valores mayores a este se evitan'
    parser.add_argument('--mav', help=help_mav)
    
    help_mav='Valor a evitar'
    parser.add_argument('--av', help=help_mav)
    
    args = parser.parse_args()
    result = cleaning_csv(args.dt, args.ai, args.v, args.ao, args.miv, args.mav,
                      args.av)
    
    print(result)