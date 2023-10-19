class Ordenador:

    """
    Clase ordenadora de datos
    """

    def ordenar(self, data, metodo, *args, **kwargs):

        ordenador = get_ordenador(metodo)
        data_ordenada = ordenador(data, *args)

        return data_ordenada

def get_ordenador(metodo):
    
    if metodo == 'atypical_groups': return _series_series_to_df
    # if metodo == 'groups_to_df': return _groups_to_df
# ## Añade variable por grupos a dataframe con grupos
# def _groups_to_df(data, kwargs):



## Convierte series en series a un arreglo de dos variables e índices
def _series_series_to_df(data, *args):

    import pandas as pd

    dic = dict()
    for index, value in data.items():
        if index[1] in list(args):
            if index[0] in dic:
                dic[index[0]].append(value)
            else:
                dic[index[0]] = [value]
    
    df = pd.DataFrame(dic).T
    df.columns = list(args)

    return df
