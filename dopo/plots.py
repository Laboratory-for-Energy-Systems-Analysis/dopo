# Imports
# -------

# common
import pandas as pd
import numpy as np

# plotting
import matplotlib.pyplot as plt
import seaborn as sns

# LEVEL 1
# -------
# Function for plotting: Level 1 dot plot with standard deviation
# and IQR range
# ------------------------------------------------------------------------------


def scores_across_activities(dataframes_dict: dict, title_key: str=None) -> None:
    """
    Plots the total score value for each activity sorted from largest
    to smallest. Visualizes IQR and standard deviation.
    Generates as many plots as methods were defined.

    :param dataframes_dict: dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param title_key: some string for the plot titles (e.g. sector name)

    """

    # Iterate over each dataframe and create individual plots
    for idx, df in dataframes_dict.items():
        # Create a new figure for each plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort the DataFrame in descending order based on the 'total' column
        sorted_df = df.sort_values(by="total", ascending=False)

        # Save the sorted index to order variable and call order variable in sns.swarmplot
        order = sorted_df.index.tolist()

        # Calculate statistics
        q1 = df["total"].quantile(0.25)
        q3 = df["total"].quantile(0.75)
        mean_gwp = df["total"].mean()
        std_gwp = df["total"].std()

        # Plot using seaborn swarmplot
        sns.swarmplot(
            data=df,
            x=df.index,
            y="total",
            dodge=True,
            ax=ax,
            order=order
        )

        # Add mean line
        ax.axhline(
            mean_gwp,
            color="grey",
            linestyle="--",
            linewidth=1,
            label="Mean"
        )

        # Add horizontal lines for Q1 and Q3
        ax.hlines(
            y=q3,
            xmin=-0.5,
            xmax=len(df) - 0.5,
            color="lightblue",
            linestyle="dotted",
            linewidth=1,
            label="Q3 (75th percentile)",
        )
        ax.hlines(
            y=q1,
            xmin=-0.5,
            xmax=len(df) - 0.5,
            color="lightblue",
            linestyle="dotted",
            linewidth=1,
            label="Q1 (25th percentile)",
        )

        # Add horizontal shading for areas above
        # and below 2 standard deviations from the mean
        ax.axhspan(
            mean_gwp - 2 * std_gwp,
            mean_gwp - 3 * std_gwp,
            color="grey",
            alpha=0.2,
            label=">2 std below mean",
        )
        ax.axhspan(
            mean_gwp + 2 * std_gwp,
            mean_gwp + 3 * std_gwp,
            color="grey",
            alpha=0.2,
            label=">2 std above mean",
        )

        # Add titles and labels
        ax.set_title(
            f"{str(title_key)} - {df['method'].iloc[0]} "
            f"in {df['method unit'].iloc[0]}"
        )
        ax.set_xlabel("Activity/ Dataset")
        ax.set_ylabel(f"{df['method unit'].iloc[0]}")

        # Rotate x-axis labels if needed
        ax.tick_params(axis="x", rotation=90)

        # Add legend
        ax.legend()

        # Generate the legend text using the first dataframe
        legend_text = generate_legend_text(dataframes_dict)

        # Add the legend text to the right of the plot
        plt.text(
            1.02,
            0.5,
            "\n".join(legend_text),
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=11,
            bbox=dict(facecolor="white", alpha=0.2, edgecolor="grey"),
        )

        # Show the plot
        plt.tight_layout()
        plt.show()


# LEVEL 2.1
# ---------
# Function for plotting: Level 2.1 Absolute stacked bar plots
# ------------------------------------------------------------


