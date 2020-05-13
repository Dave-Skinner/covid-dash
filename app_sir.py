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
from sklearn.metrics import mean_squared_error
from scipy.integrate import odeint


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
						html.Div('Select country:'),
						dcc.Dropdown(id='location-selection-sir', 
									options=[{'label': i, 'value': i} for i in getLocations()],
									value='United Kingdom',#,'United States','Italy','Spain','France','Germany'],
									placeholder='Choose Location...',
									disabled=False,
									multi=False)],
						className='masthead__column_1',
						id='location-selection-sir-div'
					),

					html.Div([
						html.Div('Select timeline type:'),
						dcc.Dropdown(id='timeline-selection-sir', 
									options=[{'label': i, 'value': i} for i in timeline_selections],
									value=timeline_selections[1],
									placeholder='Choose Timeline...',
									disabled=True,
									multi=False),
						html.Div([
							html.Div('Select X no. deaths:'),
							dcc.Dropdown(id='count-selection-sir', 
										options=[{'label': i, 'value': i} for i in range(1,10000)],
										value=25,
										placeholder='Choose X...',
										disabled=True,
										multi=False),],
							id='count-selection-sir-div',
							hidden=True)],
						className='masthead__column_2',
						id='timeline-selection-sir-div'
					),

					html.Div([
						html.Div('Choose Mortality Rate:'),
						dcc.Dropdown(id='mortality-rate-selection-sir', 
									options=[{'label': str(i)+'%', 'value': i/100.0} for i in range(1,100)],
										value=0.02),
						html.Div('No. of days a person remains infectious:'),
						dcc.Dropdown(id='infectious-days-selection-sir', 
									options=[{'label': str(i)+' Days', 'value': i} for i in range(2,14)],
										value=7),
						],
						className='masthead__column_3',
						id='data-selection-sir-div'
					),
					html.Div([
						html.Div([
							html.Div('Choose no. of days to extend prediction (using the latest sub-model):'),
							dcc.Slider(
							        id='prediction-range-selection-sir',
							        min=0,
							        max=40,
							        step=1,
							        value=10,
							        marks=getDaysMarks(40)
							    ),
							
						],className='masthead-slider'),
						html.Div([
							html.Div('Choose duration of each sub-model:'),
							dcc.Slider(
							        id='smoothing-range-selection-sir',
							        min=1,
							        max=15,
							        step=1,
							        value=9,
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
									        11: '',
									        12: '',
									        13: '',
									        14: '',
									        15: '15 Days'
									    }
							    ),
							
						],className='masthead-slider-2'),
					], className='l-subgrid'),
				], id='sir-masthead-div',
				   className='masthead l-grid'),

			])



