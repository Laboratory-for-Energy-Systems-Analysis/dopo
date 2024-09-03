"""
Module for Managing Brightway2 Methods

Provides functionality to filter and manage LCA methods in Brightway2. The `MethodFinder` class 
enables users to search for methods based on criteria and manage them efficiently.
"""

import brightway2 as bw
import bw2analyzer as ba
import bw2data as bd

class MethodFinder:
    """
    A class to find, filter, and store Brightway methods based on specific criteria.

    This class provides functionalities to search for methods within the Brightway2
    framework, apply inclusion and exclusion criteria, and store the filtered methods
    in a dictionary for easy access and management. It allows users to generate a custom
    dictionary of method objects that match certain criteria.

    Attributes
    ----------
    all_methods : dict
        A dictionary to store method objects and their metadata.
    method_counter : int
        A counter to generate unique keys for each method stored in the dictionary.

    Methods
    -------
    find_and_create_method(criteria, exclude=None, custom_key=None)
        Finds methods based on provided criteria, filters them, and stores the selected method
        in the dictionary with a unique or custom key.

    get_all_methods()
        Returns the dictionary containing all stored methods.
    """

    def __init__(self):
        """
        Initializes the MethodFinder class with an empty dictionary for storing methods
        and a counter for generating unique method keys.
        """
        self.all_methods = {}
        self.method_counter = 0

    def find_and_create_method(self, criteria, exclude=None, custom_key=None):
        """
        Finds and filters methods based on the given criteria and optionally excludes methods
        based on exclusion criteria. The selected method is then stored in a dictionary with
        a unique or custom key.

        Parameters
        ----------
        criteria : list of str
            A list of strings representing the inclusion criteria to filter the methods.
        exclude : list of str, optional
            A list of strings representing the exclusion criteria to filter out certain methods 
            (default is None).
        custom_key : str, optional
            A custom key to use for storing the method in the dictionary. If not provided,
            a unique key is generated automatically (default is None).

        Returns
        -------
        dict
            A dictionary with the method's key and its associated data including the method object,
            method name, short name, and unit.

        Raises
        ------
        ValueError
            If no methods or multiple methods are found matching the given criteria.
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
                filtered_methods = [
                    m for m in filtered_methods if exclusion not in str(m)
                ]
        # Check if we found exactly one method
        if len(filtered_methods) == 0:
            raise ValueError("No methods found matching the given criteria.")
        elif len(filtered_methods) > 1:
            raise ValueError(
                f"Multiple methods found: {filtered_methods}. Please provide more specific criteria."
            )
        # Get the first (and only) method
        selected_method = filtered_methods[0]
        # Create the Brightway Method object
        method_object = bw.Method(selected_method)

        # Generate a key for storing the method
        if custom_key is None:
            self.method_counter += 1
            key = f"method_{self.method_counter}"
        else:
            key = custom_key

        # Store the method object and additional information in the dictionary
        self.all_methods[key] = {
            "object": method_object,
            "method name": method_object.name,
            "short name": method_object.name[2],
            "unit": method_object.metadata.get("unit", "Unknown"),
        }

        # Return both the method object and its key
        return {key: self.all_methods[key]}

    def get_all_methods(self):
        """
        Returns the dictionary containing all stored methods.

        Returns
        -------
        dict
            A dictionary containing all stored methods with their associated data.
        """
        return self.all_methods
