# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 17:20:21 2017

@author: forex
"""

from scipy import stats
from matplotlib import pyplot as plt

stock_returns = [0.065, 0.0265, -0.0593, -0.001, 0.0346]
mkt_returns = [0.055, -0.09, -0.041, 0.045, 0.022]

beta, alpha, r_value, p_value, std_err = \
    stats.linregress(stock_returns, mkt_returns)