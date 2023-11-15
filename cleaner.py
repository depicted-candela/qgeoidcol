#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:16:51 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from .models import Project, GrvLvlProject, AeroRawProject, TerrainRawProject

import os, argparse, copy
import pandas as pd
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt


class Limpiadores:

    """
    Clase limpiadora de DataFrames
    """

    ## Para limpiar verticalmente (por valor de columnas) un dataframe
    def limpiar_verticalmente(self, prj, var, minor=None, major=None, avoid=None, select=None):
        
        limpiador_vertical = traer_limpiador_vertical(prj)
        df_limpio = limpiador_vertical(prj.df, var, minor, major, avoid, select)

        return df_limpio
    
    ## Para limpiar horizontalmente (por nombre de columnas) un dataframe
    def limpiar_horizontalmente(self, prj, id, var, geom='geometry'):
        
        limpiador_horizontal = traer_limpiador_horizontal(prj)
        df_limpio = limpiador_horizontal(prj.df, id, var, geom)
        
        return df_limpio
    
    ## Para limpiar por línea segmentos límite con variable comparable
    def limpiar_lineas(self, prj, calc, filt, **kwargs):

        limpiador_por_linea = traer_limpiador_por_linea(prj)
        df_limpio = limpiador_por_linea(prj, calc, filt, **kwargs)

        return prj.set_df_file_tipo(df_limpio, prj.file, prj.tipo)

## Limpia líneas utilizando variable comparadora para borrar zonas
## no convergentes al filtro
def traer_limpiador_por_linea(prj):

    if isinstance(prj, AeroRawProject) and prj.empresa == 'carson':

        return _limpiador_linea_carson
    

def _limpiador_linea_carson(prj, cal, fil, **kwargs):

    resultdf = pd.DataFrame(columns=prj.df.columns)

    calc = prj.df.columns.get_loc(cal)
    filt = prj.df.columns.get_loc(fil)

    if 'direction' not in kwargs.keys(): kwargs['direction'] = 'onward'

    for g in prj.groups:
        subdf = prj.return_subdf(g)
        subarray = np.array(subdf)
        subarray = subarray.T
        calc_subarray = subarray[calc]
        filt_subarray = subarray[filt]
        if kwargs['direction'] == 'onward':
            tempdf = __general_onward(calc_subarray, filt_subarray, subdf, g, **kwargs)
        elif kwargs['direction'] == 'backward':
            tempdf = __general_backward(calc_subarray, filt_subarray, subdf, g, **kwargs)
        elif kwargs['direction'] == 'both':
            tempdf = __general_both(calc_subarray, filt_subarray, subdf, g, calc, filt, **kwargs)
        resultdf = pd.concat([resultdf, tempdf])
    
    return resultdf

def __general_both(calc_subarray, filt_subarray, subdf, g, cal, fil, **kwargs):

    cl = __comp_lines_backward(calc_subarray, filt_subarray, g, **kwargs)
    if not cl:
        _tempdf = subdf
    else:
        _tempdf = subdf.iloc[cl:]

    subarray = np.array(_tempdf)
    subarray = subarray.T
    _calc_subarray = subarray[cal]
    _filt_subarray = subarray[fil]

    cl = __comp_lines_onward(_calc_subarray, _filt_subarray, g, **kwargs)
    if not cl:
        _tempdf_c = _tempdf
    else:
        _tempdf_c = _tempdf.iloc[:cl]
    
    return _tempdf_c

def __general_onward(calc_subarray, filt_subarray, subdf, g, **kwargs):
    cl = __comp_lines_onward(calc_subarray, filt_subarray, g, **kwargs)
    if not cl:
        tempdf = subdf
    else:
        tempdf = subdf.iloc[cl:]
    return tempdf

def __general_backward(calc_subarray, filt_subarray, subdf, g, **kwargs):
    cl = __comp_lines_backward(calc_subarray, filt_subarray, g, **kwargs)
    if not cl:
        tempdf = subdf
    else:
        tempdf = subdf.iloc[:cl]
    return tempdf

