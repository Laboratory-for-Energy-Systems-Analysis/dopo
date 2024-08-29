"""dopo."""

__all__ = (
    # Add functions and variables you want exposed in `dopo.` namespace here
    "__version__",
    'generate_sets_from_filters',
    'MethodFinder',
    'process_yaml_files',
    'sector_lca_scores',
    'sector_lca_scores_to_excel',
    'dot_plots_xcl',
    'stacked_bars_xcl',
    'relative_changes_db',
    'barchart_compare_db_xcl'
)

__version__ = "0.0.1"

from dopo.activity_filter import generate_sets_from_filters
from dopo.sector_filter import process_yaml_files
from dopo.methods import MethodFinder
from dopo.sector_lca_scores import (sector_lca_scores, sector_lca_scores_to_excel)
from dopo.plots_sector_lca_scores import (dot_plots_xcl, stacked_bars_xcl)
from dopo.database_comparison import (relative_changes_db, barchart_compare_db_xcl)


