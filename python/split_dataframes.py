import pandas as pd
import os
import requests
import zipfile
import functions as f
import numpy as np

################################################################


# Getting all downloaded zipfile names from our download folder, in case of manual renaming inbetween steps for readability

surveys = [survey for survey in os.listdir(raw_data_folder)]



# Loading all dataframes into a list in the order we defined the links previously, and fetching the year of the survey result
# as a new column on the dataframe for when we merge all dataframes and split by question categories rather than year
df_list= []

for i,j in enumerate(surveys):
    df_list.append(f.read_zip(raw_data_folder + "\\" + str(j), "survey_results_public.csv"))

    # To get the year as a string, we iterate through the entries of our surveys list to get the digits of the strings in order.
    # This assumes the filenames only have the year as numbers, but in this specific case there really isn't any reason for the files to
    # have another number in their names so it works
    year = ''
    for k in str(j):
        if k.isdigit():
            year += k
    df_list[i]['SurveyYear'] = int(year)



### Filtering unnecessary data and merging dataframes


# Getting the intersection of all dataframe columns in our dataframe list in order to discard any column that we cannot compare year-to-year

for i in range(len(df_list)):
    if i == 0:
        col0 = df_list[i].columns
    else :
        col0 = set(col0).intersection(df_list[i].columns)
    common_cols = list(col0)


# Dropping non-shared columns

for i in range(len(df_list)):
    df_list[i] = df_list[i][common_cols]


# Merging all dataframes in our list under a single master dataframe

for i,j in enumerate(df_list):
    if i == 0:
        df_master = j
    else :
        df_master = pd.concat([df_master, j])


# Running the detect_separator function to see which columns of this dataframe contain data that are checklists condensed into singular strings
# These columns are very annoying to work with as they are, so they will be split into multiple boolean columns at a later step

separator_list = f.detect_separator(df_master, 50, ';')


# By defining a new list of shared column names, we can erase columns from this list as we go along with our column categorization 
# so we have a clean list to fall back to, as well as a one-step solution to make a "misc" dataframe for any columns we deemed either
# unnecessary for our analysis or couldn't fit into a category

remaining_cols = common_cols
id_cols = ['ResponseId']
remaining_separator_cols = [x for x in separator_list]





# To start off, we organize the columns about the tech respondents have worked or want to work with into their own folders, as 
# we have a lot of dataframes and letting them all sit in one folder makes it harder to work with them outside of Python

HaveWorkedWith = [x for x in remaining_cols if 'HaveWorkedWith' in x]
WantToWorkWith = [x for x in remaining_cols if 'WantToWorkWith' in x]


if not os.path.exists(clean_data_folder + '\\HaveWorkedWith'):
    os.makedirs(clean_data_folder + '\\HaveWorkedWith')

if not os.path.exists(clean_data_folder + '\\WantToWorkWith'):
    os.makedirs(clean_data_folder + '\\WantToWorkWith')


for i,j in enumerate(HaveWorkedWith):
    df_HaveWorkedWith_temp, remaining_cols = f.columns_bucket(df_master, remaining_cols, [j], id_cols)
    if j in remaining_separator_cols:
        remaining_separator_cols.remove(j)
    df_HaveWorkedWith_temp.to_csv(f'{clean_data_folder}\\HaveWorkedWith\\df_' + j + '.csv', index=False)
    

for i,j in enumerate(WantToWorkWith):
    df_WantToWorkWith_temp, remaining_cols = f.columns_bucket(df_master, remaining_cols, [j], id_cols)
    if j in remaining_separator_cols:
        remaining_separator_cols.remove(j)
    df_WantToWorkWith_temp.to_csv(f'{clean_data_folder}\\WantToWorkWith\\df_' + j + '.csv', index=False)


# Then we define a third folder to contain all the other dataframes that correspond to columns that contain semicolon-separated
# strings as boolean checklists.


bool_dfs_folder = '\\BooleanDataframes'

if not os.path.exists(clean_data_folder + bool_dfs_folder):
    os.makedirs(clean_data_folder + bool_dfs_folder)

temp_list = []
for i,j in enumerate(remaining_separator_cols):
    df_temp, remaining_cols = f.columns_bucket(df_master, remaining_cols, [j], id_cols)
    temp_list.append(j)
    df_temp.to_csv(f'{clean_data_folder}\\{bool_dfs_folder}\\df_' + j + '.csv', index=False)

remaining_separator_cols = [x for x in remaining_separator_cols if x not in temp_list]



# Finally, we have all the columns that are not in checklist format. These columns correlate with each other in certain ways, and
# rather than storing each column in its own dataframe it makes sense here to do some manual work to decipher the surveys and categorize them based
# on these correlations.

# To get a better idea of which question in the survey each column corresponds to, it makes sense to get a list of unique entries of each
# column, which we then choose an arbitrary entry from and search the survey manually, as the data given does not include the
# information for corresponding questions outside of the survey pdf itself.
# However, this specific loop is not necessary for the functionality of this project otherwise

df_uniques = []
for column in remaining_cols:
    df_uniques.append(list(df_master[column].unique()))

col_labels = [[a] + b for a,b in zip(remaining_cols, df_uniques)]



# Then we just look at the remaining columns and group them manually

BasicInfo = ['MainBranch', 'RemoteWork', 'Age', 'SurveyYear']


df_BasicInfo, remaining_cols = f.columns_bucket(df_master, remaining_cols, BasicInfo, id_cols)
df_BasicInfo.to_csv(f'{clean_data_folder}\\df_BasicInfo.csv', index=False)


EduWork = ['EdLevel', 'YearsCode', 'YearsCodePro', 'WorkExp', 'OrgSize', 'Country', 'Currency', 'ConvertedCompYearly']


df_EduWork, remaining_cols = f.columns_bucket(df_master, remaining_cols, EduWork, id_cols)
df_EduWork.to_csv(f'{clean_data_folder}\\df_EduWork.csv', index=False)


SOInfo = ['SOVisitFreq', 'SOPartFreq', 'SOComm', 'SOAccount']


df_SOInfo, remaining_cols = f.columns_bucket(df_master, remaining_cols, SOInfo, id_cols)
df_SOInfo.to_csv(f'{clean_data_folder}\\df_SOInfo.csv', index=False)


ProfDevSeries = [x for x in remaining_cols if 'Knowledge_' in x]

for x in remaining_cols:
     if 'Frequency_' in x:
        ProfDevSeries.append(x)

ProfDevSeries.append('TimeSearching')
ProfDevSeries.append('TimeAnswering')


df_ProfDevSeries, remaining_cols = f.columns_bucket(df_master, remaining_cols, ProfDevSeries, id_cols)
df_ProfDevSeries.to_csv(f'{clean_data_folder}\\df_ProfDevSeries.csv', index=False)


df_Misc = df_master[remaining_cols]
df_Misc.to_csv(f'{clean_data_folder}\\df_Misc.csv', index=False)