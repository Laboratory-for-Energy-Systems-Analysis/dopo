"""
Generates and saves Life Cycle Assessment (LCA) scores plots for various sectors to an Excel file.

The module computes LCA scores for activities and methods, generates plots (dot plots and 
stacked bar charts), and saves them along with LCA scores tables to an Excel file. 
Includes helper functions for processing, plotting, and formatting data.
"""

from os.path import commonprefix
import bw2analyzer as ba
import bw2calc as bc
import bw2data as bd
import operator
import tabulate
import pandas as pd
import re

def sector_lca_scores_plots(activity_dict, method_dict, excel_file_name, cutoff=0.01):
    """
    Generate plots of Life Cycle Assessment (LCA) scores for different sectors and save them to an 
    Excel file.

    This function calculates LCA scores for a set of activities and methods, then generates plots 
    (dot plots and stacked bar charts) based on these scores. The generated plots are saved to an 
    Excel file.

    Args:
        activity_dict (dict): A dictionary where keys are activity names or IDs and values are 
                                corresponding activity data.
        method_dict (dict): A dictionary where keys are method names or IDs and values are 
                                corresponding method data.
        excel_file_name (str): The name of the Excel file where the LCA scores tables and plots will 
                                be saved.
        cutoff (float, optional): A cutoff value for filtering LCA scores. Any scores below this 
                                    value will be excluded. Default is 0.01.

    Returns:
        None

    The function performs the following steps:
    1. Generates LCA scores tables based on the provided activity and method dictionaries and the 
        cutoff value.
    2. Saves the generated LCA scores tables to the specified Excel file.
    3. Creates dot plots of the LCA scores and saves them in the Excel file.
    4. Creates stacked bar charts of the LCA scores and appends them to the Excel file.
    5. Prints the last row occupied in the Excel charts sheet, which indicates where the plots end.

    Note:
        - The `dot_plots_xcl` and `stacked_bars_xcl` functions are imported inside this function to 
            avoid circular imports.
        - The function relies on helper functions such as `sector_lca_scores` and 
            `sector_lca_scores_to_excel` to generate and save LCA scores, and `dot_plots_xcl` and 
            `stacked_bars_xcl` for generating plots.
    """
    from dopo.plots_sector_lca_scores import dot_plots_xcl, stacked_bars_xcl
   
    scores_dict=_sector_lca_scores(activity_dict, method_dict, cutoff)
    column_positions=_sector_lca_scores_to_excel(scores_dict, excel_file_name)
    current_row=dot_plots_xcl(excel_file_name, column_positions)
    current_row=stacked_bars_xcl(excel_file_name, column_positions, current_row)
    
    print(f"last row occupied in excel charts sheet: {current_row} --> use as current_row argument")

def _sector_lca_scores(activity_dict, method_dict, cutoff=0.01):
    """
    Generates LCA score tables for each sector's activity list, including total scores and CPC 
    input contributions.

    This function calculates LCA scores for activities within each sector using methods specified 
    in the `method_dict`. Inputs below or equal to the `cutoff` value are summarized in an "other" 
    column.

    Parameters
    ----------
    activity_dict : dict
        A dictionary returned by the `process_yaml_files` function. It should contain sector names 
        as keys, each with an 'activities' entry holding the list of activities for that sector.
    method_dict : dict
        A dictionary created with the `MethodFinder` class, containing methods for LCA score 
        calculation.
    cutoff : float, optional
        A threshold value for summarizing inputs below or equal to this value in an "other" column. 
        Default is 0.02.

    Returns
    -------
    dict
        The updated dictionary (formerly `activity_dict`) with an additional key 'lca_scores' 
        for each sector. This contains the calculated LCA scores by method.
    """
    
    # Initialize scores_dict as a copy of main_dict
    scores_dict = activity_dict.copy()

    # Loop through each sector in scores_dict
    for sector in scores_dict.keys():
        # Extract activities for the current sector
        sector_activities = scores_dict[sector]['activities']
        
        # Calculate LCA scores using the specified methods
        lca_scores = _compare_activities_multiple_methods(
            activities_list=sector_activities,
            methods=method_dict,
            identifier=sector,
            mode='absolute'
        )
        
        # Apply cutoff to summarize small inputs in an "other" column
        lca_scores_cut = _small_inputs_to_other_column(lca_scores, cutoff)
        
        # Save the LCA scores to the scores_dict
        scores_dict[sector]['lca_scores'] = lca_scores_cut

    return scores_dict

