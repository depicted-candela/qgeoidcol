import pandas as pd
import math as mt
import numpy as np

def elipsoide():  #Se cargan los valores asociados al elipsoide de referencia GRS80
    a=6378137.0
    b=6356752.31
    f=0.00335281068118363
    Omega=0.00000000007292115
    Den=2.67
    Bouguer=0.000419
    GM=398600500
    G_Ecuador=978032.67714
    G_Polo=983218.636854687
    m=0.0000000034139
    
    return a,b,Den,Bouguer,m,f,G_Ecuador,G_Polo,Omega,GM


def somigliana(a,b,G_ec,G_pol,Phi): #La funcion recibe parametros del elipsoide y datos de observaciones y calcula la altura normal somigliana correspondiente.
    
    Phi_rad=list(map(mt.radians, Phi)) #para pasar las Latitudes de los puntos a radianes
    
    def numerador(Phi_rad, G_pol, a, b, G_ec):
        
        sumando1 = a * G_ec * np.array([mt.pow(num, 2) for num in list(map(mt.cos, Phi_rad))])
        sumando2 = b * G_pol * np.array([mt.pow(num, 2) for num in list(map(mt.sin, Phi_rad))])
        
        sumandos = sumando1 + sumando2
        
        return sumandos
    
    def denominador(a, b, Phi_rad):
        
        sumando1 = a ** 2 * np.array([mt.pow(num, 2) for num in list(map(mt.cos, Phi_rad))])
        sumando2 = b ** 2 * np.array([mt.pow(num, 2) for num in list(map(mt.sin, Phi_rad))])
        raiz = list(map(mt.sqrt, sumando1 + sumando2))
        
        return raiz
        
    
    Somi1=numerador(Phi_rad, G_pol, a, b, G_ec)
    Somi2=denominador(a, b, Phi_rad)
    
    Somi = Somi1/Somi2
    
    return Somi

def aire_libre(G_obs,Somi,a,m,f,Phi,H): #La funcion recibe parametros del elipsoide y datos de observaciones y calcula la anomalia de aire libre correspondiente.
    
    Phi_rad=list(map(mt.radians, Phi)) #para pasar phi a radianes
    
    Normal=H/a  #Corresponde al ultimo factor de la ecuacion
    
    def Fac(m,f,Phi_rad,Normal):
        Sumando1= 1 + m + f - 2 * f * np.array([mt.pow(num, 2) for num in list(map(mt.sin, Phi_rad))])
        Sumando2= np.array([mt.pow(num, 2) for num in Normal])
        
        Resultado=1-2*(Sumando1*Normal)+Sumando2
        return Resultado
        
    fac=Fac(m,f,Phi_rad,Normal)
    
    Aire=G_obs-Somi*fac
    return Aire


def bouguer(Den,b,H): #La funcion recibe parametros y datos de observaciones y calcula la anomalia de Bouguer correspondiente.
    #Den se refiere a la densidad media
    Boug=Den*b*H
    return Boug


def xlsx_to_Data(inpath): #La funcion lee un xlsx y lo guarda como un DataFrame (diseñada solo para pruebas unitarias).
    ##  Lectura del archivo xlsx
    Data = pd.read_excel(inpath, sheet_name='Hoja1')
    return Data


def correcciones2(a,b,Den,Bouguer,m,f,G_Ecuador,G_Polo): #La funcion se encarga de llamar a las funciones encargadas de las anomalias, contruir y exportar el nuevo dataframe con anomalias a formato xlsx.
    Data=xlsx_to_Data('K:/Modelo Geoidal/Terrestre/Masivo.xlsx')

    Phi=Data["LATITUD"]
    H=Data["ALTURA"]
    G_obs=Data["GRAVEDAD"]
    
    Somi=somigliana(a,b,G_Ecuador,G_Polo,Phi)
    Boug=bouguer(Den,Bouguer,H)
    Aire=aire_libre(G_obs,Somi,a,m,f,Phi,H)
    
    df=pd.DataFrame({'SOMIGLIANA': Somi, 'AIRE_LIBRE': Aire, 'BOUGUER': Boug})
    
    return pd.concat([Data, df], axis=1)


''' '''
#Lineas para validacion de pruebas unitarias, 
a,b,Den,Bouguer,m,f,G_Ecuador,G_Polo,Omega,GM=elipsoide()
correcciones2(a,b,Den,Bouguer,m,f,G_Ecuador,G_Polo)
