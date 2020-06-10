# -*- coding: utf-8 -*-

from flask import Flask
import dash

import sys
import os
import json
import datadotworld as dw
import pandas as pd
from flask_caching import Cache

import requests
import datetime

local_version = False


if local_version:
    app = dash.Dash('Covid Dash')
    app.config.suppress_callback_exceptions = True
else:
    server = Flask('Covid Dash')
    server.secret_key = os.environ.get('secret_key', 'secret')
    at_config={}
    app = dash.Dash('Covid Dash', server=server)
    app.config.suppress_callback_exceptions = True 

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

timeout = 360

@cache.memoize(timeout=timeout)
def getCovidJSON():
    dataset = dw.load_dataset('markmarkoh/coronavirus-data',force_update=True)

    dfs = dataset.dataframes

    json_ret = {}
    json_ret['full_data'] = dfs['full_data'].to_json(date_format='iso', orient='split')

    json_ret['new_cases'] = dfs['new_cases'].to_json(date_format='iso', orient='split')

    json_ret['total_deaths'] = dfs['total_deaths'].to_json(date_format='iso', orient='split')

    json_ret['total_cases'] = dfs['total_cases'].to_json(date_format='iso', orient='split')

    json_ret['new_deaths'] = dfs['new_deaths'].to_json(date_format='iso', orient='split')


    return json_ret


def getCovidDataframes():
    json_ret = getCovidJSON()
    dfs = {}

    dfs['full_data'] = pd.read_json(json_ret['full_data'], orient='split')

    dfs['new_cases'] = pd.read_json(json_ret['new_cases'], orient='split')

    dfs['total_deaths'] = pd.read_json(json_ret['total_deaths'], orient='split')

    dfs['total_cases'] = pd.read_json(json_ret['total_cases'], orient='split')

    dfs['new_deaths'] = pd.read_json(json_ret['new_deaths'], orient='split')

    return dfs

def getGoogleMobilityReports():
    csv_file = 'Global_Mobility_Report.csv'
    return pd.read_csv(csv_file)

@cache.memoize(timeout=timeout)
def getStringencyData():
    today = datetime.date.today()
    response = requests.get('https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/2020-01-01/'+today.strftime('%Y-%m-%d'))
    return response.json()['data']

def getStringencyDataFrame(country='GBR'):

    data = getStringencyData()

    timeseries = []
    for key in data:
        try:
            timeseries.append([key, data[key][country]['stringency']])
        except KeyError:
            pass

    df = pd.DataFrame(timeseries,columns=['date','stringency'])
    df['date'] = pd.to_datetime(df.date)
    df = df.sort_values(by=['date'])

    return df    


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Covid 19 Tracker</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


