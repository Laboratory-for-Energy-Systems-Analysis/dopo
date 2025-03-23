# app.py
from dash import Dash, html, dcc, callback_context, no_update, ctx
from .components.sidebar import sidebar_layout
from .components.main_content import main_content_layout
from dash import Output, Input, State
from .calculations.calculation import get_projects, get_methods, get_databases, activate_project, analyze, get_classifications_from_database
from dopo.dopo import SECTORS
import plotly.graph_objects as go
from .utils.conversion import convert_dataframe_to_dict
from .plot.plot import contribution_plot, prepare_dataframe, scores_plot
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.YETI, dbc.icons.FONT_AWESOME])

app.layout = html.Div([
    # Interval component to trigger callback on page load
    dcc.Interval(id="initial-load", interval=1, n_intervals=0, max_intervals=1),
    dcc.Store(id="analyze-data-store"),

    # Main container for sidebar and main content
    html.Div([
        sidebar_layout,
        main_content_layout
    ], style={"display": "flex", "width": "100%"}),
])

# Callback to populate Projects list on page load
@app.callback(
    [Output("projects-radioitems", "options"),
     Output("projects-radioitems", "value")],
    Input("initial-load", "n_intervals")  # Triggered by interval on page load
)

def populate_projects_on_load(n_intervals):
    if n_intervals == 0:
        return [], ""  # No options until interval triggers
    options = [
        {"label": p.name[:30], "value": p.name} for p in get_projects()
    ]
    return options, options[0]["label"]  # Return options and select first by default

# Callback to update Databases and Impact Assessment lists when a project is selected
@app.callback(
    [Output("databases-checklist", "options"),],
    Input("projects-radioitems", "value")
)

def update_databases(selected_project):

    # Call activate_project with the selected project
    activate_project(selected_project)

    # Get databases and methods based on the selected project
    databases = get_databases()

    # Return the options for both Databases and Impact Assessment
    return (
        [{"label": db[:30], "value": db} for db in databases],
    )


@app.callback(
    [Output("sectors-container", "style"),
     Output("cpc-container", "style"),
     Output("isic-container", "style")],
    Input("dataset-type-checklist", "value")
)
def toggle_dataset_checklists(selected_types):
    def show_if_selected(name):
        return {"display": "block"} if name in selected_types else {"display": "none"}

    return (
        show_if_selected("sectors"),
        show_if_selected("cpc"),
        show_if_selected("isic"),
    )

@app.callback(
    [Output("sectors-checklist", "options"),
     Output("cpc-checklist", "options"),
     Output("isic-checklist", "options")],
    [Input("dataset-type-checklist", "value"),
     Input("databases-checklist", "value"),
     Input("dataset-search", "value")],
    prevent_initial_call=True
)
def update_filtered_dataset_options(selected_types, selected_databases, search_term):
    if not selected_databases or not isinstance(selected_databases, list):
        return [], [], []

    selected_db = selected_databases[0]
    search_term = (search_term or "").lower()

    # Filter helper
    def filter_items(items):
        return [item for item in items if search_term in item.lower()]

    sectors_options, cpc_options, isic_options = [], [], []

    if "sectors" in selected_types:
        all_sectors = sorted(SECTORS)
        filtered = filter_items(all_sectors)
        sectors_options = [{"label": s, "value": s} for s in filtered]

    if "cpc" in selected_types:
        cpc_data = get_classifications_from_database(selected_db, "cpc")
        filtered = filter_items(cpc_data)
        cpc_options = [{"label": item, "value": item} for item in filtered]

    if "isic" in selected_types:
        isic_data = get_classifications_from_database(selected_db, "isic")
        filtered = filter_items(isic_data)
        isic_options = [{"label": item, "value": item} for item in filtered]

    return sectors_options, cpc_options, isic_options

@app.callback(
    Output("dataset-type-checklist", "value"),
    Input("dataset-type-checklist", "value"),
    prevent_initial_call=True
)
def enforce_single_dataset_selection(current_selection):
    # Determine which item was most recently clicked
    triggered = ctx.triggered_id

    if not current_selection:
        return []

    # Enforce single selection: only keep the last clicked value
    last_selected = current_selection[-1]

    return [last_selected]

@app.callback(
    Output("dataset-search", "value"),
    Input("dataset-type-checklist", "value"),
    prevent_initial_call=True
)
def clear_search_on_dataset_change(dataset_type):
    return ""

# Combined callback for updating Impact Assessment list based on project selection and search term
@app.callback(
    Output("impact-assessment-checklist", "options"),
    [Input("impact-search", "value"),
     Input("projects-radioitems", "value")]
)
def update_impact_assessment_list(search_term, selected_project):
    # Determine which input triggered the callback
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

    # If no project is selected, return an empty list
    if not selected_project:
        return []

    activate_project(selected_project)

    # Retrieve all methods for the selected project
    all_methods = get_methods()

    # Apply filtering if the search term was used as the trigger
    if trigger == "impact-search" and search_term:
        search_term = search_term.lower()
        filtered_methods = [method for method in all_methods if search_term in str(method).lower()]
    else:
        # No filtering; return all methods
        filtered_methods = all_methods

    # Return the filtered or full list for the checklist

    return [{"label": "-".join(list(method)), "value": str(method)} for method in filtered_methods]


