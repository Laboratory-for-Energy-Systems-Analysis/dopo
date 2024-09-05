import re
import pandas as pd
from dopo import generate_sets_from_filters
from dopo import compare_activities_multiple_methods
from dopo import small_inputs_to_other_column
import openpyxl
from openpyxl import load_workbook
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart import BarChart, Reference
import copy


def process_yaml_files(files_dict, database):
    '''
    - Runs through the files_dict reading the defined filters in the yaml files.
    - With another function a list that contains the filtered activities is created from the chosen database.
    - This activity list is saved within the corresponding key (sector) in the dictionary main_dict which is based on the files_dict.

    :param files_dict: dictionary of dictionaries. It should hold the yaml file path and the title in the first row of the yaml file. 
                        Like so: files_dict['Cement']={'yaml': 'yamls\cement_small.yaml', 'yaml identifier': 'Cement'}
    :param database: premise or ecoinvent database of choice.

    It returns an updated dictionary which contains filtered activity lists for each sector.
    '''

    main_dict = copy.deepcopy(files_dict)

    for key, value in main_dict.items():
        yaml_file = value['yaml']
        yaml_identifier = value['yaml identifier']
        
        #debug
        print(f"Processing {key} with database {database.name}") # check for right database
        
        # Generate the sector activities
        sector_activities = generate_sets_from_filters(yaml_file, database)
        
        #debug
        print(f"Activities for {key}:")
        for activity in sector_activities[yaml_identifier]:
            print(f"  {activity.key}")

        # Convert the set of activities to a list
        activities_list = list(sector_activities[yaml_identifier])
        
        # Add to the sectors_dict
        main_dict[key]['activities'] = activities_list
        
    return main_dict

 # To calculate the median

database_name=ei39SSP2

# Initialize a results dictionary to store exchange data for each key
results = {}

# Iterate over each key in the premise_dict
for key, value in premise_dict.items():
    # Dictionary to store exchange data for each activity under the current key
    activities_data = {}

    try:
        # Get the list of activities for the current key
        activities_list = premise_dict[key]['activities'][:3]
    except KeyError:
        print(f"KeyError: 'activities' not found for key: {key}")
        continue

    # Check if there are activities to process
    if not activities_list:
        print(f"No activities found for key: {key}")
        continue
    
    # Iterate over each activity in the activities_list
    for activity in activities_list:
        # Initialize the counter and amounts list for this activity
        exchange_count = 0
        exchange_amounts = []

        # Retrieve the unique identifier for the activity (e.g., activity.key)
        activity_key = activity.key  # Adjust this line to match the correct attribute for key

        # Loop through all activities in the database
        for act in database_name:  # Replace 'database_name' with your actual database object
            # Loop through all exchanges in the current activity of the database
            for exc in act.exchanges():
                # Compare unique keys of exchange input and activity
                if exc.input.key == activity_key:  # Ensure we compare keys, not objects
                    exchange_count += 1
                    # Store the amount of the exchange
                    exchange_amounts.append(exc['amount'])

        # Calculate the median of the exchange amounts if there are any
        median_value = np.median(exchange_amounts) if exchange_amounts else None
        
        # Store the exchange data for the current activity
        activities_data[str(activity)] = {
            "exchange_count": exchange_count,
            "exchange_amounts": exchange_amounts,
            "median_exchange_amount": median_value
        }

    # Store the activities data in the results dictionary under the current key
    results[key] = activities_data

# Print or process the results as needed
for key, activity_data in results.items():
    print(f"Results for key: {key}")
    for activity, data in activity_data.items():
        print(f"  Activity: {activity}")
        print(f"    Total Exchanges: {data['exchange_count']}")
        print(f"    Median Exchange Amount: {data['median_exchange_amount']}")
        print(f"    Exchange Amounts: {data['exchange_amounts']}")
    print("-" * 40)
