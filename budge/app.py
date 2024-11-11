import dash
from dash import dcc, html
import pandas as pd

from agility.components import Sidebar
from budge.config.main import CONFIG_SIDEBAR, STORE_ID, DATA_STORE
from budge.project import Project

external_scripts = [
    # Tailwind CSS from JS src file
    "https://cdn.tailwindcss.com/"
]


def init_app(
    server,
    project_slug,
    app_title,
):
    route_path_name = f"/{project_slug}/"
    dash_app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True,
        use_pages=True,
        server=server,
        routes_pathname_prefix=route_path_name,
        external_stylesheets=[
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
        ],
        external_scripts=external_scripts,  # Tailwind CSS from JS src file
        title=app_title,  # Update title if needed or use a variable
    )
    #    dash_app.config.suppress_callback_exceptions = True

    sidebar = Sidebar(CONFIG_SIDEBAR, STORE_ID, Project(), dash_app)
    material_data = pd.read_csv(
        "materials_factor.csv", encoding="ISO-8859-1"
    ).to_dict()

    dash_app.layout = html.Div(
        [
            dcc.Store(id=STORE_ID, storage_type="session", data=None),
            dcc.Store(id = DATA_STORE, storage_type="session", data = material_data),
            dcc.Location(id="url", refresh=False),
            html.Div(
                sidebar.layout(),
                className="w-72 border-r-2 border-gray-200 min-h-screen",
            ),
            html.Div(
                id="page-content", children=[dash.page_container], className="w-full"
            ),
            #  dash.page_container,
        ],
        className="flex min-h-screen w-full bg-gray-100",
    )

    """ 
    dash_app.layout = html.Div(
        [
            dcc.Store(id=STORE_ID, storage_type="session", data=None),
            dcc.Location(id="url", refresh=False),
            html.Div(
                sidebar.layout(),
                className="sidebar-content",
            ),
            html.Div(
                id="page-content",
                children=[dash.page_container],
                className="page-content",
            ),
        ],
        className="app-content",
    )
    """
    return dash_app
