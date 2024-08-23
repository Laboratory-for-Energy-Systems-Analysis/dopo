import pandas as pd

import re
import pandas as pd
from dopo import generate_sets_from_filters
from dopo import compare_activities_multiple_methods
from dopo import small_inputs_to_other_column
import openpyxl
from openpyxl import load_workbook
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart import BarChart, Reference

def _lca_scores_compare(database_dict, method_dict):
    # Dictionary to store DataFrames for each sector
    sector_dataframes = {}

    # Labels for the DataFrame columns
    labels = [
        "activity",
        "activity key",
        "reference product",
        "location",
        "method name",
        "method unit",
        "total",
    ]

    # Loop through each sector in the database_dict
    for sector, sector_data in database_dict.items():
        # Initialize a dictionary to hold DataFrames for each method in the current sector
        method_dataframes = {}

        # Loop through each method in method_dict
        for meth_key, meth_info in method_dict.items():
            data = []  # Initialize a new list to hold data for the current method
            
            # Extract the 'method name' tuple from the current method info
            method_name = meth_info['method name']
            method_unit = meth_info['unit']

            # Now loop through each activity in the sector
            for act in sector_data['activities']:
                # Ensure the activity is an instance of the expected class
                if not isinstance(act, bd.backends.peewee.proxies.Activity):
                    raise ValueError("`activities` must be an iterable of `Activity` instances")
                
                # Perform LCA calculations
                lca = bw.LCA({act: 1}, method_name)
                lca.lci()
                lca.lcia()
                
                # Collect data for the current activity and method
                data.append([
                    act["name"],
                    act.key,
                    act.get("reference product"),
                    act.get("location", "")[:25],
                    method_name,
                    method_unit,
                    lca.score,
                ])
            
            # Convert the data list to a DataFrame and store it in the sector's dictionary
            method_dataframes[meth_key] = pd.DataFrame(data, columns=labels)

        # Store the method_dataframes dictionary in the sector_dataframes dictionary
        sector_dataframes[sector] = method_dataframes

    # Now `sector_dataframes` is a dictionary where each key is a sector, and the value is another dictionary with method names and their corresponding DataFrames
    return sector_dataframes


import pandas as pd

def _relative_changes_df(database_dict_eco, database_dict_premise):

    ecoinvent_scores = _lca_scores_compare(database_dict_eco)
    premise_scores = _lca_scores_compare(database_dict_premise)

    relative_dict = {}

    # Iterate over sectors
    for sector_key in ecoinvent_scores:
        # Initialize the sector key in the output dictionary
        if sector_key not in relative_dict:
            relative_dict[sector_key] = {}

        # Iterate over methods within the sector
        for method_key in ecoinvent_scores[sector_key]:
            # Check if the method_key exists in both dictionaries to avoid KeyError
            if method_key in premise_scores.get(sector_key, {}):
                # Get the corresponding DataFrames
                df_ei = ecoinvent_scores[sector_key][method_key]
                df_premise = premise_scores[sector_key][method_key]

                #print(df_ei['activity key'])
                #print(df_premise)

                # Split the 'activity key' to extract the second part
                df_ei['activity_code'] = df_ei['activity key'].apply(lambda x: x[1])  # Access the second element of the tuple
                df_premise['activity_code'] = df_premise['activity key'].apply(lambda x: x[1])

                # Merge the two dataframes based on the activity code and method name
                merged_df = pd.merge(df_ei, df_premise, on=['activity_code', 'method name'], suffixes=('_ei', '_premise'))

                # Calculate the relative change
                merged_df['relative_change'] = ((merged_df['total_premise'] - merged_df['total_ei']) / merged_df['total_ei']) * 100

                # Store the result in the dictionary
                relative_dict[sector_key][method_key] = merged_df

    return relative_dict

def _add_sector_marker(df, sector):
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

def relative_changes_db(database_dict_eco, database_dict_premise, excel_file):

    relative_dict = (_relative_changes_df(database_dict_eco, database_dict_premise))
    
    # Prepare to save each LCA score table to a different worksheet in the same Excel file

    column_positions = {} #stores the indexes of columns for plotting
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for sector in relative_dict.keys():
            relative_changes = relative_dict[sector]
            
            for method, table in relative_changes.items():
                # Create a DataFrame for the current LCA score table
                df = pd.DataFrame(table)

                # Add sector marker
                df = _add_sector_marker(df, sector) #!! ADJUST      

                # Sort the DataFrame by 'relative_change' from largest negative to largest positive
                df = df.sort_values(by='relative_change', ascending=False)

                # Add a 'rank' column based on the 'relative_change', ranking from most negative to least negative
                df['rank'] = df['relative_change'].rank(ascending=False, method='dense').astype(int)
    
                # Get the index values of columns
                columns_of_interest = ["rank", "relative_change", "method", "method unit", ]
                positions = {col: df.columns.get_loc(col) for col in columns_of_interest if col in df.columns}
                column_positions[method] = positions

                # Generate worksheet name
                worksheet_name = f"{sector}_{method}"
                if len(worksheet_name) > 31:
                    worksheet_name = worksheet_name[:31]

                # Save the DataFrame to the Excel file in a new worksheet
                df.to_excel(writer, sheet_name=worksheet_name, index=False)
    return column_positions