import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("C:\\Project\\new\\budge\\materials_factor.csv", encoding='ISO-8859-1')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Equipment Cost Estimation Tool"),
    
    # Dropdown for Method Selection
    html.Label("Choose Method:"),
    dcc.Dropdown(id='method-dropdown',
                 options=[{'label': method, 'value': method} for method in df['method'].unique()],
                 placeholder="Select a costing method",
                 style={'width': '50%'}),
    
    # Dropdown for Plant Type Selection
    html.Label("Choose Plant Type:"),
    dcc.Dropdown(id='plant-type-dropdown', 
                 placeholder="Select a plant type",
                 style={'width': '50%'}),
    
    # Dropdown for Equipment Selection
    html.Label("Choose Equipment Type:"),
    dcc.Dropdown(id='equipment-dropdown', 
                 placeholder="Select equipment type",
                 style={'width': '50%'}),
    
    # Dropdown for Specific Equipment Type Selection
    html.Label("Choose Specific Equipment Type:"),
    dcc.Dropdown(id='specific-equipment-dropdown', 
                 placeholder="Select specific equipment type",
                 style={'width': '50%'}),
    
    # Input for Sizing Quantity with dynamic guidance
    html.Label(id='sizing-label'),
    dcc.Input(id='sizing-input', type='number', placeholder="Enter sizing value", style={'width': '50%'}),
    html.Div(id='validation-message', style={'color': 'red'}),  # For displaying validation errors

    # Calculate Button
    html.Button("Calculate Costs", id='calculate-button', n_clicks=0),
    
    # Output for results
    html.Div(id='results-output', style={'whiteSpace': 'pre-line', 'marginTop': '20px'})
])

# Update Plant Type options based on selected Method
@app.callback(
    Output('plant-type-dropdown', 'options'),
    Input('method-dropdown', 'value')
)
def update_plant_type_options(method_choice):
    if method_choice:
        plant_types = df[df['method'] == method_choice]['plant_type'].dropna().unique()
        return [{'label': plant, 'value': plant} for plant in plant_types]
    return []

# Update Equipment options based on selected Plant Type
@app.callback(
    Output('equipment-dropdown', 'options'),
    Input('plant-type-dropdown', 'value')
)
def update_equipment_options(plant_choice):
    if plant_choice:
        equipment_types = df[df['plant_type'] == plant_choice]['equipment'].dropna().unique()
        return [{'label': equipment, 'value': equipment} for equipment in equipment_types]
    return []

# Update Specific Equipment Type options based on selected Equipment
@app.callback(
    Output('specific-equipment-dropdown', 'options'),
    [Input('method-dropdown', 'value'), Input('plant-type-dropdown', 'value'), Input('equipment-dropdown', 'value')]
)
def update_specific_equipment_options(method_choice, plant_choice, equipment_choice):
    if method_choice and plant_choice and equipment_choice:
        specific_types = df[(df['method'] == method_choice) &
                            (df['plant_type'] == plant_choice) &
                            (df['equipment'] == equipment_choice)]['equipment_type'].dropna().unique()
        return [{'label': equipment_type, 'value': equipment_type} for equipment_type in specific_types]
    return []

# Update Sizing Label and Input Placeholder based on selected specific equipment type
@app.callback(
    [Output('sizing-label', 'children'), Output('sizing-input', 'placeholder')],
    [Input('method-dropdown', 'value'), Input('plant-type-dropdown', 'value'), 
     Input('equipment-dropdown', 'value'), Input('specific-equipment-dropdown', 'value')]
)
def update_sizing_label(method_choice, plant_choice, equipment_choice, type_choice):
    if method_choice and plant_choice and equipment_choice and type_choice:
        selected_row = df[(df['method'] == method_choice) &
                          (df['plant_type'] == plant_choice) &
                          (df['equipment'] == equipment_choice) &
                          (df['equipment_type'] == type_choice)].iloc[0]
        sizing_quantity = selected_row['sizing_quantity']
        units = selected_row['units']
        s_lower = selected_row['s_lower']
        s_upper = selected_row['s_upper']
        
        if np.isnan(s_lower) or np.isnan(s_upper):
            placeholder = f"Enter {sizing_quantity} in {units}"
        else:
            placeholder = f"Enter {sizing_quantity} in {units} between {s_lower} and {s_upper}"
        return f"Enter {sizing_quantity} in {units}:", placeholder
    return "Enter sizing value", "Enter sizing value"

# Calculate and display the costs with validation
@app.callback(
    [Output('results-output', 'children'), Output('validation-message', 'children')],
    [Input('calculate-button', 'n_clicks')],
    [State('method-dropdown', 'value'), State('plant-type-dropdown', 'value'), 
     State('equipment-dropdown', 'value'), State('specific-equipment-dropdown', 'value'),
     State('sizing-input', 'value')]
)
def calculate_costs(n_clicks, method_choice, plant_choice, equipment_choice, type_choice, sizing_value):
    if n_clicks > 0:
        if not all([method_choice, plant_choice, equipment_choice, type_choice, sizing_value]):
            return "", "Please make selections and enter all required values to calculate costs."

        # Extract relevant row for selected equipment type
        selected_row = df[(df['method'] == method_choice) &
                          (df['plant_type'] == plant_choice) &
                          (df['equipment'] == equipment_choice) &
                          (df['equipment_type'] == type_choice)].iloc[0]

        s_lower = selected_row['s_lower']
        s_upper = selected_row['s_upper']
        
        # Validate sizing input
        if not (np.isnan(s_lower) or np.isnan(s_upper)) and not (s_lower <= sizing_value <= s_upper):
            return "", f"Error: The input value must be between {s_lower} and {s_upper}."

        # Proceed with calculations if input is valid
        a = selected_row['a']
        b = selected_row['b']
        n = selected_row['n']
        installation_factor = selected_row['installation_factor']
        material_factor = selected_row['material_factor']
        equipment_erection_factor = selected_row['equipment_erection_factor']
        piping_factor = selected_row['piping_factor']
        instrumentation_factor = selected_row['instrumentation_and_control_factor']
        electrical_factor = selected_row['electrical_factor']
        civil_factor = selected_row['civil_factor']
        structure_factor = selected_row['structures_and_buildings_factor']
        lagging_factor = selected_row['lagging_and_paint_factor']
        offsite_factor = selected_row['Offsites_factor']
        design_factor = selected_row['design_and_engineering_factor']
        contingency = selected_row['contingency']
        location_factor = selected_row['location_factor']

        # Purchased equipment cost
        purchased_cost = a + b * (sizing_value ** n)

        if method_choice == "Hand":
            installed_cost = purchased_cost * installation_factor
            return (f"Purchased Equipment Cost: ${purchased_cost:,.2f}\n"
                    f"Installed Equipment Cost: ${installed_cost:,.2f}"), ""
        else:
            ISBL_cost = purchased_cost * ((1 + piping_factor) * material_factor + 
                                          (equipment_erection_factor + electrical_factor +
                                           instrumentation_factor + civil_factor +
                                           structure_factor + lagging_factor))
            total_fixed_capital_cost = (ISBL_cost * (1 + offsite_factor) * 
                                        (1 + design_factor + contingency)) * location_factor
            return (f"Purchased Equipment Cost: ${purchased_cost:,.2f}\n"
                    f"ISBL Cost: ${ISBL_cost:,.2f}\n"
                    f"Total Fixed Capital Cost: ${total_fixed_capital_cost:,.2f}"), ""

    return "", ""

if __name__ == '__main__':
    app.run_server(debug=True)
