"""
A script to process the georgia salaries made available on https://open.ga.gov/
with the eventual goal of creating a dashboard to visualize salary data
"""

import pandas as pd
import pickle

# Is it more efficient to parse all three names at once?
def get_last(name):
    """
    Get the state employee's last name
    :param name: the name as provided in the NAME field
    :return: the employee's last name
    """
    return name.split(',')[0]


def get_first(name):
    """
    Get the state employee's first name.
    Catches the error thrown when trying to get the first name for employees
    listed as 'STUDENT EMPLOYEE'
    :param name: the name as provided in the NAME field
    :return: the employee's first name
    """
    try:
        f_name = name.split(',')[1].split(' ')[0]
    except IndexError:
        f_name = 'STUDENT EMPLOYEE'

    return f_name


def get_middle(name):
    """
    Get the state employee's middle name or initial.
    If no middle name or initial, impute nothing
    :param name: the name as provided in the NAME field
    :return: the employee's middle name or initial
    """
    try:
        m_name = name.split(',')[1].split(' ')[1]
    except IndexError:
        m_name = ''

    return m_name


print("Loading dataset")
all_salaries = pd.read_csv('SalaryTravelDataExportAllYears.txt', encoding='latin-1')

print("Extracting names and formatting values")
all_salaries['FIRST_NAME'] = all_salaries['NAME'].apply(get_first)
all_salaries['MIDDLE_NAME'] = all_salaries['NAME'].apply(get_middle)
all_salaries['LAST_NAME'] = all_salaries['NAME'].apply(get_last)

# format name as first + last
# middle name parsing can be removed
all_salaries['NAME'] = (all_salaries['FIRST_NAME'].apply(str.capitalize)
                        + ' '
                        + all_salaries['LAST_NAME'].apply(str.capitalize))

# there are a few nan Titles, so fill those before changing values to title case
all_salaries['TITLE'] = (all_salaries['TITLE'].fillna('None')
                                              .apply(str.title))

# Reformat organization values as title-case
all_salaries['ORGANIZATION'] = all_salaries['ORGANIZATION'].apply(str.title)


#  sort dataframe by year so displayed
#  results table appears in chronological order
all_salaries = all_salaries.sort_values(by=['FISCAL_YEAR', 'SALARY'], ascending=[True, False])

# only keep columns relevant to dashboard
all_salaries = all_salaries[['NAME', 'TITLE', 'ORGANIZATION', 'SALARY', 'FISCAL_YEAR']]

# rename columns
all_salaries = all_salaries.rename(columns={'NAME': 'Name',
                                            'TITLE': 'Title',
                                            'ORGANIZATION': 'Organization',
                                            'SALARY': 'Salary',
                                            'FISCAL_YEAR': 'Fiscal Year'})

with open('all_salaries.pickle', 'wb') as file1:
    pickle.dump(all_salaries, file1)



