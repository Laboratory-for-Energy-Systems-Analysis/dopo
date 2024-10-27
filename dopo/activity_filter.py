"""
This module contains functions to filter activities from a database based on
a YAML file with filter specifications.
"""

import yaml
import bw2data
from pathlib import Path

# Sector filter functions from premise
# ---------------------------------------------------


def _act_fltr(
    database: list,
    fltr: [str, list, dict] = None,
    mask: [str, list, dict] = None,
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
        else:
            filters = [a for a in filters if value in a[field]]

    if mask:
        for field, value in mask.items():
            if isinstance(value, list):
                for val in value:
                    filters = [f for f in filters if val not in f[field]]
            else:
                filters = [f for f in filters if value not in f[field]]

    return filters


def generate_sets_from_filters(filtr: dict, database: bw2data.Database) -> dict:
    """
    Generate a dictionary with sets of activity names for
    technologies from the filter specifications.

    :param mapping: path to the YAML file with filter specifications
    :type mapping: str
    :param database: A lice cycle inventory database
    :type database: brightway2 database object
    :return: A dictionary with sets of activity names for technologies
    :rtype: dict

    """

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

    subset = [a for a in database if any(x in a["name"] for x in names)]

    techs = {
        tech: _act_fltr(subset, fltr.get("fltr"), fltr.get("mask"))
        for tech, fltr in filtr.items()
    }

    mapping = {tech: {act for act in actlst} for tech, actlst in techs.items()}

    return mapping


def _get_mapping(filepath: [str, Path]) -> dict:
    """
    Load a YAML file and return a dictionary given a variable.
    :param filepath: YAML file path
    :param var: variable to return the dictionary for.
    :param model: if provided, only return the dictionary for this model.
    :return: a dictionary
    """

    with open(filepath, "r", encoding="utf-8") as stream:
        return yaml.full_load(stream)
