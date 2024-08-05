"""
This module contains functions for the premise validation framework.
It includes functions for filtering of premise transformed ecoinvent databases, collecting relevant
data in a suitable format, and visualizing datasets.
Some of the functions included are brightway2 functions.

"""
#NOTE: The comments are not all up to date.

# Python import dependencies
# --------------------------
from premise import *

# data??
import os
import yaml
import peewee as pw

#brightway
import brightway2 as bw
import bw2analyzer as ba
import bw2data as bd

#common
import pandas as pd
import numpy as np

#plotting
import matplotlib.pyplot as plt
import seaborn as sns

#to be completed
import ast

# -----------------------------------------------------------------------------
# DATABASE FILTERING
# -----------------------------------------------------------------------------


# Sector filter functions from premise
# ---------------------------------------------------

def act_fltr(
    database: list,
    fltr = None,
    mask  = None,
):
    """Filter `database` for activities_list matching field contents given by `fltr` excluding strings in `mask`.
    `fltr`: string, list of strings or dictionary.
    If a string is provided, it is used to match the name field from the start (*startswith*).
    If a list is provided, all strings in the lists are used and dataframes_dict are joined (*or*).
    A dict can be given in the form <fieldname>: <str> to filter for <str> in <fieldname>.
    `mask`: used in the same way as `fltr`, but filters add up with each other (*and*).
    `filter_exact` and `mask_exact`: boolean, set `True` to only allow for exact matches.

    :param database: A lice cycle inventory database
    :type database: brightway2 database object
    :param fltr: value(s) to filter with.
    :type fltr: Union[str, lst, dict]
    :param mask: value(s) to filter with.
    :type mask: Union[str, lst, dict]
    :return: list of activity data set names
    :rtype: list

    """
    if fltr is None:
        fltr = {}
    if mask is None:
        mask = {}

    # default field is name
    if isinstance(fltr, (list, str)):
        fltr = {"name": fltr}
    if isinstance(mask, (list, str)):
        mask = {"name": mask}

    assert len(fltr) > 0, "Filter dict must not be empty."

    # find `act` in `database` that match `fltr`
    # and do not match `mask`
    filters = database
    for field, value in fltr.items():
        if isinstance(value, list):
            for val in value:
                filters = [a for a in filters if val in a[field]]
                
            #filters.extend([ws.either(*[ws.contains(field, v) for v in value])])
        else:
            filters = [
                a for a in filters if value in a[field]
            ]

            #filters.append(ws.contains(field, value))
    

    if mask:
        for field, value in mask.items():
            if isinstance(value, list):
                for val in value:
                    filters = [f for f in filters if val not in f[field]]
                #filters.extend([ws.exclude(ws.contains(field, v)) for v in value])
            else:
                filters = [f for f in filters if value not in f[field]]
                #filters.append(ws.exclude(ws.contains(field, value)))

    return filters


def generate_sets_from_filters(yaml_filepath, database=None) -> dict:
    """
    Generate a dictionary with sets of activity names for
    technologies from the filter specifications.

    :param filtr:
    :func:`activity_maps.InventorySet.act_fltr`.
    :return: dictionary with the same keys as provided in filter
        and a set of activity data set names as values.
    :rtype: dict
    """

    filtr=get_mapping(yaml_filepath, var='ecoinvent_aliases')

    names = []

    for entry in filtr.values():
        if "fltr" in entry:
            if isinstance(entry["fltr"], dict):
                if "name" in entry["fltr"]:
                    names.extend(entry["fltr"]["name"])
            elif isinstance(entry["fltr"], list):
                names.extend(entry["fltr"])
            else:
                names.append(entry["fltr"])

    #subset = list(
    #    ws.get_many(
    #        database,
    #        ws.either(*[ws.contains("name", name) for name in names]),
    #    )
    #)

    subset=[
        a for a in database if any(
    
    
            x in a["name"] for x in names
        )
    ]


    techs = {
        tech: act_fltr(subset, fltr.get("fltr"), fltr.get("mask"))
        for tech, fltr in filtr.items()
    }

    mapping = {
        tech: {act for act in actlst} for tech, actlst in techs.items()
    }


    return mapping