def inputs_contributions(dataframes_dict: dict, title_key: str = None) -> None:
    """
    Comparing activities and the input contributions to
    the total score by plotting a stacked absolute
    bar plot for each method.

    :param dataframes_dict: dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param title_key: some string for the plot titles
    """

    # Step 1: Collect all unique categories
    all_categories = set()

    for df in dataframes_dict.values():
        if "total" in df.columns:
            total_index = df.columns.get_loc("total")
            relevant_columns = df.columns[total_index + 1 :]
        else:
            relevant_columns = df.columns

        # Update all_categories set with relevant columns
        all_categories.update(relevant_columns)

    all_categories = list(all_categories)

    # Step 2: Create a consistent color palette and color map
    distinct_colors = generate_distinct_colors(len(all_categories))
    color_map = dict(zip(all_categories, distinct_colors))

    # Step 3: Plot each DataFrame
    for key, df in dataframes_dict.items():
        if "total" in df.columns:
            df_og = (
                df.copy()
            )  # for calling method and informative column in title and axis
            total_index = df.columns.get_loc("total")
            df = df.iloc[:, total_index + 1 :]

        # Create a new figure for each plot
        fig, ax = plt.subplots(figsize=(20, 10))

        # Ensure columns match the categories used in the color map
        df = df[[col for col in df.columns if col in color_map]]

        # Plotting the DataFrame with the custom color map
        df.plot(
            kind="bar",
            stacked=True,
            ax=ax,
            color=[color_map[col] for col in df.columns],
        )

        # Add titles and labels
        ax.set_title(
            f"{str(title_key)} - {df_og['method'].iloc[0]} "
            f"in {df_og['method unit'].iloc[0]}"
        )
        ax.set_xlabel("Activity/ Dataset")
        ax.set_ylabel(f"{df_og['method unit'].iloc[0]}")

        # First legend: Categories
        first_legend = ax.legend(
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize="small",
        )

        # Add the first legend manually
        ax.add_artist(first_legend)

        # Generate the legend text using the first dataframe
        legend_text = generate_legend_text(dataframes_dict)

        # Create a second legend below the first one
        fig.text(
            1.02,
            0.1,
            "\n".join(legend_text),
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="bottom",
            bbox=dict(facecolor="white", alpha=0.2, edgecolor="grey"),
        )

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=90, ha="right")

        # Adjust layout to make room for both legends
        plt.tight_layout()
        plt.subplots_adjust(right=0.75, bottom=0.2)

        # Display the plot
        plt.show()


# LEVEL 2.2
# ----------
# Function for plotting: Level 2.2 bar plot comparing one input characterized by one method across sector/ activity list
# ----------------------------------------------------------------------------------------------------------------------


def inputs_contribution(
    dataframes_dict: dict, dataframe_key: str, input_number: str
) -> None:
    """
    Comparing one specific cpc input among activities for each method.

    :param dataframes_dict:dictionary resulting from the function "compare_activities_multiple_methods" (and subsequently "small_inputs_to_other_column")
    :param dataframe_key: Key to access a specific DataFrame from the dictionary.
    :param input_number: Unique cpc identifier number of the input that should be plotted.
    """
    # Access the specific DataFrame
    df = dataframes_dict.get(dataframe_key)

    if df is None:
        print(f"No DataFrame found for key: {dataframe_key}")
        return

    # Filter columns based on the input_number
    columns_to_plot = [col for col in df.columns if str(input_number) in str(col)]

    if not columns_to_plot:
        print(f"No columns found containing input number: {input_number}")
        return

    # Plot the filtered columns
    ax = df[columns_to_plot].plot(kind="bar", figsize=(14, 6))
    plt.xlabel("Activity/ Dataset")
    plt.ylabel(f"{df['method unit'].iloc[0]}")
    plt.title(f"Comparison Plot for Input Number {input_number}")

    # Add legend for identifying activities_list from index
    # Generate the legend text using the first dataframe
    legend_text = generate_legend_text(dataframes_dict.get(dataframe_key))

    # Add the legend text to the right of the plot
    plt.text(
        1.02,
        0.5,
        "\n".join(legend_text),
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=11,
        bbox=dict(facecolor="white", alpha=0.2, edgecolor="grey"),
    )

    plt.show()


# LEVEL 2.3
# ---------
# Function for plotting: Level 2.3 bar plot comparing input not characterized across sector/ activity list
# --------------------------------------------------------------------------------------------------------


