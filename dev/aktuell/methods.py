# Dependencies
# ------------

# brightway
import brightway2 as bw
import bw2analyzer as ba
import bw2data as bd

# Class for generating method dictionary
# --------------------------------------


class MethodFinder:
    def __init__(self):
        self.all_methods = {}
        self.method_counter = 0

    def find_and_create_method(self, criteria, exclude=None, custom_key=None):
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
        return self.all_methods
