# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 17:10:36 2016

@author: forex
"""


from __future__ import division
from __future__ import print_function

from lxml import html
import requests
import pandas as pd

class SimpleScraper():
    """
    """
    def get_page(self, page):
        page = requests.get(page)
        self.tree = html.fromstring(page.content)

    def get_text(self, xpath):
        text = self.tree.xpath('%s/text()'%xpath)[0]
        return text

if __name__ == "__main__":
     
    # buenasCasas = 'http://inmuebles.mercadolibre.com.ve/casas/colinas-de-santa-rosa-o-el-pedregal-o-la-rosaleda-o-del-este-o-las-trinitarias-o-barisi-o-el-parral-o-fundalara-o-monte-real-o-nueva-segovia-barquisimeto-lara/_PriceRange_150000000-0'

    # Setting page    
    page= 'http://casa.mercadolibre.com.ve/MLV-473847062-casas-en-venta-_JM'
    database = 'casas_este_barquisimeto.csv'
    w = SimpleScraper()

    # Xpaths
    ubicXpath = '/html/body/main/div/section[5]/h2'
    infoXpaths = ['/html/body/main/div/section[6]/div[1]/div[1]/div/ul[1]',
                  '/html/body/main/div/section[6]/div[1]/div[1]/div/ul[2]']
    precioXpath = '/html/body/main/div/section[2]/section/div/div/article/strong'
    
    # Obtener datos    
    w.get_page(page)
    df = pd.DataFrame(columns=['Ubicacion','Inmueble','Operacion','Antiguedad',
                               'Banios','Habitaciones','m2_terreno',
                               'm2_construccion','Estacionamientos', 'Precio'])
                                   
    info = {}
    info['Ubicacion'] = w.get_text(ubicXpath)
    info['Precio'] = int(w.get_text(precioXpath)[4:].replace('.', ''))
    for path in infoXpaths:
        b01 = w.tree.xpath(path)[0]
        for element in b01.getchildren():
            info[element.getchildren()[0].text] = element.getchildren()[1].text

    if info.has_key(u'Ba\xf1os de Servicio:'):
        try: 
            banios = int(info[u'Ba\xf1os de Servicio:'][-1]) + int(info[u'Ba\xf1os:'])
        except: banios = int(info[u'Ba\xf1os:'])
    else: banios = int(info[u'Ba\xf1os:'])
    antiguedad = info[u'Antig\xfcedad:'][0]
    try: 
        antiguedad += info[u'Antig\xfcedad:'][1]
        antiguedad = int(antiguedad)
    except:
        antiguedad = info[u'Antig\xfcedad:'][0]
        antiguedad = int(antiguedad)
    if info.has_key('Hab. de Servicio:'):  
        try:
            habs = int(info['Hab. de Servicio:']) + int(info['Habitaciones:'])
        except: habs = int(info['Habitaciones:'])
    else: 
        habs = int(info['Habitaciones:'])
    df.loc[len(df)] = [info['Ubicacion'], info['Inmueble:'], 
                       info[u'Operaci\xf3n:'], antiguedad, banios, habs,
                       int(info[u'Metros\xb2 de Terreno:']), 
                       int(info[u'Metros\xb2 de construcci\xf3n:']),
                       int(info['Estacionamientos:']), 
                       info['Precio']]
    
    
    # Saving.
    df.to_csv(database, mode='a', index=False, header=False, encoding='utf-8')
    
    print(df)