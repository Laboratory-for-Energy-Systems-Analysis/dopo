"""
This module processes YAML files to filter activities based on criteria and updates a dictionary 
with filtered activities from a given database. It utilizes filters defined in YAML files and 
returns an updated dictionary containing filtered activities for each sector.

It also contains a function gets the count and amount an activitiy is input.exchange to 
another activity and stores thes stats in a dictionary. These stats should be further used and 
added to generated excel tables to compare relevance of activities over the whole database.
"""

from .activity_filter import generate_sets_from_filters
import copy
import numpy as np 

def process_yaml_files(files_dict, database):
    """
    Processes YAML files to filter activities based on defined
    criteria and updates a dictionary with the filtered activities.

    This function iterates through a dictionary of YAML file paths
    and identifiers, applies filters defined in the YAML files to a
    given database, and updates the dictionary with the filtered
    activities for each sector.

    Parameters
    ----------
    files_dict : dict
        A dictionary where keys represent sector names, and values are dictionaries containing:
        - 'yaml': str
            Path to the YAML file containing filter definitions.
        - 'yaml identifier': str
            Identifier used to retrieve filtered activities from the generated set.
    database : object
        A database object (e.g., from `ecoinvent` or `premise`) used to filter activities.

    Returns
    -------
    dict
        The updated dictionary with an additional key 'activities'
        for each sector, which contains a list of filtered activities.
    """
    
    # Create a deep copy of the input dictionary to avoid modifying the original
    activity_dict = copy.deepcopy(files_dict)

    for key, value in activity_dict.items():
        yaml_file = value['yaml']
        yaml_identifier = value['yaml identifier']
        
        # Debug: print the current processing status
        # print(f"Processing {key} with database {database.name}")
        
        # Generate the filtered activities for the sector
        sector_activities = generate_sets_from_filters(yaml_file, database)
        
        # Debug: print the activities for the current sector
        # print(f"Activities for {key}:")
        # for activity in sector_activities[yaml_identifier]:
        #     print(f"  {activity.key}")

        # Convert the set of activities to a list
        activities_list = list(sector_activities[yaml_identifier])
        
        # Update the main dictionary with the list of activities
        activity_dict[key]['activities'] = activities_list
        
    return activity_dict


def activities_are_exchanges_stats(activity_dict, database_name):
    """
    Computes statistics on how often activities in a sector are exchanges to another activity
    within a database, such as total exchange counts, exchange amounts, and their median.

    Args:
        activity_dict (dict): Dictionary containing activities by sector.
        database_name (list): Database to be searched for exchanges.

    Returns:
        dict: A dictionary containing exchange statistics (count, amounts, median) for each activity 
        under each key in the input activity_dict.
    """

    
    # Initialize a results dictionary to store exchange data for each key
    results = {}

    # Iterate over each key in the premise_dict
    for key, value in activity_dict.items():
        # Dictionary to store exchange data for each activity under the current key
        activities_data = {}

        try:
            # Get the list of activities for the current key
            activities_list = activity_dict[key]['activities'][:3]
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
            activities_data[key][str(activity)] = {
                "exchange_count": exchange_count,
                "exchange_amounts": exchange_amounts,
                "median_exchange_amount": median_value,
                "activitiy_key": activity_key
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
