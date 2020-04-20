# -*- coding: utf-8 -*-

from flask import Flask
import dash

import sys
import os
import json
import datadotworld as dw




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



#@functools32.lru_cache(maxsize=32)
def getCovidDataframes():
    dataset = dw.load_dataset('markmarkoh/coronavirus-data',auto_update=True)

    dfs = dataset.dataframes

    #print (dfs.describe())

    return dfs



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