def get_mapping(filepath, var): 
    """
    Loa a YAML file and return a dictionary given a variable.
    :param filepath: YAML file path
    :param var: variable to return the dictionary for.
    :param model: if provided, only return the dictionary for this model.
    :return: a dictionary
    """

    with open(filepath, "r", encoding="utf-8") as stream:
        techs = yaml.full_load(stream)

    mapping = {}
    for key, val in techs.items():
        if var in val:
            mapping[key] = val[var]
            
    return mapping


# Example on how to call the functions to create a set of filtered activities_list 
#set_from_fltrs = generate_sets_from_filters(filtr=get_mapping(yaml_filepath, "ecoinvent_aliases"), database=ei39SSP

# -----------------------------------------------------------------------------
# METHODS
# -----------------------------------------------------------------------------

# Setting up the methods for outlier detection
# ---------------------------------------------------------------------

def find_and_create_method(criteria, exclude=None):
    """
    Find a method based on given criteria and create a Brightway Method object. This will choose the first method.
    Thus, filter criteria need to be defined precisely to pick the right method.
    
    :param criteria: List of strings that should be in the method name
    :param exclude: List of strings that should not be in the method name (optional)
    :return: Brightway Method object
    """
    methods = bw.methods

    # Start with all methods
    filtered_methods = methods

    # Apply inclusion criteria
    for criterion in criteria:
        filtered_methods = [m for m in filtered_methods if criterion in str(m)]

    # Apply exclusion criteria if provided
    if exclude:
        for exclusion in exclude:
            filtered_methods = [m for m in filtered_methods if exclusion not in str(m)]

    # Check if we found exactly one method
    if len(filtered_methods) == 0:
        raise ValueError("No methods found matching the given criteria.")
    elif len(filtered_methods) > 1:
        raise ValueError(f"Multiple methods found: {filtered_methods}. Please provide more specific criteria.")

    # Get the first (and only) method
    selected_method = filtered_methods[0]

    # Create and return the Brightway Method object storing it in a defined variable outside of the funciton.
    return bw.Method(selected_method)

#NOTE: Would a yaml filter make it easier? OR Could have predefined methods?"""

# Function for creating method dictionaries which holds method name and unit for later tracking of methods. 
# ---------------------------------------------------------------------------------------------------------

def create_method_dict(selected_methods_list):
    '''
    :selected_methods_list: a list of variables which contain the selected methods 
    
    '''
    method_dict = {}
    for method in selected_methods_list:
        method_dict[method] = {
            'method name': str(method.name),
            'method unit': str(method.metadata['unit'])
        }
    
    return method_dict

# ------------------------------------------------------------------------------------------------------------------------------
# CALCULATIONS
# ------------------------------------------------------------------------------------------------------------------------------

# Function based on brightways bw2analyzer (ba) function for generating dataframe containing total score and contribution by inputs
# -----------------------------------------------------------------------------------------------------------------------------

def compare_activities_multiple_methods(activities_list, methods, identifier, output_format='pandas', mode='absolute'):
    """
    Compares a set of activities by multiple methods, stores each generated dataframe as a variable (the method is the variable name) in a dictionary.
   
    :param activities_list: List of activities to compare
    :param methods: List of Brightway Method objects
    :param identifier: A string used in defining the variable names to better identify comparisons (e.g. sector name).
    :param output_format: Output format for the comparison (default: 'pandas')
    :param mode: Mode for the comparison (default: 'absolute'; others: 'relative')
    :return: Dictionary of resulting dataframes from the comparisons
    """
    dataframes_dict = {}
   
    for method in methods:
        result = ba.comparisons.compare_activities_by_grouped_leaves(
            activities_list,
            method.name,
            output_format=output_format,
            mode=mode
        )
        
        # Create a variable name using the method name tuple and identifier
        method_name = '_'.join(method.name).replace(' ', '_').lower()
        var_name = f"{identifier}_{method_name}"

        #add two columns method and method unit to the df
        result['method'] = str(method.name)
        result['method unit'] = str(method.metadata['unit'])
        
        #order the columns after column unit
        cols = list(result.columns)
        unit_index = cols.index('unit')
        cols.insert(unit_index + 1, cols.pop(cols.index('method')))
        cols.insert(unit_index + 2, cols.pop(cols.index('method unit')))
        result = result[cols]

        # Order the rows based on 'activity' and 'location' columns
        result = result.sort_values(['activity', 'location'])
        
        # Reset the index numbering
        result = result.reset_index(drop=True)

        # Store the result in the dictionary
        dataframes_dict[var_name] = result
   
    return dataframes_dict


