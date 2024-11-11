import pandas as pd
from InquirerPy import inquirer
import numpy as np

# Load the CSV file
df = pd.read_csv("C:\\Project\\Vessel\\materials_factor.csv", encoding='ISO-8859-1')

def select_method():
    """
    Prompts the user to choose a costing method from variations of factorial method (either 'Hand' or 'Material Factor').

    Returns:
        str: The selected method, which will determine the calculation approach.
    """
    method_choices = df['method'].unique().tolist()
    method_choice = inquirer.select(
        message="Choose method:",
        choices=method_choices
    ).execute()
    print(f"You selected method: {method_choice}")
    return method_choice

def select_plant_type(method_choice):
    """
    Prompts the user to select a plant process type based on the chosen method.

    Args:
        method_choice (str): The selected method.

    Returns:
        str: The chosen plant process type.
    """
    plant_choices = df[df['method'] == method_choice]['plant_type'].dropna().unique().tolist()
    plant_choice = inquirer.select(
        message="Choose plant type:",
        choices=plant_choices
    ).execute()
    print(f"You selected plant type: {plant_choice}")
    return plant_choice

def select_equipment(plant_choice):
    """
    Prompts the user to choose an equipment type based on the selected plant type.

    Args:
        plant_choice (str): The chosen plant type.

    Returns:
        str: The selected equipment.
    """
    equipment_choices = df[df['plant_type'] == plant_choice]['equipment'].dropna().unique().tolist()
    selected_equipment = inquirer.select(
        message="Choose equipment type:",
        choices=equipment_choices
    ).execute()
    print(f"You selected equipment: {selected_equipment}")
    return selected_equipment

def select_equipment_type(selected_equipment, method_choice, plant_choice):
    """
    Prompts the user to choose a specific type for the selected equipment.

    Args:
        selected_equipment (str): The selected equipment.
        method_choice (str): The chosen costing method.
        plant_choice (str): The chosen plant type.

    Returns:
        dict: A dictionary containing parameters for the selected equipment type, including factors and cost coefficients.
    """

    type_choices = df[(df['method'] == method_choice) & 
                      (df['plant_type'] == plant_choice) &
                      (df['equipment'] == selected_equipment)]['type'].dropna().unique().tolist()
    type_choice = inquirer.select(
        message="Choose specific type for the equipment:",
        choices=type_choices
    ).execute()
    print(f"You selected equipment type: {type_choice}")

    selected_row = df[(df['method'] == method_choice) & 
                      (df['plant_type'] == plant_choice) &
                      (df['equipment'] == selected_equipment) & 
                      (df['type'] == type_choice)].iloc[0]
    return {
        "a": selected_row['a'],
        "b": selected_row['b'],
        "n": selected_row['n'],
        "s_lower": selected_row['s_lower'],
        "s_upper": selected_row['s_upper'],
        "sizing_quantity": selected_row['sizing_quantity'],
        "units": selected_row['units'],
        "installation_factor": selected_row['installation_factor'],
        "material_factor": selected_row['material_factor'],
        "equipment_erection_factor": selected_row['equipment_erection_factor'],
        "piping_factor": selected_row['piping_factor'],
        "instrumentation_and_control_factor": selected_row['instrumentation_and_control_factor'],
        "electrical_factor": selected_row['electrical_factor'],
        "civil_factor": selected_row['civil_factor'],
        "structures_and_buildings_factor": selected_row['structures_and_buildings_factor'],
        "lagging_and_paint_factor": selected_row['lagging_and_paint_factor'],
        "ISBL_cost_factor": selected_row['ISBL_cost_factor'],
        "Offsites_factor": selected_row['Offsites_factor'],
        "design_and_engineering_factor": selected_row['design_and_engineering_factor'],
        "contingency": selected_row['contingency'],
        "location_factor": selected_row['location_factor']
    }

def purchased_equipment_cost(a, b, S, n):
    """
    Calculates the cost based on the formula C = a + b * S^n.

    Args:
        a (int): Constant 'a' in the formula.
        b (int): Constant 'b' in the formula.
        S (float): The sizing value.
        n (float): Exponent 'n' in the formula.

    Returns:
        float: The purchased cost of the selected equipment type.
    """
    return a + b * (S ** n)