def getLayout():
	return 	html.Div([
				getHeader("sirmodel"),
				getWorldwideMasthead(),


				html.Div([

						html.Div([
							dcc.Checklist(
							    options=[
							        {'label': 'Show Infections (SIR MODEL)', 'value': 'Yes'},
							    ],
							    #value=None,
							    id='show-infections-selection-sir'
							),
							html.Div(id='sir-t-graph'),
						],className='tavs__batting-graph'),
						html.Div([
							html.Div('''This is an attempt to retro-fit the simplest SIR epidemiological model to the current available data.
										The real world is far more complex than this model. This should not be considered an accurate representation of the pandemic.'''),
							html.Div('''''',className='sir_text_gap'),
							html.Div('''One of the problems with simple linear models such as SIR is that R0 (the rate of transmission) is fixed throughout time.
										This is not true in the real world as any number of factors cause R0 to vary. In particular, mitigation strategies such as
										people staying at home will cause R0 to reduce.'''),
							html.Div('''''',className='sir_text_gap'),
							html.Div('''To model this variation in R0 I have split the timeline into multiple sub-models that can have a different R0 value.
										The final state from the previous sub-model provides the initial conditions for the next. 
										I used a Mean Squared Error algorithm to choose the R0 value that best fits the actual data.'''),
							html.Div('''''',className='sir_text_gap'),
							html.Div('''This technique is very sensitive to the sub-model duration. The smoother the real world data the easier it is to fit.
										But sometimes the sub-model boundaries will coincide with kinks in the real world data. Changing the duration of the sub-model 
										can sometimes help the model fit around these kinks. Sometimes the model is unable to find a satisfactory fit at all.'''),
							html.Div('''''',className='sir_text_gap'),
							html.Div('''The bars on the graph show the R0 of the different sub-models. This gives us an idea of how R0 changes as the epidemic progresses in that 
										country. The dotted lines show the modelled number of deaths, the forecast can be extended into the future using the extend prediction slider above. 
										Changing any of the parameters will cause the model to reload, which may take some time.
										'''),
							html.Div(id='sir-d-graph'),							
						],className='sir_text'),

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
	Output('count-selection-sir', 'disabled'),
	[Input('timeline-selection-sir', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

@app.callback(
	Output('count-selection-sir-div', 'hidden'),
	[Input('timeline-selection-sir', 'value')])
def updateCountSelection(timeline):
	if timeline == 'Days since X number of deaths/cases':
		return False
	else:
		return True

# The SIR model differential equations.
def deriv(y, t, N, beta, gamma):
	S, I, R = y
	dSdt = -beta * S * I / N
	dIdt = beta * S * I / N - gamma * I
	dRdt = gamma * I
	return dSdt, dIdt, dRdt



def getBestFit(df_location,
				x_num,
				population,
				mortality_rate = 0.01,
				disease_duration = 14,
				first_pass=True, 
				S_in=None,
				I_in=None,
				R_in=None,
				D_in=None,
				x_days=None,
				print_bool=False):

	num_days = df_location.shape[0]
	N = population

	min_mse = 1000000000
	best_beta = None
	best_N = None
	best_D = None
	best_S = None
	best_I = None
	best_R = None

	if print_bool:
		print ('I in = ',int(I_in))
		print ('R in = ',int(R_in))
		print (df_location)

	beta_range = 200

	if first_pass:
		I_range = 100
	else:
		I_range = 2
	for x in range(1,beta_range):
		beta = 2*x/(beta_range)

		for y in range(1,I_range):			
			if first_pass:
				D0 = x_num
				I0 = int(D0 + D0*y*3)
				#I0 = int(D0/(y*mortality_rate/50.0))
				R0 = (D0/mortality_rate)				
				S0 = N - I0 - R0
			else:
				D0 = D_in
				I0 = int(I_in)
				R0 = int(R_in)
				S0 = N - I0 - R0

			gamma = 1./disease_duration 
			t = np.linspace(0, num_days, num_days)
			# Initial conditions vector
			y0 = S0, I0, R0
			# Integrate the SIR equations over the time grid, t.
			ret = odeint(deriv, y0, t, args=(N, beta, gamma))
			S, I, R = ret.T

			D = pd.DataFrame(R*mortality_rate)

			mse = mean_squared_error(df_location, D)
			if mse < min_mse:
				if print_bool:
					print ('Min MSE = ',mse)
				min_mse = mse
				best_beta = beta
				best_D = D
				best_S = S
				best_I = I
				best_R = R
	
	max_D = best_D.iloc[-1]
	max_df_location = df_location.iloc[-1]
	end_diff = max_df_location/max_D

	if x_days:
		t = np.linspace(0, num_days+x_days, num_days+x_days)
		# Initial conditions vector
		y0 = S0, I0, R0
		# Integrate the SIR equations over the time grid, t.
		ret = odeint(deriv, y0, t, args=(N, best_beta, gamma))
		best_S, best_I, best_R = ret.T

		best_D = pd.DataFrame(best_R*mortality_rate)
	

	best_D = best_D*end_diff
	best_R = pd.DataFrame(best_R)*end_diff 
	best_I = pd.DataFrame(best_I)*end_diff 

	print ('REGULAR min_mse = ', min_mse)
	print ('Total Infections = ', int(N - best_S[-1]))


	return t, best_D, best_I, best_R, best_beta*disease_duration


def getVariableBetaForecast(df_location,
							location,
							x_days,
							forecast_size,
							mortality_rate = 0.01,
							disease_duration = 14):

	location_key = location.lower().replace(' ','_')
	country = CountryInfo(location)
	population = country.population()

	x_num = df_location[location_key].iloc[0]
	df_location = df_location[location_key]

	num_days = df_location.shape[0]
	full_t = np.linspace(0, num_days, num_days)	
	full_loc = df_location
	r0_list = []

	t, best_D, best_I, best_R, best_r0 = getBestFit(df_location.head(forecast_size), 
													x_num,
													population,
													mortality_rate = mortality_rate,
													disease_duration = disease_duration)
	
	full_D = best_D
	full_I = best_I
	r0_list.append(best_r0)

	remain_days = num_days-forecast_size
	while remain_days > 2*forecast_size:
		df_location = df_location.tail(remain_days+1)
		print_bool = False
		if (remain_days-forecast_size + 1) < 2*forecast_size:
			print ("Best I = ", best_I.iloc[-1])
			print ("Best R = ", best_R.iloc[-1])
			print_bool = True
		t, best_D, best_I, best_R, best_r0 = getBestFit(df_location.head(forecast_size),
													x_num,
													population,
													mortality_rate = mortality_rate,
													disease_duration = disease_duration,
													first_pass=False, 
													I_in=best_I.iloc[-1],
													R_in=best_R.iloc[-1],
													print_bool=print_bool)

		full_D = pd.concat([full_D, best_D.tail(forecast_size-1)], ignore_index=True,axis=0)
		full_I = pd.concat([full_I, best_I.tail(forecast_size-1)], ignore_index=True,axis=0)
		r0_list.append(best_r0)
		if (remain_days-forecast_size + 1) < 2*forecast_size:
			print (df_location.head(forecast_size))
			print (full_D)
			print (full_I)
			
		remain_days = remain_days-forecast_size + 1

	df_location = df_location.tail(remain_days+1)

	t, best_D, best_I, best_R, best_r0 = getBestFit(df_location,
												x_num,
												population,
												mortality_rate = mortality_rate,
												disease_duration = disease_duration,
												first_pass=False,
												I_in=best_I.iloc[-1],
												R_in=best_R.iloc[-1],
												x_days=x_days)

	full_D = pd.concat([full_D, best_D.tail(-1)], ignore_index=True,axis=0)
	full_I = pd.concat([full_I, best_I.tail(-1)], ignore_index=True,axis=0)
	r0_list.append(best_r0)

	return full_D, full_I, r0_list



@app.callback(
	Output('sir-t-graph', 'children'),
	[Input('location-selection-sir', 'value'),
	Input('timeline-selection-sir', 'value'),
	Input('mortality-rate-selection-sir', 'value'),
	Input('count-selection-sir', 'value'),
	Input('smoothing-range-selection-sir', 'value'),
	Input('prediction-range-selection-sir', 'value'),
	Input('infectious-days-selection-sir', 'value'),
	Input('show-infections-selection-sir', 'value')])
def updateTotalDeathsTimeline(location,
							timeline,
							mortality_rate,
							x_num,
							forecast_size,
							x_days,
							disease_duration,
							show_infections):


	smoothing_range = 5
	forecast_size+=1 #FIX THIS THROUGHOUT
	if location:
		df = getTotalDeaths()
		data = []
		count=2

		location_key = location.lower().replace(' ','_')
		population = 1.0

		if not x_num: x_num = 0			

		if timeline == 'Days since X number of deaths/cases':
			df_location = df.fillna(0)
			df_forecast = df_location
			df_forecast[location_key] = df_forecast[location_key].rolling(smoothing_range).mean().dropna()
			df_location = df_location.drop(df_location[(df_location[location_key] < x_num/population)].index)
			
			df_location = df_location[location_key].dropna()
			df_location = df_location.reset_index()
			data.append(go.Scatter( x=df_location.index,
				    y=df_location[location_key],
				    mode='lines',
				    marker=dict(
				        color=colour_palette[count],
				    ),
				    opacity=1.0,
				    text=location,
				    name='Deaths'
				))

			df_forecast = df_forecast.drop(df_forecast[(df_forecast[location_key] < x_num/population)].index)
			df_forecast = df_forecast.dropna()
			df_forecast = df_forecast.reset_index()

			print (x_days, "***********************************************")
			prediction_df, full_I, r0_list = getVariableBetaForecast(df_forecast,
													location,
													x_days,
													forecast_size,
													mortality_rate = mortality_rate,
													disease_duration = disease_duration)
	

			data.append(go.Scatter( x=prediction_df.index,
				    y=prediction_df[0],
				    mode='lines',
				    marker=dict(
				        color=colour_palette[count],
				    ),
				    line = dict(
				    	color=colour_palette[count], 
				    	dash='dot'),
				    opacity=1.0,
				    text=location,
				    name='Deaths (SIR Model)',
				    showlegend=True
				))
			prediction_size = prediction_df.shape[0]
			num_bars = int(prediction_size/(forecast_size-1))
			bar_position = [(forecast_size-1)*(0.5+x) for x in range(num_bars)]
			diff_len = len(bar_position)-len(r0_list)
			for x in range(diff_len):
				r0_list.append(r0_list[-1])
			r0_list = [round(num, 2) for num in r0_list]
			
			data.append(go.Bar( x=bar_position ,
				    y=r0_list ,
				    marker=dict(
				        color=colour_palette[count],
				    ),
				    opacity=0.2,
				    width=forecast_size,
				    text=r0_list,
            		textposition='outside',
				    yaxis='y2',
				    showlegend=False
				))
			if show_infections:
				data.append(go.Scatter( x=full_I.index,
					    y=full_I[0]/1,
					    mode='lines',
					    marker=dict(
					        color=colour_palette[count-1],
					    ),
					    line = dict(
					    	color=colour_palette[count-1], 
					    	dash='dot'),
					    opacity=1.0,
					    text=location,
					    name='Infections (SIR Model)',
					    showlegend=True
					))
		else:	
			return None

		title_sub = ''
		figure = {
				'data': data,
				'layout': go.Layout(
								#title='Cumulative '+data_type+title_sub,
				                legend=dict(orientation="h",
			                                x=0,
			                                y=1.1),
				                 font=dict(family='Arial', size=15, color='#000000'),
				                hovermode='closest',
				                margin=dict(t=50),
				                xaxis=dict(
				                		title='Days after reaching '+str(x_num)+' dead',
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                ),
				                yaxis=dict(
				                        rangemode = 'tozero',
				                        tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000'
				                            ),
				                        showgrid=False
				                ),
				               	yaxis2=dict(
				                			rangemode = 'tozero',
				               				tickfont=dict(
				                                family='Arial',
				                                size=14,
				                                color='#000000',
				                            ),
                                   				side='right',
				                        	title = 'Estimated R0',
				                        showgrid=False),
				                height=500,
				                autosize=True,
				                paper_bgcolor='rgba(0,0,0,0)',
	            				plot_bgcolor='rgba(0,0,0,0)'
				          )
				}


		return  dcc.Graph(figure=figure,
			             config={'displayModeBar': False},
			             id='total-deaths-t-graph')




if __name__ == '__main__':
	import sys
	main(*sys.argv)