# Function for creating 'other' category for insignificant input contributions (for dataframes generated with compare_activities_multiple_methods)
# -------------------------------------------------------------------------------------------------------------------------------------------------

def small_inputs_to_other_column(dataframes_dict, cutoff=0.01):
    '''
    Aggregate values into a new 'other' column for those contributing less than or equal to the cutoff value to the 'total' column value.
    Set the aggregated values to zero in their original columns.
    Remove any columns that end up containing only zeros.

    :param dataframes_dict: the dictionary

    '''
    
    processed_dict = {}

    for key, df in dataframes_dict.items():
        # Identify the 'total' column
        total_col_index = df.columns.get_loc('total')
        
        # Separate string and numeric columns
        string_cols = df.iloc[:, :total_col_index]
        numeric_cols = df.iloc[:, total_col_index:]
        numeric_cols = numeric_cols.astype(float)
        
        # Calculate the threshold for each row (1% of total)
        threshold = numeric_cols['total'] * cutoff
        
        # Create 'other' column
        numeric_cols['other'] = 0.0
        
        # Process each numeric column (except 'total' and 'other')
        for col in numeric_cols.columns[1:-1]:  # Skip 'total' and 'other'
            # Identify values less than the threshold
            mask = abs(numeric_cols[col]) < threshold #abs() to include negative contributions
            
            # Add these values to 'other'
            numeric_cols.loc[mask, 'other'] += numeric_cols.loc[mask, col]
            
            # Set these values to zero in the original column
            numeric_cols.loc[mask, col] = 0
        
        # Remove columns with all zeros (except 'total' and 'other')
        cols_to_keep = ['total'] + [col for col in numeric_cols.columns[1:-1] 
                                             if not (numeric_cols[col] == 0).all()]
        cols_to_keep.append('other')
        
        numeric_cols = numeric_cols[cols_to_keep]
        
        # Combine string and processed numeric columns
        processed_df = pd.concat([string_cols, numeric_cols], axis=1)
        
        #Sort columns by total
        processed_df = processed_df.sort_values('total', ascending=False)
        
        # Store the processed DataFrame in the result dictionary
        processed_dict[key] = processed_df
        
    return processed_dict

# Function for saving created sector impact score dataframes to excel
# -------------------------------------------------------------------

def save_dataframes_to_excel(dataframes_dict, filepath, filename):
    '''
    :param dataframes_dict: processed with other catgeory or not processed 
    :param filename: should contain ".xlsx"
    '''
    # Ensure the directory exists
    os.makedirs(filepath, exist_ok=True)
    
    # Create the full path for the Excel file
    full_path = os.path.join(filepath, filename)
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
        # Iterate through the dictionary
        for original_name, df in dataframes_dict.items():
            # Truncate the sheet name to 31 characters
            sheet_name = original_name[:31]
            
            # Write each dataframe to a different worksheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # If the sheet name was truncated, print a warning
            if sheet_name != original_name:
                print(f"Warning: Sheet name '{original_name}' was truncated to '{sheet_name}'")
    
    print(f"Excel file '{full_path}' has been created successfully.")


# --------------------------------------------------------------------------------------------------
# PLOTS
# --------------------------------------------------------------------------------------------------

# GENERAL LEGEND
# --------------
# Level 1-2.3 plots dependency: Legend to map indexes on x-axis to activities
# ---------------------------------------------------------------------------------------

def generate_legend_text(data):
    '''
    Maps the indexes on the x-axis to the activities to list them in a legend.

    :param data: it can take in a dictionary of dataframes or just a single dataframe
    '''

    legend_text = []
    
    # Check if the input is a dictionary or a DataFrame
    if isinstance(data, dict):
        # Use the first DataFrame in the dictionary
        first_key = next(iter(data))
        df = data[first_key]
    elif isinstance(data, pd.DataFrame):
        # Use the input DataFrame directly
        df = data
    else:
        raise ValueError("Input must be either a dictionary of DataFrames or a DataFrame")
   
    # Create a list of tuples with (index, activity, location)
    items = [(str(i), row['activity'], row['location']) for i, row in df.iterrows()]
    # Sort the items based on the index
    sorted_items = sorted(items, key=lambda x: x[0])
    # Add sorted items to legend_text
    for i, activity, location in sorted_items:
        legend_text.append(f"{i}: {activity} - {location}")
    return legend_text

# LEVEL 1
# -------
# Function for plotting: Level 1 dot plot with standard deviation and IQR range
# ------------------------------------------------------------------------------

