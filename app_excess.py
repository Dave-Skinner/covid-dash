#!/usr/bin/python
# -*- coding: utf-8 -*- 

# -*- coding: utf-8 -*-
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import pycountry


import sys
import os
import json
import time
import datetime

from app import app, getCovidDataframes, getStringencyDataFrame
from header import getHeader



colour_palette = ['rgb(163,95,224)',
					'rgb(240,21,22)',
					'rgb(22,96,185)',
					'rgb(6,193,95)',
					'rgb(209,210,212)',
					'rgb(204,123,6)',
					'rgb(255,234,0)',
					'rgb(81,47,112)',
					'rgb(120,10,11)',
					'rgb(11,48,62)',
					'rgb(127,117,0)',
					'rgb(3,96,47)',
					'rgb(104,105,106)',
					'rgb(102,61,3)']

timeline_selections = ['Timeline',
						'Days since X number of deaths/cases']

data_selections = ['Deaths',
					'Cases']

pop_selections = ['Total Number',
				   '% of Population']




def getFullData():
	dfs = getCovidDataframes()
	return dfs['full_data']

def getNewCases():
	dfs = getCovidDataframes()
	return dfs['new_cases']

def getTotalDeaths():
	dfs = getCovidDataframes()
	return dfs['total_deaths']

def getTotalCases():
	dfs = getCovidDataframes()
	return dfs['total_cases']

def getNewDeaths():
	dfs = getCovidDataframes()
	return dfs['new_deaths']

def getLocations():
	df = getFullData()
	s = df['location'].drop_duplicates()
	return s.tolist()

def convert_to_datetime(d):
	return datetime.datetime.strptime(np.datetime_as_string(d,unit='s'), '%Y-%m-%dT%H:%M:%S')

def convert_iso_to_datetime(d):
	return datetime.datetime.strptime(d, '%Y-%m-%d')

def getStringencyMasthead():

	return html.Div([
				html.Div([
					html.Div([
						html.Div('Select country:'),
						dcc.Dropdown(id='location-selection-excess', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value=['United Kingdom','Italy','France','Germany','Sweden','Spain'],
									placeholder='Choose Location...',
									disabled=True,
									multi=True)],
						className='masthead__column_1',
						id='location-selection-excess-div'
					),
					html.Div([
						html.Div('Select timeline type:'),
						dcc.Dropdown(id='timeline-selection-excess', 
									options=[{'label': i, 'value': i} for i in timeline_selections],
									value=timeline_selections[0],
									placeholder='Choose Timeline...',
									disabled=False,
									multi=False),
						html.Div([
							html.Div('Select X no. deaths/cases:'),
							dcc.Dropdown(id='count-selection-excess', 
										options=[{'label': i, 'value': i} for i in range(1,10000)],
										value=25,
										placeholder='Choose X...',
										disabled=True,
										multi=False),],
							id='count-selection-excess-div',
							hidden=True)],
						className='masthead__column_2',
						id='timeline-selection-excess-div'
					),

					html.Div([
						html.Div('Select deaths or cases::'),
						dcc.Dropdown(id='data-selection-excess', 
									options=[{'label': i, 'value': i} for i in data_selections],
									value=data_selections[0],
									placeholder='Choose Data...',
									disabled=True,
									multi=False),

						],
						className='masthead__column_3',
						id='data-selection-excess-div'
					),
									html.Div([
						html.Div([
							html.Div('Choose number of days to shift deaths/cases data by:'),
							dcc.Slider(
							        id='shift-range-selection-excess',
							        min=0,
							        max=20,
							        step=1,
							        value=0,
							        marks={
									        0: '0 Days',
									        1: '',
									        2: '',
									        3: '',
									        4: '',
									        5: '5 Days',
									        6: '',
									        7: '',
									        8: '',
									        9: '',
									        10: '10 Days',
									        11: '',
									        12: '',
									        13: '',
									        14: '',
									        15: '15 Days',
									        16: '',
									        17: '',
									        18: '',
									        19: '',
									        20: '20 Days',
									    }
							    ),
							
						],className='masthead-slider',
						  hidden=True),
						html.Div([
							html.Div([
							html.Div('Smooth data over x no. days:'),
							dcc.Slider(
							        id='smoothing-range-selection-excess',
							        min=1,
							        max=10,
							        step=1,
							        value=7,
							        marks={
									        1: '1 Day',
									        2: '',
									        3: '',
									        4: '',
									        5: '5 Days',
									        6: '',
									        7: '',
									        8: '',
									        9: '',
									        10: '10 Days',
									    }
							    ),
							
						]),							
							
						],className='masthead-slider-3'),


			], className='l-subgrid'),
				], id='excess-masthead-div',
				   className='masthead l-grid'),

			])


