# sidebar.py
from dash import html, dcc

sidebar_layout = html.Div([
    # Projects Section
    html.H4("Projects", style={"margin": "10px 0"}),

    dcc.RadioItems(
        id="projects-radioitems",
        options=[],
        value="",
        style={"height": "100px", "overflowY": "auto"}
    ),


    # Databases Section
    html.H4("Databases", style={"margin": "10px 0"}),
    dcc.Checklist(
        id="databases-checklist",
        inline=False,
        style={"overflowY": "auto", "height": "100px", "padding": "5px"}
    ),

    # Sectors selection
    html.H4("Sectors", style={"margin": "10px 0"}),
    dcc.Checklist(
        id="sectors-checklist",
        inline=False,
        style={"overflowY": "auto", "height": "150px", "padding": "5px"}
    ),

    # Impact Assessment Section
    html.H4("Impact Assessment", style={"margin": "10px 0"}),
    dcc.Input(id="impact-search", type="text", placeholder="Search impact assessments...", debounce=True),
    dcc.Checklist(
        id="impact-assessment-checklist",
        inline=False,
        style={"overflowY": "auto", "height": "150px", "padding": "5px"}
    ),

    # Bottom Section with Calculation Button
    html.Div([
        html.Button("Run Calculation", id="calc-button", n_clicks=0),
    ], style={"padding": "10px", "border": "1px solid #0099CC", "textAlign": "center"})

], style={"width": "20%", "height": "100vh", "display": "inline-block", "verticalAlign": "top", "padding": "10px"})
