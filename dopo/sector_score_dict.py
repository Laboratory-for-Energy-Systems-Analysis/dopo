# Inputs
# ------
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
   
    for method_key, method_details in methods.items():
        result = ba.comparisons.compare_activities_by_grouped_leaves(
            activities_list,
            method_details['object'].name,
            output_format=output_format,
            mode=mode
        )

        # Create a variable name using the method name tuple and identifier
        method_name = method_details['object'].name[2].replace(' ', '_').lower()
        var_name = f"{identifier}_{method_name}"

        #add two columns method and method unit to the df
        result['method'] = str(method_details['object'].name[2])
        result['method unit'] = str(method_details['object'].metadata['unit'])
        
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