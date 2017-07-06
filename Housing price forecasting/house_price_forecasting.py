# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 18:20:01 2016

@author: forex
"""

from sklearn.linear_model import LinearRegression
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn

# Datos del inmueble.
Antiguedad = 15
Banios = 5
Habitaciones = 5
Estacionamientos = 5
m2_terreno = 408
m2_construccion = 420

plotapto = True

# Base de datos
#Extracting data
datafile = 'casas_este_barquisimeto.csv'
#path = os.getcwd()+'\\'+datafile
data = pd.read_csv(datafile)
data = data.dropna()
data = data.drop_duplicates()
data = data.drop(['Ubicacion','Operacion','Inmueble'], axis=1)

"""
#Making the working directory = file directory
abspath = os.path.abspath('__file__')
dname = os.path.dirname(abspath)
os.chdir(dname)
"""

#All set of data
X = data.drop('Precio', axis=1)
y = data.Precio

model = LinearRegression()
model.fit(X, y)
coef = model.coef_

X_predict = np.array([Antiguedad, Banios, Habitaciones,  
                      m2_terreno, m2_construccion, Estacionamientos])  # put the new data
y_predict = model.predict(X_predict.reshape(1,-1))

#Alternative set of data
X2 = pd.concat([data.m2_terreno, data.m2_construccion, data.Antiguedad, 
                data.Habitaciones, data.Banios], axis=1)
model.fit(X2, y)
coef2 = model.coef_

X_predict2 = np.array([m2_terreno, m2_construccion, Antiguedad, 
                       Habitaciones, Banios])  # put the new data
y_predict2 = model.predict(X_predict2.reshape(1,-1))

#Small set of data
X3 = pd.concat([data.m2_terreno, data.m2_construccion, data.Antiguedad], axis=1)
model.fit(X3, y)
coef3 = model.coef_

X_predict3 = np.array([m2_terreno, m2_construccion, Antiguedad])  # put the new data
y_predict3 = model.predict(X_predict3.reshape(1,-1))

#Average
averagePrice = int(np.mean([y_predict, y_predict2, y_predict3]))

#Plots
ylim = 1200000000
ytick = 100000000
y_plot = averagePrice

plt.figure(1, figsize = (11,40))

model.fit(data.m2_terreno.reshape(-1,1), y)
plt.subplot(611)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.m2_terreno, y)
y_max = model.intercept_ + model.coef_*(max(data.m2_terreno))
plt.plot([0, max(data.m2_terreno)], [model.intercept_,y_max])
plt.xlabel("Area del terreno en metros cuadrados", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[3], y_plot, c='red', s=100)
    
model.fit(data.m2_construccion.reshape(-1,1), y)
plt.subplot(612)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.m2_construccion, y)
y_max = model.intercept_ + model.coef_*(max(data.m2_construccion))
plt.plot([0, max(data.m2_construccion)], [model.intercept_,y_max])
plt.xlabel("Area de la construccion en metros cuadrados", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[4], y_plot, c='red', s=100)
   
plt.subplot(613)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.Antiguedad, y)
model.fit(data.Antiguedad.reshape(-1,1), y)
y_max = model.intercept_ + model.coef_*(max(data.Antiguedad))
plt.plot([0, max(data.Antiguedad)], [model.intercept_,y_max])
plt.xlabel("Antiguedad del inmueble", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[0], y_plot, c='red', s=100)

plt.subplot(614)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.Banios, y)
model.fit(data.Banios.reshape(-1,1), y)
y_max = model.intercept_ + model.coef_*(max(data.Banios))
plt.plot([0, max(data.Banios)], [model.intercept_,y_max])
plt.xlabel("Cantidad de banos", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[1], y_plot, c='red', s=100)

plt.subplot(615)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.Habitaciones, y)
model.fit(data.Habitaciones.reshape(-1,1), y)
y_max = model.intercept_ + model.coef_*(max(data.Habitaciones))
plt.plot([0, max(data.Habitaciones)], [model.intercept_,y_max])
plt.xlabel("Cantidad de habitaciones", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[2], y_plot, c='red', s=100)

plt.subplot(616)
plt.yticks(range(0, ylim, ytick))
plt.scatter(data.Estacionamientos, y)
model.fit(data.Estacionamientos.reshape(-1,1), y)
y_max = model.intercept_ + model.coef_*(max(data.Estacionamientos))
plt.plot([0, max(data.Estacionamientos)], [model.intercept_,y_max])
plt.xlabel("Puestos de estacionamiento", fontsize=14)
plt.ylabel("Precio (en miles de millones de bolivares)", fontsize=14)
if plotapto == True: plt.scatter(X_predict[5], y_plot, c='red', s=100)


plt.figure(2, figsize = (7,12))

plt.subplot(311)
plt.title('Modelo 1')
plt.xlabel("%1.0f, %1.0f, %1.0f, %1.0f, %1.0f, %1.0f"%(coef[0], coef[1],
            coef[2], coef[3], coef[4], coef[5]))
plt.bar(range(len(X.columns)), coef)
plt.xticks(range(len(X.columns)), X.columns, rotation=30)
plt.show()

plt.figure(3, figsize = (7,12))

plt.subplot(312)
plt.title('Modelo 2')
plt.xlabel("%1.0f, %1.0f, %1.0f, %1.0f, %1.0f"%(coef2[0], coef2[1],
            coef2[2], coef2[3], coef[4]))
plt.bar(range(len(X2.columns)), coef2)
plt.xticks(range(len(X2.columns)), X2.columns, rotation=30)
plt.show()

plt.figure(4, figsize = (7,12))
  
plt.subplot(313)
plt.title('Modelo 3')
plt.xlabel("%1.0f, %1.0f, %1.0f"%(coef3[0], coef3[1], coef3[2]))
plt.bar(range(len(X3.columns)), coef3)
plt.xticks(range(len(X3.columns)), X3.columns, rotation=30)
plt.show()

#Prints
print "\nPrecio tomando en cuenta toda la información: %1.0f" %y_predict
print "\nPrecio tomando en cuenta los ...: %1.0f" %y_predict2
print "\nPrecio tomando en cuenta los m2, antiguedad: %1.0f" %y_predict3
print "\nPrecio average: %1.0f" %averagePrice



