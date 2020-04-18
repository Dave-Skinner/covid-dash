# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask
import base64

from app import app
import app_worldwide




app.layout = html.Div([

    dcc.Location(id='url', refresh=False),
    #getMasthead(),

    html.Div(id='page-content', className='l-grid'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if not pathname: 
        return app_worldwide.getLayout()

    if pathname == "/worldwide": 
        layout = app_worldwide.getLayout()
        return layout
    else:
        return app_worldwide.getLayout()





if __name__ == '__main__':
    app.run_server(debug=True)
