# sidebar.py
from dash import html, dcc
import dash_bootstrap_components as dbc

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
        style={"overflowY": "auto", "height": "80px", "padding": "5px"}
    ),

    # Dataset Selection
    html.H4("Datasets", style={"margin": "10px 0"}),
    html.Div([
        # Dataset type radio-style checkboxes
        dcc.Checklist(
            id="dataset-type-checklist",
            options=[
                {"label": "Sectors", "value": "sectors"},
                {"label": "CPC", "value": "cpc"},
                {"label": "ISIC", "value": "isic"},
                {"label": "Dataset", "value": "dataset"},
            ],
            value=["sectors"],
            inline=True,
            labelStyle={"marginRight": "10px"},
            style={"paddingBottom": "0px", "marginBottom": "0px"}
        ),

        # Exclude markets checkbox — tightly below
        dcc.Checklist(
            id="excl-markets-check",
            options=[{"label": "excl. markets", "value": "exclude"}],
            value=[],
            inline=True,
            style={"marginTop": "4px", "marginLeft": "2px"}
        )
    ]),
    dcc.Input(
        id="dataset-search",
        type="text",
        placeholder="Search",
        debounce=True,
        style={"marginBottom": "10px", "width": "100%"}
    ),

    # Checklist containers
    html.Div(dcc.Checklist(id="sectors-checklist", style={"overflowY": "auto", "height": "100px", "padding": "15px"}),
             id="sectors-container"),
    html.Div(dcc.Checklist(id="cpc-checklist", style={"overflowY": "auto", "height": "100px", "padding": "15px"}),
             id="cpc-container"),
    html.Div(dcc.Checklist(id="isic-checklist", style={"overflowY": "auto", "height": "100px", "padding": "15px"}),
             id="isic-container"),
    html.Div(dcc.Checklist(id="dataset-checklist", style={"overflowY": "auto", "height": "100px", "padding": "15px"}),
             id="dataset-container"),

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
        dcc.Loading(
            id="loading-calc",
            type="circle",
            children=html.Div(id="loading-placeholder", children=[
                dbc.Button("Run Calculation", id="calc-button", n_clicks=0)
            ])
        )
    ], style={"padding": "10px", "border": "1px solid #0099CC", "textAlign": "center"})

], style={"width": "20%", "height": "100vh", "display": "inline-block", "verticalAlign": "top", "padding": "10px"})
