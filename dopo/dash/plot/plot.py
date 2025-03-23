import plotly.graph_objects as go
import pandas as pd


def prepare_dataframe(df, sector, impact):
    # Select the initial filtered data for the first sector and method
    filtered_data = df[sector]

    if not isinstance(impact, str):
        impact = str(impact)

    filtered_data = pd.DataFrame.from_dict(filtered_data)
    filtered_data = filtered_data.loc[
        (filtered_data["method"] == "-".join(list(eval(impact)))), :
    ]

    # Add a descriptive name to each entry for the plot
    filtered_data["name"] = filtered_data.apply(
        lambda x: f"{x['activity']} - {x['location']} - {x['database']}", axis=1
    )

    return filtered_data


def contribution_plot(df, sector, impact_assessment):
    fig = go.Figure()
    for input_name in df["input"].unique():
        input_data = df[df["input"] == input_name]
        fig.add_trace(
            go.Bar(x=input_data["name"], y=input_data["score"], name=input_name)
        )

    # Update layout for stacked bar plot
    fig.update_layout(
        barmode="stack",
        title=f"{sector} analysis - {impact_assessment}",
        xaxis_title="Activity",
        yaxis_title=input_data["method unit"].iloc[0],
        legend_title="Input",
        height=700,
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white'
    )

    return fig

def scores_plot(df, sector, impact_assessment):
    """
    Scatter plot of scores for each activity in the sector.
    Add a line for the average score.
    Add a line for standard deviation above and below the average score.
    """

    fig = go.Figure()


    df = df[["name", "score", "method unit"]].groupby(["name", "method unit"]).sum().reset_index()

    # Add scatter plot of scores (the sum of all inputs)
    fig.add_trace(
        go.Scatter(x=df["name"], y=df["score"], mode='markers', name='Score', marker=dict(size=12))
    )

    # Add average score line
    avg_score = df["score"].mean()
    fig.add_trace(
        go.Scatter(x=df["name"], y=[avg_score]*len(df), mode='lines', name='Average', line=dict(color='black', width=2))
    )

    # Add median score line
    median_score = df["score"].median()
    fig.add_trace(
        go.Scatter(x=df["name"], y=[median_score]*len(df), mode='lines', name='Median', line=dict(color='green', width=2))
    )

    # Add standard deviation lines
    std_dev = df["score"].std()
    fig.add_trace(
        go.Scatter(x=df["name"], y=[avg_score + std_dev]*len(df), mode='lines', name='Average + Std Dev', line=dict(color='blue', width=2))
    )
    fig.add_trace(
        go.Scatter(x=df["name"], y=[avg_score - std_dev]*len(df), mode='lines', name='Average - Std Dev', line=dict(color='blue', width=2))
    )

    # Add 5th percentile line
    percentile_5 = df["score"].quantile(0.05)
    fig.add_trace(
        go.Scatter(x=df["name"], y=[percentile_5]*len(df), mode='lines', name='5th Percentile', line=dict(color='red', width=2))
    )

    # Add 95th percentile line
    percentile_95 = df["score"].quantile(0.95)
    fig.add_trace(
        go.Scatter(x=df["name"], y=[percentile_95]*len(df), mode='lines', name='95th Percentile', line=dict(color='red', width=2))
    )

    # Update layout for scatter plot
    fig.update_layout(
        title=f"{sector} analysis - {impact_assessment}",
        xaxis_title="Activity",
        yaxis_title=df["method unit"].iloc[0],
        legend_title="Input",
        height=700,
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white'
    )

    return fig
