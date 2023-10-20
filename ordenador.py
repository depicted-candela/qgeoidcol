import pandas as pd

class Ordenador:

    """
    Clase ordenadora de datos
    """

    def ordenar(self, data, metodo, *args, **kwargs):

        ordenador = get_ordenador(metodo)
        data_ordenada = ordenador(data, *args, **kwargs)

        return data_ordenada

def get_ordenador(metodo):
    
    if metodo == 'atypical_groups': return _series_series_to_df
    if metodo == 'groups_to_df': return _groups_to_df

## Añade variable por grupos y aparición a dataframe con grupos
def _groups_to_df(data, args, **kwargs):

    try:
        agg = kwargs['agrupador']
        dic = kwargs['dic']
        var = kwargs['var']
    except:
        raise ValueError("Debe ser especificado antes el agrupador, diccionario y variable")

    if type(dic) != dict: raise ValueError(f"La variable {dic} debe ser un diccionario")
    if type(var) != str: raise ValueError(f"La variable {var} debe ser de tipo string")
    if not isinstance(data, pd.core.frame.DataFrame): raise ValueError(f"La variable {data} debe ser un data frame de pandas")

    ## Crea diccionario para iterar
    category_count = {category: 0 for category in dic.keys()}

    ## Crea la nueva variable poniendo la lista por grupo en las filas del grupo
    data[var] = data[agg].apply(lambda x: __map_and_order(x, dic, category_count))

    return data

## Crea función para el mapeo con apply
def __map_and_order(category, category_dict, category_count):
    ## Extracts the values per category
    values = category_dict.get(category, [])
    ## Extracts how many values were added to the list
    ## to know what value will be added
    idx = category_count[category]
    ## Añade al contador uno
    category_count[category] += 1
    ## Si la cantidad de valores es mayor al índice, devuelva el valor,
    ## sino, ninguno
    return values[idx] if idx < len(values) else None

## Convierte series a un data frame de dos variables e índices
def _series_series_to_df(data, *args):

    if type(data) != dict: raise ValueError(f"La variable {data} debe ser un diccionario")

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
