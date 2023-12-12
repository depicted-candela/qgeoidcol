import numpy as np

class Geoides():

    """
    Clase con herramientas para extraer información de modelos geoidales globales
    """

    def extractor(self, prj, metodo, **kwargs):

        extraer = get_extractor(metodo)
        extraccion = extraer(prj, metodo, **kwargs)
        
        return extraccion

def get_extractor(metodo):

    if metodo == 'altura_anomala' or metodo == 'ondulacion_geoidal':

        return _measurement_interp
    
    else: raise ValueError(f"Variable {metodo} no implementada")

def __interp_validator(prj):

    if "GEOM" not in prj.df.columns: raise ValueError("Debe tener una variable geométrica")

 
def _measurement_interp(prj, metodo, **kwargs):
    
    __interp_validator(prj)

    import threading
    
    ## Si el hilo principal no está en uso
    if threading.current_thread() is threading.main_thread():
        import jpype
        if not jpype.isJVMStarted():
            # jpype.startJVM(classpath=['/home/depiction/geodesia/JToolsQgeoid/bin/'])
            jpype.startJVM(classpath=['/home/depiction/geodesia/JToolsQgeoid/bin/',
                                    '/home/depiction/Documents/libraries/TinfourCore-2.1.7.jar'])
        array = np.array([prj.df['GEOM'].apply(lambda x : ___geom_lambda(x)),
                        prj.df['GEOM'].apply(lambda x : ___geom_phi(x))])
        values_array = __tinfour_natural_neighbor(array,
                                                  jpype=jpype,
                                                  measurement=metodo,
                                                  modelo=kwargs["modelo"])
        values_list = list(values_array)
        if threading.current_thread() is not threading.main_thread():
            threading.current_thread().join()
        jpype.shutdownJVM()
    ## Si el hilo principal está usándose
    else:
        array = np.array([prj.df['GEOM'].apply(lambda x : ___geom_lambda(x)),
                          prj.df['GEOM'].apply(lambda x : ___geom_phi(x))])
        values_array = __tinfour_natural_neighbor(array,
                                                  jpype=None,
                                                  measurement=metodo,
                                                  modelo=kwargs["modelo"])
        values_list = list(values_array)
    return values_list

def __tinfour_natural_neighbor(array, **kwargs):

    """
    INTERPOLA ONDULACIONES GEOIDALES CON LIBRERÍA TINFOUR DE JAVA
    https://github.com/gwlucastrig/Tinfour (INFORMACIÓN RELACIONADA
    EN https://gwlucastrig.github.io/TinfourDocs/). FUE UTILIZADO UN
    MODELO GEOIDAL GLOBAL DESCARGADO DE http://icgem.gfz-potsdam.de/home
    PARA EL PAQUETE DE JAVA.

    Parameters
    ----------
    array : numpy.ndarray

    Returns
    -------
    numpy.ndarray
        ARREGLO DE ONDULACIONES GEOIDALES

    """

    if kwargs["jpype"]:

        ## Initiliaze the NaturalNeighbor class
        NaturalNeighbor = kwargs["jpype"].JClass('interpolations.NaturalNeighbor')

        ## Uses the NaturalNeighnor constructor
        if "measurement" in kwargs.keys() and "modelo" in kwargs.keys():
            nni = NaturalNeighbor(array[0, :].tolist(), array[1, :].tolist(), kwargs["measurement"], kwargs["modelo"])
        else:
            nni = NaturalNeighbor(array[0, :].tolist(), array[1, :].tolist())

        ## Interpolates all the points with NaturalNeighbor
        values = nni.getInterps()

        ## Java instance to array
        values_array = np.array(list(values))
    
    else:

        import jpype

        ## Initiliaze the NaturalNeighbor class
        NaturalNeighbor = jpype.JClass('interpolations.NaturalNeighbor')

        ## Uses the NaturalNeighnor constructor
        if "measurement" in kwargs.keys() and "modelo" in kwargs.keys():
            nni = NaturalNeighbor(array[0, :].tolist(), array[1, :].tolist(), kwargs["measurement"], kwargs["modelo"])
        else:
            nni = NaturalNeighbor(array[0, :].tolist(), array[1, :].tolist())

        ## Interpolates all the points with NaturalNeighbor
        values = nni.getInterps()

        ## Java instance to array
        values_array = np.array(list(values))

    return values_array

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