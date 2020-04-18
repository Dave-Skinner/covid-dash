# -*- coding: utf-8 -*-
import dash_html_components as html
import dash_core_components as dcc

def getHeader(active):
	header_logo = html.Div([html.A(className="header__logo",
										   href='/')])
	header_items = [
		html.Li(
			dcc.Link("Worldwide", href="/worldwide", className="header__link"),
			className="header__item {0}".format("is-active" if active == "worldwide" else "")
		),
		html.Li(
			dcc.Link("Players", href="/players", className="header__link"),
			className="header__item {0}".format("is-active" if active == "players" else "")
		),
	]
	header_list = html.Ul(header_items, className="header__list")


	return html.Div([
		header_logo,
		header_list,
	], className="header t-sans")
