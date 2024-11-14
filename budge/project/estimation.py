import pandas as pd
import numpy as np
from agility.utils.pydantic import validate_data

from budge.schemas.estimation import EstimationInput
from budge.core.definitions import Factors
from budge.config.main import STORE_ID, DATA_STORE

import traceback


def filter_material_data(
    data, method=None, plant_type=None, equipment=None, equipment_type=None
):
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
        raise ValueError(
            "Input data must be a DataFrame or a dictionary convertible to a DataFrame."
        )

    # Check if required columns are present
    required_columns = {
        Factors.METHOD,
        Factors.PLANT_TYPE,
        Factors.EQUIPMENT,
        Factors.EQUIPMENT_TYPE,
    }
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"The following required columns are missing in the data: {', '.join(missing_columns)}"
        )

    # Start with the full dataframe and apply filters only if criteria are provided
    filtered_data = data
    if method:
        filtered_data = filtered_data[filtered_data[Factors.METHOD] == method]
        if filtered_data.empty:
            raise KeyError(
                "Empty Dataframe! Check the input criteria as no matching data was found."
            )
    if plant_type:
        filtered_data = filtered_data[filtered_data[Factors.PLANT_TYPE] == plant_type]
        if filtered_data.empty:
            raise KeyError(
                "Empty Dataframe! Check the input criteria as no matching data was found."
            )
    if equipment:
        filtered_data = filtered_data[filtered_data[Factors.EQUIPMENT] == equipment]
        if filtered_data.empty:
            raise KeyError(
                "Empty Dataframe! Check the input criteria as no matching data was found."
            )
    if equipment_type:
        filtered_data = filtered_data[
            filtered_data[Factors.EQUIPMENT_TYPE] == equipment_type
        ]
        if filtered_data.empty:
            raise KeyError(
                "Empty Dataframe! Check the input criteria as no matching data was found."
            )

    # Check if filtered data is empty
    if filtered_data.empty:
        raise KeyError(
            "Empty Dataframe! Check the input criteria as no matching data was found."
        )

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
    estimation_input, estimation_errors = validate_input(estimation_input)

    if estimation_errors:
        ready = False
        msgs.append("Estimation Inputs Invalid")
        msgs.extend([f"{field}: {error}" for field, error in estimation_errors.items()])

    return ready, msgs


def run_calculation(data, material_data):
    estimation_output = {"result": "This is the output of the calculation"}
    # estimation_input = data["estimation_input"]
    estimation_input = EstimationInput(**data["estimation_input"])

    selected_row = filter_material_data(
        material_data, estimation_input.method, estimation_input.plant_type, estimation_input.equipment, estimation_input.equipment_type
    )
    selected_row = selected_row.iloc[0]
    s_lower = selected_row[Factors.S_LOWER]
    s_upper = selected_row[Factors.S_UPPER]


    if not (np.isnan(s_lower) or np.isnan(s_upper)) and not (
        s_lower <= estimation_input.sizing_value <= s_upper
    ):
        return "", f"Error: The input value must be between {s_lower} and {s_upper}."

    if selected_row.empty:
        raise ValueError("No matching data found for the selected options.")

    a = selected_row[Factors.A]
    b = selected_row[Factors.B]
    n = selected_row[Factors.N]

    purchased_equipment_cost = a + b * (estimation_input.sizing_value) ** float(n)
    purchased_cost_output = f"${purchased_equipment_cost:,.2f}"

    if estimation_input.method == "Hand":
        installation_factor = selected_row[Factors.INSTALLATION_FACTOR]
        installed_equipment_cost = purchased_equipment_cost * installation_factor
        total_cost_output = f"${installed_equipment_cost:,.2f}"
    else:
        fm = selected_row[Factors.MATERIAL_FACTOR]
        fer = selected_row[Factors.EQUIPMENT_ERECTION_FACTOR]
        fp = selected_row[Factors.PIPING_FACTOR]
        fi = selected_row[Factors.INSTRUMENTATION_AND_CONTROL_FACTOR]
        fel = selected_row[Factors.ELECTRICAL_FACTOR]
        fc = selected_row[Factors.CIVIL_FACTOR]
        fs = selected_row[Factors.STRUCTURES_AND_BUILDINGS_FACTOR]
        fl = selected_row[Factors.LAGGING_AND_PAINT_FACTOR]
        OS = selected_row[Factors.OFFSITES_FACTOR]
        DE = selected_row[Factors.DESIGN_AND_ENGINEERING_FACTOR]
        X = selected_row[Factors.CONTINGENCY]
        location_factor = selected_row[Factors.LOCATION_FACTOR]

        ISBL_cost = purchased_equipment_cost * (
            (1 + float(fp)) * fm + (fer + fel + fi + fc + fs + fl)
        )
        total_fixed_capital_cost = ISBL_cost * (1 + OS) * (1 + DE + X) * location_factor
        total_cost_output = f"${ISBL_cost:,.2f}"

    estimation_output = {}
    estimation_output["purchased_cost_output"] = f"{purchased_cost_output}"
    estimation_output["total_cost_output"] = f"{total_cost_output}"

    data["estimation_output"] = estimation_output
    return data


def save_reset(data):
    try:
        data.pop("estimation_output")
        data = run_reset(data)
    except KeyError:
        pass
    return data


def run_reset(data):
    try:
        data.pop(
            "estimation_output"
        )  # remove the output data that is dependent on current page output
        data.pop("report")
    except KeyError:
        pass
    return data
