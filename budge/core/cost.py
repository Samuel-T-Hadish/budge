import os
import traceback
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from agility.components import ButtonCustom, DropdownCustom, InputCustom, MessageCustom, DisplayField
from pydantic import BaseModel, field_validator
from typing import Final

# Initialize Dash app
app = Dash(__name__)

df = pd.read_csv("data.csv", encoding='ISO-8859-1')

# Page identifiers
class PageIDs:
    def __init__(self):
        prefix = "cost_estimation"
        self.prefix = prefix
        self.status = f"{prefix}_status"
        self.input = f"{prefix}_input"
        self.save_btn = f"{prefix}_save_btn"
        self.run_btn = f"{prefix}_run_btn"
        self.output = f"{prefix}_output"
        self.method_dropdown = f"{prefix}_method_dropdown"
        self.plant_dropdown = f"{prefix}_plant_dropdown"
        self.equipment_dropdown = f"{prefix}_equipment_dropdown"
        self.equipment_type_dropdown = f"{prefix}_equipment_type_dropdown"
        self.sizing_quantity_input = f"{prefix}_sizing_quantity_input"
        self.method_dropdown: Final[str] = f"{prefix}_method_dropdown"
        self.plant_dropdown: Final[str] = f"{prefix}_plant_dropdown"
        self.equipment_dropdown: Final[str] = f"{prefix}_equipment_dropdown"
        self.equipment_type_dropdown: Final[str] = f"{prefix}_equipment_type_dropdown"
        self.sizing_quantity_label: Final[str] = f"{prefix}_sizing_quantity_label"
        self.sizing_quantity_input: Final[str] = f"{prefix}_sizing_quantity_input"
        self.purchased_equipment_cost_output: Final[str] = f"{prefix}_purchased_equipment_cost_output"
        self.total_cost_output: Final[str] = f"{prefix}_total_cost_output"

ids = PageIDs()

app.layout = html.Div(
    [
        html.H1("Cost Estimation App", className="app-title"),
        html.Div(id=ids.status),
        html.Div(id=ids.input),
        html.Div(id=ids.output),
    ],
)

# Data validation with Pydantic
class CostEstimationInput(BaseModel):
    method: str
    plant_type: str
    equipment: str
    equipment_type: str
    sizing_quantity: float

    @field_validator('method', 'plant_type', 'equipment', 'equipment_type')
    def must_not_be_empty(cls, value):
        if not value:
            raise ValueError("Field cannot be empty.")
        return value

    @field_validator('sizing_quantity')
    def valid_sizing_quantity(cls, value):
        if value <= 0:
            raise ValueError("Sizing quantity must be positive.")
        return value

# Load input fields based on selections
@app.callback(
    Output(ids.input, "children"),
    Input(ids.method_dropdown, "value"),
    Input(ids.plant_dropdown, "value"),
    Input(ids.equipment_dropdown, "value"),
)
def display_input_fields(selected_method, selected_plant, selected_equipment):
    method_options = [{"label": m, "value": m} for m in df['method'].unique()]
    plant_options = [{"label": p, "value": p} for p in df[df['method'] == selected_method]['plant_type'].unique()]
    equipment_options = [{"label": e, "value": e} for e in df[df['plant_type'] == selected_plant]['equipment'].unique()]
    equipment_type_options = [{"label": t, "value": t} for t in df[(df['method'] == selected_method) & 
                                                                  (df['plant_type'] == selected_plant) & 
                                                                  (df['equipment'] == selected_equipment)]['type'].unique()]
    
    return html.Div([
        DropdownCustom(id=ids.method_dropdown, label="Select Method", options=method_options).layout,
        DropdownCustom(id=ids.plant_dropdown, label="Select Plant Type", options=plant_options).layout,
        DropdownCustom(id=ids.equipment_dropdown, label="Select Equipment", options=equipment_options).layout,
        DropdownCustom(id=ids.equipment_type_dropdown, label="Select Equipment Type", options=equipment_type_options).layout,
        InputCustom(id=ids.sizing_quantity_input, type="number", label="Sizing Quantity").layout,
        ButtonCustom(id=ids.save_btn, label="Save", color="bg-blue-500").layout,
    ])

# Save input data and validate
@app.callback(
    Output("store_data", "data"),
    Output(ids.status, "children"),
    Input(ids.save_btn, "n_clicks"),
    State(ids.method_dropdown, "value"),
    State(ids.plant_dropdown, "value"),
    State(ids.equipment_dropdown, "value"),
    State(ids.equipment_type_dropdown, "value"),
    State(ids.sizing_quantity_input, "value"),
    prevent_initial_call=True
)
def save_data(n_clicks, method, plant_type, equipment, equipment_type, sizing_quantity):
    if not n_clicks:
        raise PreventUpdate

    try:
        validated_data = CostEstimationInput(
            method=method,
            plant_type=plant_type,
            equipment=equipment,
            equipment_type=equipment_type,
            sizing_quantity=sizing_quantity
        )
        data = validated_data.dict()
        return data, MessageCustom("Data saved successfully", success=True).layout
    except ValueError as e:
        return None, MessageCustom(str(e), success=False).layout

# Run calculations and display output
@app.callback(
    Output(ids.output, "children"),
    Input(ids.run_btn, "n_clicks"),
    State("store_data", "data"),
    prevent_initial_call=True
)
def run_calculations(n_clicks, data):
    if not n_clicks:
        raise PreventUpdate

    try:
        # Extract parameters from selected row
        row = df[(df['method'] == data['method']) & 
                 (df['plant_type'] == data['plant_type']) & 
                 (df['equipment'] == data['equipment']) & 
                 (df['type'] == data['equipment_type'])].iloc[0]

        # Calculate costs
        purchased_cost = row['a'] + row['b'] * (data['sizing_quantity'] ** row['n'])
        if data['method'] == "Hand":
            installed_cost = purchased_cost * row['installation_factor']
            output_message = f"Purchased Equipment Cost: ${purchased_cost:,.2f}\nInstalled Equipment Cost: ${installed_cost:,.2f}"
        else:
            ISBL_cost = purchased_cost * ((1 + row['piping_factor']) * row['material_factor'] +
                                          (row['equipment_erection_factor'] + row['electrical_factor'] +
                                           row['instrumentation_and_control_factor'] + row['civil_factor'] +
                                           row['structures_and_buildings_factor'] + row['lagging_and_paint_factor']))
            total_fixed_cost = ISBL_cost * (1 + row['Offsites_factor']) * (1 + row['design_and_engineering_factor'] + 
                                                                           row['contingency']) * row['location_factor']
            output_message = (f"Purchased Equipment Cost: ${purchased_cost:,.2f}\n"
                              f"ISBL Cost: ${ISBL_cost:,.2f}\nTotal Fixed Capital Cost: ${total_fixed_cost:,.2f}")

        return html.Div([
            DisplayField(id="purchased_cost", label="Purchased Equipment Cost", value=f"${purchased_cost:,.2f}").layout,
            DisplayField(id="installed_cost", label="Installed Equipment Cost", value=f"${installed_cost:,.2f}").layout,
            DisplayField(id="total_fixed_cost", label="Total Fixed Capital Cost", value=f"${total_fixed_cost:,.2f}").layout,
        ])
    except Exception as e:
        return MessageCustom(f"Calculation error: {str(e)}", success=False).layout

if __name__ == '__main__':
    app.run_server(debug=True)
