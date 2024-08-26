def sector_lca_scores(main_dict, method_dict):
    '''
    Generates the LCA score tables for activity list of each sector.
    The tables contain total scores and cpc input contributions.
    This is done by each method defined in the method dictionary.

    :param main_dict: dictionary which is returned by process_yaml_files function
    :param method_dict: dictionary which is created with MethodFinder class

    It returns the main dictionary updated as scores dictionary which also holds the former information for each sector.
    The LCA scores are stored by method name in the respective sector dictionary within the main dictionary.
    '''

    # Initialize scores_dict as a copy of main_dict
    scores_dict = main_dict.copy()

    # Loop through each sector in main_dict
    for sector in scores_dict.keys():
        # Extract activities for the current sector
        sector_activities = scores_dict[sector]['activities']
        
        # Calculate LCA scores using the specified method
        lca_scores = compare_activities_multiple_methods(
            activities_list=sector_activities,
            methods=method_dict,
            identifier=sector,
            mode='absolute'
        )
        
        # Apply the small_inputs_to_other_column function with the cutoff value
        lca_scores = small_inputs_to_other_column(lca_scores, cutoff=0.02)
        
        # Save the LCA scores to the scores_dict
        scores_dict[sector]['lca_scores'] = lca_scores

    return scores_dict

# -----------------------------------------
# CREATING EXCEL SHEETS WITH LCA TABLES
# -----------------------------------------

def sector_lca_scores_to_excel_and_column_positions(scores_dict, excel_file_name):
    """ 
    What it does:
        - Creates a dataframe for each method and sector from the lca scores dictionary
        - Before storing each df in a worksheet in an excel file it:
                - shortens the column labels of the input (removing cpc code)
                - adds a sector name marker for keeping track in excel (when plotting can use it for labeling)
                - adds statistics for plotting
                - creates a dictionary which holds the indexes to the columns we need to call for plotting, this makes it dynamic. Otherwise need to hardcode index column number for openpxyl.
    What it returns:
        - Returns the index positions dictionary where the key is "sector_method"
        - Creates excel file as defined by user
    """

    # Prepare to save each LCA score table to a different worksheet in the same Excel file
    excel_file = excel_file_name
    column_positions = {} #stores the indexes of columns for plotting
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for sector in scores_dict.keys():
            lca_scores = scores_dict[sector]['lca_scores']
            for method, table in lca_scores.items():
                # Create a DataFrame for the current LCA score table
                df = pd.DataFrame(table)

                # Add sector marker
                df = add_sector_marker(df, sector) #!! ADJUST POSITION

                # Add statistics to the DataFrame
                df = add_statistics(df)

                # Get the index values of columns
                columns_of_interest = ["total", "rank", "mean", "2std_abv", "2std_blw", "q1", "q3", "method", "method unit"]
                positions = {col: df.columns.get_loc(col) for col in columns_of_interest if col in df.columns}
                column_positions[method] = positions

                # Find the first input column and add it to the positions dictionary
                first_input_col_index = find_first_input_column(df)
                if first_input_col_index is not None:
                    positions["first_input"] = first_input_col_index
                
                # Store the positions for this method
                column_positions[method] = positions

                # remove cpc from input labels
                df = clean_column_labels(df)

                # Generate a worksheet name
                worksheet_name = f"{method}" #f"{sector}_{method}"
                if len(worksheet_name) > 31:
                    worksheet_name = worksheet_name[:31]
                    
                # Save the DataFrame to the Excel file in a new worksheet
                df.to_excel(writer, sheet_name=worksheet_name, index=False)
        return column_positions
    

def add_statistics(df, column_name='total'):

    '''
    It is called in the function sector_lca_scores_to_excel_and_column_positions

    It adds statistical indicators to a dataframe based on total column which are used for plotting.

    returns updated dataframe
    '''

    #Need a rank row to plot the total LCA scores in descending order (satter opepyxl function takes in non categorial values)
    df['rank'] = df[column_name].rank(method="first", ascending="False")

    # Calculate mean, standard deviation, and IQR
    df['mean'] = df[column_name].mean()
    df['2std_abv'] = df['mean'] + df[column_name].std() * 2
    df['2std_blw'] = df['mean'] - df[column_name].std() * 2
    df['q1'] = df[column_name].quantile(0.25)
    df['q3'] = df[column_name].quantile(0.75)
    
    # Reorder the columns to place the new columns after 'total'
    cols = df.columns.tolist()
    total_index = cols.index(column_name) + 1
    new_cols = ['rank', 'mean', '2std_abv', '2std_blw', 'q1', 'q3']
    cols = cols[:total_index] + new_cols + cols[total_index:-len(new_cols)]
    
    return df[cols]


def find_first_input_column(df):
    '''
    It is called in the function sector_lca_scores_to_excel_and_column_positions. Needs to be called before clean_column_labels function.
    Detects the first column in the dataframe which contains input contribution data and saves its index. 
    This is relevant for calling the right column for defining the to be plotted data dynamically as not all dataframes have the same column order (some contain "direct emissions" for instance).
    '''
    
    def clean_label(label):
        return label if label is not None else 'Unnamed'
    
    # Apply the cleaning function to all column names
    df.columns = [clean_label(col) for col in df.columns]
    
    # Regular expression pattern to match "Number: Name"
    pattern = r'^\d+:\s*'
    
    for idx, column in enumerate(df.columns):
        if (column is not None and re.match(pattern, column)) or column == 'Unnamed' or column == 'direct emissions':
            return idx

    return None

def clean_column_labels(df):

    '''
    It is called in the function sector_lca_scores_to_excel_and_column_positions. Needs to be run after find_first_input_column.

    It removes unnecessary numbers in the column header.

    Returns df with formated column labels.
    '''
    # Function to remove numbers and colon from column names
    def clean_label(label):
        if label is None:
            return 'Unnamed'  # or return 'Unnamed' if you prefer a placeholder
        return re.sub(r'^\d+:\s*', '', str(label))

    # Apply the cleaning function to all column names
    df.columns = [clean_label(col) for col in df.columns]

    return df

def add_sector_marker(df, sector):
    '''
    It is called in the function sector_lca_scores_to_excel_and_column_positions.

    It adds information about the sector for titel and labeling in plotting.

    Returns df with added column.
    '''
    
    # Add sector marker column
    df['sector']=str(sector) # potentially remove!
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
