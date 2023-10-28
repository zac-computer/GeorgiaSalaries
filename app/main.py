""""""

import os
import pandas as pd
from dotenv import load_dotenv
from dash import Dash, dash_table, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate

# Load environment variables
load_dotenv()

# constants
YEARS = list(range(2022, 2012, -1))  # values for the year dropdown (based on available data)
PAGE_SIZE = int(os.getenv('PAGE_SIZE', 15))
GITHUB_URL = os.getenv("GITHUB_URL")
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', os.getenv("PROCESSED_DATA_FILE_NAME"))

# DATA_PATH = os.path.join(os.getenv("DATA_DIR_PATH"), "processed", os.getenv("PROCESSED_DATA_FILE_NAME"))
all_salaries = pd.read_csv(DATA_PATH)

# create a small initial dataframe to not overwhelm the server!
# df_init = all_salaries.query("Name == 'Kirby Smart' & `Fiscal Year` == 2022")
df_init = all_salaries.query("`Fiscal Year` == 2022").iloc[0:16]

# define a format for salaries
money = dash_table.FormatTemplate.money(0)

# add external font stylesheet
external_stylesheet_url = os.getenv('EXTERNAL_STYLESHEET_URL')
external_stylesheets = [
    {
        "href": external_stylesheet_url,
        "rel": "stylesheet",
    }
] if external_stylesheet_url else []

# I should make a visual of the layout
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = 'GA Salaries'
app.layout = html.Div(
    children=[  # header
        html.Div(children=
                 html.H1(children='Georgia Employee Salaries By Year', className='header-title')
                 , className='header'),
        html.Div(children=[  # main content
            html.Div(children=[  # filters
                html.Div(children=[  # search bar and text tip
                    html.Div('Search Salaries',
                             className='search-tip'),
                    dcc.Input(type='text', debounce=False, id='my-dynamic-input',
                              className='search-bar')
                ], className='search-filter'),
                html.Div(children=[  # year dropdown and text above
                    html.Div("Year"),
                    dcc.Dropdown(value=2022, options=YEARS, id='my-year-dropdown', maxHeight=200, searchable=False,
                                 className='year-dropdown')
                ], className="year-filter"),
                dcc.RadioItems(options=['Name', 'Title', 'Organization'], value='Name', id='my-search-toggle',
                               className="search-toggle")
            ], className='filters'
            ),
            html.Div(children=
            dash_table.DataTable(
                id='tbl',
                page_size=PAGE_SIZE,
                page_action='custom',
                page_current=0,
                columns=[
                    dict(id='Name', name='Name'),
                    dict(id='Title', name='Title'),
                    dict(id='Organization', name='Organization'),
                    dict(id='Salary', name='Salary', type='numeric', format=money),
                    dict(id='Fiscal Year', name='Fiscal Year', type='numeric')
                ],
                data=df_init.to_dict("records"),
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df_init.to_dict('records')
                ],
                tooltip_delay=0,
                tooltip_duration=None,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left',
                            'font-family': '"Lato", sans-serif',
                            'fontSize': 12,
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0,
                            },
                style_cell_conditional=[
                    {'if': {'column_id': 'Name'},
                     'width': '15%'},
                    {'if': {'column_id': 'Title'},
                     'width': '30%'},
                    {'if': {'column_id': 'Organization'},
                     'width': '30%'},
                    {'if': {'column_id': 'Salary'},
                     'width': '15%'},
                    {'if': {'column_id': 'Fiscal Year'},
                     'width': '10%'},
                ],
                style_data_conditional=[
                    {'if': {'row_index': 'odd'},
                     'backgroundColor': 'RGB(200, 220, 240)'}  # stripe rows
                ]
            ),
                className='table'
            )
        ],
            className='main-content'),
        html.Footer(children=[html.A("Ben Muhlmann",
                                     href=GITHUB_URL,
                                     target="_blank"),
                              html.Span(" 2023")],
                    className='footer')
    ])

# callback to filter by year and name and title
"""
potential performance improvements:
1. [x] Filter first by year, then filter by name (create an intermediate df before returning)
2. save the start-stop indices for each year in a dictionary
3. Commit to displaying one year at a time and save each year's data in a separate df
"""


@app.callback(
    Output("tbl", "data"),
    Output("tbl", "tooltip_data"),
    Input("my-year-dropdown", "value"),
    Input("my-dynamic-input", "value"),
    Input("my-search-toggle", "value"),
    Input("tbl", "page_current")
)
def display_table(year_value, search_value, search_toggle, page_current):
    """
    Callback function for table filtering and displaying based on user inputs.
    Defaults to unfiltered data when nothing is inputted in the search bar

    :param year_value: the year selected from the dropdown
    :param search_value: the user's inputted search value (text)
    :param search_toggle: Name, Title, or Organization
    :param page_current: The selected data page
    :return: A dataframe to be displayed, and a list of tooltip values
    """

    df_year = all_salaries[all_salaries['Fiscal Year'] == year_value]

    # If there's no search value, display everything
    if not search_value:
        dff = df_year

    # otherwise, filter based on the user's search
    elif search_toggle == "Name":
        dff = df_year[df_year['Name'].str.contains(search_value, case=False, regex=False)]
    elif search_toggle == "Title":
        dff = df_year[df_year['Title'].str.contains(search_value, case=False, regex=False)]
    elif search_toggle == "Organization":
        dff = df_year[df_year['Organization'].str.contains(search_value, case=False, regex=False)]

    # Filter dff to just the current page - huge performance improvements with backend pagination
    dff = dff.iloc[page_current*PAGE_SIZE:(page_current+ 1)*PAGE_SIZE]

    # Generate a tooltip list for the currently displayed page
    new_tooltip_list = [
        {
            column: {'value': str(value), 'type': 'text'}
            for column, value in row.items()
        } for row in dff.to_dict('records')
    ]

    return dff.to_dict("records"), new_tooltip_list


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
