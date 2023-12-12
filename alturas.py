from .geoids import Geoides

class Alturas():

    """
    Clase para determinar alturas
    """
    
    def calcular_altura(self, prj, metodo, **kwargs):

        calculador = get_calculador(metodo)
        df_con_grav = calculador(prj, **kwargs)

        return prj.set_df_file_tipo(df_con_grav, prj.file, prj.tipo)

def get_calculador(metodo):

    if metodo == "altura_anomala":

        return _altura_anomala

    if metodo == "ondulacion_geoidal":

        return _ondulacion_geoidal

    else: raise ValueError("Ese método no ha sido implementado")

def _altura_anomala(prj, **kwargs):

    if 'modelo' not in kwargs.keys():
        kwargs['modelo'] = "eigen_6c4"
    geoid = Geoides()
    height_anomaly = geoid.extractor(prj,
                                     "altura_anomala",
                                     **kwargs)
    subdf = prj.df
    subdf["zeta"] = height_anomaly

    return subdf

def _ondulacion_geoidal(prj, **kwargs):

    if 'modelo' not in kwargs.keys():
        kwargs['modelo'] = "eigen_6c4"

    geoid = Geoides()
    ondulacion_geoidal = geoid.extractor(prj,
                                         "ondulacion_geoidal",
                                         **kwargs)
    
    subdf = prj.df
    subdf["N"] = ondulacion_geoidal

    return subdf