def _sector_lca_scores_to_excel(scores_dict, excel_file_name):
    """
    Writes LCA scores to an Excel file, organizing data by sector and method.

    For each sector in the `scores_dict`, this function performs the following:
    - Creates a DataFrame for each method within that sector.
    - Shortens column labels by removing CPC codes.
    - Adds a sector name marker to facilitate tracking in Excel.
    - Adds statistical columns for plotting purposes.
    - Creates a dictionary of column index positions used for plotting, making it dynamic and 
        avoiding hardcoded column indices.

    Parameters
    ----------
    scores_dict : dict
        A dictionary where each key is a sector name and each value contains LCA scores and other 
        relevant data. The structure should be compatible with the output of the `sector_lca_scores` 
        function.
    excel_file_name : str
        The name of the Excel file to be created, including the file extension 
        (e.g., 'lca_scores.xlsx').

    Returns
    -------
    dict
        A dictionary where each key is a "sector_method" string and each value is another dictionary 
        mapping column names to their index positions. This dictionary aids in dynamic plotting.
    """
    
    # Dictionary to store positions of columns for each method
    column_positions = {}

    # DataFrames to store combined sector data
    combined_sector_dfs = {}
    method_dfs = []

    # Process each sector and its methods
    for sector in scores_dict.keys():
        sector_dfs = []
        lca_scores = scores_dict[sector]['lca_scores']

        # Process each method for the current sector
        for method, table in lca_scores.items():
            df = pd.DataFrame(table)

            # Add sector marker
            df = _add_sector_marker(df, sector)

            # Add statistics to the DataFrame
            df = _add_statistics(df)

            # Get the index values of columns
            columns_of_interest = ["total", "rank", "mean", "2std_abv", "2std_blw", "q1", "q3", 
                                   "method", "method unit"]
            positions = {col: df.columns.get_loc(col) for col in columns_of_interest 
                         if col in df.columns}
            column_positions[f"{sector}_{method}"] = positions

            # Find the first input column and add it to the positions dictionary
            first_input_col_index = _find_first_input_column(df)
            if first_input_col_index is not None:
                positions["first_input"] = first_input_col_index

            # Remove CPC from input labels
            df = _clean_column_labels(df)

            sector_dfs.append(df)

            # Store method-specific DataFrames for later
            #
            # method_dfs.append((f"{sector}_{method}", df))
            method_dfs.append((f"{method}", df))
            # print('key in method_dfs')
            # print(method)

        # Combine all dataframes for this sector
        combined_df = pd.concat(sector_dfs, axis=0, ignore_index=True, sort=False).fillna(0)
        combined_sector_dfs[sector] = combined_df

    # Write to Excel file
    with pd.ExcelWriter(excel_file_name, engine='openpyxl') as writer:
        # Write all combined sector sheets
        for sector, combined_df in combined_sector_dfs.items():
            worksheet_name_big = f"{sector}"
            if len(worksheet_name_big) > 31:
                worksheet_name_big = worksheet_name_big[:31]
            combined_df.to_excel(writer, sheet_name=worksheet_name_big, index=False)

        # Write all method-specific sheets
        for worksheet_name, df in method_dfs:
            if len(worksheet_name) > 31:
                worksheet_name = worksheet_name[:31]
            df.to_excel(writer, sheet_name=worksheet_name, index=False)

    return column_positions

