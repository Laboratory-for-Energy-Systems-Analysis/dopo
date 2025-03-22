# top_bar.py
from dash import html
import dash_daq as daq

top_bar_layout = html.Div([
    html.Label("Progress", style={"marginRight": "10px"}),

    # Progress indicator (could be adjusted based on actual progress logic)
    daq.Indicator(
        label="55%", value=True, color="#0099CC"
    ),

    # Custom Progress Bar
    html.Div([
        html.Div(style={
            "width": "55%",  # Set this width dynamically if progress is variable
            "height": "100%",
            "backgroundColor": "#0099CC",
            "textAlign": "center",
            "lineHeight": "30px",
            "color": "white"
        }, children="55%")  # Display percentage inside the bar
    ], style={
        "width": "50%",  # Outer container width
        "backgroundColor": "#e0e0e0",
        "height": "30px",
        "borderRadius": "5px",
        "overflow": "hidden",
        "display": "inline-block"
    })
], style={"padding": "10px", "border": "1px solid #0099CC", "marginBottom": "10px", "width": "100%",
          "display": "inline-block"})
