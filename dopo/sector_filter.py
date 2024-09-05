"""
This module processes YAML files to filter activities based on criteria and updates a dictionary 
with filtered activities from a given database. It utilizes filters defined in YAML files and 
returns an updated dictionary containing filtered activities for each sector.
"""

from dopo import generate_sets_from_filters
import copy

def process_yaml_files(files_dict, database):
    """
    Processes YAML files to filter activities based on defined criteria and updates a dictionary 
    with the filtered activities.

    This function iterates through a dictionary of YAML file paths and identifiers, applies filters 
    defined in the YAML files to a given database, and updates the dictionary with the filtered 
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
        The updated dictionary with an additional key 'activities' for each sector, which contains 
        a list of filtered activities.
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
        for activity in sector_activities[yaml_identifier]:
            # print(f"  {activity.key}")

        # Convert the set of activities to a list
        activities_list = list(sector_activities[yaml_identifier])
        
        # Update the main dictionary with the list of activities
        activity_dict[key]['activities'] = activities_list
        
    return activity_dict
