#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 20:59:57 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from metpy import interpolate as interp

from .string_tools import split_text_in_equal_lines as stiql

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Gráfico de todas las líneas
def values_per_group(proj, var_name):
    
    df = proj.df
    aggr = proj.aggregator
    
    ## Para determinar agregador
    if aggr in df.columns:
        grpd_data = df.groupby([aggr])[var_name].apply(list).to_dict()
    else:
        raise ValueError("Primero determine la variable agregadora con instance.aggregator_group('variable agregadora')")
    
    # Plotting the graph
    for key, values in grpd_data.items():
        plt.plot(values, label=key)
    
    # Customize the plot
    plt.xlabel('X')
    plt.ylabel(f'{var_name}')
    plt.title('Todos los grupos')
    plt.legend()
    
    # Display the plot
    plt.show()


# Gráfico de diez líneas
def values_per_group_limited(project, var_name, start, end):
    
    df = project.df
    aggr = project.aggregator
    grps = project.groups
    
    ## Para confirmar agregador
    if aggr in df.columns:
        grpd_data = df.groupby([aggr])[var_name].apply(list).to_dict()
    else:
        raise ValueError("Primero determine la variable agregadora con instance.aggregator_group('variable agregadora')")
        
    keys = list(grpd_data.keys())[start: end]
    subset_dict = {key: grpd_data[key] for key in keys if key in grpd_data}
    
    # Plotting the graph
    for key, values in subset_dict.items():
        plt.plot(values, label=key)
    
    # Customize the plot
    plt.xlabel('obs')
    plt.ylabel(f'{var_name}')
    plt.title(f'Grupos desde {start} hasta {end} de {len(grps)}')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Display the plot
    plt.show()


def natural_neighbor(prj, **kwargs):
    
    variable = kwargs['var']
    try:
        avoid = kwargs['avoid']
    except:
        avoid = None
    
    df = prj.df
    
    not_null_variable = df[df[variable] != avoid]
    clean_variable = not_null_variable[['GEOM', variable]]
    
    ## Extracción de valores del dataframe
    LAT = np.array(df['GEOM'].apply(lambda point: point.y))
    LONG = np.array(df['GEOM'].apply(lambda point: point.x))
    
    variable_num = clean_variable[[variable]]
    variable_num = np.array([i[0] for i in variable_num.values])
    
    # Define the grid to interpolate Into
    LATi = np.linspace(min(LAT), max(LAT), 100)
    LONGi = np.linspace(min(LONG), max(LONG), 100)
    LONGi, LATi = np.meshgrid(LONGi, LATi)
    
    
    # Interpolate data onto the grid using Natural Neighbor interpolation
    variable_intplt = interp.natural_neighbor_to_grid(LONG,
                                                      LAT,
                                                      variable_num,
                                                      LONGi,
                                                      LATi)
    
    ## A float
    variable_intplt = np.array(variable_intplt, dtype=float)
    
    # Create a plot
    fig, ax = plt.subplots()
    im = ax.imshow(variable_intplt, extent=[min(LONG), max(LONG), min(LAT),
                                       max(LAT)],
              origin='lower', cmap='viridis')
    
    # Set the scales of the x and y axes to be the same
    ax.set_xlim([min(LONG), max(LONG)])
    ax.set_ylim([min(LAT), max(LAT)])
    plt.axis('equal')
    plt.colorbar(im, extend='both')
    
    # Add a title
    ax.set_title(f'Interpolación de {variable} con Vecinos Naturales')
    
    # Show the plot
    plt.show()


