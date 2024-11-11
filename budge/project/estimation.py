import pandas as pd
import numpy as np
from agility.utils.pydantic import validate_data

from budge.schemas.estimation import EstimationInput

import pandas as pd

def filter_material_data(data, method=None, plant_type=None, equipment=None, equipment_type=None):
    """
    Helper function to filter material data based on specified criteria.
    Filters are only applied if their corresponding parameter is not None or empty.
    
    Parameters:
    - data: pd.DataFrame or dict
        The input data containing material information. It can be a DataFrame or a dictionary that can be converted to a DataFrame.
    - method: str, optional
        The method to filter by. If None or empty, this filter is ignored.
    - plant_type: str, optional
        The plant type to filter by. If None or empty, this filter is ignored.
    - equipment: str, optional
        The equipment to filter by. If None or empty, this filter is ignored.
    - equipment_type: str, optional
        The equipment type to filter by. If None or empty, this filter is ignored.
    
    Returns:
    - pd.DataFrame
        Filtered dataframe based on the input criteria.
    
    Raises:
    - KeyError: If the filtered dataframe is empty.
    - ValueError: If data is not in a valid format or required columns are missing.
    """
    # Ensure data is a DataFrame
    if isinstance(data, dict):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a DataFrame or a dictionary convertible to a DataFrame.")
    
    # Check if required columns are present
    required_columns = {'method', 'plant_type', 'equipment', 'equipment_type'}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(f"The following required columns are missing in the data: {', '.join(missing_columns)}")
    
    # Start with the full dataframe and apply filters only if criteria are provided
    filtered_data = data
    if method:
        filtered_data = filtered_data[filtered_data['method'] == method]
    if plant_type:
        filtered_data = filtered_data[filtered_data['plant_type'] == plant_type]
    if equipment:
        filtered_data = filtered_data[filtered_data['equipment'] == equipment]
    if equipment_type:
        filtered_data = filtered_data[filtered_data['equipment_type'] == equipment_type]
    
    # Check if filtered data is empty
    if filtered_data.empty:
        raise KeyError("Empty Dataframe! Check the input criteria as no matching data was found.")
    
    return filtered_data




def validate_input(page_input):
    """
    Check if the page_input data is valid.
    """
    page_input, errors = validate_data(page_input, EstimationInput)
    return page_input, errors

def all_inputs_ready(data):
    msgs = []
    ready = True
    if not data or "estimation_input" not in data:
        message = "Missing Page 3 input in data"
        msgs.append(message)
        ready = False

    estimation_input = data.get("estimation_input", {})
    estimation_input, page3_errors = validate_input(estimation_input)

    if page3_errors:
        ready = False
        msgs.append("Page 3 Inputs Invalid")
        msgs.extend([f"{field}: {error}" for field, error in page3_errors.items()])

    return ready, msgs

def run_calculation(data, material_data):
    df = pd.DataFrame(material_data)
    page3_output = {"result": "This is the output of the calculation"}
    estimation_input = data["estimation_input"]

    method = estimation_input['method']
    plant_type = estimation_input['plant_type']  
    equipment = estimation_input['equipment']
    equipment_type = estimation_input['equipment_type']
    sizing_value = estimation_input['sizing_value']
    
    selected_row = df[
        (df['method'] == method) &
        (df['plant_type'] == plant_type) &  
        (df['equipment'] == equipment) &
        (df['equipment_type'] == equipment_type)
    ].iloc[0]
    s_lower = selected_row['s_lower']
    s_upper = selected_row['s_upper']

    print(s_lower)
    print(s_upper)

    if not (np.isnan(s_lower) or np.isnan(s_upper)) and not (s_lower <= sizing_value <= s_upper):
            return "", f"Error: The input value must be between {s_lower} and {s_upper}."

    if selected_row.empty:
        raise ValueError("No matching data found for the selected options.")
    
    a = selected_row['a']
    b = selected_row['b']
    n = selected_row['n']
    print(f"a:{a}")

    Purchased_equipment_cost = int(a) + int(b) * (int(sizing_value) ** float(n))
    purchased_cost_output = f"${Purchased_equipment_cost:,.2f}"

    if method == "Hand":
        installation_factor = selected_row['installation_factor']
        Installed_equipment_cost = Purchased_equipment_cost * installation_factor
        total_cost_output = f"${Installed_equipment_cost:,.2f}"
    else:
        fm = selected_row['material_factor']
        fer = selected_row['equipment_erection_factor']
        fp = selected_row['piping_factor']
        fi = selected_row['instrumentation_and_control_factor']
        fel = selected_row['electrical_factor']
        fc = selected_row['civil_factor']
        fs = selected_row['structures_and_buildings_factor']
        fl = selected_row['lagging_and_paint_factor']
        OS = selected_row['Offsites_factor']
        DE = selected_row['design_and_engineering_factor']
        X = selected_row['contingency']
        location_factor = selected_row['location_factor']

        ISBL_cost = Purchased_equipment_cost * ((1 + float(fp)) * fm + (fer + fel + fi + fc + fs + fl))
        Total_fixed_capital_cost = ISBL_cost * (1 + OS) * (1 + DE + X) * location_factor
        total_cost_output = f"${Total_fixed_capital_cost:,.2f}"

    page3_output = {}
    page3_output["purchased_cost_output"] = f"{purchased_cost_output}"
    page3_output["total_cost_output"] = f"{total_cost_output}"

    data["page3_output"] = page3_output
    return data

def save_reset(data):
    try:
        data.pop("page3_output")
        data = run_reset(data)
    except KeyError:
        pass
    return data

def run_reset(data):
    try:
        data.pop(
            "pagex_output"
        )  # remove the output data that is dependent on current page output
        data.pop("report")
    except KeyError:
        pass
    return data