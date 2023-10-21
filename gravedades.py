from .models import AeroRawProject
from .string_tools import split_text_in_equal_lines as stiql

class Gravedades:
    
    """
    Clase calculadora de aceleraciones
    """
    
    def calcular_gravedad(self, prj, metodo, **kwargs):
        
        calculador = get_gravedades(prj, metodo)
        df_con_grav = calculador(prj.df, kwargs)
        
        return prj.set_df_file_tipo(df_con_grav, prj.file, prj.tipo)


def get_gravedades(prj, metodo):
    
    """
    TRAE LAS ACELERACIONES.

    Parameters
    ----------
    prj : qgeoidcol.models.RawProject
        PROYECTO A CALCULAR.

    Returns
    -------
    pandas.core.frame.DataFrame
        DATA FRAME DEL PROYECTO MÁS CORRECCIONES.

    """

    if isinstance(prj, AeroRawProject) or str(type(prj)) == str(AeroRawProject):

        if metodo == 'relativa':

            return _aerogravimetria_relativa

        elif metodo == 'relativa_vertacc':

            return _aerogravimetria_relativa_vertacc

        elif metodo == 'relativa_vertacc_eotvos':
    
            return _aerogravimetria_relativa_vertacc_eotvos
        
        elif metodo == 'relativa_eotvos':

            return _aerogravimetria_relativa_eotvos
        
        else:

            raise ValueError("El método no está disponible, los métodos son 'relativa', 'relativa_vertacc', 'relativa_vertacc_eotvos' y 'relativa_eotvos'")
    
    else:

        raise ValueError("Tipo de proyecto no soportado")

def _aerogravimetria_relativa(df, kwargs):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VARIABLES DE RESORTE Y HAZ.
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    if len(kwargs) != 2:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo dos")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in df.columns or spring not in df.columns):
        raise ValueError(f"Las variables {beam} o {spring} no están en los datos del objeto")

    df['GRAV_REL'] = df[beam] + df[spring]

    return df


def _aerogravimetria_relativa_vertacc(df, kwargs):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VARIABLES DE RESORTE Y HAZ.
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    if len(kwargs) != 3:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo dos")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        vertacc = kwargs["vertacc"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in df.columns or spring not in df.columns or vertacc not in df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {vertacc} no están en los datos del objeto")

    df['GRAV_REL_VA'] = df[beam] + df[spring] - df[vertacc]

    return df


def _aerogravimetria_relativa_vertacc_eotvos(df, kwargs):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VARIABLES DE RESORTE Y HAZ.
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    if len(kwargs) != 4:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo dos")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        vertacc = kwargs["vertacc"]
        eotvos = kwargs["eotvos"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in df.columns or spring not in df.columns or vertacc not in df.columns or eotvos not in df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {vertacc} o {eotvos} no están en los datos del objeto")

    df['GRAV_REL_VA_E'] = df[beam] + df[spring] - df[vertacc] + df[eotvos]

    return df

def _aerogravimetria_relativa_eotvos(df, kwargs):
    
    """
    PARA REGRESAR ACELERACIONES DE PROYECTOS AÉREOS

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VARIABLES DE RESORTE Y HAZ.
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """

    if len(kwargs) != 3:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo dos")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        eotvos = kwargs["eotvos"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in df.columns or spring not in df.columns or eotvos not in df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {eotvos} no están en los datos del objeto")

    df['GRAV_REL_E'] = df[beam] + df[spring] + df[eotvos]

    return df