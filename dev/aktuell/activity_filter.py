# Imports
# -------

import yaml

# Sector filter functions from premise
# ---------------------------------------------------


def _act_fltr(
    database: list,
    fltr=None,
    mask=None,
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

            # filters.extend([ws.either(*[ws.contains(field, v) for v in value])])
        else:
            filters = [a for a in filters if value in a[field]]

            # filters.append(ws.contains(field, value))

    if mask:
        for field, value in mask.items():
            if isinstance(value, list):
                for val in value:
                    filters = [f for f in filters if val not in f[field]]
                # filters.extend([ws.exclude(ws.contains(field, v)) for v in value])
            else:
                filters = [f for f in filters if value not in f[field]]
                # filters.append(ws.exclude(ws.contains(field, value)))

    return filters


def generate_sets_from_filters(yaml_filepath, database) -> dict:
    """
    Generate a dictionary with sets of activity names for
    technologies from the filter specifications.

    :param filtr:
    :func:`activity_maps.InventorySet._act_fltr`.
    :return: dictionary with the same keys as provided in filter
        and a set of activity data set names as values.
    :rtype: dict
    """

    filtr = _get_mapping(yaml_filepath, var="ecoinvent_aliases")

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

    # subset = list(
    #    ws.get_many(
    #        database,
    #        ws.either(*[ws.contains("name", name) for name in names]),
    #    )
    # )

    subset = [a for a in database if any(x in a["name"] for x in names)]

    techs = {
        tech: _act_fltr(subset, fltr.get("fltr"), fltr.get("mask"))
        for tech, fltr in filtr.items()
    }

    mapping = {tech: {act for act in actlst} for tech, actlst in techs.items()}

    return mapping


def _get_mapping(filepath, var):
    """
    Loa a YAML file and return a dictionary given a variable.
    :param filepath: YAML file path
    :param var: variable to return the dictionary for.
    :param model: if provided, only return the dictionary for this model.
    :return: a dictionary
    """

    with open(filepath, "r", encoding="utf-8") as stream:
        techs = yaml.full_load(stream)

    mapping = {}
    for key, val in techs.items():
        if var in val:
            mapping[key] = val[var]

    return mapping


# Example on how to call the functions to create a set of filtered activities_list
# set_from_fltrs = generate_sets_from_filters(yaml_filepath, database=ei39SSP)