@app.callback(
    [Output("analyze-data-store", "data"),
     Output("main-plot", "figure"),
     Output("dropdown-1", "options"),
     Output("dropdown-1", "value"),
     Output("dropdown-2", "options"),
     Output("dropdown-2", "value"),
     Output("dropdown-3", "options"),
     Output("dropdown-3", "value"),
     Output("loading-placeholder", "children")],  # ← new dummy output
    [Input("calc-button", "n_clicks"),
     Input("dropdown-1", "value"),      # Sector dropdown as input
     Input("dropdown-2", "value"),
     Input("dropdown-3", "value"),
     ],     # Impact assessment dropdown as input
    [
        State("projects-radioitems", "value"),
        State("databases-checklist", "value"),
        State("sectors-checklist", "value"),  # Still keep this
        State("cpc-checklist", "value"),  # Add this
        State("isic-checklist", "value"),  # And this
        State("impact-assessment-checklist", "value"),
        State("analyze-data-store", "data"),
        State("dataset-type-checklist", "value"),
    ]
)

def run_analysis_and_plot(n_clicks, selected_sector, selected_method, selected_plot,
                          project, databases, sectors, cpc, isic,
                          methods, stored_data, search_type):
    # Determine which input triggered the callback
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # Case 1: Run Calculation button is clicked
    if triggered_id == "calc-button" and n_clicks > 0:

        # extract the selected search_type ("sector", "cpc", or "isic")
        if isinstance(search_type, list) and search_type:
            search_type = search_type[0]
        else:
            search_type = "sectors"

        # Dynamically select dataset values based on search_type
        if search_type == "cpc":
            selected_items = cpc
        elif search_type == "isic":
            selected_items = isic
        else:
            selected_items = sectors

        selected_items = [item.strip() for item in selected_items]

        if not databases:
            message = "Please select at least one database."
        elif not methods:
            message = "Please select at least one impact assessment method."
        elif not selected_items:
            message = f"Please select at least one {search_type.upper()} entry."
        else:
            message = None

        if message:
            return None, go.Figure(), [], None, [], None, [], None, html.Div(message, style={"color": "red"})

        # Ensure there is at least one database, impact assessment, and sector selected
        if not databases or not methods or not selected_items:
            return None, go.Figure(), [], None, [], None, [], None, dbc.Button("Run Calculation", id="calc-button",
                                                                          n_clicks=n_clicks)

        # Call analyze() with the selected values to get data for plotting
        result_data = analyze(project, databases, methods, selected_items, search_type=search_type)

        for key, val in result_data.items():
            result_data[key] = convert_dataframe_to_dict(val)

        # Populate dropdown options for sectors and set the default value
        sector_options = [{"label": s, "value": s} for s in selected_items]
        default_sector = sector_options[0]["value"] if sector_options else None

        # Populate dropdown options for impact assessments and set the default value
        impact_options = [{"label": method, "value": method} for method in methods]
        default_impact = impact_options[0]["value"] if impact_options else None

        # Populate dropdown options for graphic type (total scores or contribution)
        plot_options = [{"label": "Total Scores", "value": "total"},
                             {"label": "Contribution", "value": "contribution"}]
        default_plot = plot_options[0]["value"] if plot_options else None

        filtered_data = prepare_dataframe(
            df=result_data,
            sector=default_sector,
            impact=default_impact
        )


        # check the plot type
        if default_plot == "total":
            fig = scores_plot(
                df=filtered_data,
                sector=default_sector,
                impact_assessment=default_impact
            )
        else:
            fig = contribution_plot(
                df=filtered_data,
                sector=default_sector,
                impact_assessment=default_impact
            )

        # Store result data in `dcc.Store` and return updated plot and dropdowns
        return result_data, fig, sector_options, default_sector, impact_options, default_impact, plot_options, default_plot, dbc.Button("Run Calculation", id="calc-button", n_clicks=n_clicks)

    # Case 2: Update plot based on selected sector or impact assessment without re-running analyze()
    elif triggered_id in ["dropdown-1", "dropdown-2", "dropdown-3"] and stored_data:

        filtered_data = prepare_dataframe(
            df=stored_data,
            sector=selected_sector,
            impact=selected_method
        )

        if selected_plot == "total":
            fig = scores_plot(
                df=filtered_data,
                sector=selected_sector,
                impact_assessment=selected_method
            )
        else:
            fig = contribution_plot(
                df=filtered_data,
                sector=selected_sector,
                impact_assessment=selected_method
            )

        return stored_data, fig, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    # Default return if no specific case is triggered
    return no_update, go.Figure(), no_update, no_update, no_update, no_update, no_update, no_update, no_update

def main():
    app.run(debug=True)