def lvl1_plot(dataframes_dict, title_key=None):
    '''
    Plots the total score value for each activity sorted from largest to smallest. Visualizes IQR and standard deviation. 
    Generates as many plots as methods were defined.

    :param dataframes_dict: dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param title_key: some string for the plot titles (e.g. sector name)

    '''
    #NOTE: Units are not correctly shown on the y-axis yet.

    # Iterate over each dataframe and create individual plots
    for idx, df in dataframes_dict.items():
        # Create a new figure for each plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort the DataFrame in descending order based on the 'total' column
        sorted_df = df.sort_values(by='total', ascending=False)
        
        # Save the sorted index to order variable and call order variable in sns.swarmplot
        order = sorted_df.index.tolist()

        # Calculate statistics
        q1 = df['total'].quantile(0.25)
        q3 = df['total'].quantile(0.75)
        mean_gwp = df['total'].mean()
        std_gwp = df['total'].std()
        
        # Plot using seaborn swarmplot
        sns.swarmplot(data=df, x=df.index, y='total', dodge=True, ax=ax, order=order)

        # Add mean line
        ax.axhline(mean_gwp, color='grey', linestyle='--', linewidth=1, label='Mean')

        # Add horizontal lines for Q1 and Q3
        ax.hlines(y=q3, xmin=-0.5, xmax=len(df)-0.5, color='lightblue', linestyle='dotted', linewidth=1, label='Q3 (75th percentile)')
        ax.hlines(y=q1, xmin=-0.5, xmax=len(df)-0.5, color='lightblue', linestyle='dotted', linewidth=1, label='Q1 (25th percentile)')

        # Add horizontal shading for areas above and below 2 standard deviations from the mean
        ax.axhspan(mean_gwp - 2 * std_gwp, mean_gwp - 3 * std_gwp, color='grey', alpha=0.2, label=">2 std below mean")
        ax.axhspan(mean_gwp + 2 * std_gwp, mean_gwp + 3 * std_gwp, color='grey', alpha=0.2, label=">2 std above mean")

        # Add titles and labels
        ax.set_title(f"{str(title_key)} - {df['method'].iloc[0]} in {df['method unit'].iloc[0]}")
        ax.set_xlabel('Activity/ Dataset')
        ax.set_ylabel(f"{df['method unit'].iloc[0]}")

        # Rotate x-axis labels if needed
        ax.tick_params(axis='x', rotation=90)

        # Add legend
        ax.legend()

        # Generate the legend text using the first dataframe
        legend_text = generate_legend_text(dataframes_dict)

        # Add the legend text to the right of the plot
        plt.text(1.02, 0.5, '\n'.join(legend_text), transform=ax.transAxes, ha='left', va='center', fontsize=11, bbox=dict(facecolor='white', alpha=0.2, edgecolor='grey'))

        # Show the plot
        plt.tight_layout()
        plt.show()

# LEVEL 2.1
# --------
# Function for plotting: Level 2.1 Absolute stacked bar plots
# ------------------------------------------------------------

def lvl21_plot_stacked_absolute(dataframes_dict, title_key=None):
    '''
    Comparing activities and the input contributions to the total score by plotting a stacked absolute bar plot for each method.

    :param dataframes_dict: dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param title_key: some string for the plot titles
    '''
    # Step 1: Collect all unique categories
    all_categories = set()
   
    for df in dataframes_dict.values():
        if 'total' in df.columns:
            total_index = df.columns.get_loc('total')
            relevant_columns = df.columns[total_index + 1:]
        else:
            relevant_columns = df.columns
       
        # Update all_categories set with relevant columns
        all_categories.update(relevant_columns)
   
    all_categories = list(all_categories)
   
    # Step 2: Create a consistent color palette and color map
    distinct_colors = generate_distinct_colors(len(all_categories))
    color_map = dict(zip(all_categories, distinct_colors))

    # Step 3: Plot each DataFrame
    for key, df in dataframes_dict.items():
        if 'total' in df.columns:
            total_index = df.columns.get_loc('total')
            df = df.iloc[:, total_index + 1:]
       
        # Create a new figure for each plot
        fig, ax = plt.subplots(figsize=(20, 10))
       
        # Ensure columns match the categories used in the color map
        df = df[[col for col in df.columns if col in color_map]]
        
        # Plotting the DataFrame with the custom color map
        df.plot(kind='bar', stacked=True, ax=ax, color=[color_map[col] for col in df.columns])
       
        # Add titles and labels
        method = df['method'].iloc[0] if 'method' in df else 'Method'
        method_unit = df['method unit'].iloc[0] if 'method unit' in df else 'Unit'
        ax.set_title(f"{title_key} - {method} in {method_unit}", fontsize=16)
        ax.set_xlabel('Activity/ Dataset')
        ax.set_ylabel(f"{method_unit}")
        
        # First legend: Categories
        first_legend = ax.legend(title='Categories', loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
        
        # Add the first legend manually
        ax.add_artist(first_legend)
        
        # Set the title
        ax.set_title(key, fontsize=16)
        
        # Generate the legend text using the first dataframe
        legend_text = generate_legend_text(dataframes_dict)
        
        # Create a second legend below the first one
        fig.text(1.02, 0.1, '\n'.join(legend_text), transform=ax.transAxes, fontsize=11, 
                 verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.2, edgecolor='grey'))
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
       
        # Adjust layout to make room for both legends
        plt.tight_layout()
        plt.subplots_adjust(right=0.75, bottom=0.2)
       
        # Display the plot
        plt.show()

