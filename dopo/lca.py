"""
Generates and saves Life Cycle Assessment (LCA) scores plots for various sectors.

The module computes LCA scores for activities and methods.
"""

from bw2analyzer.comparisons import group_leaves, commonprefix, get_value_for_cpc
import operator
import tabulate
import bw2data as bd
from bw2calc import __version__ as bc_version
import bw2calc as bc
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

if isinstance(bc_version, str):
    bc_version = tuple(map(int, bc_version.split(".")))


def sector_lca_scores(sectors, methods, cutoff=0.01) -> dict:
    """
    Generates LCA score tables for each sector's activity list, including total scores and CPC 
    input contributions.

    This function calculates LCA scores for activities within each sector using methods specified 
    in the `method_dict`. Inputs below or equal to the `cutoff` value are summarized in an "other" 
    column.

    :param sectors: A dictionary where keys are sector names and values are lists of activities.
    :type sectors: dict
    :param methods: A list of methods to use for LCA calculations.
    :type methods: list
    :param cutoff: A threshold value for summarizing inputs below or equal to this value in an "other" column.
    :type cutoff: float, optional
    :return: A dictionary where each key is a sector name and each value is a DataFrame containing LCA scores.
    :rtype: dict
    """

    results, cache = {}, {}

    # Loop through each sector in scores_dict
    for sector, activities in sectors.items():
        results[sector] = {}
        
        # Calculate LCA scores using the specified methods
        scores = _compare_activities_multiple_methods(
            activities=activities,
            methods=methods,
            cutoff=cutoff,
            cache=cache
        )

        # turn lca_scores into a long tables
        scores = scores.melt(
            id_vars=['activity', 'product', 'database', 'location', 'unit', 'method', 'method unit',],
            var_name='input',
            value_name='score'
        )

        # Apply cutoff to summarize small inputs in an "other" column
        scores = _agg_small_inputs(scores, cutoff)
        
        # Save the LCA scores to the scores_dict
        results[sector] = scores

    return results


def _compare_activities_multiple_methods(
    activities: list,
    methods: list,
    output_format: str ="pandas",
    mode: str ="absolute",
    cutoff: float = 0.01,
    cache=None
) -> pd.DataFrame:
    """
    Compares a list of activities using multiple LCA methods and stores the results in a dictionary 
    of DataFrames.

    This function generates comparison results for each method in `methods`, formats them into 
    DataFrames, and organizes them in a dictionary where the keys are method-specific names derived 
    from the `identifier` and method details. Each DataFrame contains total scores and input 
    contributions, with columns ordered and indexed appropriately.

    :param activities: A list of activities to compare.
    :type activities: list
    :param methods: A list of methods to use for comparison.
    :type methods: list
    :param output_format: The format of the output DataFrame.
    :type output_format: str, optional
    :param mode: The mode of the comparison.
    :type mode: str, optional
    :return: A pandas DataFrame containing LCA scores.
    :rtype: pd.DataFrame
    """
    dataframe = pd.DataFrame()

    for method in methods: # method_key is not called, but necessary
        # Perform the comparison using the Brightway2 analyzer
        result, cache = compare_activities_by_grouped_leaves(
            activities,
            method,
            output_format=output_format,
            mode=mode,
            max_level=1,
            cutoff=cutoff,
            cache=cache
        )

        # Add method and method unit columns to the DataFrame
        result["method"] = "-".join(method)
        result["method unit"] = bd.Method(method).metadata["unit"]

        # Reorder columns to place 'method' and 'method unit' after 'unit'
        columns = result.columns.tolist()
        columns = columns[:2] + columns[-2:] + columns[2:-2]
        result = result[columns]

        # Sort rows by 'total' column and reset index
        result = result.sort_values('total').reset_index(drop=True)

        # Store the result DataFrame in the dictionary
        dataframe = pd.concat([dataframe, result], axis=0)

    return dataframe

def _agg_small_inputs(dataframe, cutoff=0.01):
    """
    Aggregates small inputs in a DataFrame into an "other" input category.

    This function calculates the sum of scores for each group of activities and then calculates the
    percentage for each row. Rows with less than the specified cutoff percentage are labeled as
    "Other". The function then groups the DataFrame by the same columns and 'input' to aggregate
    scores.

    :param dataframe: A DataFrame containing LCA scores for activities.
    :type dataframe: pandas DataFrame
    :param cutoff: A threshold value for summarizing inputs below or equal to this value in an "other" column.
    :type cutoff: float, optional
    :return: A DataFrame with aggregated scores.
    :rtype: pandas DataFrame
    """


    # remove rows with 'total' in the input column
    dataframe = dataframe[~dataframe['input'].str.contains("total")]


    # First, we will calculate the sum of scores for each group
    group_columns = ['activity', 'product', 'location', 'database', 'method', 'method unit']
    dataframe.loc[:, 'total_score'] = dataframe.groupby(group_columns)['score'].transform('sum').copy()

    # Next, calculate the percentage for each row
    dataframe.loc[:, 'percentage'] = dataframe.loc[:, 'score'] / dataframe.loc[:, 'total_score']

    # Now, create a condition where rows with less than 1% are considered "Other"
    dataframe.loc[:, 'input'] = dataframe.apply(lambda x: 'Other' if x['percentage'] < cutoff else x['input'], axis=1)
    # Remove HS code from labels
    dataframe.loc[:, "input"] = dataframe.apply(lambda x: x["input"].split(": ")[-1][:45], axis=1)

    # After labeling "Other", we will group again by the same columns but also by 'input' to aggregate scores
    aggregated_df = dataframe.groupby(group_columns + ['input'], as_index=False).agg({'score': 'sum'})

    # Remove rows with zero values
    aggregated_df = aggregated_df.loc[aggregated_df["score"] != 0, :]


    return aggregated_df

