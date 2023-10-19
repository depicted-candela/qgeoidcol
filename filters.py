from .models import AeroRawProject, RawProject, TerrainRawProject
from .string_tools import split_text_in_equal_lines as stiql

import numpy as np

class Filtros:
    
    """
    Clase calculadora de aceleraciones
    """
    
    def filtrar(self, prj, metodo, **kwargs):
        
        filtrador = get_filtros(prj, metodo)
        fil_df = filtrador(prj, kwargs)
        
        return fil_df
        # return prj.set_df_file_tipo(fil_df, prj.file, prj.tipo)


def get_filtros(prj, metodo):
    
    """
    TRAE LAS ACELERACIONES.

    Parameters
    ----------
    prj : qgeoidcol.models.RawProject
        PROYECTO A CALCULAR.
    metodo : string
        MÉTODO A UTILIZAR PARA FILTRAR
    Returns
    -------
    pandas.core.frame.DataFrame
        DATA FRAME DEL PROYECTO MÁS CORRECCIONES.

    """

    cond1 = isinstance(prj, AeroRawProject) or str(type(prj)) == str(AeroRawProject)
    cond2 = isinstance(prj, RawProject) or str(type(prj)) == str(RawProject)
    cond3 = isinstance(prj, TerrainRawProject) or str(type(prj)) == str(TerrainRawProject)

    if cond1 or cond2 or cond3:

        if metodo == 'carson':

            return _filtro_carson
    
    else:

        raise ValueError("Tipo de proyecto no soportado")

def _filtro_carson(prj, kwargs):

    import numpy as np
    
    NUM_VARS = 3

    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VARIABLE A FILTRAR, PERIODO DE LA SEÑAL PARA FILTRAR Y CANTIDAD DE FILTRADOS
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    if len(kwargs) != NUM_VARS:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo {NUM_VARS}")
    
    try:
        var = kwargs["var"]
        w = kwargs["w0"]
        f = kwargs["f"]
        print(var, w, f)
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (var not in prj.df.columns): raise ValueError(f"La variable {var} no están en los datos del objeto")
    if (type(w) != int): raise ValueError(f"La variable {w} debe ser de tipo int")
    if (type(f) != int): raise ValueError(f"La variable {f} debe ser de tipo int")
    if (w < 1): raise ValueError(f"La variable {w} debe ser mayor a cero")
    if (f < 1): raise ValueError(f"La variable {f} debe ser mayor a cero")

    ## Performs the filter by Carson
    w0 = 1 / w
    a = (w0 * w) / 2
    raw = __ida_carson(prj.groups, prj.aggregator, prj.df, a, w, f, var)
    raw = __vuelta_carson(prj.groups, prj.aggregator, prj.df, a, w, f, var)

    # tempdf = prj.df
    # tempdf[var+'_CARSON_F'] = raw

    # return tempdf
    return raw

## Filtra con Carson desde el principio
def __ida_carson(gr, aggr, df, a, lag, f, var):

    final_list = dict()

    # Filtra por grupo
    for g in gr:

        ## Segmenta por grupo
        group_df = df[df[aggr] == g][var]
        group_array = np.array(group_df)

        ## Veces para filtrar
        for j in range(f):
            
            # Filtro
            for i in range(0, len(group_array) - 1):
                if i == 0:
                    x_b = group_array[0]
                elif i < lag:
                    x_b = group_array[:i].mean()
                else:
                    x_b = group_array[i-lag:i].mean()
                x_n = group_array[i]
                x_n_1 = group_array[i + 1]
                x_b_n_1 = ((1 - a)/(1 + a)) * x_b + (a / (1 + a)) * (x_n_1 + x_n)
                group_array[i + 1] = x_b_n_1
        
        final_list[g] = group_array

    return final_list

## Filtra con Carson desde el final
def __vuelta_carson(gr, aggr, df, a, lag, f, var):

    final_list = dict()

    # Filtra por grupo
    for g in gr:

        ## Segmenta por grupo
        group_df = df[df[aggr] == g][var]
        group_array = np.array(group_df)

        ## Veces para filtrar
        for j in range(f):

            ## Filtro inverson de Carson
            for j in range(-1, -len(group_array), -1):
                if j >= -lag:
                    x_b = group_array[j:].mean()
                else:
                    x_b = group_array[j:j+lag].mean()
                x_n = group_array[j]
                x_n_1 = group_array[j - 1]
                x_b_n_1 = ((1 - a)/(1 + a)) * x_b + (a / (1 + a)) * (x_n_1 + x_n)
                group_array[j - 1] = x_b_n_1

        final_list[g] = group_array

    return final_list