def _compare_activities_multiple_methods(
    activities_list, methods, identifier, output_format="pandas", mode="absolute"
):
    """
    Compares a list of activities using multiple LCA methods and stores the results in a dictionary 
    of DataFrames.

    This function generates comparison results for each method in `methods`, formats them into 
    DataFrames, and organizes them in a dictionary where the keys are method-specific names derived 
    from the `identifier` and method details. Each DataFrame contains total scores and input 
    contributions, with columns ordered and indexed appropriately.

    Parameters
    ----------
    activities_list : list
        A list of activities to be compared.
    methods : dict
        A dictionary where keys are method names and values are dictionaries with the key "object" 
        being a Brightway Method object used for comparisons.
    identifier : str
        A string used to construct unique variable names for the comparison results 
        (e.g., sector name).
    output_format : str, optional
        The format for the output DataFrame. Default is "pandas". Other formats can be specified 
        if supported.
    mode : str, optional
        The mode of comparison. Options are "absolute" (default) and "relative".

    Returns
    -------
    dict
        A dictionary where each key is a unique name derived from the `identifier` and method name,
        and each value is a DataFrame containing the comparison results.
    """
    dataframes_dict = {}

    for method_key, method_details in methods.items(): # method_key is not called, but necessary
        # Perform the comparison using the Brightway2 analyzer
        result = _compare_activities_by_grouped_leaves(
            activities_list,
            method_details["object"].name,
            output_format=output_format,
            mode=mode,
        )

        # Create a variable name using the method name and identifier
        method_name = method_details["object"].name[2].replace(" ", "_").lower()
        var_name = f"{identifier}_{method_name}"

        # Add method and method unit columns to the DataFrame
        result["method"] = str(method_details["object"].name[2])
        result["method unit"] = str(method_details["object"].metadata["unit"])

        # Reorder columns to place 'method' and 'method unit' after 'unit'
        cols = list(result.columns)
        unit_index = cols.index("unit")
        cols.insert(unit_index + 1, cols.pop(cols.index("method")))
        cols.insert(unit_index + 2, cols.pop(cols.index("method unit")))
        result = result[cols]

        # Sort rows by 'total' column and reset index
        result = result.sort_values('total').reset_index(drop=True)

        # Store the result DataFrame in the dictionary
        dataframes_dict[var_name] = result

    return dataframes_dict

def _small_inputs_to_other_column(dataframes_dict, cutoff=0.01):
    """
    Aggregates insignificant input contributions into an 'other' column for each DataFrame in the 
    input dictionary.
    
    Contributions that are less than or equal to the specified cutoff value (relative to the 'total'
    column) are combined into a new 'other' column. The original columns with these contributions 
    are set to zero. Columns that end up containing only zeros are removed, and columns named None 
    or "Unnamed" are also combined into the 'other' column before removal.

    Parameters
    ----------
    dataframes_dict : dict
        A dictionary where each key corresponds to a DataFrame. Each DataFrame should contain a 
        'total' column and may include columns to be aggregated into the 'other' column based on 
        their contributions.
    cutoff : float, optional
        The cutoff value for determining insignificant contributions. Contributions less than or 
        equal to this value (relative to the 'total' column) are aggregated into the 'other' column. 
        Default is 0.01.

    Returns
    -------
    dict
        A dictionary with the same keys as `dataframes_dict`, but with each DataFrame updated to 
        include an 'other' column and without insignificant columns.
    """
    
    processed_dict = {}

    for key, df in dataframes_dict.items():
        # Identify the 'total' column
        total_col_index = df.columns.get_loc('total')
        
        # Separate string and numeric columns
        string_cols = df.iloc[:, :total_col_index]
        numeric_cols = df.iloc[:, total_col_index:]
        numeric_cols = numeric_cols.astype(float)
        
        # Create 'other' column
        numeric_cols['other'] = 0.0
        
        # Identify and handle columns that are None or called "Unnamed"
        columns_to_remove = []
        for col in df.columns:
            if col is None or col == "None" or str(col).startswith("Unnamed"):
                numeric_cols['other'] += df[col].fillna(0) 
                columns_to_remove.append(col)
        
        # Drop the identified columns
        numeric_cols.drop(columns=columns_to_remove, inplace=True)

        for col in numeric_cols.columns[1:-1]:  # Skip 'total' and 'other'
            mask_positive_total = numeric_cols['total'] > 0
            mask_negative_total = ~mask_positive_total
            
            # For rows with positive total values
            mask_pos = mask_positive_total & ((numeric_cols[col] < numeric_cols['total'] * cutoff) & 
                                            (numeric_cols[col] > numeric_cols['total'] * (-cutoff)))
            
            # For rows with negative total values
            mask_neg = mask_negative_total & ((numeric_cols[col] > numeric_cols['total'] * cutoff) & 
                                            (numeric_cols[col] < numeric_cols['total'] * (-cutoff)))
            
            # Apply the logic for both positive and negative totals
            numeric_cols.loc[mask_pos | mask_neg, 'other'] += numeric_cols.loc[mask_pos | 
                                                                               mask_neg, col]
            numeric_cols.loc[mask_pos | mask_neg, col] = 0

            # Add these values to 'other'
            numeric_cols.loc[mask_pos, 'other'] += numeric_cols.loc[mask_pos, col]
            numeric_cols.loc[mask_neg, 'other'] += numeric_cols.loc[mask_neg, col]

            # Set these values to zero in the original column
            numeric_cols.loc[mask_pos, col] = 0
            numeric_cols.loc[mask_neg,col] = 0
        
        # Remove columns with all zeros (except 'total' and 'other')
        cols_to_keep = ['total'] + [col for col in numeric_cols.columns[1:-1] 
                                             if not (numeric_cols[col] == 0).all()]
        cols_to_keep.append('other')
        
        numeric_cols = numeric_cols[cols_to_keep]
        
        # Combine string and processed numeric columns
        processed_df = pd.concat([string_cols, numeric_cols], axis=1)
        
        # Sort DataFrame by total (optional)
        processed_df = processed_df.sort_values('total', ascending=False)
        
        # Store the processed DataFrame in the result dictionary
        processed_dict[key] = processed_df
        
    return processed_dict

