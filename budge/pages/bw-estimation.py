import sys
import os
import pandas as pd
import dash
from dash import Dash, html, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_ag_grid.AgGrid import AgGrid
import traceback
from collections import namedtuple
import numpy as np
from agility.components import (
    ButtonCustom,
    DropdownCustom,
    InputCustom,
    MessageCustom,
    DisplayField,
)

from budge.config.main import STORE_ID, PROJECT_NAME, DATA_STORE
from budge.project import estimation


dash.register_page(__name__)
app: Dash = dash.get_app()

from typing import Final


class PageIDs:
    def __init__(self):
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

        self.method_dropdown: Final[str] = f"{prefix}_method_dropdown"
        self.plant_dropdown: Final[str] = f"{prefix}_plant_dropdown"
        self.equipment_dropdown: Final[str] = f"{prefix}_equipment_dropdown"
        self.equipment_type_dropdown: Final[str] = f"{prefix}_equipment_type_dropdown"
        self.sizing_quantity_input: Final[str] = f"{prefix}_sizing_quantity_input"
        self.purchased_equipment_cost_output: Final[str] = (
            f"{prefix}_purchased_equipment_cost_output"
        )
        self.total_cost_output: Final[str] = f"{prefix}_total_cost_output"


ids = PageIDs()

PAGE_TITLE = "Capital Cost Estimation"

layout = html.Div(
    [
        html.H1(
            "BudgeWiser",
            className="app-title",
        ),
        html.H2(
            PAGE_TITLE,
            className="page-title",
        ),
        html.Hr(),
        html.Div(id=ids.status),
        html.Div(id=ids.input, className="px-6 pb-2 w-100"),
        html.Div(id=ids.save_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_save, className="px-6 pb-2 w-96"),
        html.Div(id=ids.run_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_run, className="px-6 pb-2 w-96"),
        html.Div(id=ids.output, className="px-6 pb-2 w-60"),
    ],
    className="w-full",
)


# Callback to check if the project is loaded
@app.callback(
    Output(ids.status, "children"),
    Input(STORE_ID, "data"),
)
def load_status(data):
    if data is None:
        return MessageCustom(
            messages="Project not loaded. Go to start page and create new or open existing project.",
            success=False,
        ).layout


# Callback to display the input fields and save button
@app.callback(
    Output(ids.input, "children"),
    Output(ids.save_container, "children"),
    Input(STORE_ID, "data"),
    State(DATA_STORE, "data"),
)
def display_input(data, material_data):

    if data is None:
        raise PreventUpdate

    estimation_input = data.get("estimation_input", {})
    estimation_input, errors = estimation.validate_input(estimation_input)
    df = pd.DataFrame(material_data)

    input_fields = html.Div(
        [
            html.H1("Input", className="dash-h1"),
            DropdownCustom(
                id=ids.method_dropdown,
                label="Select Method",
                value=estimation_input.get("method", "Select a costing method"),
                options=[
                    {"label": method, "value": method}
                    for method in df["method"].unique()
                ],
                error_message=errors.get("method", ""),
            ).layout,
            DropdownCustom(
                id=ids.plant_dropdown,
                label="Select Plant Type",
                value=estimation_input.get("plant", ""),
                options=[],
                error_message=errors.get("plant", ""),
            ).layout,
            DropdownCustom(
                id=ids.equipment_dropdown,
                label="Select Equipment",
                value=estimation_input.get("equipment", ""),
                options=[],
                error_message=errors.get("equipment", ""),
            ).layout,
            DropdownCustom(
                id=ids.equipment_type_dropdown,
                label="Select specific equipment type:",
                value=estimation_input.get("equipment_type", ""),
                options=[],
                error_message=errors.get("equipment_type", ""),
            ).layout,
            InputCustom(
                id=ids.sizing_quantity_input,
                type="number",
                label="Sizing Quantity",
                value=estimation_input.get("sizing_value", 0),
                error_message=errors.get("sizing_value", ""),
            ).layout,
        ]
    )

    save_btn = ButtonCustom(
        id=ids.save_btn,
        label="Save",
        color="bg-blue-500",
    ).layout

    return input_fields, save_btn


# Callbacks to update options based on selections
@app.callback(
    Output(ids.plant_dropdown, "options"),
    Input(ids.method_dropdown, "value"),
    State(DATA_STORE, "data"),
)
def update_plant_options(method_choice, material_data):
    if method_choice:
        df = pd.DataFrame(material_data)
        plant_types = df[df["method"] == method_choice]["plant_type"].dropna().unique()
        return [{"label": plant, "value": plant} for plant in plant_types]
    return []


@app.callback(
    Output(ids.equipment_dropdown, "options"),
    Input(ids.plant_dropdown, "value"),
    State(DATA_STORE, "data"),
)
def update_equipment_options(plant_choice, material_data):
    if plant_choice:
        df = pd.DataFrame(material_data)
        equipment_types = (
            df[df["plant_type"] == plant_choice]["equipment"].dropna().unique()
        )
        return [
            {"label": equipment, "value": equipment} for equipment in equipment_types
        ]
    return []


