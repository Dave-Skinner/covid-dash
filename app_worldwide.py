#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from countryinfo import CountryInfo


import sys
import os
import json
import time
import datetime

import collections

from app import app, getCovidDataframes
from header import getHeader


'''Use this library to get population and area ---> Pop density

https://pypi.org/project/countryinfo/
'''

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

def convert_to_datetime(d):
	return datetime.datetime.strptime(np.datetime_as_string(d,unit='s'), '%Y-%m-%dT%H:%M:%S')

def getDaysMarks(days):
	marks = {}

	for x in range(0,days+1):
		if x%5 == 0:
			marks[x] = str(x)+ " Days"
		else:
			marks[x] = ""
	#marks[1] = "1 Day"
	return marks

def getWorldwideMasthead():

	return html.Div([
				html.Div([
					html.Div([
						html.Div('Select countries for comparison:'),
						dcc.Dropdown(id='location-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value=['United Kingdom','United States','Italy','Brazil','France','Germany'],
									placeholder='Choose Location...',
									disabled=False,
									multi=True)],
						className='masthead__column_1',
						id='location-selection-worldwide-div'
					),

					html.Div([
						html.Div('Select timeline type:'),
						dcc.Dropdown(id='timeline-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in timeline_selections],
									value=timeline_selections[0],
									placeholder='Choose Timeline...',
									disabled=False,
									multi=False),
						html.Div([
							html.Div('Select X no. deaths/cases:'),
							dcc.Dropdown(id='count-selection-worldwide', 
										options=[{'label': i, 'value': i} for i in range(1,10000)],
										value=25,
										placeholder='Choose X...',
										disabled=True,
										multi=False),],
							id='count-selection-worldwide-div',
							hidden=True)],
						className='masthead__column_2',
						id='timeline-selection-worldwide-div'
					),

					html.Div([
						html.Div('Select deaths or cases::'),
						dcc.Dropdown(id='data-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in data_selections],
									value=data_selections[0],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),
						html.Div('Select total or % of population:'),
						dcc.Dropdown(id='population-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in pop_selections],
									value=pop_selections[0],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),
						],
						className='masthead__column_3',
						id='data-selection-worldwide-div'
					),
					html.Div([
						html.Div([
							html.Div('Choose no. of days to extend prediction (made using the latest rate of change with smoothing applied):'),
							dcc.Slider(
							        id='prediction-range-selection-worldwide',
							        min=0,
							        max=40,
							        step=1,
							        value=5,
							        marks=getDaysMarks(40)
							    ),
							
						],className='masthead-slider'),
						html.Div([
							html.Div('Smooth rate of change data over x no. days:'),
							dcc.Slider(
							        id='smoothing-range-selection-worldwide',
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
							
						],className='masthead-slider-3'),
					], className='l-subgrid'),
				], id='worldwide-masthead-div',
				   className='masthead l-grid'),

			])



def getLayout():
	return 	html.Div([
				getHeader("worldwide"),
				getWorldwideMasthead(),


				html.Div([

						html.Div(id='worldwide-t-graph',className='tavs__batting-graph'),
						html.Div([
							html.Div(id='worldwide-d-graph'),							
						],className='tavs__batting-mod-graph'),

			], className='l-subgrid'),

			html.Div([
				html.Div([
					html.Div("Covid-19 Deaths/Cases Data Source:" ),
					dcc.Link("https://data.world/markmarkoh/coronavirus-data", href="https://data.world/markmarkoh/coronavirus-data"),
					html.Div("  " ),
					dcc.Link("https://ourworldindata.org/coronavirus-source-data", href="https://ourworldindata.org/coronavirus-source-data"),
					html.Div("This data has been collected, aggregated, and documented by Diana Beltekian, Daniel Gavrilov, Joe Hasell, Bobbie Macdonald, Edouard Mathieu, Esteban Ortiz-Ospina, Hannah Ritchie, Max Roser."),
					
				],className='worldwide_data_footer')
			], className='l-subgrid'),

		], id='team-stats-page', className='shown-grid l-grid')



	
def sumLocations(s,
				locations):
	s_sum = 0
	for location in locations:
		location_key = location.lower().replace(' ','_')
		s_sum += s[location_key]
	return s_sum


@app.callback(
	Output('count-selection-worldwide', 'disabled'),
	[Input('timeline-selection-worldwide', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('count-selection-worldwide-div', 'hidden'),
	[Input('timeline-selection-worldwide', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('worldwide-t-graph', 'children'),
	[Input('location-selection-worldwide', 'value'),
	Input('timeline-selection-worldwide', 'value'),
	Input('data-selection-worldwide', 'value'),
	Input('count-selection-worldwide', 'value'),
	Input('smoothing-range-selection-worldwide', 'value'),
	Input('prediction-range-selection-worldwide', 'value'),
	Input('population-selection-worldwide', 'value')])
def updateTotalDeathsTimeline(locations,
							timeline,
							data_type,
							x_num,
							smoothing_range,
							x_days,
							pop_type):



	if locations:
		if data_type == 'Deaths':			
			df = getTotalDeaths()
		elif data_type == 'Cases':
			df = getTotalCases()
		else:
			return None
		df['sum_data'] = df.apply(lambda x: sumLocations(x, locations), axis=1)
		df = df.drop(df[(df['sum_data'] == 0)].index)
		data = []
		count=0
		for location in locations:
			location_key = location.lower().replace(' ','_')
			if pop_type == '% of Population':
				country = CountryInfo(location)
				population = country.population()
				area = country.area()
				pop_density = float(population)/area
				print (population)
				print (area)
				print (pop_density)
				df[location_key] = 100.0*df[location_key]/population
			else:
				population = 1.0

			if not x_num: x_num = 0			

			if timeline == 'Days since X number of deaths/cases':
				df_location = df.fillna(0)
				df_location = df_location.drop(df_location[(df_location[location_key] < x_num/population)].index)
				df_location = df_location.reset_index()
				data.append(go.Scatter( x=df_location.index,
					    y=df_location[location_key],
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    opacity=1.0,
					    text=location,
					    name=location
					))

				prediction_df = df_location[['date',location_key]]
				prediction_df['rolling_mean'] = 1.0 + df_location[location_key].fillna(0).pct_change().rolling(smoothing_range).mean()
				prediction_df = prediction_df.iloc[[-1]]
				r_index = prediction_df.index.values[0]

				r_mean = prediction_df['rolling_mean'].values[0]
				r_num = prediction_df[location_key].values[0]
				for x in range(1,x_days):
					extra_df = pd.DataFrame([[float(r_num)*r_mean**x,
											 r_mean]], columns = [location_key,"rolling_mean"])
					prediction_df = pd.concat([prediction_df, extra_df], ignore_index=True,axis=0)

				prediction_df.index = pd.RangeIndex(start=r_index, stop=r_index+x_days, step=1)

				data.append(go.Scatter( x=prediction_df.index,
					    y=prediction_df[location_key],
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    line = dict(
					    	color=colour_palette[count], 
					    	dash='dot'),
					    opacity=1.0,
					    text=location,
					    name=location,
					    showlegend=False
					))
			else:	

				data.append(go.Scatter( x=df['date'],
					    y=df[location_key].fillna(0),
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    opacity=1.0,
					    text=location,
					    name=location
					))
				prediction_df = df[['date',location_key]]
				prediction_df['rolling_mean'] = 1.0 + df[location_key].fillna(0).pct_change().rolling(smoothing_range).mean()
				prediction_df = prediction_df.iloc[[-1]]
				r_date = prediction_df['date'].values[0]
				r_mean = prediction_df['rolling_mean'].values[0]
				r_num = prediction_df[location_key].values[0]
				
				for x in range(1,x_days):
					r_dt = convert_to_datetime(r_date)#datetime.datetime.strptime(r_date, '%Y-%m-%d') 
					extra_df = pd.DataFrame([[r_dt+datetime.timedelta(days=x),
											 float(r_num)*r_mean**x,
											 r_mean]], columns = ["date", location_key,"rolling_mean"])
					prediction_df = pd.concat([prediction_df, extra_df], ignore_index=True,axis=0)

				data.append(go.Scatter( x=prediction_df['date'],
					    y=prediction_df[location_key],
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    line = dict(
					    	color=colour_palette[count], 
					    	dash='dot'),
					    opacity=1.0,
					    text=location,
					    name=location,
					    showlegend=False
					))				

			count+=1
		if pop_type == "% of Population":
			title_sub = ' (% of population)'
		else:
			title_sub = ''
		figure = {
				'data': data,
				'layout': go.Layout(
								title='Cumulative '+data_type+title_sub,
				                legend=dict(orientation="h",
			                                x=0,
			                                y=1.1),
				                 font=dict(family='Arial', size=15, color='#000000'),
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
				                        #range=y_axis_range,
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                ),
				                height=400,
				                autosize=True,
				                paper_bgcolor='rgba(0,0,0,0)',
	            				plot_bgcolor='rgba(0,0,0,0)'
				          )
				}


		return  dcc.Graph(figure=figure,
			             config={'displayModeBar': False},
			             id='total-deaths-t-graph')


@app.callback(
	Output('worldwide-d-graph', 'children'),
	[Input('location-selection-worldwide', 'value'),
	Input('timeline-selection-worldwide', 'value'),
	Input('data-selection-worldwide', 'value'),
	Input('count-selection-worldwide', 'value'),
	Input('smoothing-range-selection-worldwide', 'value')])
def updateRatesTimeline(locations,
							timeline,
							data_type,
							x_num,
							smoothing_range):
						
	if locations:
		if data_type == 'Deaths':			
			df = getTotalDeaths()
		elif data_type == 'Cases':
			df = getTotalCases()
		else:
			return None

		df['sum_data'] = df.apply(lambda x: sumLocations(x, locations), axis=1)
		df = df.drop(df[(df['sum_data'] == 0)].index)
		df = df.fillna(0)
		
		data = []
		count=0
		for location in locations:
			if not x_num: x_num = 0
			location_key = location.lower().replace(' ','_')
			if timeline == 'Days since X number of deaths/cases':
				df_location = df.fillna(0)
				df_location = df_location.drop(df_location[(df_location[location_key] < x_num)].index)
				df_location = df_location.reset_index()
				data.append(go.Scatter( x=df_location.index,
					    y=100.0*df_location[location_key].pct_change().rolling(smoothing_range).mean(),
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    opacity=1.0,
					    text=location,
					    name=location
					))
			else:	

				data.append(go.Scatter( x=df['date'],
					    y=100.0*df[location_key].fillna(0).pct_change().rolling(smoothing_range).mean(),
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count],
					    ),
					    opacity=1.0,
					    text=location,
					    name=location
					))
			count+=1
		
		figure = {
				'data': data,
				'layout': go.Layout(
								title='Daily rate of change for '+data_type+' (%)',
								showlegend=False,
				                legend=dict(orientation="h",
			                                x=0,
			                                y=1.1),
				                 font=dict(family='Arial', size=15, color='#000000'),
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
				                        #range=y_axis_range,
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                ),
				                height=400,
				                autosize=True,
				                paper_bgcolor='rgba(0,0,0,0)',
	            				plot_bgcolor='rgba(0,0,0,0)'
				          )
				}


		return  dcc.Graph(figure=figure,
			             config={'displayModeBar': False},
			             id='total-deaths-d-graph')




if __name__ == '__main__':
	import sys
	main(*sys.argv)
