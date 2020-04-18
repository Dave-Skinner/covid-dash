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

import functools32
import collections

from app import app, getBattingDataframe, getBowlingDataframe, getMatchesDataframe
from header import getHeader





seasons = ['2018','2019','All']
match_types = ['Full Length', '20 Overs','All']
disciplines = ['Batting', 'Bowling']
inter_tav_types = ["Railway Taverners CC","Inter Tavs","All"]
inter_tav_teams = ["President's XI", "Andy James Invitational XI", "Railway Taverners XI"]



def getTeamMasthead():

	return html.Div([
				html.Div(
					dcc.Dropdown(id='discipline-selection-team', 
								options=[{'label': i, 'value': i} for i in disciplines],
								placeholder='Choose Discipline...',
								disabled=True),
					className='masthead__column_1',
					id='discipline-selection-div-team'
				),
				html.Div(
					dcc.Dropdown(
						id='season-selection-team',
						options=[{'label': i, 'value': i} for i in seasons],
						value='2019',
						placeholder='Choose Season...'
					),
					className='masthead__column_2',
					id='season-selection-div-team'
				),
				html.Div(
					dcc.Dropdown(
						id='match-type-selection-team',
						options=[{'label': i, 'value': i} for i in match_types],
						value='All',
						clearable=False
					),
					className='masthead__column_3',
					id='match-type-selection-div-team'
				),
				html.Div(
					dcc.Dropdown(
						id='inter-tav-selection-team',
						options=[{'label': i, 'value': i} for i in inter_tav_types],
						clearable=False,
						placeholder='Choose Match Type...',
						disabled=True
					),
					className='masthead__column_4',
					id='inter-tav-selection-div-team'
				),
				html.Div([
					dt.DataTable(
						id='team-table',
						columns=[
					        {"name": "Date", "id": "date"},
					        {"name": "Opposition", "id": "opposition"},
					        {"name": "Match Type", "id": "match_type"},
					        {"name": "Bat First", "id": "bat_first"},
					        {"name": "Result", "id": "result"},
					        {"name": "Runs For", "id": "runs_for"},
					        {"name": "Wickets Against", "id": "wickets_against"},
					        {"name": "Runs Against", "id": "runs_against"},
					        {"name": "Wickets For", "id": "wickets_for"},			        
					    ],
					    style_cell_conditional=[
							{'if': {'column_id': 'date'},
							 'width': '10%'},
							{'if': {'column_id': 'opposition'},
							 'width': '10%'},
							{'if': {'column_id': 'match_type'},
							 'width': '10%'},
							{'if': {'column_id': 'bat_first'},
							 'width': '10%'},
							{'if': {'column_id': 'result'},
							 'width': '10%'},
							{'if': {'column_id': 'runs_for'},
							 'width': '10%'},
							{'if': {'column_id': 'wickets_against'},
							 'width': '10%'},
							{'if': {'column_id': 'runs_against'},
							 'width': '10%'},
							{'if': {'column_id': 'wickets_for'},
							 'width': '10%'},
						],
						style_header={
					        'fontWeight': 'bold',
						    'font-family':'sans-serif',
						    'fontSize':15,
						    'background': 'rgb(242, 242, 242)'
					    },
					    style_table={
						    'maxHeight': 345,
						    'overflowY': 'auto',
						},
						style_cell={
						    'textAlign': 'center',
						    'font-family':'sans-serif',
						    'fontSize':20
						},
						editable=False,
						n_fixed_rows=1,
						sorting=True,
						sorting_type="single",
						row_selectable="single",
						selected_rows=[0],
						style_as_list_view=True				
					)
				],id='team-table-div',
					className='tavs__player-table')
			], id='team-masthead-div',
			   className='masthead l-grid')

def getLayout():
	return 	html.Div([
				html.Div([
						getHeader("team"),
						getTeamMasthead(),
						html.Div(id='team-stats-div',className='tavs__batting-stats'),
						html.Div(id='team-t-graph',className='tavs__batting-graph'),
						html.Div(id='team-match-report',className='tavs__batting-mod-graph'),
						#html.Div(id='batting-pos-graph',className='tavs__batting-pos-graph')

			], className='l-subgrid'),

		], id='team-stats-page', className='shown-grid l-grid')




'''*********************************************************************************************************8
	GET DATA
*****************************************************************************************************************'''