@app.callback(
    Output(ids.equipment_type_dropdown, "options"),
    [
        Input(ids.method_dropdown, "value"),
        Input(ids.plant_dropdown, "value"),
        Input(ids.equipment_dropdown, "value"),
    ],
    State(DATA_STORE, "data"),
)
def update_equipment_type_options(
    method_choice, plant_choice, equipment_choice, material_data
):
    if method_choice and plant_choice and equipment_choice:
        specific_types = (
            estimation.filter_material_data(
                material_data, method_choice, plant_choice, equipment_choice
            )["equipment_type"]
            .dropna()
            .unique()
        )

        # specific_types = df[(df['method'] == method_choice) &
        #                     (df['plant_type'] == plant_choice) &
        #                     (df['equipment'] == equipment_choice)]['equipment_type'].dropna().unique()
        return [
            {"label": equipment_type, "value": equipment_type}
            for equipment_type in specific_types
        ]
    return []


# Update Sizing Label and Input Placeholder based on selected specific equipment type
@app.callback(
    Output(ids.sizing_quantity_input, "placeholder"),
    [
        Input(ids.method_dropdown, "value"),
        Input(ids.plant_dropdown, "value"),
        Input(ids.equipment_dropdown, "value"),
        Input(ids.equipment_type_dropdown, "value"),
    ],
    State(DATA_STORE, "data"),
)
def update_sizing_label(
    method_choice, plant_choice, equipment_choice, type_choice, material_data
):
    if method_choice and plant_choice and equipment_choice and type_choice:
        selected_row = estimation.filter_material_data(
            material_data, method_choice, plant_choice, equipment_choice, type_choice
        )
        selected_row = selected_row.iloc[0]

        sizing_quantity = selected_row["sizing_quantity"]
        units = selected_row["units"]
        s_lower = selected_row["s_lower"]
        s_upper = selected_row["s_upper"]

        if np.isnan(s_lower) or np.isnan(s_upper):
            placeholder = f"Enter {sizing_quantity} in {units}"
        else:
            placeholder = (
                f"Enter {sizing_quantity} in {units} between {s_lower} and {s_upper}"
            )
        return placeholder
    return "Enter sizing value"


# Callback to save data
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    Output(ids.feedback_save, "children", allow_duplicate=True),
    Output(ids.feedback_run, "children", allow_duplicate=True),
    [
        Input(ids.save_btn, "n_clicks"),
        State(ids.method_dropdown, "value"),
        State(ids.plant_dropdown, "value"),
        State(ids.equipment_dropdown, "value"),
        State(ids.equipment_type_dropdown, "value"),
        State(ids.sizing_quantity_input, "value"),
        State(STORE_ID, "data"),
    ],
    prevent_initial_call=True,
)
def save_data(n_clicks, method, plant, equipment, equipment_type, sizing_value, data):

    if n_clicks is None:
        raise PreventUpdate
    estimation_input = {
        "method": method,
        "plant": plant,
        "equipment": equipment,
        "equipment_type": equipment_type,
        "sizing_value": sizing_value,
    }
    data["estimation_input"] = estimation_input

    print(data)

    data = estimation.save_reset(data)
    return (
        data,
        MessageCustom(messages="Data saved successfully", success=True).layout,
        None,
    )


# Callback to display the run button if inputs are valid
@app.callback(
    Output(ids.run_container, "children"),
    Input(STORE_ID, "data"),
)
def display_run_btn(data):
    if data is None:
        raise PreventUpdate

    all_inputs_ready, messages = estimation.all_inputs_ready(data)
    if all_inputs_ready:
        run_btn = ButtonCustom(
            id=ids.run_btn,
            label="Run",
            color="bg-purple-500",
        ).layout
        return run_btn
    else:
        return MessageCustom(messages=messages, success=False).layout


# Callback to run calculations
@app.callback(
    Output(STORE_ID, "data", allow_duplicate=True),
    Output(ids.feedback_run, "children"),
    Output(ids.feedback_save, "children"),
    Input(ids.run_btn, "n_clicks"),
    State(STORE_ID, "data"),
    State(DATA_STORE, "data"),
    prevent_initial_call=True,
)
def run_calculation(n_clicks, data, material_data):
    if n_clicks is None:
        raise PreventUpdate
    message = []

    is_ready, msgs = estimation.all_inputs_ready(data)

    if is_ready:
        try:
            data = estimation.run_calculation(data, material_data)
            data = estimation.run_reset(data)
            msg = "Calculation successful"
            feedback_html = MessageCustom(messages=msg, success=True).layout
            return data, feedback_html, None
        except Exception as e:
            traceback.print_exc()
            message.append("Failure in Calculations")
            message.append(f"Error: {str(e)}")
            feedback_html = MessageCustom(messages=message, success=False).layout
            return data, feedback_html, None
    else:
        message.extend(msgs)
        feedback_html = MessageCustom(messages=message, success=False).layout
        return data, feedback_html, None


# Callback to display the output
@app.callback(
    Output(ids.output, "children"),
    Input(STORE_ID, "data"),
    prevent_initial_call=True,
)
def display_output(data):
    if not data:
        return None
    page3_output = data.get("page3_output", None)

    if page3_output is None:
        return None
    page3_output = data.get("page3_output", {})

    return html.Div(
        [
            html.H1(
                "Output",
                className="dash-h1",
            ),
            DisplayField(
                id=ids.purchased_equipment_cost_output,
                label="Purchased Equipment Cost",
                value=page3_output["purchased_cost_output"],
            ).layout,
            DisplayField(
                id=ids.total_cost_output,
                label="Total Fixed Capital Cost",
                value=page3_output["total_cost_output"],
            ).layout,
        ]
    )
