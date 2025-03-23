from typing import List, Tuple, Union
from dash import Dash, html, dcc, callback_context, no_update, ctx
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from .components.sidebar import sidebar_layout
from .components.main_content import main_content_layout
from .calculations.calculation import (
    get_projects, get_methods, get_databases,
    activate_project, analyze, get_classifications_from_database, get_datasets
)
from dopo.dopo import SECTORS
from .utils.conversion import convert_dataframe_to_dict
from .plot.plot import contribution_plot, prepare_dataframe, scores_plot

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.YETI, dbc.icons.FONT_AWESOME])

# App layout: sidebar + main content
app.layout = html.Div([
    dcc.Interval(id="initial-load", interval=1, n_intervals=0, max_intervals=1),
    dcc.Store(id="analyze-data-store"),
    html.Div([
        sidebar_layout,
        main_content_layout
    ], style={"display": "flex", "width": "100%"}),
])


@app.callback(
    [Output("projects-radioitems", "options"),
     Output("projects-radioitems", "value")],
    Input("initial-load", "n_intervals")
)
def populate_projects_on_load(n_intervals: int) -> Tuple[List[dict], str]:
    """Populate the project list on initial load."""
    if n_intervals == 0:
        return [], ""
    options = [{"label": p.name[:30], "value": p.name} for p in get_projects()]
    return options, options[0]["label"]


@app.callback(
    Output("databases-checklist", "options"),
    Input("projects-radioitems", "value")
)
def update_databases(selected_project: str) -> List[dict]:
    """Update the database list based on selected project."""
    activate_project(selected_project)
    databases = get_databases()
    return [{"label": db[:30], "value": db} for db in databases]


@app.callback(
    [Output("sectors-container", "style"),
     Output("cpc-container", "style"),
     Output("isic-container", "style"),
     Output("dataset-container", "style"),],
    Input("dataset-type-checklist", "value")
)
def toggle_dataset_checklists(selected_types: List[str]) -> Tuple[dict, dict, dict, dict]:
    """Show/hide dataset checklist containers based on selected type."""
    def show_if_selected(name: str) -> dict:
        return {"display": "block"} if name in selected_types else {"display": "none"}

    return (
        show_if_selected("sectors"),
        show_if_selected("cpc"),
        show_if_selected("isic"),
        show_if_selected("dataset"),
    )


@app.callback(
    [Output("sectors-checklist", "options"),
     Output("cpc-checklist", "options"),
     Output("isic-checklist", "options"),
     Output("dataset-checklist", "options"),
     ],
    [Input("dataset-type-checklist", "value"),
     Input("databases-checklist", "value"),
     Input("dataset-search", "value")],
    prevent_initial_call=True
)
def update_filtered_dataset_options(
    selected_types: List[str],
    selected_databases: List[str],
    search_term: Union[str, None]
) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    """Update checklist options for sectors, CPC, and ISIC based on selection and search."""
    if not selected_databases:
        return [], [], [], []

    selected_db = selected_databases[0]
    search_term = (search_term or "").lower()

    def filter_items(items: List[str]) -> List[str]:
        return [item for item in items if search_term in item.lower()]

    sectors_options, cpc_options, isic_options, dataset_options = [], [], [], []

    if "sectors" in selected_types:
        sectors_options = [{"label": s, "value": s} for s in filter_items(sorted(SECTORS))]
    if "cpc" in selected_types:
        cpc_data = get_classifications_from_database(selected_db, "cpc")
        cpc_options = [{"label": item, "value": item} for item in filter_items(cpc_data)]
    if "isic" in selected_types:
        isic_data = get_classifications_from_database(selected_db, "isic")
        isic_options = [{"label": item, "value": item} for item in filter_items(isic_data)]
    if "dataset" in selected_types:
        dataset_options = [{"label": item, "value": item} for item in filter_items(list(set([ds["name"] for ds in get_datasets(selected_db)])))]

    return sectors_options, cpc_options, isic_options, dataset_options


@app.callback(
    Output("dataset-type-checklist", "value"),
    Input("dataset-type-checklist", "value"),
    prevent_initial_call=True
)
def enforce_single_dataset_selection(current_selection: List[str]) -> List[str]:
    """Enforce single selection in the dataset type checklist."""
    if not current_selection:
        return []
    return [current_selection[-1]]


@app.callback(
    Output("dataset-search", "value"),
    Input("dataset-type-checklist", "value"),
    prevent_initial_call=True
)
def clear_search_on_dataset_change(_: List[str]) -> str:
    """Clear the dataset search bar when switching dataset types."""
    return ""


