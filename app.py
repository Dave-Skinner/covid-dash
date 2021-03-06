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

from google.cloud import bigquery
from google.oauth2 import service_account

local_version = False


json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
gcp_project = os.environ.get('GCP_PROJECT') 

json_data = json.loads(json_str)
json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')

gbq_credentials = service_account.Credentials.from_service_account_info(json_data)


if local_version:
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Covid Mobility-369735b5a910.json'
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
    dataset = dw.load_dataset('markmarkoh/coronavirus-data',auto_update=True)

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
    csv_file = 'https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv'
    df = pd.read_csv(csv_file)
    print (df.info())
    return df

def getGoogleMobilityReportsFromCountry(country):
    sql = """SELECT * 
             FROM   `bigquery-public-data.covid19_google_mobility_eu.mobility_report` mobility 
             WHERE country_region = "%s" 
             AND sub_region_1 IS NULL 
    """ % country

    # Run a Standard SQL query using the environment's default project
    df = pd.read_gbq(sql, dialect='standard',credentials=gbq_credentials)

    return df

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

#@cache.memoize(timeout=timeout)
def getUSDeathData():
    url = 'https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/source-data/united-states/united_states_total_source_latest.csv'
    df = pd.read_csv(url, error_bad_lines=False)
    return df 


def getUSWeekWindows():
    url = 'https://github.com/TheEconomist/covid-19-excess-deaths-tracker/blob/master/source-data/united-states/united_states_week_windows.csv'
    df = pd.read_csv(url, error_bad_lines=False)
    return df 

def getUSStateCodes():
    url = 'https://github.com/TheEconomist/covid-19-excess-deaths-tracker/blob/master/source-data/united-states/united_states_states.csv'
    df = pd.read_csv(url, error_bad_lines=False)
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


