#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 17:35:21 2023
## Código implementado con ayuda de ChatGPT-4: openai
@author: nicalcoca
"""

from sklearn.cluster import KMeans
from numpy import where, take

## Para segmentar en dos un array unidimensional (array), el resultado depende
## de la necesidad

def simpleKMeans(array, todo):
    
    ## Si es para conocer los valores límites superiores
    ## e inferiores de un conjunto de outliers
    if todo == 'limits-outliers':
        
        # Límites de valores para trazar líneas
        # limítrofes de outliers
        
        # Segmenta en altos y bajos outliers
        kmeans = KMeans(n_clusters=2, n_init='auto')
        kmeans.fit(array.reshape(-1,1))
        labels = kmeans.labels_
        
        # Valores outliers segmentados en altos y bajos
        ones = where(labels==1)[0]
        zeros = where(labels==0)[0]
        
        # Creación de límites altos y bajos
        minus = take(array, zeros)
        maxis=  take(array, ones)
        limits = [min(minus), max(minus), min(maxis), max(maxis)]
        
        return limits
    
    else:
        
        return f"Necesidad {todo} desconocida"
    