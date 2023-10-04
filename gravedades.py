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