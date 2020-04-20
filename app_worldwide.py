#!/usr/bin/python
# -*- coding: utf-8 -*- 

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


import sys
import os
import json
import time

#import functools32
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
					'rgb(204,123,6)']

timeline_selections = ['Timeline',
						'Days since X number of deaths/cases']

data_selections = ['Deaths',
					'Cases']

count_selections = [25]


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

def getWorldwideMasthead():

	return html.Div([
				html.Div([
					html.Div([
						html.Div('Select countries for comparison:'),
						dcc.Dropdown(id='location-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value=['United Kingdom','United States','Italy','Spain','France','Germany'],
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
							html.Div('Choose X no. deaths/cases:'),
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
						html.Div('Choose deaths or cases::'),
						dcc.Dropdown(id='data-selection-worldwide', 
									options=[{'label': i, 'value': i} for i in data_selections],
									value=data_selections[0],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),
						html.Div('Smooth data over x no. days:'),
						dcc.Slider(
						        id='smoothing-range-selection-worldwide',
						        min=1,
						        max=10,
						        step=1,
						        value=1,
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
						    )],
						className='masthead__column_3',
						id='data-selection-worldwide-div'
					),

				], id='worldwide-masthead-div',
				   className='masthead l-grid'),

			])



def getLayout():
	return 	html.Div([
				html.Div([
						#getHeader("worldwide"),
						getWorldwideMasthead(),
						html.Div('Total Deaths/Cases',id='worldwide-t-stats-div',className='tavs__batting-stats'),
						html.Div(id='worldwide-t-graph',className='tavs__batting-graph'),
						html.Div(id='worldwide-t-report',className='tavs__batting-mod-graph'),
						#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

			], className='l-subgrid'),
				html.Div([
						#getHeader("worldwide"),
						#getWorldwideMasthead(),
						html.Div('Daily Growth Rate in Deaths/Cases',id='worldwide-d-stats-div',className='tavs__batting-stats'),
						html.Div(id='worldwide-d-graph',className='tavs__batting-graph'),
						html.Div(id='worldwide-d-report',className='tavs__batting-mod-graph'),
						#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

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
def updateTotalDeathsTimeline(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('count-selection-worldwide-div', 'hidden'),
	[Input('timeline-selection-worldwide', 'value')])
def updateTotalDeathsTimeline(timeline):
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
	Input('smoothing-range-selection-worldwide', 'value')])
def updateTotalDeathsTimeline(locations,
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
					    y=df_location[location_key].rolling(smoothing_range).sum(),
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
					    y=df[location_key].fillna(0).rolling(smoothing_range).sum(),
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
		#df = df.rolling(5).sum()

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
					    y=100.0*df_location[location_key].rolling(smoothing_range).sum().pct_change(),
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
					    y=100.0*df[location_key].fillna(0).rolling(smoothing_range).sum().pct_change(),
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