def input_contribution_across_activities(
    activities_list: list,
    input_type,
    input_number: str,
) -> None:
    """
    Comparing one specific cpc input among activities without method.

    :param activities_list: list of activities to plot inputs for. Perhabs the one defined at the beginning.
    :param input_type: type of the activities input default 'list', other 'dict'
    :param input_number: the cpc code of the input that is supposed to be plotted

    """
    cpc_input_dataframe = get_cpc_inputs_of_activities(activities_list, input_type)

    x_input_fltr = [
        x for x in cpc_input_dataframe.columns if str(input_number) in str(x)
    ][0]

    df = cpc_input_dataframe[x_input_fltr]

    df = df.sort_values(ascending=False)
    ax = df.plot(kind="bar", x=x_input_fltr, figsize=(14, 6))
    ax.set_xlabel("Activity/ Dataset")
    ax.set_ylabel(f"{cpc_input_dataframe['unit'].iloc[0]}")
    ax.set_title(f"Comparison Plot for not characterized Input - {x_input_fltr}")

    # Generate the legend text to map index to activity
    legend_text = generate_legend_text(cpc_input_dataframe)
    # Add the legend text to the right of the plot
    ax.text(
        1.02,
        0.5,
        "\n".join(legend_text),
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=11,
        bbox=dict(facecolor="white", alpha=0.2, edgecolor="grey"),
    )


# LEVEL 3
# --------
# Function for plotting: Level 3 S-curve difference of og database and premise adapted database by one meth
# ------------------------------------------------------------------------------------------------------------


def activities_across_databases(database, premise_database, method):
    """
    A function that plots the relative changes in activitiy LCA scores (for one defined method) between a "raw" ecoinvent database and a premise transformed ecoinvent database.

    :param database: an ecoinvent database or set of activities from an ecoinvent database.
    :premise_database: a premise transformed database or a set of activities which has intersections with the ecoinvent database.
    :method: a method the relative changes should be calculated and plotted for.

    """

    ecoinvent_scores = calculate_lca_ecoinvent_scores(database, method)
    premise_scores = calculate_lca_premise_scores(premise_database, method)

    relative_changes = calc_relative_changes(ecoinvent_scores, premise_scores)

    # Filter out entries where the value is a tuple (method)
    filtered_changes = {
        k: v for k, v in relative_changes.items() if not isinstance(v, tuple)
    }

    # Sort the relative changes by magnitude
    sorted_changes = sorted(filtered_changes.items(), key=lambda x: x[1])

    # Prepare data for plotting
    activities_list = [f"{key}" for key, _ in sorted_changes]
    changes = [change for _, change in sorted_changes]

    # Create the plot
    fig, ax = plt.subplots(
        figsize=(12, len(activities_list) * 0.4)
    )  # Adjust figure height based on number of activities_list
    fig.suptitle(f"Relative Changes in LCA Scores {relative_changes['method']}")
    y_pos = np.arange(len(activities_list))
    ax.barh(y_pos, changes, align="center", color="lightgrey", alpha=0.7)

    # Plot curve through datapoints
    ax.plot(changes, y_pos, color="darkblue", linewidth=2, marker="o", markersize=6)

    # Set labels and title
    ax.set_yticks(y_pos)
    ax.set_yticklabels(activities_list)
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel("Relative Change")


# Formatting
# ----------
# Level 1-2.3 plots dependency: Legend to map indexes on x-axis to activities
# ---------------------------------------------------------------------------------------


def generate_legend_text(data):
    """
    Maps the indexes on the x-axis to the activities to list them in a legend.

    :param data: it can take in a dictionary of dataframes or just a single dataframe
    """

    legend_text = []

    # Check if the input is a dictionary or a DataFrame
    if isinstance(data, dict):
        # Use the first DataFrame in the dictionary
        first_key = next(iter(data))
        df = data[first_key]
    elif isinstance(data, pd.DataFrame):
        # Use the input DataFrame directly
        df = data
    else:
        raise ValueError(
            "Input must be either a dictionary of DataFrames or a DataFrame"
        )

    # Create a list of tuples with (index, activity, location)
    items = [(str(i), row["activity"], row["location"]) for i, row in df.iterrows()]
    # Sort the items based on the index
    sorted_items = sorted(items, key=lambda x: x[0])
    # Add sorted items to legend_text
    for i, activity, location in sorted_items:
        legend_text.append(f"{i}: {activity} - {location}")
    return legend_text


# Level 2.1 plot dependencies: Function for formating plot: Unique colors for Level 2.1 Absolute stacked bar plots
# -----------------------------------------------------------------------------------


def generate_distinct_colors(n):
    """Generate n distinct colors using HSV color space."""
    hues = np.linspace(0, 1, n, endpoint=False)
    colors = [plt.cm.hsv(h) for h in hues]
    return colors