def _add_statistics(df, column_name='total'):
    """
    Adds statistical indicators to a DataFrame for plotting purposes.

    This function computes several statistics based on the values in the specified column 
    (`column_name`). It adds columns for ranking, mean, standard deviation bounds, 
    and interquartile range (IQR). The statistics are added to aid in visual analysis and plotting.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to which statistical indicators will be added.
    column_name : str, optional
        The name of the column on which to base the statistics. Default is 'total'.

    Returns
    -------
    pandas.DataFrame
        The updated DataFrame with added columns for ranking, mean, standard deviation bounds, 
        and IQR.
    """
    
    # Add a rank column based on the specified column
    df['rank'] = df[column_name].rank(method="first", ascending=False)

    # Calculate mean, standard deviation bounds, and IQR
    df['mean'] = df[column_name].mean()
    df['2std_abv'] = df['mean'] + df[column_name].std() * 2
    df['2std_blw'] = df['mean'] - df[column_name].std() * 2
    df['q1'] = df[column_name].quantile(0.25)
    df['q3'] = df[column_name].quantile(0.75)
    
    # Reorder the columns to place the new columns after the specified column
    cols = df.columns.tolist()
    total_index = cols.index(column_name) + 1
    new_cols = ['rank', 'mean', '2std_abv', '2std_blw', 'q1', 'q3']
    cols = cols[:total_index] + new_cols + cols[total_index:-len(new_cols)]
    
    return df[cols]

def _find_first_input_column(df):
    """
    Identifies the index of the first column in a DataFrame that contains input contribution data.

    This function is used to locate the column in the DataFrame that holds input contribution data,
    which is essential for dynamically selecting the correct column for plotting. 
    It ensures compatibility with DataFrames that may have different column orders or names, such as
    those including "direct emissions."

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame in which to find the first input contribution column.

    Returns
    -------
    int or None
        The index of the first column containing input data. Returns `None` if no such column 
        is found.
    """
    
    def _clean_label(label):
        return label if label is not None else 'Unnamed'
    
    # Apply the cleaning function to all column names
    df.columns = [_clean_label(col) for col in df.columns]
    
    # Regular expression pattern to match "Number: Name"
    pattern = r'^\d+:\s*'
    
    for idx, column in enumerate(df.columns):
        if (column is not None and re.match(pattern, column)) or column == 'Unnamed' or column == 'direct emissions':
            return idx

    return None

def _clean_column_labels(df):
    """
    Cleans and formats column labels in the DataFrame by removing unnecessary numbers and colons.

    This function is used to standardize column headers by removing leading numbers and colons, 
    which can be present in columns used for input contributions or other data. It should be called 
    after `_find_first_input_column` to ensure column order and identification are correctly handled.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose column labels are to be cleaned.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with formatted column labels, where unnecessary numbers and colons have 
        been removed.
    """
    
    # Function to remove numbers and colon from column names
    def _clean_label(label):
        if label is None:
            return 'Unnamed'  # Placeholder for missing or unnamed columns
        return re.sub(r'^\d+:\s*', '', str(label))

    # Apply the cleaning function to all column names
    df.columns = [_clean_label(col) for col in df.columns]

    return df

