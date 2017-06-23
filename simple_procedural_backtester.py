# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 12:12:20 2017

@author: Paúl Herrera
"""

# from __future__ import division
# from __future__ import print_function

import numpy as np
import pandas as pd
from scipy import stats
import time
from tqdm import tqdm
import sys


def get_decimals(Series):
        """
        Gets the current symbol number of decimals after the comma.
        """
        decimals = map(lambda x: str(Series.iloc[x]).split('.')[1], 
                   range(len(Series))) 
        decimals = [len(x) for x in decimals]
        decimals = stats.mode(decimals)[0][0]
        
        return decimals


def parseKeyArgs(args):
    keyArgsDict = {'pair': '', 'SL': '', 'TP': '', 'period': '', 'level': '',}
    for arg in args[1:]:
        k = arg.split('=')[0]
        v = arg.split('=')[1]
        keyArgsDict[k] = v
        
    return keyArgsDict


def read_csv(name):
    """
    Reads a .csv files into a pandas DataFrame.
    """
    header = ['Time', 'Open', 'High', 'Low', 'Close', 'Vol']
    df = pd.read_csv(name, header=None, parse_dates = [[0,1]])
    df.columns = header
    df.set_index('Time', inplace=True)              
    df.drop('Vol', axis=1, inplace=True)
    
    return df



if __name__ == "__main__":
    # External variables.
    keyArgs = parseKeyArgs(sys.argv)
    
    pair = keyArgs['pair'] if keyArgs['pair'] else 'USD_CAD'
    SL = int(keyArgs['SL']) if keyArgs['SL'] else 57
    TP = int(keyArgs['TP']) if keyArgs['TP'] else 102
    days = int(keyArgs['period']) if keyArgs['period'] else 3
    entryLevel = int(keyArgs['level']) if keyArgs['level'] else 45
    
    print("\nBacktesting with this parameters:")
    print("Currency pair: {}".format(pair))
    print("Stop Loss: {}".format(SL))
    print("Take Profit: {}".format(TP))
    print("Lookback period: {}".format(days))
    print("Entry level: {}".format(entryLevel))
        
    #Reading files.
    print("\nReading data files")
    df01 = read_csv('{}_CASH__1_min_MIDPOINT.csv'.format(pair))
    df02 = read_csv('{}_CASH__1_hour_MIDPOINT.csv'.format(pair))
    
    # Same last date for both timeframes.
    minDate = min(df01.index[-1], df02.index[-1])
    df01 = df01[df01.index <= minDate]
    df02 = df02[df02.index <= minDate]
    
    #Internal variables.
    decimals = get_decimals(df02.Close)
    divisor = pow(10, decimals - 2)
    
    # Finding the 24h high/low.
    print("Calculating variables")
    highs = df02.resample('24h', base=17).max().dropna().High
    
    # Building the break level DataFrame.
    hours = days * 24        
    highs = pd.DataFrame({'Highs': highs})
    columns = []
    for i in range(1, days + 1):
        colName = 'shift{}'.format(i)
        highs[colName] = highs.Highs.shift(i)
        columns.append(colName)
    highs['Break_level'] = highs[columns].max(axis=1)
    df02['Break_level'] = [round(highs.Break_level[highs.Break_level.index < x][-1], 
                           decimals) for x in df02.index]
                           
    # Two positive bars in a row.                            
    df02['PositiveX2'] = np.where(((df02.Close.shift(1) - df02.Open.shift(1) > 0) 
                         & (df02.Close.shift(2) - df02.Open.shift(2) > 0)), 1, 0)
                         
    # Highest high hit and target price.
    df02['Break_level_Hit'] = np.where((df02.Open < df02.Break_level) \
                                    & (df02.High >= df02.Break_level) \
                                    & (df02.PositiveX2 == 1), 1, 0)
    try:
        df02['Target'] = np.where(df02.Break_level_Hit == 1, 
                              df02.Open.shift(2).fillna(0) + entryLevel / divisor, 0)  
    except TypeError:
        print(entryLevel, divisor)
        raise TypeError

    # Entry prices calculation.
    df02['Target_hit01'] = np.where((df02.Target != 0) \
                                     & (df02.High >= df02.Target), 1, 0)   
                        
    df02['Target_hit02'] = np.where((df02.Open < df02.Target.shift()) \
                                     & (df02.High >= df02.Target.shift()) \
                                     & (df02.Target_hit01 == 0), 1, 0)
    
    df02['Entry_Price'] = np.where(df02.Target_hit02 == 1, df02.Target.shift(), 
                          np.where(df02.Target_hit01 == 1, 
                                   df02[['Target', 'Break_level']].max(axis=1), 0))

    # Signals generation.
    print("Generating entry signals")
    signalsHours = df02[df02.Entry_Price != 0].index
    entryPrices =  df02[df02.Entry_Price != 0].Entry_Price
    takeProfits = entryPrices + TP / divisor
    stopLosses = entryPrices - SL / divisor
    
    entryTime = []
    for i in tqdm(range(len(signalsHours))):
        filter01 = df01[df01.index >= signalsHours[i]]
        filter02 = filter01[filter01.Open < entryPrices[i]]
        filter03 = filter02[filter02.High >= entryPrices[i]]
        entryTime.append(filter03.iloc[0].name)

    # Generating exit signals.
    print("Generating exit signals")
    exitTime = []
    exitPrices = []
    for i in tqdm(range(len(entryTime))):
        df = df01[df01.index >= entryTime[i]]
        counter = 0
        while True:
            row = df.iloc[counter,:]
            if row.Low < stopLosses[i]:
                exitTime.append(row.name)
                exitPrices.append(stopLosses[i])
                break
            elif row.High > takeProfits[i]:
                exitTime.append(row.name)
                exitPrices.append(takeProfits[i])
                break
            counter += 1
    exitPrices = np.round(exitPrices, decimals)
    entryPrices = np.round(entryPrices, decimals)
    profits = np.round((exitPrices - entryPrices) * divisor, 2)
    
    # Stats dataframe from signals list.
    columns = ['Entry_time', 'Entry_price', 'Exit_time',
               'Exit_price', 'Profit']
    
    signals = pd.DataFrame(np.column_stack([list(entryTime), list(entryPrices), 
                            list(exitTime), list(exitPrices), list(profits)]),
                            columns = columns)
    
    signals.set_index('Entry_time', inplace=True)
    signalsMonthly = signals.resample('M')
    winnerSignals = signals[signals.Profit > 0].resample('M')
    
    # Stats calculation.
    PnL = signals.Profit.sum()
    PositionsPerMonth = signalsMonthly.count().Profit
    winsPerMonth = signals[signals.Profit > 0].resample('M').count().Profit
    lossPerMonth = signals[signals.Profit <= 0].resample('M').count().Profit
    months = PositionsPerMonth.index.to_period('M')
    statsDF = pd.concat([PositionsPerMonth, winsPerMonth, lossPerMonth], 
                        axis=1).fillna(0)
    statsDF.columns = ['PositionsPerMonth', 'winsPerMonth', 'lossPerMonth']

    # Writing output file.
    lt = time.localtime()
    fileName01 = "{}{}{}_{}-{}_{}_signals.txt".format(lt.tm_year, lt.tm_mon,
                                                      lt.tm_mday, lt.tm_hour,
                                                      lt.tm_min, pair)
    fileName02 = "{}{}{}_{}-{}_{}_stats.txt".format(lt.tm_year, lt.tm_mon,
                                                      lt.tm_mday, lt.tm_hour,
                                                      lt.tm_min, pair)
    
    with open(fileName01, "w") as text_file:
        text_file.write("Entry time       |  Entry price  |  Exit time  |   Exit price  |  Profits\n")
        for t, p, et, ep, pips in zip(entryTime, entryPrices, exitTime, exitPrices, profits):
            text_file.write("{}  {} - {}  {} - {} pips\n".format(t, p, et, ep, pips))
    
    with open(fileName02, "w") as text_file:
        text_file.write("Backtesting for the {}\n".format(pair))
        text_file.write("\n\nParameters:\n\nStop Loss: {}\n".format(SL))
        text_file.write("Take Profit: {}\n".format(TP))
        text_file.write("Lookback period: {}\n".format(days))
        text_file.write("Entry level: {}\n".format(entryLevel))
        text_file.write("\n\nStats:\n\nTotal PnL (pips): {}\n".format(PnL))
        text_file.write("\nMonth | Number of positions | Winning trades  |  Loosing trades\n")
        for m, p, w, l in zip(months, statsDF.PositionsPerMonth, 
                              statsDF.winsPerMonth, statsDF.lossPerMonth):
            text_file.write("{}     {}     {}     {} \n".format(m, int(p), 
                                                                int(w), int(l)))
            
    



#    input("Press enter to exit")
                                 