def getTeamDataTable(season,
						match_type,
						inter_tav_type):

	df_team = getMatchesDataframe()

	if season:
		if season != "All":
			df_team = df_team[df_team['season'] == season]
	if df_team.empty: return []

	if match_type:
		if match_type != "All":
			if match_type == "20 Overs":
				df_team = df_team[df_team['match_type'] == match_type]
			else:
				df_team = df_team[df_team['match_type'] != "20 Overs"]

	data = []
	for match in df_team['date'].unique():
		df_match = df_team[df_team['date'] == match]
		date = df_match['date']
		ground = df_match['ground']
		opposition = df_match['opposition']
		result = df_match['result']
		overs_batted = None
		runs_for = df_match['tav_runs']
		wickets_against = df_match['tav_wickets_down']
		overs_bowled = None
		runs_against = df_match['oppo_runs']
		wickets_for = df_match['oppo_wickets_down']
		bat_first = df_match['bat_first']
		match_type = df_match['match_type']

		data.append([date,
					 opposition,
					 match_type,
					 bat_first,
					 result,
					 runs_for,
					 wickets_against,
					 runs_against,
					 wickets_for])

	data.reverse()

	df_data = pd.DataFrame(data,columns=["date",
										"opposition",
										"match_type",
										"bat_first",
										"result",
										"runs_for",
										"wickets_against",
										"runs_against",
										"wickets_for"])
	#df_data = df_data.sort_values('date',ascending=0)

	data_dict = df_data.to_dict('records')

	return data_dict

@app.callback(
	Output('team-table', 'data'),
	[Input('season-selection-team', 'value'),
	Input('match-type-selection-team', 'value'),
	Input('inter-tav-selection-team', 'value')
])
def teamTableRender(season,
					 match_type,
					 inter_tav_type):
	print match_type
	return getTeamDataTable(season, match_type,inter_tav_type)




def getTopScoreMD(df_top_score):
	top_score_str = ""+df_top_score['name']+"  "+"{:,}".format(int(df_top_score['runs']))+""
	if df_top_score["dismissal"] == "NOT OUT":
		top_score_str = top_score_str + "*"

	return top_score_str

def getMaxWicketsMD(df_max_wickets):
	return "" + df_max_wickets['name'] + "  " + "{:,}".format(int(df_max_wickets['wickets'])) + " for " + "{:,}".format(int(df_max_wickets['runs']))+""


@app.callback(
	Output('team-stats-div', 'children'),
	[Input('team-table', "derived_virtual_data"),
     Input('team-table', "derived_virtual_selected_rows")])
def populateMatchStats(table_data,
						 match_row):
	df_team = getMatchesDataframe()
	df_batting = getBattingDataframe()
	df_bowling = getBowlingDataframe()
	
	try:
		match_date = table_data[match_row[0]]['date']
		#print match_date
		df_batting = df_batting[df_batting['date'] == match_date[0]]#df_batting.iloc[match_date[0]]["date"]
		df_tavs = df_batting[df_batting['team'] == "Railway Taverners CC"]
		df_inter = df_batting[df_batting['team'].isin(inter_tav_teams)]
		df_batting = pd.concat([df_tavs, df_inter]) 

		df_bowling = df_bowling[df_bowling['date'] == match_date[0]]
		df_tavs = df_bowling[df_bowling['team'] == "Railway Taverners CC"]
		df_inter = df_bowling[df_bowling['team'].isin(inter_tav_teams)]
		df_bowling = pd.concat([df_tavs, df_inter]) 

		df_team = df_team[df_team['date'] == match_date[0]]
		#print "Innings",innings
	except (IndexError, TypeError):
		return None

	oppo = df_team['opposition']#table_data[match_row[0]]['opposition'][0]

	df_top_scores = df_batting.nlargest(2, ['runs']) 
	try:
		df_top_score_1 = df_top_scores.iloc[0]
		top_score_str_1 = getTopScoreMD(df_top_score_1)
	except IndexError:
		top_score_str_1 = None

	try:
		df_top_score_2 = df_top_scores.iloc[1]
		top_score_str_2 = getTopScoreMD(df_top_score_2)
	except IndexError:
		top_score_str_2 = None

	#df_max_wickets = df_bowling.ix[df_bowling['wickets'].idxmax()]
	#top_bowling_str = "**" + df_max_wickets['name'] + "**  " + "{:,}".format(int(df_max_wickets['wickets'])) + " for " + "{:,}".format(int(df_max_wickets['runs']))

	df_max_wickets = df_bowling.nlargest(2, ['wickets']) 
	try:
		df_max_wicket_1 = df_max_wickets.iloc[0]
		top_bowling_str_1 = getMaxWicketsMD(df_max_wicket_1)
	except IndexError:
		top_bowling_str_1 = None
	try:
		df_max_wicket_2 = df_max_wickets.iloc[1]	
		top_bowling_str_2 = getMaxWicketsMD(df_max_wicket_2)
	except IndexError:
		top_bowling_str_2 = None

	caps_tank =  df_team['captains_tankard']


	return html.Div([
					html.Div(
						[	html.Div([
								html.H2('Tavs vs ' + oppo, className='tavs-stat-title'),
								dcc.Markdown("**Top Batting**"),
								dcc.Markdown(top_score_str_1),
								dcc.Markdown(top_score_str_2),
								dcc.Markdown("**Top Bowling**"),
								dcc.Markdown(top_bowling_str_1),
								dcc.Markdown(top_bowling_str_2),
								dcc.Markdown("**Captain's Tankard**"),
								dcc.Markdown(caps_tank),
							], className='tavs-unit__extra-content'),
						],
						className='tavs-unit',
					),
				], className='tavs-grid__unit tavs-grid__unit--half')


