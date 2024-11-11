import os
import dash
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash_ag_grid.AgGrid import AgGrid
from collections import namedtuple
from typing import Final
import traceback
import math

from agility.components import (
    ButtonCustom,
    InputCustom,
    MessageCustom,
    DropdownCustom,
    CheckboxCustom,
    DisplayField,
    ContainerCustom,
)

from budge.config.main import STORE_ID
from budge.project import page2
from budge.schemas.page2 import Page2Input, generate_table_record

from typing import Final

dash.register_page(__name__)
app: Dash = dash.get_app()


PAGE_TITLE = "Page Two"


class PageIDs:
    def __init__(self) -> None:
        # Get the base name of the file where this instance is created
        filename = os.path.basename(__file__)
        # Remove the file extension to use only the file name as the prefix
        prefix: Final[str] = filename.replace(".py", "")
        self.prefix: Final[str] = prefix
        self.status: Final[str] = f"{prefix}_status"
        self.input: Final[str] = f"{prefix}_input"
        self.add_btn: Final[str] = f"{prefix}_add_btn"
        self.delete_btn: Final[str] = f"{prefix}_delete_btn"
        self.save_btn: Final[str] = f"{prefix}_save_btn"
        self.save_container: Final[str] = f"{prefix}_save_container"
        self.feedback_save: Final[str] = f"{prefix}_feedback_save"
        self.run_btn: Final[str] = f"{prefix}_run_btn"
        self.run_container: Final[str] = f"{prefix}_run_container"
        self.feedback_run: Final[str] = f"{prefix}_feedback_run"
        self.output: Final[str] = f"{prefix}_output"
        self.table_grid: Final[str] = f"{prefix}_table_grid"


ids = PageIDs()


table_columns = [
    {"field": "table_id", "headerName": "ID", "editable": False},
    {"field": "category", "headerName": "Category", "editable": True},
    {"field": "x", "headerName": "Col X", "editable": True},
    {"field": "y", "headerName": "Col Y", "editable": True},
]

layout = html.Div(
    [
        html.H1(
            "budge",
            className="app-title",
        ),
        html.H2(
            PAGE_TITLE,
            className="page-title",
        ),
        html.Hr(),
        html.Div(id=ids.status),
        html.Div(id=ids.input, className="px-6 pb-2"),
        html.Div(id=ids.save_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_save, className="px-6 pb-2 w-96"),
        html.Div(id=ids.run_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_run, className="px-6 pb-2 w-96"),
        html.Div(id=ids.output, className="px-6 pb-2 w-1/2"),
    ],
    className="w-full",
)


# callback function : if data in store is none then show project as not loaded in Div with id = "load_status" , show nothing otherwise
@app.callback(
    Output(ids.status, "children"),
    [Input(STORE_ID, "data")],
)
def load_status(data):

    if data is None:
        return MessageCustom(
            messages="Project not loaded. Go to start page and create new or open existing project.",
            success=False,
        ).layout


# callback function to display the input fields and save btn if project is loaded
@app.callback(
    Output(ids.input, "children"),
    Output(ids.save_container, "children"),
    [Input(STORE_ID, "data")],
)
def display_input(data):

    if data is None:
        raise PreventUpdate
    page2_input = data.get("page2_input", {})
    page2_input, errors = page2.validate_input(page2_input)
    table = page2_input.get("table", [])

    table_grid = AgGrid(
        id=ids.table_grid,
        columnDefs=table_columns,
        rowData=table,
        dashGridOptions={
            "rowHeight": 40,
            "editable": True,
            "rowSelection": "single",
        },
        defaultColDef={
            "editable": True,
            "sortable": True,
            "filter": True,
            "resizable": True,
        },
        style={"height": "300px", "width": "100%"},
    )

    add_btn = html.Button(
        [html.I(className="fas fa-plus")],
        id=ids.add_btn,
        className="bg-green-500 text-white p-1 w-12",
    )

    delete_btn = html.Button(
        [html.I(className="fas fa-trash")],
        id=ids.delete_btn,
        className="bg-red-500 text-white w-12",
    )

    save_btn = html.Button(
        [html.I(className="fas fa-save")],
        id=ids.save_btn,
        className="bg-blue-500 text-white w-12",
    )

    buttons = html.Div(
        [add_btn, delete_btn, save_btn], className="flex flex-row space-x-2"
    )

    return table_grid, buttons


