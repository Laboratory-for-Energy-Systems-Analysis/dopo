"""dopo."""

__all__ = (
    # Add functions and variables you want exposed in `dopo.` namespace here
    "__version__",
    'generate_sets_from_filters',
    'MethodFinder',
    'compare_activities_multiple_methods',
    'scores_across_activities',
    'inputs_contributions',
    'inputs_contribution',
    'input_contribution_across_activities',
    'activities_across_databases'
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