def _add_sector_marker(df, sector):
    """
    Adds a sector marker to the DataFrame for labeling and identification purposes.

    This function is used to add a new column to the DataFrame that indicates the sector associated 
    with the data. The sector information is useful for identifying and labeling data in plots and 
    Excel sheets. The column is positioned immediately after the 'product' column if it exists, or 
    appended at the end if 'product' is not present.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to which the sector marker will be added.

    sector : str
        The name of the sector to be added as a marker.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with an added 'sector' column, positioned immediately after the 'product' 
        column if present,
        or at the end otherwise.
    """
    
    # Add sector marker column
    df['sector'] = str(sector)
    
    # Reorder the columns to move 'sector' after 'product'
    columns = list(df.columns)

    if 'product' in df.columns:
        product_index = columns.index('product')
        # Insert 'sector' after 'product'
        columns.insert(product_index + 1, columns.pop(columns.index('sector')))
    else:
        # If 'product' does not exist, 'sector' remains in the last column
        columns.append(columns.pop(columns.index('sector')))
        
    # Reassign the DataFrame with the new column order
    df = df[columns]
    
    return df

def _compare_activities_by_grouped_leaves(
    activities,
    lcia_method,
    mode="relative",
    max_level=4,
    cutoff=7.5e-3,
    output_format="list",
    str_length=50,
):
    """
    Adapted birghtway2 analyzer function. It stores additional labels and data per activity.

    Compare activities by the impact of their different inputs, aggregated by the product classification of those inputs.

    Args:
        activities: list of ``Activity`` instances.
        lcia_method: tuple. LCIA method to use when traversing supply chain graph.
        mode: str. If "relative" (default), results are returned as a fraction of total input. Otherwise, results are absolute impact per input exchange.
        max_level: int. Maximum level in supply chain to examine.
        cutoff: float. Fraction of total impact to cutoff supply chain graph traversal at.
        output_format: str. See below.
        str_length; int. If ``output_format`` is ``html``, this controls how many characters each column label can have.

    Raises:
        ValueError: ``activities`` is malformed.

    Returns:
        Depends on ``output_format``:

        * ``list``: Tuple of ``(column labels, data)``
        * ``html``: HTML string that will print nicely in Jupyter notebooks.
        * ``pandas``: a pandas ``DataFrame``.

    """
    for act in activities:
        if not isinstance(act, bd.backends.peewee.proxies.Activity):
            raise ValueError("`activities` must be an iterable of `Activity` instances")

    objs = [
        ba.comparisons.group_leaves(ba.comparisons.find_leaves(act, lcia_method, max_level=max_level, cutoff=cutoff))
        for act in activities
    ]
    sorted_keys = sorted(
        [
            (max([el[0] for obj in objs for el in obj if el[2] == key]), key)
            for key in {el[2] for obj in objs for el in obj}
        ],
        reverse=True,
    )
    name_common = commonprefix([act["name"] for act in activities])

    if " " not in name_common:
        name_common = ""
    else:
        last_space = len(name_common) - operator.indexOf(reversed(name_common), " ")
        name_common = name_common[:last_space]
        # print("Omitting activity name common prefix: '{}'".format(name_common))

    product_common = commonprefix(
        [act.get("reference product", "") for act in activities]
    )

    lca = bc.LCA({act: 1 for act in activities}, lcia_method)
    lca.lci()
    lca.lcia()

    labels = [
        "activity",
        "activity key",
        "product",
        "location",
        "unit",
        "total",
        "direct emissions",
    ] + [key for _, key in sorted_keys]
    data = []
    for act, lst in zip(activities, objs):
        lca.redo_lcia({act: 1})
        data.append(
            [
                act["name"].replace(name_common, ""),
                act.key,
                act.get("reference product", "").replace(product_common, ""),
                act.get("location", "")[:25],
                act.get("unit", ""),
                lca.score,
            ]
            + [
                (
                    lca.characterization_matrix
                    * lca.biosphere_matrix
                    * lca.demand_array
                ).sum()
            ]
            + [ba.comparisons.get_value_for_cpc(lst, key) for _, key in sorted_keys]
        )

    data.sort(key=lambda x: x[4], reverse=True)

    if mode == "relative":
        for row in data:
            for index, point in enumerate(row[5:]):
                row[index + 5] = point / row[4]

    if output_format == "list":
        return labels, data
    elif output_format == "pandas":
        return pd.DataFrame(data, columns=labels)
    elif output_format == "html":
        return tabulate.tabulate(
            data,
            [x[:str_length] for x in labels],
            tablefmt="html",
            floatfmt=".3f",
        )
