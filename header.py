# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_core_components as dcc

def getHeader(active):
	header_title = html.Div('''This app is built using various Covid-19 related data sources. 
								The Worldwide page tracks cumulative Covid-19 deaths/cases and
								extends predictions using the latest daily rate of change.
								The Excess Deaths page compares excess death data to reported Covid 19 deaths in several countries.
								The Mobility page compares Google Mobility Reports data, alongside the OxCGRT Stringency Index (a measurement of 
								Covid-19 policy responses around the world), to daily Covid-19 deaths/cases in each country. 
								The SIR Model page retrofits a series of SIR models to the latest data and uses this to estimate 
								R0 throughout the epidemic. ''',className='header_title')
	header_items = [
		html.Li(
			dcc.Link("Worldwide", href="/worldwide", className="header__link"),
			className="header__item {0}".format("is-active" if active == "worldwide" else "")
		),
		html.Li(
			dcc.Link("Excess Deaths", href="/excessdeaths", className="header__link"),
			className="header__item {0}".format("is-active" if active == "excessdeaths" else "")
		),
		html.Li(
			dcc.Link("Mobility", href="/mobility", className="header__link"),
			className="header__item {0}".format("is-active" if active == "mobility" else "")
		),
		html.Li(
			dcc.Link("SIR Model", href="/sirmodel", className="header__link"),
			className="header__item {0}".format("is-active" if active == "sirmodel" else "")
		),
	]
	header_list = html.Ul(header_items, className="header__list")


	return html.Div([
		header_title,
		header_list,
	], className="header t-sans")