## Para atípicos de una variable anormal
def anormal_histogram_outlier(prj, var, contamination, estacion, grav, alt):
    
    import numpy as np

    condition1 = pd.isna(prj.df[grav])
    condition2 = pd.isna(prj.df[alt])
    conditions = condition1 | condition2
    subdf = prj.df[~conditions]

    if var == grav:
        var2 = alt
    else:
        var2 = grav


    if not prj.groups:
        subdf = subdf[[var, var2, 'GEOM', estacion]]
    else:
        subdf = subdf[[var, var2, 'GEOM', estacion, prj.aggregator]]

    values = np.array(subdf[[var, var2]])
    values_h = np.array(subdf[var])
    
    ## Extracción de valores del dataframe
    x = np.array(subdf['GEOM'].apply(lambda point: point.x))
    y = np.array(subdf['GEOM'].apply(lambda point: point.y))

    del subdf['GEOM']
    
    ## Creación de nuevo dataframe para prevenir warnings
    coordinates = pd.DataFrame({'x': x, 'y': y})
    
    data = np.column_stack((coordinates, values))
    
    # Paquete para LocalOutlierFactor
    from sklearn.neighbors import LocalOutlierFactor
    
    lof = LocalOutlierFactor(n_neighbors=1, contamination=contamination)
    labels = lof.fit_predict(data)
    
    # Si hay valores atípicos
    if -1 in labels:
        
        spatial_outliers = data[labels == -1]
        
        # Para acceder a posiciones y valores atípicos
        positions = np.where(labels == -1)[0]
        
        # values = np.take(array, positions)
        spatial_outliers = data[labels == -1]
        spatial_outliers = [i[2] for i in data[labels == -1]]
        
        dictionary = {'values': subdf[var].iloc[positions], 'id': positions,
                      'nomenclatura': subdf[estacion].iloc[positions]}
        
        print(f'Hay {len(spatial_outliers)} valores atípicos')
        
        # Histograma
        if not prj.groups:

            plt.hist(values_h, bins=30, alpha=0.5)

            # Líneas límite
            for out in spatial_outliers:
                plt.axvline(x=out, color='red', linestyle='--')

            # Configuración del gráfico
            plt.xlabel(var)
            plt.ylabel('Frecuencia')
            title = f'Histograma con detetección de outliers para: {var}'
            title = stiql(title, 52)
            plt.title(title)
            plt.show()

        else:

            # Group data by Category
            grouped = subdf.groupby(prj.aggregator)

            # Calculate the number of rows and columns for the subplot grid
            num_categories = len(grouped)
            num_cols = 4
            num_rows = (num_categories + 1) // num_cols

            if num_rows == 0: num_rows = 1
            if num_cols == 0: num_cols = 1

            # Create subplots for histograms in a grid layout
            fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(12, 6 * num_rows))

            # Flatten the axes array if there's only one row
            if num_rows == 1:
                axes = [axes]

            for idx, (category, group) in enumerate(grouped):
                row_idx = idx // num_cols
                col_idx = idx % num_cols
                try:
                    ax = axes[row_idx][col_idx]
                    group[var].plot(kind='hist', ax=ax, bins=20, title=f'Histograma para Categoría: {category}')
                    # ax.set_xlabel(var, fontsize=5)
                    # ax.set_ylabel('Frecuencia', fontsize=5)
                    ax.title.set_fontsize(7)
                    # ax.tick_params(axis='both', labelsize=5)

                    # Remove x and y labels and tick labels
                    ax.set_xticks([])  # Remove x-axis tick labels
                    ax.set_yticks([])  # Remove y-axis tick labels
                    ax.set_xlabel('')  # Remove x-axis label
                    ax.set_ylabel('')  # Remove y-axis label

                    # Set the title font size
                    ax.set_axis_off()

                except:
                    pass

            # Remove any empty subplots
            try:
                for idx in range(len(grouped), num_rows * num_cols):
                    fig.delaxes(axes.flatten()[idx])
            except:
                pass

            plt.tight_layout()
            plt.show()
        
        return dictionary
    
    else:
        
        ## Histograma sin valores atípicos
        plt.hist(values_h, bins=30, alpha=0.5)
        
        # Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma outliers para variable sin outliers: {var}'
        title = stiql(title, 52)
        plt.title(title)
        plt.show()
        
        print("No hay valores atípicos")
        
        return None


## Para atípicos de una variable normal
def normal_histogram_outlier(array, umbral, var):
    
    from scipy import stats
    
    ## Cálculo de outliers
    z_scores = stats.zscore(array)
    outliers_pos = np.where(np.abs(z_scores) > umbral)
    outliers = array[outliers_pos]
    
    ## Si no hay outliers, terminar
    if len(outliers) == 0:
        
        ## Histograma de variable normal sin atípicos
        plt.hist(array, bins=30, alpha=0.5)
        
        ## Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        
        ## Mostrar gráfico
        plt.show()
        
        ## Mensaje explicativo
        mensaje = f"Con un umbral de {umbral} no hay atípicos, "
        mensaje += "para subir el detalle de detección baje el"
        mensaje += "valor de 'umbral'"
        stiql(mensaje, 60)
        
        print(mensaje)
        
        return None
    
    # Cuando hay outliers
    else:
        
        from .cluster import simpleKMeans
        
        print(f'Hay {len(outliers)} valores atípicos')
        
        ## Determina límites
        limits = simpleKMeans(outliers, 'limits-outliers')
        
        plt.figure(1)
        plt.hist(array, bins=30, alpha=0.5)
        
        for limit in limits:
            plt.axvline(x=limit, color='red', linestyle='--')
        
        ## Configuración del gráfico
        plt.xlabel(var)
        plt.ylabel('Frecuencia')
        title = f'Histograma con detetección de outliers para: {var}'
        title = stiql(title, 52)
        plt.title(title)
        
        ## Mostrar gráfico
        plt.show()
        
        return outliers


## Para determinar gráficamente grupos atípicos dadas dos métricas
def atypical_group_per_statistics(series, *args):
    
    if len(args) != 2:

        raise ValueError("Debe ingresar dos nombres de estadísticos para comparar, son variance, entropy, mean, median, kurtosis, skewness, std, max y min")
    