# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 15:18:06 2017

@author: Paul Herrera
"""
import pandas as pd


def transform_grouped_data(data, config):
    """
    """
    # Creating the new DataFrame.
    dateRange = [x.strftime('%Y-%m-%d') for x \
                 in pd.date_range(min(data.Date), max(data.Date))]
    columns = ['Company', 'Region'] + dateRange
    df = pd.DataFrame(columns=columns)

    # Populating the DataFrame.
    df['Company'] = config.Company
    df['Region'] = config.Region
    for c in df.Company:
        for d in dateRange:
            columnToSum = config[config.Company == c]['ColumnToSum']
            value = data[(data.Date == d) & (data.Company == c)][columnToSum]
            try:
                df.set_value(df[df.Company == c].index[0], d, value.iloc[0,0])
            except: pass
    
    return df
    

if __name__ == "__main__":
    with pd.ExcelFile('For Example.xlsx') as excel:
        data = pd.read_excel(excel.io, 'Data').dropna(axis=1)
        config = pd.read_excel(excel.io, 'Configuration')
        output = transform_grouped_data(data, config)
        output.to_excel('Output.xlsx', 'Output I want to see', index=False)
    
