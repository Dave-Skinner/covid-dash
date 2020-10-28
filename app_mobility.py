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
from countryinfo import CountryInfo
import pycountry
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.metrics import mean_squared_error, r2_score


import sys
import os
import json
import time
import datetime

#import functools32
import collections

from app import app, getCovidDataframes, getGoogleMobilityReports,getStringencyDataFrame, getGoogleMobilityReportsFromCountry
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
				   'Per Million']

mobility_selections = [
			{'label': 'Retail and Recreation', 'value': 'retail_and_recreation_percent_change_from_baseline'},
			{'label': 'Grocery and Pharmacy', 'value': 'grocery_and_pharmacy_percent_change_from_baseline'},
			#{'label': 'Parks', 'value': 'parks_percent_change_from_baseline'},
			{'label': 'Transit Stations', 'value': 'transit_stations_percent_change_from_baseline'},
			{'label': 'Workplaces', 'value': 'workplaces_percent_change_from_baseline'},
			{'label': 'Residential', 'value': 'residential_percent_change_from_baseline'}
]
mobility_list = ['retail_and_recreation_percent_change_from_baseline',
				'grocery_and_pharmacy_percent_change_from_baseline',
				#'parks_percent_change_from_baseline',
				'transit_stations_percent_change_from_baseline',
				'workplaces_percent_change_from_baseline',
				'residential_percent_change_from_baseline']

mobility_dict = {'retail_and_recreation_percent_change_from_baseline':'Retail and Recreation',
			'grocery_and_pharmacy_percent_change_from_baseline':'Grocery and Pharmacy',
			#'parks_percent_change_from_baseline':'Parks',
			'transit_stations_percent_change_from_baseline':'Transit Stations',
			'workplaces_percent_change_from_baseline':'Workplaces', 
			'residential_percent_change_from_baseline':'Residential'}

def getMobilityLabel(value):
	for mob_sel in mobility_selections:
		if mob_sel['value'] == value:
			return mob_sel['label']
	return None


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

def getMobilityMasthead():

	return html.Div([
				html.Div([
					html.Div([
						html.Div('Select country:'),
						dcc.Dropdown(id='location-selection-mobility', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value=['United Kingdom','Sweden','Italy','Spain','France','Germany'],
									placeholder='Choose Location...',
									disabled=False,
									multi=True)],
						className='masthead__column_1',
						id='location-selection-mobility-div'
					),

					html.Div([
						html.Div('Select mobility data:'),
						dcc.Dropdown(id='mobility-selection-mobility', 
									options=mobility_selections,
									value=mobility_selections[3]['value'],
									placeholder='Choose Mobility Data...',
									disabled=False,
									multi=False),
						],
						className='masthead__column_2',
						id='timeline-selection-mobility-div'
					),

					html.Div([
						html.Div('Choose deaths or cases::'),
						dcc.Dropdown(id='data-selection-mobility', 
									options=[{'label': i, 'value': i} for i in data_selections],
									value=data_selections[1],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),
						html.Div('Select total or % of population:'),
						dcc.Dropdown(id='population-selection-mobility', 
									options=[{'label': i, 'value': i} for i in pop_selections],
									value=pop_selections[0],
									placeholder='Choose Data...',
									disabled=False,
									multi=False),

						],
						className='masthead__column_3',
						id='data-selection-mobility-div'
					),

				], id='mobility-masthead-div',
				   className='masthead l-grid'),

			])

def getDaysMarks():
	marks = {}

	for x in range(0,101):
		if x%20 == 0:
			marks[x] = str(x)+ " Days"
		else:
			marks[x] = ""
	marks[1] = "1 Day"
	return marks

