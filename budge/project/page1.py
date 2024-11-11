# check if page1_inputs are valid and generate errors if not
import math
from agility.utils.pydantic import validate_data

from budge.schemas.page1 import Page1Input
from budge.project.page2 import validate_input as validate_page2_input


def validate_input(page_input):
    """
    Check if the page_input data is valid.
    """
    page_input, errors = validate_data(page_input, Page1Input)
    return page_input, errors


def all_inputs_ready(data):
    msgs = []
    ready = True
    if not data or "page1_input" not in data:
        message = "Missing Page 1 input in data"
        msgs.append(message)
        ready = False

    page1_input = data["page1_input"]
    page1_input, page1_errors = validate_input(page1_input)

    # set ready to false if there are errors
    if page1_errors:
        ready = False
        msgs.append("Page 1 Inputs Invalid")

    """
    if not "page2_input" in data:
        message = "Missing Page 2 input in data"
        msgs.append(message)
        ready = False
  
    page2_input = data["page2_input"]
    page2_input, page2_errors = validate_page2_input(page2_input)

  
    if not page2_errors:
        message = "Page 2 Inputs Invalid"
        msgs.append(message)
        ready = False
    """

    return ready, msgs


def run_calculation(data):
    page1_output = {"result": "This is the output of the calculation"}
    page1_input = data["page1_input"]
    a = page1_input["a"]
    b = page1_input["b"]
    c = page1_input["c"]
    number_operands = page1_input["numbers_operands"]
    operation = page1_input["operation"]
    if operation == "addition":
        if number_operands == "two":
            result = a + b
        else:
            result = a + b + c
    elif operation == "multiplication":
        if number_operands == "two":
            result = a * b
        else:
            result = a * b * c
    else:
        result = math.nan

    page1_output = {}
    page1_output["result"] = result
    data["page1_output"] = page1_output
    return data


def save_reset(data):
    try:
        data.pop("page1_output")
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
