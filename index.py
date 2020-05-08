# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask

from app import app
import app_worldwide, app_stringency#, app_mobility, app_ons, app_density


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
    elif pathname == "/stringency": 
        layout = app_stringency.getLayout()
        return layout
    else:
        return app_worldwide.getLayout()
    '''elif pathname == "/mobility": 
        layout = app_mobility.getLayout()
        return layout
    elif pathname == "/ons_data": 
        layout = app_ons.getLayout()
        return layout
    elif pathname == "/density": 
        layout = app_density.getLayout()
        return layout'''






if __name__ == '__main__':
    app.run_server(debug=True)