## Compara si la diferencia entre dos valores es positiva False
## o negativa True
def __comparador_simple(calc, filt):
    dif = calc - filt
    return True if dif < 0 else False

## Detecta primera intersección entre dos líneas
def __sign_change_onward(calc, filt):
    cl = __comparador_simple(calc[0], filt[0])
    for i, csa in enumerate(calc):
        if cl != __comparador_simple(csa, filt[i]):
            return i
    return False

## Detecta primera intersección entre dos líneas
def __sign_change_backward(calc, filt):
    cl = __comparador_simple(calc[0], filt[0])
    for i, csa in enumerate(reversed(calc)):
        if cl != __comparador_simple(csa, filt[len(calc) - 1 - i]):
            return len(calc) - 1 - i
    return False

## Compara si dos muestras son estadísticamente diferentes
def __comp_lines_backward(calc, filt, g, **kwargs):
    index = __sign_change_backward(calc, filt)
    sub_calc = calc[index-1:]
    sub_filt = filt[index-1:]
    sub_calc = pd.to_numeric(sub_calc, errors='coerce')
    sub_filt = pd.to_numeric(sub_filt, errors='coerce')
    time = np.array(range(len(sub_calc)))
    if len(sub_calc) < 7: return None
    t_stat, p_value = stats.ttest_ind(sub_calc, sub_filt, equal_var=True)
    alpha = 0.05  # significance level
    if p_value < alpha:
        if 'plot' in kwargs.keys() and kwargs['plot'] == True:
            plt.plot(time, sub_calc)
            plt.plot(time, sub_filt)
            plt.title(f"Different (bakward {g})")
            plt.show()
        return index
    else:
        if 'plot' in kwargs.keys() and kwargs['plot'] == True:
            plt.plot(time, sub_calc)
            plt.plot(time, sub_filt)
            plt.title(f"Not different (bakward {g})")
            plt.show()
        return None

## Compara si dos muestras son estadísticamente diferentes
def __comp_lines_onward(calc, filt, g, **kwargs):
    index = __sign_change_onward(calc, filt)
    sub_calc = calc[:index+1]
    sub_filt = filt[:index+1]
    sub_calc = pd.to_numeric(sub_calc, errors='coerce')
    sub_filt = pd.to_numeric(sub_filt, errors='coerce')
    time = np.array(range(len(sub_calc)))
    if len(sub_calc) < 7: return None
    t_stat, p_value = stats.ttest_ind(sub_calc, sub_filt, equal_var=True)
    alpha = 0.05  # significance level
    if p_value < alpha:
        if 'plot' in kwargs.keys() and kwargs['plot'] == True:
            plt.plot(time, sub_calc)
            plt.plot(time, sub_filt)
            plt.title(f"Different (onward {g})")
            plt.show()
        return index
    else:
        if 'plot' in kwargs.keys() and kwargs['plot'] == True:
            plt.plot(time, sub_calc)
            plt.plot(time, sub_filt)
            plt.title(f"Not different (onward {g})")
            plt.show()
        return None

## Segmenta el limpiador vertical por tipo de archivo
def traer_limpiador_vertical(prj):
    
    if isinstance(prj, TerrainRawProject):

        if prj.tipo == 'nivelacion' or prj.tipo == 'gravterrabs' or prj.tipo == 'gravterrrel':
            
            return _limpiador_vertical
        
        elif prj.tipo == 'gravs':

            return f"El tipo {prj.tipo} no tiene métodos aún"
        
        else:

            raise ValueError(f"El tipo {prj.tipo} no es adecuado para un proyecto {prj}")
    
    elif isinstance(prj, AeroRawProject):
        
        if prj.tipo == 'crudo-aereo':
            
            return _limpiador_vertical
        
        else:
            
            raise ValueError(f"El tipo {prj.tipo} no tiene métodos aún")
            
    else:

        raise ValueError(f"La clase de proyecto {prj} no es adecuado")
    