@app.callback(
    Output("impact-assessment-checklist", "options"),
    [Input("impact-search", "value"),
     Input("projects-radioitems", "value")]
)
def update_impact_assessment_list(
    search_term: str,
    selected_project: str,
    triggered_id: str = None
) -> List[dict]:
    """Update the impact assessment list based on search and selected project."""
    trigger = (
        triggered_id or
        callback_context.triggered[0]["prop_id"].split(".")[0]
    )
    if not selected_project:
        return []

    activate_project(selected_project)
    all_methods = get_methods()

    if trigger == "impact-search" and search_term:
        search_term = search_term.lower()
        filtered = [m for m in all_methods if search_term in str(m).lower()]
    else:
        filtered = all_methods

    return [{"label": "-".join(method), "value": str(method)} for method in filtered]

@app.callback(
    [Output("analyze-data-store", "data"),
     Output("main-plot", "figure"),
     Output("dropdown-1", "options"),
     Output("dropdown-1", "value"),
     Output("dropdown-2", "options"),
     Output("dropdown-2", "value"),
     Output("dropdown-3", "options"),
     Output("dropdown-3", "value"),
     Output("loading-placeholder", "children")],
    [Input("calc-button", "n_clicks"),
     Input("dropdown-1", "value"),
     Input("dropdown-2", "value"),
     Input("dropdown-3", "value")],
    [State("projects-radioitems", "value"),
     State("databases-checklist", "value"),
     State("sectors-checklist", "value"),
     State("cpc-checklist", "value"),
     State("isic-checklist", "value"),
     State("dataset-checklist", "value"),
     State("impact-assessment-checklist", "value"),
     State("analyze-data-store", "data"),
     State("dataset-type-checklist", "value"),
     State("excl-markets-check", "value"),
     ]
)
def run_analysis_and_plot(
    n_clicks: int,
    selected_sector: str,
    selected_method: str,
    selected_plot: str,
    project: str,
    databases: List[str],
    sectors: List[str],
    cpc: List[str],
    isic: List[str],
    dataset: List[str],
    methods: List[str],
    stored_data: dict,
    search_type: List[str],
    exclude_markets: List[str]
) -> Tuple:
    """Main analysis and plot callback. Handles running the analysis and updating the UI."""
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    search_type = search_type[0] if isinstance(search_type, list) and search_type else "sectors"
    exclude_flag = bool(exclude_markets and "exclude" in exclude_markets)

    # Choose correct dataset based on search_type
    if search_type == "cpc":
        selected_items = cpc
    elif search_type == "isic":
        selected_items = isic
    elif search_type == "dataset":
        selected_items = dataset
    else:
        selected_items = sectors

    selected_items = [item.strip() for item in selected_items or []]

    if triggered_id == "calc-button" and n_clicks > 0:
        if not databases:
            msg = "Please select at least one database."
        elif not methods:
            msg = "Please select at least one impact assessment method."
        elif not selected_items:
            msg = f"Please select at least one {search_type.upper()} entry."
        else:
            msg = None

        if msg:
            return None, go.Figure(), [], None, [], None, [], None, html.Div(msg, style={"color": "red"})

        result_data = analyze(
            project,
            databases,
            methods,
            selected_items,
            search_type=search_type,
            exclude_markets=exclude_flag,
        )
        for key, val in result_data.items():
            result_data[key] = convert_dataframe_to_dict(val)

        sector_options = [{"label": s, "value": s} for s in selected_items]
        if search_type == "dataset":
            default_sector = "selected datasets"
        else:
            default_sector = sector_options[0]["value"] if sector_options else None

        impact_options = [{"label": m, "value": m} for m in methods]
        default_impact = impact_options[0]["value"] if impact_options else None

        plot_options = [
            {"label": "Total Scores", "value": "total"},
            {"label": "Contribution", "value": "contribution"}
        ]
        default_plot = plot_options[0]["value"]

        filtered_data = prepare_dataframe(df=result_data, sector=default_sector, impact=default_impact)

        fig = scores_plot(df=filtered_data, sector=default_sector, impact_assessment=default_impact) \
            if default_plot == "total" else \
            contribution_plot(df=filtered_data, sector=default_sector, impact_assessment=default_impact)

        return (
            result_data, fig,
            sector_options, default_sector,
            impact_options, default_impact,
            plot_options, default_plot,
            dbc.Button("Run Calculation", id="calc-button", n_clicks=n_clicks)
        )

    elif triggered_id in ["dropdown-1", "dropdown-2", "dropdown-3"] and stored_data:
        if search_type == "dataset":
            selected_sector = "selected datasets"
        filtered_data = prepare_dataframe(df=stored_data, sector=selected_sector, impact=selected_method)
        fig = scores_plot(df=filtered_data, sector=selected_sector, impact_assessment=selected_method) \
            if selected_plot == "total" else \
            contribution_plot(df=filtered_data, sector=selected_sector, impact_assessment=selected_method)

        return stored_data, fig, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    return no_update, go.Figure(), no_update, no_update, no_update, no_update, no_update, no_update, no_update

def main():
    app.run(debug=True)