# LEVEL 2.2
# ----------
# Function for plotting: Level 2.2 bar plot comparing one input characterized by one method across sector/ activity list
# ----------------------------------------------------------------------------------------------------------------------

def lvl22_plot_input_comparison_with_method(dataframes_dict, dataframe_key, input_number):
    """
    Comparing one specific cpc input among activities for each method.

    :param dataframes_dict:dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param dataframe_key: Key to access a specific DataFrame from the dictionary. 
    :param input_number: Unique cpc identifier number of the input that should be plotted.
    """
    # Access the specific DataFrame
    df = dataframes_dict.get(dataframe_key)
    
    if df is None:
        print(f"No DataFrame found for key: {dataframe_key}")
        return

    # Filter columns based on the input_number
    columns_to_plot = [col for col in df.columns if str(input_number) in str(col)]
    
    if not columns_to_plot:
        print(f"No columns found containing input number: {input_number}")
        return
    
    # Plot the filtered columns
    ax = df[columns_to_plot].plot(kind='bar', figsize=(14, 6))
    plt.xlabel('Activity/ Dataset')
    plt.ylabel(f"{df['method unit'].iloc[0]}")
    plt.title(f'Comparison Plot for Input Number {input_number}')

    # Add legend for identifying activities_list from index
    # Generate the legend text using the first dataframe
    legend_text = generate_legend_text(dataframes_dict.get(dataframe_key))
        
    # Add the legend text to the right of the plot
    plt.text(1.02, 0.5, '\n'.join(legend_text), transform=ax.transAxes, ha='left', va='center', fontsize=11, bbox=dict(facecolor='white', alpha=0.2, edgecolor='grey'))
    
    plt.show()

# Level 2.2 plot dependencies: Function for formating plot: Unique colors for Level 2.1 Absolute stacked bar plots
# -----------------------------------------------------------------------------------

def generate_distinct_colors(n):
    """Generate n distinct colors using HSV color space."""
    hues = np.linspace(0, 1, n, endpoint=False)
    colors = [plt.cm.hsv(h) for h in hues]
    return colors

# LEVEL 2.3
# ---------
# Function for plotting: Level 2.3 bar plot comparing input not characterized across sector/ activity list
# --------------------------------------------------------------------------------------------------------

def lvl23_plot_input_comparison_plot_no_method(activities_list, input_type, input_number,):
    '''
    Comparing one specific cpc input among activities without method.

    :param activities_list: list of activities to plot inputs for. Perhabs the one defined at the beginning.
    :param input_type: type of the activities input default 'list', other 'dict'
    :param input_number: the cpc code of the input that is supposed to be plotted

    '''
    cpc_input_dataframe = get_cpc_inputs_of_activities(activities_list, input_type)

    x_input_fltr= [x for x in cpc_input_dataframe.columns if str(input_number) in str(x)][0]
    
    df= cpc_input_dataframe[x_input_fltr]
    
    df = df.sort_values(ascending=False)
    ax = df.plot(kind='bar', x=x_input_fltr, figsize=(14, 6))
    ax.set_xlabel('Activity/ Dataset')
    ax.set_ylabel(f"{cpc_input_dataframe['unit'].iloc[0]}")
    ax.set_title(f'Comparison Plot for not characterized Input - {x_input_fltr}')

    # Generate the legend text to map index to activity
    legend_text = generate_legend_text(cpc_input_dataframe)
    # Add the legend text to the right of the plot
    ax.text(1.02, 0.5, '\n'.join(legend_text), transform=ax.transAxes, ha='left', va='center', fontsize=11, bbox=dict(facecolor='white', alpha=0.2, edgecolor='grey'))