def compare_activities_by_grouped_leaves(
    activities,
    lcia_method,
    mode="relative",
    max_level=4,
    cutoff=7.5e-3,
    output_format="list",
    str_length=50,
    cache=None
):
    """Compare activities by the impact of their different inputs, aggregated by the product classification of those inputs.

    Args:
        activities: list of ``Activity`` instances.
        lcia_method: tuple. LCIA method to use when traversing supply chain graph.
        mode: str. If "relative" (default), results are returned as a fraction of total input. Otherwise, results are absolute impact per input exchange.
        max_level: int. Maximum level in supply chain to examine.
        cutoff: float. Fraction of total impact to cutoff supply chain graph traversal at.
        output_format: str. See below.
        str_length; int. If ``output_format`` is ``html``, this controls how many characters each column label can have.

    Raises:
        ValueError: ``activities`` is malformed.

    Returns:
        Depends on ``output_format``:

        * ``list``: Tuple of ``(column labels, data)``
        * ``html``: HTML string that will print nicely in Jupyter notebooks.
        * ``pandas``: a pandas ``DataFrame``.

    """

    lca = bc.LCA({act: 1 for act in activities}, lcia_method)
    lca.lci(factorize=True)
    lca.lcia()

    objs = []

    activities_to_exclude_from_cache = [
        (lcia_method, a["database"], a["code"])
        for a in activities
    ]

    for act in activities:
        leaves, cache = find_leaves(
                activity=act,
                lcia_method=lcia_method,
                max_level=max_level,
                cutoff=cutoff,
                lca_obj=lca,
                cache=cache,
                activities_to_exclude_from_cache=activities_to_exclude_from_cache
            )

        grouped_leaves = group_leaves(leaves)

        objs.append(
            grouped_leaves
        )

    sorted_keys = sorted(
        [
            (max([el[0] for obj in objs for el in obj if el[2] == key]), key)
            for key in {el[2] for obj in objs for el in obj}
        ],
        reverse=True,
    )

    labels = [
        "activity",
        "product",
        "database",
        "location",
        "unit",
        "total",
        "Direct emissions",
    ] + [key for _, key in sorted_keys]
    data = []
    for act, lst in zip(activities, objs):
        if bc_version >= (2, 0, 0):
            lca.lcia({act.id: 1})
        else:
            lca.redo_lcia({act: 1})
        data.append(
            [
                act["name"],
                act.get("reference product", ""),
                act["database"],
                act.get("location", "")[:25],
                act.get("unit", ""),
                lca.score,
            ]
            + [
                (
                    lca.characterization_matrix
                    * lca.biosphere_matrix
                    * lca.demand_array
                ).sum()
            ]
            + [get_value_for_cpc(lst, key) for _, key in sorted_keys]
        )

    data.sort(key=lambda x: x[4], reverse=True)

    if mode == "relative":
        for row in data:
            for index, point in enumerate(row[5:]):
                row[index + 5] = point / row[4]

    if output_format == "list":
        return labels, data
    elif output_format == "pandas":
        return pd.DataFrame(data, columns=labels), cache
    elif output_format == "html":
        return tabulate.tabulate(
            data,
            [x[:str_length] for x in labels],
            tablefmt="html",
            floatfmt=".3f",
        )

def find_leaves(
    activity,
    lcia_method,
    results=None,
    lca_obj=None,
    amount=1,
    total_score=None,
    level=0,
    max_level=3,
    cutoff=2.5e-2,
    cache=None,
    activities_to_exclude_from_cache=None
):
    """Traverse the supply chain of an activity to find leaves - places where the impact of that
    component falls below a threshold value.

    Returns a list of ``(impact of this activity, amount consumed, Activity instance)`` tuples."""
    first_level = results is None

    activity = bd.get_activity(activity)

    k = (lcia_method, activity["database"], activity["code"])

    if first_level:
        level = 0
        results = []

        total_score = lca_obj.score
        if k not in activities_to_exclude_from_cache:
            cache[k] = lca_obj.score
    else:
        if k not in cache:
            if bc_version >= (2, 0, 0):
                lca_obj.lcia({activity.id: amount})
            else:
                lca_obj.redo_lcia({activity: amount})
            if k not in activities_to_exclude_from_cache:
                cache[k] = lca_obj.score
            sub_score = lca_obj.score
        else:
            sub_score = cache[k]

        # If this is a leaf, add the leaf and return
        if abs(sub_score) <= abs(total_score * cutoff) or level >= max_level:

            # Only add leaves with scores that matter
            if abs(sub_score) > abs(total_score * 1e-4):
                results.append((sub_score, amount, activity))

            return results, cache

        else:
            # Add direct emissions from this demand
            direct = (
                    lca_obj.characterization_matrix
                    * lca_obj.biosphere_matrix
                    * lca_obj.demand_array
            ).sum()
            if abs(direct) >= abs(total_score * 1e-4):
                results.append((direct, amount, activity))

    for exc in activity.technosphere():
        _, cache = find_leaves(
            activity=exc.input,
            lcia_method=lcia_method,
            results=results,
            lca_obj=lca_obj,
            amount=amount * exc["amount"],
            total_score=total_score,
            level=level + 1,
            max_level=max_level,
            cutoff=cutoff,
            cache=cache,
            activities_to_exclude_from_cache=activities_to_exclude_from_cache
        )

    return sorted(results, reverse=True), cache