def getLayout():
	return 	html.Div([
				getHeader("excessdeaths"),
				getStringencyMasthead(),


			html.Div([
						html.Div(id='excess-reg1-graph',className='mobility-reg1-graph'),						
						html.Div(id='excess-reg2-graph',className='mobility-reg2-graph'),					
						html.Div(id='excess-reg3-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='excess-reg4-graph',className='mobility-reg1-graph'),						
						html.Div(id='excess-reg5-graph',className='mobility-reg2-graph'),					
						html.Div(id='excess-reg6-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='excess-reg7-graph',className='mobility-reg1-graph'),						
						html.Div(id='excess-reg8-graph',className='mobility-reg2-graph'),					
						html.Div(id='excess-reg9-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
				html.Div([
					html.Div("Covid-19 Deaths/Cases Data Source:" ),
					dcc.Link("https://data.world/markmarkoh/coronavirus-data", href="https://data.world/markmarkoh/coronavirus-data"),
					html.Div("  " ),
					dcc.Link("https://ourworldindata.org/coronavirus-source-data", href="https://ourworldindata.org/coronavirus-source-data"),
					html.Div("This data has been collected, aggregated, and documented by Diana Beltekian, Daniel Gavrilov, Joe Hasell, Bobbie Macdonald, Edouard Mathieu, Esteban Ortiz-Ospina, Hannah Ritchie, Max Roser."),
					
					html.Div("Excess Deaths Data Source:" ),
					dcc.Link("https://github.com/TheEconomist/covid-19-excess-deaths-tracker", href="https://github.com/TheEconomist/covid-19-excess-deaths-tracker"),
					html.Div("The Economist. This data has been collected, cleaned and analysed by James Tozer and Martín González."),
				],className='worldwide_data_footer')
			], className='l-subgrid'),
		], id='team-stats-page', className='shown-grid l-grid')



@app.callback(
	Output('count-selection-excess', 'disabled'),
	[Input('timeline-selection-excess', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('count-selection-excess-div', 'hidden'),
	[Input('timeline-selection-excess', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True


def getStringencyPlots(locations,
						data_type,
						shift_days,
						smoothing_range,
						timeline,
						x_num,
						location_num,
						df_excess):
	
				
	if len(locations)<=location_num:
		return None
	else:
		if data_type == 'Deaths':			
			df = getNewDeaths()
			df_total = getTotalDeaths()
		elif data_type == 'Cases':
			df = getNewCases()
			df_total = getTotalCases()
		else:
			return None

		data = []

		if not x_num: x_num = 0	

		location = locations[location_num]
		location_key = location.lower().replace(' ','_')

		if timeline == 'Days since X number of deaths/cases':
			return None
		else:

			df[location_key] = df[location_key].fillna(0).rolling(smoothing_range).mean()
			df_loc = df[['date', location_key]].copy()
			df_loc['date'] = df_loc['date'] - datetime.timedelta(days=shift_days)	

			data.append(go.Bar( x=df_loc['date'] ,
				    y=df_loc[location_key] ,
				    marker=dict(
				        color=colour_palette[1],
				    ),
				    opacity=1.0,
				    text=location,
				    name=location + ' Covid 19 ' + data_type,
				    yaxis='y1',
				    showlegend=True
				))

			df_excess['start_datetime'] = df_excess.apply(lambda x: convert_iso_to_datetime(x['start_date']), axis=1)
			df_excess['end_datetime'] = df_excess.apply(lambda x: convert_iso_to_datetime(x['end_date']), axis=1)
			
			df_excess = df_excess.set_index('start_datetime').resample('D').ffill().reset_index()
			df_excess['excess_deaths'] = df_excess['excess_deaths']/7.0
			df_excess['excess_deaths'] = df_excess['excess_deaths'].rolling(smoothing_range).mean().dropna()

			data.append(go.Bar( x=df_excess['start_datetime'] ,
				    y=df_excess['excess_deaths'] ,
				    marker=dict(
				        color=colour_palette[2],
				    ),
				    opacity=0.5,
				    text=location,
				    name=location + ' Excess ' + data_type,
				    yaxis='y1',
				    showlegend=True
				))			


		figure = {
				'data': data,
				'layout': go.Layout(
								title={
								        'text': None,
								        'y':0.8,
								        'x':0.35,
								        'xanchor': 'center',
								        'yanchor': 'top'},
				                showlegend=True,#show_legend,
				                legend=dict(orientation="h",
			                                x=0,
			                                y=1.1,
			                                font=dict(
									            family="Arial",
									            size=14,
									            color="#000000"
									        ),
								),
				                 font=dict(family='Arial', size=12, color='#000000'),
				                hovermode='closest',
				                margin=dict(t=50),
				                xaxis=dict(
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                ),
				                yaxis=dict(
				                        #range=[0,25],
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                        title = data_type,
				                        showgrid=False
				                ),


				                height=400,
				                autosize=True,
				                paper_bgcolor='rgba(0,0,0,0)',
	            				plot_bgcolor='rgba(0,0,0,0)'
				          )
				}


		return  dcc.Graph(figure=figure,
			             config={'displayModeBar': False},
			             id='reg-str-graph')

 



@app.callback(
	Output('excess-reg1-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/britain_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'Britain']
	df = df[df['region'] == 'Britain']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							0,
							df)

@app.callback(
	Output('excess-reg2-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):	
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/italy_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'Italy']
	df = df[df['region'] == 'Italy']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							1,
							df)


@app.callback(
	Output('excess-reg3-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/france_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'France']
	df = df[df['region'] == 'France']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							2,
							df)

@app.callback(
	Output('excess-reg4-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/germany_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'Germany']
	df = df[df['region'] == 'Germany']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							3,
							df)

@app.callback(
	Output('excess-reg5-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/sweden_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'Sweden']
	df = df[df['region'] == 'Sweden']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							4,
							df)

@app.callback(
	Output('excess-reg6-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	url = "https://raw.githubusercontent.com/TheEconomist/covid-19-excess-deaths-tracker/master/output-data/excess-deaths/spain_excess_deaths.csv"
	df = pd.read_csv(url, error_bad_lines=False)
	df = df.fillna(0)
	df = df[df['country'] == 'Spain']
	df = df[df['region'] == 'Spain']
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							5,
							df)

'''@app.callback(
	Output('excess-reg7-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							6)


@app.callback(
	Output('excess-reg8-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							7)


@app.callback(
	Output('excess-reg9-graph', 'children'),
	[Input('location-selection-excess', 'value'),
	Input('data-selection-excess', 'value'),
	Input('shift-range-selection-excess', 'value'),
	Input('smoothing-range-selection-excess', 'value'),
	Input('timeline-selection-excess', 'value'),
	Input('count-selection-excess', 'value')])
def updateStringencyReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num):
	return getStringencyPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							timeline,
							x_num,
							8)'''





if __name__ == '__main__':
	import sys
	main(*sys.argv)
