# main_content.py
from dash import html, dcc

main_content_layout = html.Div([
    # Row of Dropdowns
    html.Div([
        dcc.Dropdown(id="dropdown-1", placeholder="Sector", style={"width": "80%"}),
        dcc.Dropdown(id="dropdown-2", placeholder="Method", style={"width": "80%"}),
        dcc.Dropdown(id="dropdown-3", placeholder="Plot", style={"width": "80%"}),
    ], style={"display": "flex", "gap": "10px", "marginBottom": "20px"}),

    # Main Plot Area
    dcc.Graph(id="main-plot", style={"height": "500px"}),

], style={"width": "80%", "padding": "10px", "display": "inline-block", "verticalAlign": "top"})
