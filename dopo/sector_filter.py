import re
import pandas as pd
import copy
from dopo import generate_sets_from_filters
from openpyxl import load_workbook
from openpyxl.chart import ScatterChart, BarChart, Reference, Series


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