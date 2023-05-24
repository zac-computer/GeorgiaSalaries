# imports
from dash import Dash, dash_table, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import pickle

with open("all_salaries.pickle", "rb") as input_file:
    all_salaries = pickle.load(input_file)

# create a list of fiscal year dropdown options
options = list(range(2013, 2023))

# create a small initial dataframe to not overwhelm the server!
df_init = all_salaries.query("Name == 'Kirby Smart' & `Fiscal Year` == 2022")

# define a format for salaries
money = dash_table.FormatTemplate.money(0)

# add external font stylesheet
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    }
]

# I should make a visual of the layout
app = Dash(__name__, external_stylesheets=external_stylesheets)
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
                    dcc.Input(value='Kirby Smart', type='text', minLength=3, debounce=False, id='my-dynamic-input',
                              className='search-bar')
                ], className='search-filter'),
                html.Div(children=[  # year dropdown and text above
                    html.Div("Year"),
                    dcc.Dropdown(value=2022, options=options, id='my-year-dropdown', maxHeight=200, searchable=False,
                                 className='year-dropdown')
                ], className="year-filter"),
                dcc.RadioItems(options=['Name', 'Title', 'Organization'], value='Name', id='my-search-toggle',
                               className="search-toggle")
            ], className='filters'
            ),
            html.Div(children=
            dash_table.DataTable(
                id='tbl',
                columns=[
                    dict(id='Name', name='Name'),
                    dict(id='Title', name='Title'),
                    dict(id='Organization', name='Organization'),
                    dict(id='Salary', name='Salary', type='numeric', format=money),
                    dict(id='Fiscal Year', name='Fiscal Year', type='numeric')
                ],
                data=df_init.to_dict("records"),
                style_cell={'textAlign': 'left', 'font-family': '"Lato", sans-serif', 'fontSize': 12},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'RGB(200, 220, 240)',  # stripe rows
                    }
                ]
            ),
                className='table'
            )
        ],
            className='main-content'),
        html.Footer(children="Ben Muhlmann. 2023", className='footer')
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
    Input("my-year-dropdown", "value"),
    Input("my-dynamic-input", "value"),
    Input("my-search-toggle", "value")
)
def display_table(year_value, search_value, search_toggle):
    if not search_value:
        raise PreventUpdate
    if len(search_value) < 3:  # filtering on too few characters is slow
        raise PreventUpdate
    df_year = all_salaries[all_salaries['Fiscal Year'] == year_value]
    if search_toggle == "Name":
        dff = df_year[df_year['Name'].str.contains(search_value, case=False, regex=False)]
    if search_toggle == "Title":
        dff = df_year[df_year['Title'].str.contains(search_value, case=False, regex=False)]
    if search_toggle == "Organization":
        dff = df_year[df_year['Organization'].str.contains(search_value, case=False, regex=False)]
    return dff.to_dict("records")


if __name__ == '__main__':
    app.run_server(debug=True)
