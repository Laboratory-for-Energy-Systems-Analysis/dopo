"""dopo."""

__all__ = (
    "__version__",
    # Add functions and variables you want exposed in `dopo.` namespace here
)

__version__ = "0.0.1"

from dopo.activity_filter import generate_sets_from_filters
from dopo.methods import MethodFinder, find_and_create_method, get_all_methods
from dopo.sector_score_dict import compare_activities_multiple_methods
from dopo.plots import (
    lvl1_plot, 
    lvl21_plot_stacked_absolute, 
    lvl22_plot_input_comparison_with_method, 
    lvl23_plot_input_comparison_plot_no_method, 
    lvl3_plot_relative_changes 
)
