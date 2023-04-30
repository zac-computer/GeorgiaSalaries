# imports
from process_data import all_salaries  # import data processing script to get salary df. Replace with i/o
from dash import Dash, dash_table, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import numpy as np

# create a list of fiscal year dropdown options
options = list(range(2013, 2023))

# separately sort dataframe by year so displayed
#  results table appears in chronological order
all_salaries = all_salaries.sort_values(by=['FISCAL_YEAR', 'SALARY'], ascending=[True, False])

# only keep relevant columns
# this should be done in data processing script
all_salaries = all_salaries[['NAME', 'TITLE', 'SALARY', 'FISCAL_YEAR']]

# rename columns
# this should be done in data processing script
all_salaries = all_salaries.rename(columns={'NAME': 'Name',
                                            'TITLE': 'Title',
                                            'SALARY': 'Salary',
                                            'FISCAL_YEAR': 'Fiscal Year'})

# create a small initial dataframe to not overwhelm the server!
df_init = all_salaries.query("Name == 'Kirby Smart' & `Fiscal Year` == 2022")

# define a format for salaries
money = dash_table.FormatTemplate.money(0)

# I should make a visual of the layout
app = Dash(__name__)
app.title = 'GA Salaries'
app.layout = html.Div(
    children=[  # header
        html.Div(children=
                 html.H1(children='Georgia Employee Salaries By Year', className='header-title')
                 , className='header'),
        html.Div(children=[  # main content
            html.Div(children=[  # filters
                html.Div(children=[  # search bar and text tip
                    dcc.Input(value='Kirby Smart', type='text', minLength=3, debounce=False, id='my-dynamic-input',
                              className='search-bar'),
                    html.Div('Filter by name or title. Enter least 3 characters to filter.', className='search-tip'),
                ], className='search'),
                dcc.Dropdown(value=2022, options=options, id='my-year-dropdown', maxHeight=200, searchable=False,
                             className='year-dropdown')
            ], className='filters'
            ),
            html.Div(children=
            dash_table.DataTable(
                id='tbl',
                columns=[
                    dict(id='Name', name='Name'),
                    dict(id='Title', name='Title'),
                    dict(id='Salary', name='Salary', type='numeric', format=money),
                    dict(id='Fiscal Year', name='Fiscal Year', type='numeric')
                ],
                data=df_init.to_dict("records"),
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(250, 250, 235)',  # stripe rows
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
1. Filter first by year, then filter by name (create an intermediate df before returning)
2. save the start-stop indices for each year in a dictionary
3. Commit to displayoing one year at a time and save each year's data in a separate df
"""


@app.callback(
    Output("tbl", "data"),
    Input("my-year-dropdown", "value"),
    Input("my-dynamic-input", "value")
)
def display_table(year_value, name_value):
    if not name_value:
        raise PreventUpdate
    if len(name_value) < 3:  # filtering on too few characters is slow
        raise PreventUpdate
    df_year = all_salaries[all_salaries['Fiscal Year'] == year_value]
    dff = df_year[(df_year['Name'].str.contains(name_value, case=False, regex=False)
                   | (df_year['Title'].str.contains(name_value, case=False, regex=False)))]
    return dff.to_dict("records")


# create a separate series to hold lowercase names. This will prevent .lower() being called every filter
# don't think it sped things up much
# lowercase_names = all_salaries['Name'].str.lower()


# @app.callback(
#     Output("tbl", "data"),
#     Input("my-dynamic-input", "value")
# )
# def display_table(value):
#     if not value:
#         raise PreventUpdate
#     if len(value) < 3:
#         raise PreventUpdate
#     dff = all_salaries[lowercase_names.str.contains(value, regex=False, case=False)]
#     return dff.to_dict("records")


if __name__ == '__main__':
    app.run_server(debug=True)
