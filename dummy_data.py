import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import pdb


def build_date_list(start, end, delta): #return list of datetimes @ interval delta
    datetimes = []
    curr = start
    while curr < end:
        datetimes.append(curr)
        curr += delta
    return datetimes

def set_weekend(df,val): # set weekend values
    df.loc[df.weekday >= 5, 'value'] = val
    return df

def set_weekday(df,val):  # set weekday values
    df.loc[df.weekday < 5, 'value'] = val
    return df

def split_datetime(df): # split datetime
    temp = pd.DatetimeIndex(df['datetime'])
    df['date'] = temp.date
    df['time'] = temp.time
    return df

def set_months(df, inputs): # set month values
    df.loc[df['month'].isin(inputs['month_value']), 'value'] = inputs['rate_value'] 
    if inputs['tou'] != None:
        for i in inputs['tou']:
            if inputs['tou'][i]['weekends_included'] == True:
                df.loc[df.month.isin(inputs['month_value']) & df.hour.isin(inputs['tou'][i]['hour_value']), 'value'] = inputs['tou'][i]['rate_value']
            else:
                df.loc[(df['month'].isin(inputs['month_value'])) & (df['hour'].isin(inputs['tou'][i]['hour_value'])) & (df['weekday'].isin([0,1,2,3,4])), 'value'] = inputs['tou'][i]['rate_value']
    return df


def set_rates(df, inputs):
    if inputs['summer_months'] != None:
        df = set_months(df, inputs['summer_months'])
    if inputs['winter_months'] != None:
        df = set_months(df, inputs['winter_months'])
    return df

def data_builder(params):  #compile list of datetimes, set kw values and ouput to csv

    b = build_date_list(params['start'],params['end'],params['delta'])
    df = pd.DataFrame(b)
    df.columns = ['datetime']
    df['weekday'] = df['datetime'].apply(lambda x: x.weekday())
    df['hour'] = df['datetime'].apply(lambda x: x.hour)
    df['month'] = df['datetime'].apply(lambda x: x.month)

    if params['index'] == False:
        df = split_datetime(df)

    df['value'] = params['kw']
    if params['weekend_val'] != 0:
        df = set_weekend(df, params['weekday_val'])
    if params['weekday_val'] != 0:
        df = set_weekday(df, params['weekday_val'])
    if params['detail'] != None:
        df = set_rates(df, params['detail'])

    df = df.drop('weekday', 1)
    df = df.drop('hour', 1)
    df = df.drop('month', 1)
    
    if params['index'] == True:
        df = df.set_index('datetime')
    else:
        df = df.set_index('date')
        del df['datetime']

    df.to_csv(params['filename'], index=True)


def main():
    # Set the params to make a datetime pandas load profile with the corresponding loads.
    # Rate value is the load value in kW
    params = { 'start' : datetime(2010,1,1,0,0,0),
            'end' : datetime(2020,12,31,0,0,0),
            'delta' : timedelta(minutes = 15),
            'filename'  : 'test_data_100_2010-2020.csv',
           'weekend_val' : 0,
           'weekday_val' : 0,
           'index' : True,
           'kw' : 100,
           'detail' : { 
                    'summer_months' : {'rate_value' : 100,
                                       'month_value' : [4,5,6,7],
                                       'tou' : {'peak_hours'   : {'rate_value' : 100,
                                                           'hour_value' : [10,11,12,13,14,15,16,17,18],
                                                           'weekends_included' : False},
                                        'mid_peak_hours' : { 'rate_value' : 100,
                                                            'hour_value' : [8,9,19,20],
                                                            'weekends_included' : False },
                                        'off_peak_hours' : {'rate_value' : 100,
                                                            'hour_value' : [0,1,2,3,4,5,6,7,21,22,23,24],
                                                             'weekends_included' : True }}
                                                             },
                    'winter_months' : {'rate_value' : 100,
                                       'month_value' : [0,1,2,3,8,9,10,11,12],
                                        'tou' : 
                                        {'peak_hours'   : {'rate_value' : 100,
                                                           'hour_value' : [10,11,12,13,14,15,16,17,18],
                                                           'weekends_included' : False},
                                        'mid_peak_hours' : { 'rate_value' : 100,
                                                            'hour_value' : [8,9,19,20],
                                                            'weekends_included' : False },
                                        'off_peak_hours' : {'rate_value' : 100,
                                                            'hour_value' : [0,1,2,3,4,5,6,7,21,22,23,24],
                                                             'weekends_included' : False }},
                                                             }
                    }
         }
    data_builder(params)

if __name__ == "__main__":
    main()