@app.callback(
	Output('team-match-report', 'children'),
	[Input('team-table', "derived_virtual_data"),
     Input('team-table', "derived_virtual_selected_rows")])
def populateMatchReport(table_data,
						 match_row):
	df_team = getMatchesDataframe()
	
	try:
		match_date = table_data[match_row[0]]['date']
		#print match_date
		df_team = df_team[df_team['date'] == match_date[0]]
		#print "Innings",innings
	except (IndexError, TypeError):
		return None

	oppo = df_team['opposition']#table_data[match_row[0]]['opposition'][0]
	#print oppo

	match_report = df_team['match_report']
	#print match_report

	return html.Div([
					html.Div(
						[	html.H2('Match Report', className='tavs-stat-title'),
							html.Div([
								dcc.Markdown(match_report)
							], className='tavs-match_report'),
						],
						className='tavs-unit',
					),
				], className='tavs-grid__unit tavs-grid__unit--half')

@app.callback(
	Output('team-t-graph', 'children'),
	[Input('team-table', "derived_virtual_data"),
     Input('team-table', "derived_virtual_selected_rows"),
	Input('season-selection-team', 'value'),
	Input('match-type-selection-team', 'value'),
	Input('discipline-selection-team', 'value'),
	Input('inter-tav-selection-team', 'value')])
def updateMatchInningsTimeline(table_data,
								match_row,
								 season,
								 match_type,
								 discipline,
								 inter_tav_type):
	df_batting = getBattingDataframe()
	
	try:
		match_date = table_data[match_row[0]]['date']
		print match_date
		df_innings = df_batting[df_batting['date'] == match_date[0]]#df_batting.iloc[match_date[0]]["date"]
		#print "Innings",innings
	except (IndexError, TypeError):
		return None

	return  dcc.Graph(figure=updateMatchInningsGraph(df_innings),
		             config={'displayModeBar': False},
		             id='match-t-graph')

	


def updateMatchInningsGraph(df_match):
	df_tavs = df_match[df_match['team'] == "Railway Taverners CC"]
	df_oppo = df_match[df_match['team'] != "Railway Taverners CC"]

	data = []

	if not df_tavs.empty:
		tav_runs = [0] + df_tavs["fow_runs"].values.tolist()
		tav_runs = [x for x in tav_runs if str(x) != 'nan']
		tav_runs.sort()
		tav_overs = [0.0] + df_tavs["fow_overs"].values.tolist()
		tav_overs = [x for x in tav_overs if str(x) != 'nan']
		tav_overs.sort()
		print tav_runs
		print tav_overs
		data.append(go.Scatter( x=tav_overs,
					    y=tav_runs,
					    mode='lines+markers',
					    marker=dict(
					        color='rgb(240,21,22)',
					    ),
					    opacity=1.0,
					    text=df_tavs['team'].values.tolist()[0],
					    #width=50000000,
					    name=df_tavs['team'].values.tolist()[0]
					))

	if not df_oppo.empty:
		oppo_runs = [0] + df_oppo["fow_runs"].values.tolist()
		oppo_runs = [x for x in oppo_runs if str(x) != 'nan']
		oppo_runs.sort()
		oppo_overs = [0.0] + df_oppo["fow_overs"].values.tolist()
		oppo_overs = [x for x in oppo_overs if str(x) != 'nan']
		oppo_overs.sort()
		data.append(go.Scatter( x=oppo_overs,
					    y=oppo_runs,
					    mode='lines+markers',
					    marker=dict(
					        color='rgb(22,96,185)',
					    ),
					    opacity=1.0,
					    text=df_oppo['team'].values.tolist()[0],
					    #width=50000000,
					    name=df_oppo['team'].values.tolist()[0]
					))

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
	return figure



