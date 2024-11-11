import os
import tempfile
import dash
import pandas as pd
from dash import Dash, Input, Output, State, dcc, html, dash_table
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid
from plotly import graph_objects as go
import plotly.express as px
from collections import namedtuple
from typing import Final
import traceback
import math
from flask import Flask, send_from_directory  # Import Flask

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
from budge.project import Project as PRJ
from budge.project.report import generate_report
from budge.schemas.page2 import Page2Input, generate_table_record

from typing import Final

dash.register_page(__name__)
app: Dash = dash.get_app()

PAGE_TITLE = "Report"


class PageIDs:
    def __init__(self) -> None:
        filename = os.path.basename(__file__)
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
        self.report_download: Final[str] = f"{prefix}_report_download"


ids = PageIDs()


table_columns = [
    {"field": "table_id", "headerName": "ID", "editable": False},
    {"field": "x", "headerName": "Col X", "editable": True},
    {"field": "y", "headerName": "Col Y", "editable": True},
    {"field": "z", "headerName": "Col Z", "editable": True},
]

layout = html.Div(
    [
        html.H1("budge", className="app-title"),
        html.H2(PAGE_TITLE, className="page-title"),
        html.Hr(),
        html.Div(id=ids.status),
        html.Div(id=ids.input, className="px-6 pb-2 w-96"),
        html.Div(id=ids.save_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_save, className="px-6 pb-2 w-96"),
        html.Div(id=ids.run_container, className="px-6 pb-2 w-96"),
        html.Div(id=ids.feedback_run, className="px-6 pb-4 w-96"),
        html.Div(id=ids.report_download, className="px-6 pb-2"),
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
    return None


# callback function to display the input fields and save btn if project is loaded
@app.callback(
    Output(ids.input, "children"),
    [Input(STORE_ID, "data")],
)
def display_input(data):
    if data is None:
        raise PreventUpdate

    progress_dict = PRJ.get_progress(data)
    steps_column = ["Page One", "Page Two"]
    progress_levels = ["Not Started", "In Progress", "Completed"]
    status_column = []

    for step in steps_column:
        status_column.append(progress_levels[progress_dict[step]])

    df = pd.DataFrame({"Step": steps_column, "Status": status_column})

    progress_layout = html.Div(
        [
            dash_table.DataTable(
                id="progress_table",
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict("records"),
                style_cell={"textAlign": "left", "padding": "10px"},
                style_header={
                    "backgroundColor": "light-grey",
                    "fontWeight": "bold",
                    "textAlign": "center",
                },
                style_data_conditional=[
                    {
                        "if": {"filter_query": '{Status} = "Completed"'},
                        "backgroundColor": "#10B981",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": '{Status} = "In Progress"'},
                        "backgroundColor": "#F59E0B",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": '{Status} = "Not Started"'},
                        "backgroundColor": "#9CA3AF",
                        "color": "black",
                    },
                ],
            )
        ]
    )

    return progress_layout


# callback to show generate report button if all steps are completed
@app.callback(
    Output(ids.run_container, "children"),
    [Input(STORE_ID, "data")],
)
def show_run_button(data):
    if not data:
        return None
    progress_dict = PRJ.get_progress(data)
    if progress_dict["Page One"] == 2 and progress_dict["Page Two"] == 2:
        return html.Button(
            "Generate Report",
            id=ids.run_btn,
            className="bg-blue-500 text-white p-1 w-40",
        )


# callback to run the report generation and save the zipped folder in the store
@app.callback(
    Output(ids.report_download, "children"),
    Output(ids.feedback_run, "children"),
    Output(STORE_ID, "data", allow_duplicate=True),
    Input(ids.run_btn, "n_clicks"),
    State(STORE_ID, "data"),
    prevent_initial_call=True,
)
def report_run(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate

    memory_output = generate_report(data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(memory_output.getvalue())
        tmp_path = tmp.name

    report_link = html.A(
        "Click to Download Report",
        href=f"/budge/download/{os.path.basename(tmp_path)}",
        target="_blank",
        style={"color": "blue", "textDecoration": "underline"},
    )
    report = {"report": "generated"}
    data["report"] = report
    msg = MessageCustom(
        messages="Report generated successfully.",
        success=True,
    )
    return report_link, msg.layout, data


# Serve the file from the temporary directory
@app.server.route("/budge/download/<filename>")
def serve_file(filename):
    directory = tempfile.gettempdir()
    return send_from_directory(directory, filename, as_attachment=True)
