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

from agility.components import (
    ButtonCustom,
    InputCustom,
    MessageCustom,
    DropdownCustom,
    CheckboxCustom,
    DisplayField,
    ContainerCustom,
)

from budge.config.main import STORE_ID, PROJECT_NAME, PROJECT_SLUG
from budge.project import page1


dash.register_page(__name__)
app: Dash = dash.get_app()

from typing import Final


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
        self.feedback_save: Final[str] = f"{prefix}_feedback_save"
        self.run_btn: Final[str] = f"{prefix}_run_btn"
        self.feedback_run: Final[str] = f"{prefix}_feedback_run"
        self.output: Final[str] = f"{prefix}_output"


ids = PageIDs()

PAGE_TITLE = "Page Demo"

# Define the layout
demo_layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Section 1: Heading Level 1 ",
                            className="dash-h1",
                        ),
                        html.P("This is some text."),
                        html.P("This is some text."),
                        html.H2(
                            "Section 1.1: Heading Level 2",
                            className="dash-h2",
                        ),
                        html.P("This is some text."),
                        html.H3(
                            "Section 1.1.1: Heading  Level 3",
                            className="dash-h3",
                        ),
                        html.P("This is some text.", className="text-sm mb-2"),
                        InputCustom(
                            id="input1", placeholder="Enter text here", addon_text="m"
                        ).layout,
                        DropdownCustom(
                            id="dropdown1",
                            options=[
                                {"label": "Option 1", "value": "1"},
                                {"label": "Option 2", "value": "2"},
                            ],
                        ).layout,
                        CheckboxCustom(
                            id="checkbox1",
                            options=["Apples", "Oranges", "Banana"],
                            value=[1, 2, 3],
                            label="Check me out",
                        ).layout,
                    ]
                ),
                html.Div(
                    [
                        #        html.H2("Section 2: Outputs"),
                        #        DisplayField(id='display1', value='Initial Value'),
                    ],
                    style={"padding": "20px", "flex": "2"},
                ),
            ],
            style={"display": "flex"},
        ),
    ]
)

# create a sample dash page layout with heading and subheading
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
        html.Div(id=ids.input, className="p-6", children=demo_layout),
        html.Div(id=ids.save_btn, className="p-6"),
        html.Div(id=ids.feedback_save, className="p-6"),
        html.Div(id=ids.run_btn, className="p-6"),
        html.Div(id=ids.feedback_run, className="p-6"),
        html.Div(id=ids.output, className="p-6"),
    ],
    className="w-full",
)


@app.callback(Output(ids.status, "children"), [Input("url", "pathname")])
def display_page_message(pathname: str) -> html.Div | None:
    message = "Message to test callback"

    htmlx = MessageCustom(id="message1", messages=message, success=False).layout
    return htmlx