# Level 2.3 plot dependencies: Function to generate dataframes containing inputs in cpc format not characterized from an activity list 
# ---------------------------------------------------------------------------------------------------------

def get_cpc_inputs_of_activities(activities_list, input_type='list'):

    '''
    for param description see function lvl23_plot_input_comparison_plot_no_method

    !!! NOTE: Adapt this function to get the outputs !!!
    
    '''

    def activity_list_inputs_cpc(activities_list, input_type):
        all_inputs = []
        
        if input_type == 'list':
            activity_iterator = activities_list
        elif input_type == 'dict':
            activity_iterator = activities_list.values()
        else:
            raise ValueError("input_type must be either 'list' or 'dict'")
        
        for activity in activity_iterator:
            inputs_keys = pd.Series({bw.get_activity(exc.input).key: exc.amount for exc in activity.technosphere()},
                                    name=activity['name'] + ', ' + activity['location'])
            
            # Adjust the way the key is presented
            inputs_keys = inputs_keys.reset_index()
            inputs_keys['full_key'] = inputs_keys.apply(lambda row: f"('{row['level_0']}', '{row['level_1']}')", axis=1)
            inputs_keys = inputs_keys.drop(['level_0', 'level_1'], axis=1).set_index('full_key')
            
            # Add empty cpc column and activity information
            inputs_keys.insert(0, 'identifier', activity['name'] + ', ' + activity['location'])
            inputs_keys.insert(1, 'activity', activity['name'])
            inputs_keys.insert(2, 'location', activity['location'])
            inputs_keys.insert(3, 'unit', activity['unit'])
            inputs_keys.insert(4, 'cpc', None)
            
            all_inputs.append(inputs_keys)
        
        # Combine all inputs into a single DataFrame
        combined_inputs = pd.concat(all_inputs, axis=0)
        
        return combined_inputs

    def update_cpc_information(combined_inputs):
        for index, row in combined_inputs.iterrows():
            # Transform each key to tuple
            tuple_key = ast.literal_eval(index)
            
            # Get input activity for the key
            input_activity = bw.get_activity(tuple_key)
            
            # Get cpc name for activity
            cpc_name = ba.comparisons.get_cpc(input_activity)
            
            # Store cpc_name in the 'cpc' column of the combined_inputs dataframe
            combined_inputs.at[index, 'cpc'] = cpc_name
        
        return combined_inputs

    def transform_dataframe(combined_inputs):
        # Set 'identifier' as the new index and drop the 'full_key' index
        combined_inputs = combined_inputs.reset_index().set_index('identifier').drop('full_key', axis=1)
        
        # Determine the index of the 'unit' column
        unit_index = combined_inputs.columns.get_loc('unit')
        
        # Split the dataframe into two parts
        combined_inputs_identifier = combined_inputs.iloc[:, :unit_index+1]
        combined_inputs_cpc = combined_inputs.iloc[:, unit_index+1:]
        #set index of to 'cpc' in combined_input_cpc
        combined_inputs_cpc = combined_inputs_cpc.set_index('cpc')
        
        # Combine rows with the same index value in combined_inputs_cpc
        combined_inputs_cpc = combined_inputs_cpc.groupby(level=0).agg(lambda x: np.sum(x) if x.dtype.kind in 'biufc' else x.iloc[0])
        # Transpose combined_inputs_cpc
        combined_inputs_cpc_trans = combined_inputs_cpc.T
        
        # Merge combined_inputs_identifier and combined_inputs_cpc_trans
        result = combined_inputs_identifier.join(combined_inputs_cpc_trans)
        result = result.drop_duplicates()

        # Sort dataframe by activity and location aplphabetically and reset the index
        result = result.sort_values(by=['activity', 'location'])
        result = result.reset_index(drop=True)
        return result

    # Execute the workflow
    combined_inputs = activity_list_inputs_cpc(activities_list, input_type)
    combined_inputs_with_cpc = update_cpc_information(combined_inputs)
    final_result = transform_dataframe(combined_inputs_with_cpc)

    return final_result


