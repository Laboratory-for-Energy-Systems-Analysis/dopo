"""
Module for Managing Brightway2 Methods

Provides functionality to filter and manage LCA methods in Brightway2. The `MethodFinder` class 
enables users to search for methods based on criteria and manage them efficiently.
"""

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
    methods : list
        A list of method objects that match the specified criteria.

    Methods
    -------
    find_and_create_method(criteria, exclude=None, custom_key=None)
        Finds methods based on provided criteria, filters them, and stores the selected method
        in the dictionary with a unique or custom key.

    """

    def __init__(self):
        """
        Initializes the MethodFinder class with an empty dictionary for storing methods
        and a counter for generating unique method keys.
        """
        self.methods = []

    def find_methods(
            self,
            criteria: list,
            exclude: list = None,
    ) -> None:
        """
        Finds and filters methods based on the given criteria and optionally
        excludes methods based on exclusion criteria. The tuple representation
        of the selected method is then added to `self.methods`.

        :param criteria: A list of strings to search for in the method names.
        :type criteria: list
        :param exclude: A list of strings to exclude from the method names.
        :type exclude: list, optional
        :return: None

        """

        # Start with all methods
        filtered_methods = bd.methods

        # test presence of methods
        if not filtered_methods:
            raise ValueError("No methods found in the Brightway2 project.")

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

        print(f"Found {len(filtered_methods)} methods matching the criteria.")

        return filtered_methods

    def add_methods(self, methods: list) -> None:
        """
        Add a list of method objects to the `self.methods` attribute.

        :param methods: A list of method objects to add.
        :type methods: list
        :return: None

        """
        self.methods.extend(methods)
        print(f"Added {len(methods)} methods to the list.")
