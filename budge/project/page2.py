import pandas as pd
from plotly import graph_objects as go
import plotly.express as px

from agility.utils.pydantic import validate_data
from budge.schemas.page2 import Page2Input


def validate_input(page_input):
    """
    Check if the page_input data is valid.
    """
    page_input, errors = validate_data(page_input, Page2Input)
    return page_input, errors


def all_inputs_ready(data):
    msgs = []
    ready = True
    if not data or "page2_input" not in data:
        message = "Missing Page 2 input in data"
        msgs.append(message)
        ready = False

    page2_input = data["page2_input"]
    page2_input, page2_errors = validate_input(page2_input)

    # set ready to false if there are errors
    if page2_errors:
        ready = False
        msgs.append("Page 2 Inputs Invalid")

    """
    if not "page1_input" in data:
        message = "Missing Page 1 input in data"
        msgs.append(message)
        ready = False
  
    page1_input = data["page1_input"]
    page1_input, page1_errors = validate_page1_input(page1_input)

  
    if page1_errors:
        message = "Page 1 Inputs Invalid"
        msgs.append(message)
        ready = False
    """

    return ready, msgs


def run_calculation(data):
    page2_input = data["page2_input"]
    table = page2_input["table"]
    table_df = pd.DataFrame(table)

    # Define all possible categories
    all_categories = pd.DataFrame({"category": ["A", "B", "C"]})

    # Group by 'category' and calculate the sum of 'x' and 'y' for each category
    result_df = table_df.groupby("category").sum().reset_index()

    # Merge with all possible categories to ensure all categories are present
    result_df = all_categories.merge(result_df, on="category", how="left").fillna(0)

    # Convert the resulting DataFrame back to a dictionary
    result = result_df.to_dict(orient="records")

    page2_output = {}
    page2_output["result"] = result
    data["page2_output"] = page2_output
    return data


def save_reset(data):
    try:
        data.pop("page2_output")
        data = run_reset(data)
    except KeyError:
        pass
    return data


def run_reset(data):
    try:
        data.pop("report")
    except KeyError:
        pass
    return data


def plot_results(data):
    page2_output = data.get("page2_output", {})
    result = page2_output.get("result", [])
    if not result:
        return None

    result_df = pd.DataFrame(result)
    fig = px.bar(result_df, x="category", y="x", color="category")

    fig.update_layout(
        title="Category wise X values",
        xaxis_title="Category",
        yaxis_title="X",
        legend_title="Category",
        xaxis=dict(
            type="category", categoryorder="array", categoryarray=["A", "B", "C"]
        ),
    )

    return fig
