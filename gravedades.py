from .models import AeroRawProject
from .string_tools import split_text_in_equal_lines as stiql


class Gravedades:
    
    """
    Clase calculadora de aceleraciones
    """
    
    def calcular_gravedad(self, prj, metodo, **kwargs):
        
        calculador = get_gravedades(prj, metodo)
        df_con_grav = calculador(prj, **kwargs)
        
        return prj.set_df_file_tipo(df_con_grav, prj.file, prj.tipo)


def __base(name, df, prj, **kwargs):

    """
    PARA AÑADIR BASE GRAVIMÉTRICA A LECTURAS RELATIVAS DE PROYECTOS AÉREOS

    Parameters
    ----------
    name : string
        NOMBRE DE NUEVA VARIABLE SIN BASE GRAVIMÉTRICA ASOCIADA
    df : pandas.core.frame.DataFrame
        PROYECTO A CALCULAR.
    kwargs : lista de string
        VALOR DECIMAL DE LA BASE GRAVIMÉTRICA ASOCIADA AL PROYECTO.
    Raises
    ------
    ValueError
        MENSAJE DE ERROR POR VARIABLES ERRONEAS.

    Returns
    -------
    pandas.core.frame.DataFrame.
        DATAFRAME CON ACELERACIÓN CALCULADA

    """
        
    if 'base' in kwargs.keys():
        if type(kwargs['base']) != float: raise ValueError("El valor de la base debe ser decimal")
        df[name + '_CON_ABSOLUTA'] = df[name] + kwargs['base']
        return df
    if 'exact' in kwargs.keys() and type(kwargs['exact']) == float and kwargs['exact'] > 0:
        prj.set_exactitud(kwargs['exact'])
    else:
        raise ValueError("La exactitud debe ser decimal y positiva")


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

        elif metodo == 'normal':

            return _gravedad_normal_elip
        
        elif metodo == 'carson_indirect':

            return _aerogravimetria_relativa_carson_indirect

        else:

            raise ValueError("El método no está disponible, los métodos son 'relativa', 'relativa_vertacc', 'relativa_vertacc_eotvos' y 'relativa_eotvos'")
    
    else:

        raise ValueError("Tipo de proyecto no soportado")

def __aerograv_rel_carson_ind_validator(**kwargs):

    if 'free_air' not in kwargs.keys() or 'free_air_corr' not in kwargs.keys():
        raise ValueError("Debes prover variables de 'free_air_corr' y 'free_air'")
    
def _aerogravimetria_relativa_carson_indirect(prj, **kwargs):

    __aerograv_rel_carson_ind_validator(**kwargs)

    if 'normal' not in kwargs.keys():
        kwargs['normal'] = 'NORMAL_GRAV'
        subdf = _gravedad_normal_elip(prj)
    else:
        subdf = prj.df
    
    subdf['GRAV'] = subdf[kwargs['free_air']] + subdf[kwargs['normal']] - subdf[kwargs['free_air_corr']]

    return subdf

    
def __grv_normal_validator(prj):

    if 'GEOM' not in prj.df.columns: raise ValueError('El objeto debe tener una variable geométrica GEOM')

def _gravedad_normal_elip(prj):

    __grv_normal_validator(prj)

    from pyshtools.gravmag import NormalGravity as ng
    from .elipsoides import GRS_80

    grs80 = GRS_80()

    ## Gravedad normal con elipsoide GRS80
    normalgrav = ng(prj.df['GEOM'].apply(lambda x: ___geom_phi(x)),
                    grs80.GM, grs80.W,
                    grs80.A, grs80.B) * 100000
    
    subdf = prj.df
    subdf['NORMAL_GRAV'] = normalgrav

    return subdf

def _aerogravimetria_relativa(prj, **kwargs):
    
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

    if len(kwargs) not in [2, 3, 4]:
        raise ValueError(f"Las variables en {kwargs.values} deben ser dos, tres o cuatro")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in prj.df.columns or spring not in prj.df.columns):
        raise ValueError(f"Las variables {beam} o {spring} no están en los datos del objeto")

    df = prj.df
    df['REL'] = df[beam] + df[spring]

    df = __base('REL', df, prj, **kwargs)

    return df

def _aerogravimetria_relativa_vertacc(prj, **kwargs):
    
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

    if len(kwargs) not in  [3, 4, 5]:
        raise ValueError(f"Las variables en {kwargs.values} deben ser solo dos")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        vertacc = kwargs["vertacc"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in prj.df.columns or spring not in prj.df.columns or vertacc not in prj.df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {vertacc} no están en los datos del objeto")

    ## Calcula lectura relativa corrigiendo con aceleración
    ## vertical
    df = prj.df
    df['REL_VA'] = df[beam] + df[spring] - df[vertacc]

    df = __base('REL_VA', df, prj, **kwargs) ## Si es proporcionada la base gravimétrica

    return df


def _aerogravimetria_relativa_vertacc_eotvos(prj, **kwargs):
    
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

    if len(kwargs) not in [4, 5, 6]:
        raise ValueError(f"Las variables en {kwargs.values} deben ser cuatro, cinco o seis")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        vertacc = kwargs["vertacc"]
        eotvos = kwargs["eotvos"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in prj.df.columns or spring not in prj.df.columns or vertacc not in prj.df.columns or eotvos not in prj.df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {vertacc} o {eotvos} no están en los datos del objeto")

    ## Calcula lectura relativa corrigiendo con aceleración vertical
    ## y Eötvös
    df = prj.df
    df['REL_VA_E'] = df[beam] + df[spring] - df[vertacc] - df[eotvos]

    if 'base' in kwargs.keys():
        df = __base('REL_VA_E', df, prj, **kwargs) ## Si es proporcionada la base gravimétrica

    return df

def _aerogravimetria_relativa_eotvos(prj, **kwargs):
    
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

    if len(kwargs) not in [3, 4, 5]:
        raise ValueError(f"Las variables en {kwargs.values} deben ser tres, cuatro o 5")
    
    try:
        beam = kwargs["haz"]
        spring = kwargs["resorte"]
        eotvos = kwargs["eotvos"]
    except:
        raise ValueError(f"Las variables en {kwargs.values} deben ser especifiadas como 'haz' y 'resorte'")

    if (beam not in prj.df.columns or spring not in prj.df.columns or eotvos not in prj.df.columns):
        raise ValueError(f"Las variables {beam} o {spring} o {eotvos} no están en los datos del objeto")

    ## Calcula lectura relativa corrigiendo con Eötvös
    df = prj.df
    df['REL_E'] = df[beam] + df[spring] - df[eotvos]

    if 'base' in kwargs.keys():
        df = __base('REL_E', df, prj, **kwargs) ## Si es proporcionada la base gravimétrica

    return df

def ___geom_phi(geom):
    
    """
    Para pasar de Point a latitud

    Parameters
    ----------
    geom : lista de shapely.geometry.point.Point
        GEOMETRÍA DEL PUNTO DE OBSERVACIÓN.

    Returns
    -------
    Lista de latitudes.

    """
    
    return geom.y

def ___geom_lambda(geom):
    
    """
    Para pasar de Point a latitud

    Parameters
    ----------
    geom : lista de shapely.geometry.point.Point
        GEOMETRÍA DEL PUNTO DE OBSERVACIÓN.

    Returns
    -------
    Lista de latitudes.

    """
    
    return geom.x