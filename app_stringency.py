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
					'rgb(255,234,0)',
					'rgb(6,193,95)',
					'rgb(209,210,212)',
					'rgb(204,123,6)',
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

def getStringencyMasthead():

	return html.Div([
				html.Div([
					html.Div([
						html.Div('Select country:'),
						dcc.Dropdown(id='location-selection-stringency', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value=['United Kingdom','Italy','Spain','France','Germany','Sweden'],
									placeholder='Choose Location...',
									disabled=False,
									multi=True)],
						className='masthead__column_1',
						id='location-selection-stringency-div'
					),
					html.Div([
						html.Div('Select timeline type:'),
						dcc.Dropdown(id='timeline-selection-stringency', 
									options=[{'label': i, 'value': i} for i in timeline_selections],
									value=timeline_selections[1],
									placeholder='Choose Timeline...',
									disabled=False,
									multi=False),
						html.Div([
							html.Div('Select X no. deaths/cases:'),
							dcc.Dropdown(id='count-selection-stringency', 
										options=[{'label': i, 'value': i} for i in range(1,10000)],
										value=25,
										placeholder='Choose X...',
										disabled=True,
										multi=False),],
							id='count-selection-stringency-div',
							hidden=True)],
						className='masthead__column_2',
						id='timeline-selection-stringency-div'
					),

					html.Div([
						html.Div('Select deaths or cases::'),
						dcc.Dropdown(id='data-selection-stringency', 
									options=[{'label': i, 'value': i} for i in data_selections],
									value=data_selections[0],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),

						],
						className='masthead__column_3',
						id='data-selection-stringency-div'
					),
									html.Div([
						html.Div([
							html.Div('Choose number of days to shift deaths/cases data by:'),
							dcc.Slider(
							        id='shift-range-selection-stringency',
							        min=0,
							        max=20,
							        step=1,
							        value=16,
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
							
						],className='masthead-slider'),
						html.Div([
							html.Div([
							html.Div('Smooth data over x no. days:'),
							dcc.Slider(
							        id='smoothing-range-selection-stringency',
							        min=1,
							        max=10,
							        step=1,
							        value=5,
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
				], id='stringency-masthead-div',
				   className='masthead l-grid'),

			])


def getLayout():
	return 	html.Div([
				getHeader("stringency"),
				getStringencyMasthead(),


			html.Div([
						html.Div(id='stringency-reg1-graph',className='mobility-reg1-graph'),						
						html.Div(id='stringency-reg2-graph',className='mobility-reg2-graph'),					
						html.Div(id='stringency-reg3-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='stringency-reg4-graph',className='mobility-reg1-graph'),						
						html.Div(id='stringency-reg5-graph',className='mobility-reg2-graph'),					
						html.Div(id='stringency-reg6-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='stringency-reg7-graph',className='mobility-reg1-graph'),						
						html.Div(id='stringency-reg8-graph',className='mobility-reg2-graph'),					
						html.Div(id='stringency-reg9-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
				html.Div([
					html.Div("Covid-19 Deaths/Cases Data Source:" ),
					dcc.Link("https://data.world/markmarkoh/coronavirus-data", href="https://data.world/markmarkoh/coronavirus-data"),
					html.Div("  " ),
					dcc.Link("https://ourworldindata.org/coronavirus-source-data", href="https://ourworldindata.org/coronavirus-source-data"),
					html.Div("This data has been collected, aggregated, and documented by Diana Beltekian, Daniel Gavrilov, Joe Hasell, Bobbie Macdonald, Edouard Mathieu, Esteban Ortiz-Ospina, Hannah Ritchie, Max Roser."),
					
					html.Div("Stringency Index Data Source:" ),
					dcc.Link("https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker", href="https://www.bsg.ox.ac.uk/research/research-projects/coronavirus-government-response-tracker"),
					html.Div("Hale, Thomas, Sam Webster, Anna Petherick, Toby Phillips, and Beatriz Kira (2020). Oxford COVID-19 Government Response Tracker, Blavatnik School of Government. Data use policy: Creative Commons Attribution CC BY standard."),
				],className='worldwide_data_footer')
			], className='l-subgrid'),
		], id='team-stats-page', className='shown-grid l-grid')



@app.callback(
	Output('count-selection-stringency', 'disabled'),
	[Input('timeline-selection-stringency', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('count-selection-stringency-div', 'hidden'),
	[Input('timeline-selection-stringency', 'value')])
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
						location_num):
	
				
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
			df_total_loc = df_total.fillna(0)
			df_total_loc['date'] = df_total_loc['date'] - datetime.timedelta(days=shift_days)
			df_total_loc = df_total_loc.drop(df_total_loc[(df_total_loc[location_key] < x_num)].index)
			df_total_loc = df_total_loc.reset_index()
			df_total_loc = df_total_loc.drop([location_key], axis=1)

			df[location_key] = df[location_key].fillna(0).rolling(smoothing_range).mean()
			df_loc = df[['date', location_key]].copy()
			df_loc['date'] = df_loc['date'] - datetime.timedelta(days=shift_days)

			df_loc = pd.merge(df_total_loc, df_loc, how='left', on='date')

			country = pycountry.countries.get(name=location).alpha_3
			stringency_df = getStringencyDataFrame(country)	
			stringency_df['date'] = pd.to_datetime(stringency_df.date)
			stringency_df.sort_values(by=['date'])	

			df_loc = pd.merge(df_loc, stringency_df, how='left', on='date')

			data.append(go.Bar( x=df_loc.index ,
				    y=df_loc[location_key] ,
				    marker=dict(
				        color=colour_palette[location_num],
				    ),
				    opacity=1.0,
				    text=location,
				    name=location + ' ' + data_type,
				    yaxis='y2',
				    showlegend=True
				))

			data.append(go.Scatter( x=df_loc.index ,
				    y=df_loc['stringency'] ,
					    mode='lines',
					    marker=dict(
					        color='rgb(0,0,0)',
					    ),
					    line = dict(
					    	color='rgb(0,0,0)', 
					    	dash='dot'),
				    opacity=1.0,
				    text=location,
				    name='Stringency Index',
				    yaxis='y1',
				    showlegend=True
				))

		else:

			df[location_key] = df[location_key].fillna(0).rolling(smoothing_range).mean()
			df_loc = df[['date', location_key]].copy()
			df_loc['date'] = df_loc['date'] - datetime.timedelta(days=shift_days)	

			data.append(go.Bar( x=df_loc['date'] ,
				    y=df_loc[location_key] ,
				    marker=dict(
				        color=colour_palette[location_num],
				    ),
				    opacity=1.0,
				    text=location,
				    name=location + ' ' + data_type,
				    yaxis='y2',
				    showlegend=True
				))

			country = pycountry.countries.get(name=location).alpha_3
			stringency_df = getStringencyDataFrame(country)	
			stringency_df['date'] = pd.to_datetime(stringency_df.date)
			stringency_df.sort_values(by=['date'])

			data.append(go.Scatter( x=stringency_df['date'] ,
				    y=stringency_df['stringency'] ,
					    mode='lines',
					    marker=dict(
					        color='rgb(0,0,0)',
					    ),
					    line = dict(
					    	color='rgb(0,0,0)', 
					    	dash='dot'),
				    opacity=1.0,
				    text=location,
				    name='Stringency Index',
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
				                yaxis2=dict(
				                        #range=[0,25],
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                        side='left',
				                        title = data_type,
				                        showgrid=False
				                ),
				                yaxis=dict(
				                			range=[0,100],
				               				tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
                                   				side='right',
				                        	title = 'Stringency Index',
				                        showgrid=False),

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
	Output('stringency-reg1-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							0)

@app.callback(
	Output('stringency-reg2-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							1)


@app.callback(
	Output('stringency-reg3-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							2)

@app.callback(
	Output('stringency-reg4-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							3)

@app.callback(
	Output('stringency-reg5-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							4)

@app.callback(
	Output('stringency-reg6-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							5)

@app.callback(
	Output('stringency-reg7-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
	Output('stringency-reg8-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
	Output('stringency-reg9-graph', 'children'),
	[Input('location-selection-stringency', 'value'),
	Input('data-selection-stringency', 'value'),
	Input('shift-range-selection-stringency', 'value'),
	Input('smoothing-range-selection-stringency', 'value'),
	Input('timeline-selection-stringency', 'value'),
	Input('count-selection-stringency', 'value')])
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
							8)





if __name__ == '__main__':
	import sys
	main(*sys.argv)
