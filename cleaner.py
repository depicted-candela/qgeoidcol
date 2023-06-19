#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:16:51 2023

@author: nicalcoca
"""

import os, argparse
import pandas as pd
import copy

from .models import Project, GrvLvlProject


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


## Unir gravedad absoluta y relativa
def join_gravities(*args):
    
    _args = list(args)
    
    ## dataframe nuevo para almacenar
    data = pd.DataFrame({'ID': [], 'GEOM': [], 'GRAV': []})
    
    if check_class(args):
        
        files = join_files(_args)
        
        data = join_df(_args)
        
        """Crea el objeto Project de gravedades absolutas
        y relativas unidas"""
        
        joined_gravs = Project(files, data, 'gravedades')
        
        return joined_gravs

## Para unir nombres de archivos
def join_files(fs):
    #Para trazar los archivos unidos"
    files = ''
    for f in fs:
        
        files += f.file + ' '
        
    return files.rstrip()

## Para unir data frames
def join_df(datas):
    
    ## dataframe nuevo para almacenar
    data = pd.DataFrame({'ID': [], 'GEOM': [], 'GRAV': []})
    
    for d in datas:
        
        _data = d.df
        
        if list(d.df.columns) == ['ID', 'GEOM', 'GRAV']:
            
            data = pd.concat([data, _data], axis=0)
        
    return data

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
    
    df1 = arg1.df
    df2 = arg2.df

    ## Detecta coincidencias por coordenadas para nivelación
    if len(_args) == 4 and tipo == 'nivelacion' and arg3 == True:

        arg4 = _args[3]
        common = df1[df1['GEOM'].apply(lambda point: any(point.distance(other) <= arg4 for other in df2['GEOM']))]
        
        __df2 = copy.deepcopy(df2)

        del __df2['GEOM']
        common = pd.merge(common, __df2, left_on='ID', right_on='ID')
        
        return common
            
    ## Detecta coincidencias por nomenclaturas para nivelación
    elif len(_args) == 3 and tipo == 'nivelacion' and arg3 == False:
        
        common = pd.merge(df1, df2, left_on='ID', right_on='ID')
        del common['GEOM_y']
        
        return common.rename(columns={'GEOM_x': 'GEOM'})
    
    ## Detecta coincidencias por coordenadas para gravimetría
    elif len(_args) == 4 and tipo in Project.VALID_TYPES[1:len(Project.VALID_TYPES)] and arg3 == True:
        
        arg4 = _args[3]
        common = df2[df2['GEOM'].apply(lambda point: any(point.distance(other) <= arg4 for other in df1['GEOM']))].merge(df1[['GEOM','ALTURA_M_S']], on='GEOM')

        __df1 = copy.deepcopy(df1)
        del __df1['GEOM']
        
        common = pd.merge(common, __df1, left_on='ID', right_on='ID')
        
        return common
    
    ## Detecta coincidencias por nomenclatura para nivelación
    elif len(_args) == 3 and tipo in Project.VALID_TYPES[1:len(Project.VALID_TYPES)] and arg3 == False:
        
        common = pd.merge(df2, df1, left_on='ID', right_on='ID')
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
    prj_coords: tipo de objeto de coordenadas base
    coordenadas: True si el metodo para intersectar es por coordenadas, si no, False para utilizar nomenclaturas
    umbral: si coordenadas es True numérico, si no, omitir
    """
    
    prj1 = kwargs['nivelacion']
    prj2 = kwargs['gravimetria']
    prj_coords = kwargs['prj_coords']
    coords = kwargs['coordenadas']
    
    
    ## Para verificar que objetos no sean el mismo
    if prj1.file == prj2.file:
        raise ValueError("Está utilizando el mismo objeto")
    else:
        pass
    
    ## Para verificar que objetos sean de la clase Project
    if type(prj1) == type(prj2) == Project:
        pass
    else:
        raise ValueError(f"Objetos no son de la clase: {Project}")
        
    ## Para verificar que la proveniencia de coordenadas sea bien especificada
    if prj_coords in Project.VALID_TYPES:
        pass
    else:
        raise ValueError(f"El tipo de objeto {prj_coords} de coordenadas de base no existe")

    
    ## Para segmentar las funcionalidades de la función por método
    largs = len(kwargs)
    if largs == 5 and coords == True:

        umbral = kwargs['umbral']
        
        # Para objetos de nivelación
        if prj_coords == Project.VALID_TYPES[0]:
            
            ## Unir nombres de archivos
            files = join_files([prj1, prj2])
            
            return GrvLvlProject(files, intersects(prj1, prj2, coords, umbral),
                                 GrvLvlProject.VALID_TYPES[0])
        
        ## Para objetos de gravimetría
        elif prj_coords in Project.VALID_TYPES[1:len(Project.VALID_TYPES)]:
            
            ## Unir nombres de archivos
            files = join_files([prj2, prj1])
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            return GrvLvlProject(files, intersects(prj2, prj1, coords, umbral),
                                 GrvLvlProject.VALID_TYPES[0])
    
    elif largs == 4 and coords == False:
        
        # Para objetos de nivelación
        if prj_coords == Project.VALID_TYPES[0]:
            
            ## Unir nombres de archivos
            files = join_files([prj1, prj2])
            
            return GrvLvlProject(files, intersects(prj1, prj2, coords),
                                 GrvLvlProject.VALID_TYPES[0])
        
        ## Para objetos de gravimetría
        elif prj_coords in Project.VALID_TYPES[1:len(Project.VALID_TYPES)]:
            
            ## Unir nombres de archivos
            files = join_files([prj2, prj1])
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            
            return GrvLvlProject(files, intersects(prj2, prj1, coords),
                                 GrvLvlProject.VALID_TYPES[0])
        
        
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