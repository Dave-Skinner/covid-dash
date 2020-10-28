# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import flask

from app import app
import app_worldwide, app_sir, app_excess,app_mobility#, app_stringency, app_seir, app_excess_us##, app_ons, app_density, app_mobility, app_compliance
#import app_mobility_new as app_mobility


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
        return app_worldwide.getLayout()
    #elif pathname == "/stringency": 
    #    return app_stringency.getLayout()

    #elif pathname == "/seirmodel": 
    #    return app_seir.getLayout() 

    elif pathname == "/sirmodel": 
        return app_sir.getLayout() 

    elif pathname == "/excessdeaths": 
        return app_excess.getLayout() 
    elif pathname == "/mobility": 
        return app_mobility.getLayout()   
           
    '''elif pathname == "/excessdeaths_us": 
        return app_excess_us.getLayout()              
    else:
        return app_worldwide.getLayout()
    elif pathname == "/ons_data": 
        layout = app_ons.getLayout()
        return layout
    elif pathname == "/density": 
        layout = app_density.getLayout()
        return layout'''
    ''' 
    elif pathname == "/compliance": 
        return app_compliance.getLayout() ''' 





if __name__ == '__main__':
    app.run_server(debug=True)