# callback function to add record to table
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    [Input(ids.add_btn, "n_clicks")],
    [State(STORE_ID, "data")],
    prevent_initial_call=True,
)
def add_record(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate

    page2_input = data.get("page2_input", {})

    page2_input, errors = page2.validate_input(page2_input)
    table = page2_input.get("table", [])
    table.append(generate_table_record())
    page2_input["table"] = table
    data["page2_input"] = page2_input
    data = page2.save_reset(data)

    return data


# Callback function to delete record from table based on selected row
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    [Input(ids.delete_btn, "n_clicks")],
    [State(STORE_ID, "data"), State(ids.table_grid, "selectedRows")],
    prevent_initial_call=True,
)
def delete_record(n_clicks, data, selected_rows):
    if n_clicks is None or not selected_rows:
        raise PreventUpdate

    page2_input = data.get("page2_input", {})
    page2_input, errors = page2.validate_input(page2_input)
    table = page2_input.get("table", [])

    # Get the ID of the selected row
    selected_id = selected_rows[0]["table_id"]

    # Remove the selected row from the table
    table = [record for record in table if record["table_id"] != selected_id]

    page2_input["table"] = table
    data["page2_input"] = page2_input
    data = page2.save_reset(data)

    return data


# Callback function to update the data in the table with save button click
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    [Input(ids.save_btn, "n_clicks")],
    [State(ids.table_grid, "rowData"), State(STORE_ID, "data")],
    prevent_initial_call=True,
)
def save_table_data(n_clicks, row_data, data):
    if n_clicks is None:
        raise PreventUpdate

    page2_input = data.get("page2_input", {})
    page2_input, errors = page2.validate_input(page2_input)
    page2_input["table"] = row_data
    data["page2_input"] = page2_input
    data = page2.save_reset(data)

    return data


# callback function to show the run button if data is valid and all inputs ready
@app.callback(
    Output(ids.run_container, "children"),
    [Input(STORE_ID, "data")],
)
def display_run_btn(data):
    if data is None:
        raise PreventUpdate

    all_inputs_ready, messages = page2.all_inputs_ready(data)
    if all_inputs_ready:
        run_btn = ButtonCustom(
            id=ids.run_btn,
            label="Run",
            color="bg-purple-500",
        ).layout
        return run_btn
    else:
        return MessageCustom(messages=messages, success=False).layout


# perform the calculation
# callback function to run the calculation on click of run button
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    Output(ids.feedback_run, "children"),
    Output(ids.feedback_save, "children"),
    [Input(ids.run_btn, "n_clicks")],
    [State(STORE_ID, "data")],
    prevent_initial_call=True,
)
def run_calculation(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate
    message = []

    is_ready, msg = page2.all_inputs_ready(data)
    if is_ready:
        try:
            data = page2.run_calculation(data)
            data = page2.run_reset(data)
            msg = "Page calculation successfull"
            feedback_html = MessageCustom(messages=msg, success=True).layout
            return data, feedback_html, None
        except Exception as e:
            traceback.print_exc()
            message.append("Failure in Page Calculations")
            message.append(f"Error: {str(e)}")
            feedback_html = MessageCustom(messages=message, success=False).layout
            return data, feedback_html, None
    else:
        message.append(msg)
        feedback_html = MessageCustom(messages=message, success=False).layout
        return data, feedback_html, None


# Callback function to display the result table in page2_output in data
@app.callback(
    Output(ids.output, "children"),
    [Input(STORE_ID, "data")],
)
def display_output(data):
    if data is None:
        return None
    fig = page2.plot_results(data)
    if fig is None:
        return None
    fig_html = dcc.Graph(figure=fig)
    return fig_html
