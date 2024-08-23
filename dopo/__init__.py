"""dopo."""

__all__ = (
    # Add functions and variables you want exposed in `dopo.` namespace here
    "__version__",
    'generate_sets_from_filters',
    'MethodFinder',
    ''
    'compare_activities_multiple_methods',
    'scores_across_activities',
    'inputs_contributions',
    'inputs_contribution',
    'input_contribution_across_activities',
    'activities_across_databases',
    'process_yaml_files',
    'sector_lca_scores',
    'sector_lca_scores_to_excel_and_column_positions',
    'dot_plots_xcl',
    'stacked_bars_xcl',
    'barchart_compare_db_xcl',
    'relative_changes_db'

)

__version__ = "0.0.1"

from dopo.activity_filter import generate_sets_from_filters
from dopo.methods import MethodFinder
from dopo.sector_score_dict import compare_activities_multiple_methods
from dopo.sector_score_dict import small_inputs_to_other_column
from dopo.plots import (
    scores_across_activities,
    inputs_contributions,
    inputs_contribution,
    input_contribution_across_activities,
    activities_across_databases
    )
# from dopo.dopo_excel import (
#     process_yaml_files,
#     sector_lca_scores,
#     sector_lca_scores_to_excel_and_column_positions,
#     dot_plots,
#     stacked_bars
# )

from dopo.filter_sectors import process_yaml_files
from dopo.lca_to_xcl import (
    sector_lca_scores,
    sector_lca_scores_to_excel_and_column_positions
)
from dopo.compare_db_to_xcl import relative_changes_db
from dopo.plots_in_xcl import (
    dot_plots_xcl,
    stacked_bars_xcl,
    barchart_compare_db_xcl
)

