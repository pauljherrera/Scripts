# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 11:25:03 2017

@author: forex
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import datetime as dt
from matplotlib import finance
from lxml import html
import requests
import sys


def get_arg(index, default):
    try:
        return sys.argv[index]
    except IndexError:
        return default

if __name__ == '__main__':
    # Variables
    timeframe = get_arg(1, '60') + 'S'
    columns = ['Time', 'Price']
    data = pd.DataFrame(columns=columns)

    # Figure
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
             
    def animate(i):
        global data
        global timeframe
        
        # Scraping page.
        page = requests.get('https://bitcoinwisdom.com/markets/bitstamp/btcusd')
        tree = html.fromstring(page.content)
        p = float(tree.xpath('//*[@id="price"]/text()')[0])
        t = dt.datetime.now()
        columns = ['Time', 'Price']
        data = pd.concat([data, pd.DataFrame([(t,p)], columns=columns)])
          
        # Resamplig data.
        if len(data) > 1:
            df = data.set_index('Time')
            opensList = list(df.Price.resample(timeframe).first())
            closesList = list(df.Price.resample(timeframe).last())
            highsList = list(df.Price.resample(timeframe).max())
            lowsList = list(df.Price.resample(timeframe).min())
        
            # Plotting.
            ax1.clear()
            finance.candlestick2_ochl(ax1, opensList, closesList, highsList, 
                                      lowsList, width=0.8, colorup='k', 
                                      colordown='r', alpha=0.75)
        
    
    # Updating plot.
    ani = animation.FuncAnimation(fig, animate, interval=250)
    plt.show()


    
    
    
    
    