# LEVEL 3
# --------
# Function for plotting: Level 3 S-curve difference of og database and premise adapted database by one meth
# ------------------------------------------------------------------------------------------------------------

def lvl3_plot_relative_changes(database, premise_database, method):

    '''
    A function that plots the relative changes in activitiy LCA scores (for one defined method) between a "raw" ecoinvent database and a premise transformed ecoinvent database.

    :param database: an ecoinvent database or set of activities from an ecoinvent database.
    :premise_database: a premise transformed database or a set of activities which has intersections with the ecoinvent database.
    :method: a method the relative changes should be calculated and plotted for.

    '''

    ecoinvent_scores = calculate_lca_ecoinvent_scores(database, method)
    premise_scores = calculate_lca_premise_scores(premise_database, method)

    relative_changes = calc_relative_changes(ecoinvent_scores, premise_scores)

    # Filter out entries where the value is a tuple (method)
    filtered_changes = {k: v for k, v in relative_changes.items() if not isinstance(v, tuple)}

    # Sort the relative changes by magnitude
    sorted_changes = sorted(filtered_changes.items(), key=lambda x: x[1])

    # Prepare data for plotting
    activities_list = [f"{key}" for key, _ in sorted_changes]
    changes = [change for _, change in sorted_changes]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, len(activities_list) * 0.4))  # Adjust figure height based on number of activities_list
    fig.suptitle(f"Relative Changes in LCA Scores {relative_changes['method']}")
    y_pos = np.arange(len(activities_list))
    ax.barh(y_pos, changes, align='center', color='lightgrey', alpha=0.7)

    # Plot curve through datapoints
    ax.plot(changes, y_pos, color='darkblue', linewidth=2, marker='o', markersize=6)

    # Set labels and title
    ax.set_yticks(y_pos)
    ax.set_yticklabels(activities_list)
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Relative Change')
  

    # Add a vertical line at x=0
    ax.axvline(x=0, color='k', linestyle='--')
    
    # Adjust layout and display
    plt.tight_layout()
    plt.show()

# Level 3 plot dependencies: Functions for generating lca scores of ecoinvent and premise database to plot their relative changes
# -------------------------------------------------------------------------------------------------------------------------------

def calculate_lca_ecoinvent_scores(database, method):

    ecoinvent_scores= {}
    ecoinvent_scores['method']=method #save the method used for plotting the data
    all_activities=[x for x in database]
    
    for activity in all_activities:
        activity_LCA = bw.LCA({activity:1}, bw.Method(method).name)
        activity_LCA.lci()
        activity_LCA.lcia()
        score=activity_LCA.score

         # Create a tuple key with relevant information
        key = (activity['name'], activity['unit'], activity['location'], activity.get('reference product'))

        ecoinvent_scores[key]=score

    return ecoinvent_scores

def calculate_lca_premise_scores(premise_database, method):

    premise_scores= {}

    premise_scores['method']=method #save the method used for plotting the data

    all_activities=[x for x in premise_database]
    
    for activity in all_activities:
        activity_LCA = bw.LCA({activity:1}, bw.Method(method).name)
        activity_LCA.lci()
        activity_LCA.lcia()
        score=activity_LCA.score

         # Create a tuple key with relevant information
        key = (activity['name'], activity['unit'], activity['location'], activity.get('reference product'))

        premise_scores[key]=score

    return premise_scores


# relative_changes contains the activity names as keys and their relative changes as values

def compute_relative_change(original, transformed):
    if original == 0:
        return float('inf') if transformed != 0 else 0
    return (transformed - original) / original


def calc_relative_changes(ecoinvent_scores, premise_scores):

    # Match activities_list and calculate relative changes
    relative_changes = {}
    relative_changes['method']=ecoinvent_scores['method']
    
    for key, original_score in ecoinvent_scores.items():
        if key in premise_scores:
            # Skip if original_score is a tuple
            if isinstance(original_score, tuple):
                continue
            
            transformed_score = premise_scores[key]
            relative_change = compute_relative_change(original_score, transformed_score)
            relative_changes[key] = relative_change

    # Print the dataframes_dict
    for key, change in relative_changes.items():
        print(f"{key}: {change}")
    
    return relative_changes

''' NOTE: It is yet not considered how to treat activities if they are only contained in premise but not in ecoinvent database'''