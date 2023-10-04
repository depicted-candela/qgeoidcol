from .models import AeroRawProject, RawProject, TerrainRawProject

class Estandarizadores:

    """
    Clase ordenadora de datos
    """

    def estandarizar(self, prj, metodo, var):

        estandarizador = get_estandarizador(prj)
        df_stand = estandarizador(prj, metodo, var)

        return prj.set_df_file_tipo(df_stand, prj.file, prj.tipo)

## Estandarizador para variables
def get_estandarizador(prj):

    if isinstance(prj, AeroRawProject) or isinstance(prj, RawProject) or isinstance(prj, TerrainRawProject):

        return _raw_to

## Divisor de estandarizadores
def _raw_to(prj, metodo, var):

    if metodo == 'z-score':

        return _raw_to_zcore(prj, var)

## Convierte series en series a un arreglo de dos variables e índices
def _raw_to_zcore(prj, var):

    import pandas as pd
    import numpy as np
    
    """
    TRAE LAS ACELERACIONES NORMALIZADAS.

    Parameters
    ----------
    prj : qgeoidcol.models.AeroRawProject
        PROYECTO A CALCULAR.

    Returns
    -------
    pandas.core.frame.DataFrame
        DATA FRAME DEL PROYECTO MÁS CORRECCIONES.

    """

    if var not in prj.df.columns: raise ValueError("Ese variable no existe en el data frame")
    
    array_list = []
    
    ## Itera sobre grupos para extraer variables
    for g in prj.groups:
        
        ## Segmenta por grupo
        group_df = prj.df[prj.df[prj.aggregator] == g]
        group_df = group_df[group_df[var].notnull()]
        group_array = np.array(group_df)
        var_to_change = np.array(group_df[var])
        var_df = group_df[var]
        
        ## Calcula media y desviación estándar
        mean = np.mean(var_df)
        std_dev = np.std(var_df, ddof=0)

        ## Array estandarizado
        z_scores = (var_to_change - mean) / std_dev
        
        ## Concatena arrays
        z_scores = z_scores.reshape(-1, 1)
        group_array = np.hstack((group_array, z_scores))
        
        ## Almacena arrays en lista
        array_list.append(group_array)
    
    # Concatenate arrays vertically
    result_array = np.vstack(array_list)
    
    ## Crea el nuevo data frame con aceleración vertical
    columns = prj.df.columns.to_list()
    columns.append(var + '_zcore')
    acc_df = pd.DataFrame(result_array, columns=columns)
    
    return acc_df