def installed_equipment_cost(f, purchased_equipment_cost):
    """
    Calculates the installed equipment cost based on the purchased equipment cost 
    and an installation factor.

    Args:
        f (float): The installation factor.
        purchased_equipment_cost (float): The cost of purchasing the equipment.

    Returns:
        float: The total installed equipment cost.
    """
    return purchased_equipment_cost * f

def total_fixed_capital_cost(fm, fer,fp, fi,fel, fc,fs,fl, OS, DE, X, location_factor, purchased_equipment_cost):
    """
    Calculates the total fixed capital cost based on various factors.

    Args:
        fm (float): Material factor.
        fer (float): Equipment erection factor.
        fp (float): Piping factor.
        fi (float): Instrumentation and control factor.
        fel (float): Electrical factor.
        fc (float): Civil factor.
        fs (float): Structures and buildings factor.
        fl (float): Lagging and paint factor.
        OS (float): Offsites factor.
        DE (float): Design and engineering factor.
        X (float): Contingency factor.
        purchased_equipment_cost (float): The cost of purchasing the equipment.

    Returns:
        tuple: The ISBL cost and the total fixed capital cost.
    """
    ISBL_cost =purchased_equipment_cost * ((1+fp)*fm + (fer+fel+fi+fc+fs+fl))
    Total_fixed_capital_cost = (ISBL_cost*(1+OS) * (1+DE + X))* location_factor
    return ISBL_cost, Total_fixed_capital_cost

def get_valid_sizing_input(s_lower, s_upper, sizing_quantity, units):
    """
    Prompts the user to enter a valid sizing value within the specified range.

    Args:
        s_lower (float): The lower bound of the sizing value.
        s_upper (float): The upper bound of the sizing value.
        sizing_quantity (str): The description of the sizing quantity.
        units (str): The units for the sizing quantity.

    Returns:
        float: A valid sizing value within the specified range.
    """
    while True:
        try:
            if np.isnan(s_lower) or np.isnan(s_upper):
                s = float(input(f"Enter a value for {sizing_quantity} in {units}: "))
                return s
            else:
                s = float(input(f"Enter a value for {sizing_quantity} in {units} between {s_lower} and {s_upper}: "))
                if s_lower <= s <= s_upper:
                    return s
                else:
                    print(f"Error: The input value must be between {s_lower} and {s_upper}. Please try again.")
        
        except ValueError:
            print("Error: Please enter a numeric value. Try again.")

method_choice = select_method()
plant_choice = select_plant_type(method_choice)
selected_equipment = select_equipment(plant_choice)
type_info = select_equipment_type(selected_equipment, method_choice, plant_choice)
s = get_valid_sizing_input(type_info['s_lower'], type_info['s_upper'], type_info['sizing_quantity'], type_info['units'])
Purchased_equipment_cost = purchased_equipment_cost(type_info['a'], type_info['b'], s, type_info['n'])
print(f"\nThe Purchased equipment cost is: ${int(Purchased_equipment_cost): ,}")
if method_choice == "Hand":
    Installed_equipment_cost = installed_equipment_cost(type_info['installation_factor'], Purchased_equipment_cost)
    print(f"The Installed equipment cost is: ${int(Installed_equipment_cost): ,}\n")
else:
    ISBL_cost, Total_fixed_capital_cost = total_fixed_capital_cost(type_info['material_factor'], type_info['equipment_erection_factor'], type_info['piping_factor'], type_info['instrumentation_and_control_factor'], type_info['electrical_factor'], type_info['civil_factor'], type_info['structures_and_buildings_factor'], type_info['lagging_and_paint_factor'], type_info['Offsites_factor'], type_info['design_and_engineering_factor'], type_info['contingency'], type_info['location_factor'],  Purchased_equipment_cost)
    ISBL_cost = ISBL_cost
    Total_fixed_capital_cost = Total_fixed_capital_cost
    print(f"The total installed ISBL cost is: ${int(ISBL_cost): ,}\n")
    print(f"Total fixed capital cost is: ${int(Total_fixed_capital_cost): ,}\n")