def getLayout():
	return 	html.Div([
				getHeader("mobility"),
				getMobilityMasthead(),
				html.Div([
						html.Div([
							html.Div([
							html.Div('Smooth data over x no. days:'),
							dcc.Slider(
							        id='smoothing-range-selection-mobility',
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

							
							
						],className='mobility-slider'),
						html.Div([
							html.Div('Choose number of days to shift mobility data by:'),
							dcc.Slider(
							        id='shift-range-selection-mobility',
							        min=0,
							        max=20,
							        step=1,
							        value=5,
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
							
						],className='mobility-slider-2'),
						
						#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

			], className='l-subgrid'),
			html.Div([

						#html.Div('Total Deaths/Cases',id='mobility-t-stats-div',className='tavs__batting-stats'),
						#html.Div(id='mobility-t-graph',className='tavs__batting-graph'),
						html.Div(id='mobility-t-graph',className='mobility-t-graph'),						
						html.Div([
							html.Div(id='mobility-d-graph',className='mobility-stringency-graph'),
							
							
						],className='tavs__batting-mod-graph'),
						#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

			], className='l-subgrid'),
			html.Div([
						html.Div(id='mobility-reg1-graph',className='mobility-reg1-graph'),						
						html.Div(id='mobility-reg2-graph',className='mobility-reg2-graph'),					
						html.Div(id='mobility-reg3-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='mobility-reg4-graph',className='mobility-reg1-graph'),						
						html.Div(id='mobility-reg5-graph',className='mobility-reg2-graph'),					
						html.Div(id='mobility-reg6-graph',className='mobility-reg3-graph'),

			], className='l-subgrid'),
			html.Div([
						html.Div(id='mobility-reg7-graph',className='mobility-reg7-graph'),						
						html.Div(id='mobility-reg8-graph',className='mobility-reg2-graph'),					
						html.Div(id='mobility-reg9-graph',className='mobility-reg3-graph'),

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
					
					html.Div("Google Mobility Data Source:" ),
					dcc.Link("https://www.google.com/covid19/mobility/", href="https://www.google.com/covid19/mobility/"),					
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






def getShowLegend(mob_data_num,
					count):
	if mob_data_num > 2:
		return False
	#print (mob_data_num, count, "~~~~~~~~~~~~~~~~~~~~~~~#")
	if count%3 == mob_data_num:
		return True
	else:
		return False




 


def getMobilityPlots(locations,
						data_type,
						shift_days,
						smoothing_range,
						mobility_type,
						pop_type,
						location_num):
	
	timeline = 'Days since X number of deaths/cases'
	x_num = 10
	if len(locations)<=location_num:
		return None
	else:
		mob_loc_df = getGoogleMobilityReportsFromCountry(locations[location_num])
		#print (mob_reports_df.head(10))
		#mob_loc_df = mob_reports_df[mob_reports_df['sub_region_1'].isnull()]
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

		if pop_type == 'Per Million':
			country = CountryInfo(location)
			population = country.population()
			area = country.area()
			pop_density = float(population)/area
			print (population)
			print (area)
			print (pop_density)
			df[location_key] = 1000000.0*df[location_key]/population
		else:
			population = 1.0

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

			#mob_loc_df = mob_reports_df[mob_reports_df['country_region']==location]  
			print (mob_loc_df.info())
			#print (mob_loc_df['sub_region_1'])
			#mob_loc_df = mob_loc_df[mob_loc_df['sub_region_1'].isnull()]
			mob_loc_df['date'] = pd.to_datetime(mob_loc_df.date)
			mob_loc_df.sort_values(by=['date'])
			mob_loc_df[mobility_type] = mob_loc_df[mobility_type].fillna(0).rolling(smoothing_range).mean()

			country = pycountry.countries.get(name=location).alpha_3
			stringency_df = getStringencyDataFrame(country)	
			stringency_df['date'] = pd.to_datetime(stringency_df.date)
			stringency_df.sort_values(by=['date'])	

			df_loc = pd.merge(df_loc, mob_loc_df, how='left', on='date')
			df_loc = pd.merge(df_loc, stringency_df, how='left', on='date')

			if mobility_type != 'residential_percent_change_from_baseline':
				df_loc[mobility_type] = -df_loc[mobility_type]
				mobility_name = '% Time less at ' + mobility_dict[mobility_type]
			else:
				mobility_name = '% Time more at ' + mobility_dict[mobility_type]

			#print (df_loc[mobility_type])

			data.append(go.Bar( x=df_loc.index ,
				    y=df_loc[location_key] ,
				    marker=dict(
				        color=colour_palette[location_num],
				    ),
				    opacity=0.7,
				    text=location,
				    #name=location + ' ' + data_type,
				    yaxis='y2',
				    showlegend=False
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
			data.append(go.Scatter( x=df_loc.index ,
				    y=df_loc[mobility_type] ,
					    mode='lines',
					    marker=dict(
					        color='rgb(0,0,0)',
					    ),
					    line = dict(
					    	color='rgb(0,0,0)', 
					    	dash='solid'),
				    opacity=1.0,
				    text=location,
				    name=mobility_name,
				    yaxis='y1',
				    showlegend=True
				))


		else:
			return None

		if mobility_type == 'residential_percent_change_from_baseline':
			y_range = [0,100]
		else:
			y_range = [0,100]

		if pop_type == "Per Million":
			title_sub = ' (per million)'
		else:
			title_sub = ''

		figure = {
				'data': data,
				'layout': go.Layout(
								title={
								        'text': location,
								        'y':1.0,
								        'x':0.5,
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
				                        #range=[0,1200],
				                        rangemode="tozero",
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                        side='left',
				                        title = data_type + title_sub,
				                        showgrid=False
				                ),
				                yaxis=dict(
				                			
				                			#autorange='reversed',
				                			range=y_range,
				                			rangemode='tozero',
				                			anchor='x',
        									overlaying= 'y',
				               				tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
                                   				side='right',
				                        	title = 'Mobility/Stringency',
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
	Output('mobility-reg1-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							0)

@app.callback(
	Output('mobility-reg2-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							1)

@app.callback(
	Output('mobility-reg3-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							2)

@app.callback(
	Output('mobility-reg4-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							3)

@app.callback(
	Output('mobility-reg5-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							4)

@app.callback(
	Output('mobility-reg6-graph', 'children'),
	[Input('location-selection-mobility', 'value'),
	Input('data-selection-mobility', 'value'),
	Input('shift-range-selection-mobility', 'value'),
	Input('smoothing-range-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'value'),
	Input('mobility-selection-mobility', 'label'),
	Input('population-selection-mobility', 'value')])
def updateMobilityReportsRegression(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							mobility_label,
							pop_type):
	return getMobilityPlots(locations,
							data_type,
							shift_days,
							smoothing_range,
							mobility_data,
							pop_type,
							5)







if __name__ == '__main__':
	import sys
	main(*sys.argv)