## Limpiador vertical de dataframes
def _limpiador_vertical(df, var, minor, major, avoid, select):

    if minor != None:
                
        df = df[df[var] > minor]
        
    if major != None:
        
        df = df[df[var] < major]
    
    if avoid != None:
        
        df = df[(df[var] != avoid)]
        
    elif select != None:
            
        df = df[(df[var] == select)]
    
    elif avoid != None and select != None:
        
        raise ValueError("No puede seleccionar únicamente un valor de atributo y evitar otro")
    
    else:
        
        raise ValueError("Los parámetros de limpieza no limpiaron nada")

    return df


def traer_limpiador_horizontal(prj):

    if isinstance(prj, TerrainRawProject):

        if prj.tipo == 'nivelacion':
            
            pass
        
        elif prj.tipo == 'gravterrabs' or prj.tipo == 'gravterrrel':

            pass
        
        elif prj.tipo == 'gravs':

            pass
        
        else:

            raise ValueError(f"El tipo {prj.tipo} no es adecuado para un proyecto {prj}")

    elif isinstance(prj, AeroRawProject):

        if prj.tipo == 'crudo-aereo':
            
            return _limpiador_horizontal_aerogravimetria

    else:

        raise ValueError(f"La clase de proyecto {prj} no es adecuado")


def _limpiador_horizontal_aerogravimetria(df, **kwargs):
    
    try:
        
        _id = kwargs['id']
        lat = kwargs['lat']
        long = kwargs['long']
        raw_alt = kwargs['raw_alt']
        radar = kwargs['radar']
        terrain = kwargs['terrain']
        raw_vertacc = kwargs['raw_vertacc']
        raw_beamdiff = kwargs['raw_beamdiff']
        adjspten = kwargs['adjspten']
        latcorr = kwargs['latcorr']
        raw_eotv = kwargs['raw_eotv']
        line = kwargs['line']
    
    except:
        
        raise ValueError("Debe ingresar todos los parámetros de la función")
    
    pass




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
        return f'Save to {wd}/{output}'
    
    else:
        
        return clean_df


## Unir gravedad absoluta y relativa
def join_gravities(*args):
    
    _args = list(args)
    
    ## dataframe nuevo para almacenar
    data = pd.DataFrame({'ID': [], 'GEOM': [], 'GRAV': []})
    
    if check_class(args):
        
        files = join_files(_args)
        data = join_df_horizontal(_args)
        
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
def join_df_horizontal(datas):
    
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
                                 GrvLvlProject.VALID_TYPES[0], 'coordenadas')
        
        ## Para objetos de gravimetría
        elif prj_coords in Project.VALID_TYPES[1:len(Project.VALID_TYPES)]:
            
            ## Unir nombres de archivos
            files = join_files([prj2, prj1])
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            return GrvLvlProject(files, intersects(prj2, prj1, coords, umbral),
                                 GrvLvlProject.VALID_TYPES[0], 'coordenadas')
    
    elif largs == 4 and coords == False:
        
        # Para objetos de nivelación
        if prj_coords == Project.VALID_TYPES[0]:
            
            ## Unir nombres de archivos
            files = join_files([prj1, prj2])
            
            return GrvLvlProject(files, intersects(prj1, prj2, coords),
                                 GrvLvlProject.VALID_TYPES[0], 'nomenclatura')
        
        ## Para objetos de gravimetría
        elif prj_coords in Project.VALID_TYPES[1:len(Project.VALID_TYPES)]:
            
            ## Unir nombres de archivos
            files = join_files([prj2, prj1])
            
            ## Para determinar si el proyecto a intersectar es de nivelacion
            ## dado un proyecto de gravimetria
            
            return GrvLvlProject(files, intersects(prj2, prj1, coords),
                                 GrvLvlProject.VALID_TYPES[0], 'nomenclatura')
        
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