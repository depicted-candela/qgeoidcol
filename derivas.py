class Derivas():

    """
    Las derivas para restar a las comparaciones para gravedad relativa
    """

    def corregir_deriva(self, prj, drift, **kwargs):
        
        corrector_deriva = get_corrector_deriva(prj, drift)
        resultado = corrector_deriva(prj, drift.data, **kwargs)
        prj.set_df_file_tipo(resultado, prj.file, prj.tipo)

    
def get_corrector_deriva(prj, drift):

    if prj.empresa != drift.empresa: raise ValueError("El archivo para corregir derivas debe ser de la misma empresa que el archivo a corregir")

    ## Segregador para corregir
    if prj.empresa == 'carson':

        return _deriva_carson

def _deriva_carson(prj, data, **kwargs):

    if 'var' in kwargs.keys():
        import pandas as pd
        df = pd.DataFrame()
        for g in prj.groups:
            tempdf = prj.return_subdf(g)
            tempdata = data[data['LINE'] == g]
            try:
                deriva_g = abs(tempdata.iloc[0]['AfterFlight'] - tempdata.iloc[0]['AfterFlight']) / len(tempdf)
                tempdf[kwargs['var']] = tempdf[kwargs['var']] - deriva_g
                print(f"Grupo {g} tiene deriva en documento fuente")
            except:
                print(f"Grupo {g} no tiene deriva en documento fuente")
            
            df = pd.concat([df, tempdf], axis=0)
        return df
    else:
        return set(data['LINE'])
