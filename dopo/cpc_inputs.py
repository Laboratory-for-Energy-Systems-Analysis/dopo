
# Imports
# --------

#brightway
import brightway2 as bw
import bw2analyzer as ba

#common
import pandas as pd
import numpy as np

#to be completed
import ast

# Function to generate dataframes containing inputs in cpc format not characterized from an activity list 
# Level 2.3 plot dependency
# ------------------------------------------------------------------------------------------------------------------------------------

def _get_cpc_inputs_of_activities(activities_list, input_type='list'):

    '''
    for param description see function lvl23_plot_input_comparison_plot_no_method

    NOTE: could adapt this function to get the outputs, or create another one. At the moment only inputs are considered.
    
    '''

    def _activity_list_inputs_cpc(activities_list, input_type):
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

    def _update_cpc_information(combined_inputs):
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

    def _transform_dataframe(combined_inputs):
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
    combined_inputs = _activity_list_inputs_cpc(activities_list, input_type)
    combined_inputs_with_cpc = _update_cpc_information(combined_inputs)
    final_result = _transform_dataframe(combined_inputs_with_cpc)

    return final_result
