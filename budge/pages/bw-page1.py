import os
import dash
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash_ag_grid.AgGrid import AgGrid
from plotly import graph_objects as go
import plotly.express as px
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
from budge.project import page1

from typing import Final

dash.register_page(__name__)
app: Dash = dash.get_app()


PAGE_TITLE = "Page One"


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

        self.numbers_operands: Final[str] = f"{prefix}_numbers_operands"
        self.operation: Final[str] = f"{prefix}_operation"
        self.a: Final[str] = f"{prefix}_a"
        self.b: Final[str] = f"{prefix}_b"
        self.c: Final[str] = f"{prefix}_c"
        self.c_container = f"{prefix}_c_div"


ids = PageIDs()

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
        html.Div(id=ids.input, className="px-6 pb-2 w-60"),
        html.Div(id=ids.save_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_save, className="px-6 pb-2 w-96"),
        html.Div(id=ids.run_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_run, className="px-6 pb-2 w-96"),
        html.Div(id=ids.output, className="px-6 pb-2 w-60"),
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

    page1_input = data.get("page1_input", {})
    page1_input, errors = page1.validate_input(page1_input)

    input_fields = html.Div(
        [
            html.H1(
                "Input",
                className="dash-h1",
            ),
            DropdownCustom(
                id=ids.numbers_operands,
                label="Numbers Operands",
                value=page1_input.get("numbers_operands", "two"),
                options=[
                    {"label": "Two", "value": "two"},
                    {"label": "Three", "value": "three"},
                ],
                error_message=errors.get("numbers_operands", ""),
            ).layout,
            DropdownCustom(
                id=ids.operation,
                options=[
                    {"label": "Add", "value": "addition"},
                    {"label": "Subtract", "value": "subtract"},
                    {"label": "Multiply", "value": "multiplication"},
                    {"label": "Divide", "value": "divide"},
                ],
                value=page1_input.get("operation", "addition"),
                label="Operation",
                error_message=errors.get("operation", ""),
            ).layout,
            InputCustom(
                id=ids.a,
                type="number",
                label="A",
                value=page1_input.get("a", 1),
                error_message=errors.get("a", ""),
            ).layout,
            InputCustom(
                id=ids.b,
                type="number",
                label="B",
                value=page1_input.get("b", 2),
                error_message=errors.get("b", ""),
            ).layout,
            html.Div(
                [
                    InputCustom(
                        id=ids.c,
                        type="number",
                        label="C",
                        value=page1_input.get("c", 3),
                        error_message=errors.get("c", ""),
                    ).layout,
                ],
                id=ids.c_container,
                style={"display": "none"},
            ),
        ]
    )

    save_btn = ButtonCustom(
        id=ids.save_btn,
        label="Save",
        color="bg-blue-500",
    ).layout

    return input_fields, save_btn


# callback function to display the input field c if numbers operands is three
@app.callback(
    Output(ids.c_container, "style"),
    [Input(ids.numbers_operands, "value")],
)
def display_c(value):

    if value == "three":
        return {"display": "block"}

    return {"display": "none"}


# callback function to save the input data to store on click of save button. Output to have store and save feedback
@app.callback(
    Output(STORE_ID, "data"),
    Output(ids.feedback_save, "children", allow_duplicate=True),
    Output(ids.feedback_run, "children", allow_duplicate=True),
    [Input(ids.save_btn, "n_clicks")],
    [
        State(ids.numbers_operands, "value"),
        State(ids.operation, "value"),
        State(ids.a, "value"),
        State(ids.b, "value"),
        State(ids.c, "value"),
        State(STORE_ID, "data"),
    ],
    prevent_initial_call=True,
)
def save_data(n_clicks, numbers_operands, operation, a, b, c, data):
    if n_clicks is None:
        raise PreventUpdate
    if n_clicks > 0:
        page1_input = {
            "numbers_operands": numbers_operands,
            "operation": operation,
            "a": a,
            "b": b,
            "c": c,
        }
        data["page1_input"] = page1_input
        data = page1.save_reset(data)
        return (
            data,
            MessageCustom(messages="Data saved successfully", success=True).layout,
            None,
        )
    else:
        raise PreventUpdate


# callback function to show the run button if data is valid and all inputs ready
@app.callback(
    Output(ids.run_container, "children"),
    [Input(STORE_ID, "data")],
)
def display_run_btn(data):
    if data is None:
        raise PreventUpdate

    all_inputs_ready, messages = page1.all_inputs_ready(data)
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

    is_ready, msg = page1.all_inputs_ready(data)
    if is_ready:
        try:
            data = page1.run_calculation(data)
            data = page1.run_reset(data)
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


# display the output of the calculation
@app.callback(
    Output(ids.output, "children"),
    [Input(STORE_ID, "data")],
    prevent_initial_call=True,
)
def display_output(data):
    if not data:
        return None
    page1_output = data.get("page1_output", None)

    if page1_output is None:
        return None

    page1_output = data.get("page1_output", {})

    return html.Div(
        [
            html.H1(
                "Output",
                className="dash-h1",
            ),
            DisplayField(
                id="output_field",
                label="Result",
                value=page1_output["result"],
            ).layout,
        ]
    )
