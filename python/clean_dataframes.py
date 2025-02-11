import pandas as pd
import os
import requests
import zipfile
import functions as f
import numpy as np

################################################################

# At this point we have a lot of csv files that have plenty of columns with NaN values, as well as csv files containing dataframes that
# all have only boolean columns outside of the ResponseId columns. The first problem is easy to solve using dropna with no issues,
# but the second problem has multiple situational fixes that may or may not be preferred based on the dataframe we apply the fix to

# The first step is to dropna the normal dataframes with mixed column types.

files_list = os.listdir(clean_data_folder)
files_list_df = [item for item in files_list if item.startswith('df_')]

for csv in files_list_df:
    df_temp = pd.read_csv(f'{clean_data_folder}\\{csv}')
    df_temp['ResponseId'] = np.arange(df_temp.shape[0]).astype(int)
    df_temp.dropna(axis=0, thresh=2, inplace=True)
    
    for column in separator_list:
        # This for loop would be useful, if not for our categorization of dataframes into folders. It is still left here
        # on the off-chance we made an oversight or go back to a "all files in one folder" format later on
        if column in df_temp:
            df_temp = f.split_string_checklist(df_temp, column, ';')
    df_temp.to_csv(f'{clean_data_folder}\\{csv}', index=False)







# When it comes to the dataframes that store checklist answer (ie. select all that apply)
# data as strings with semicolon separators, we split these into
# a multitude of boolean columns. This splitting makes the data easier to work with, but can increase filesizes depending on
# how many different possible entires there were on the checklist

files_list = os.listdir(clean_data_folder)
folders_list = [item for item in files_list if not item.startswith('df_')]

for folder in folders_list:
    files_list2 = os.listdir(clean_data_folder + '\\' + folder)
    files_list2_df = [item for item in files_list2 if item.startswith('df_')]
    
    for csv_name in files_list2_df:
        df_temp = pd.read_csv(f'{clean_data_folder}\\{folder}\\{csv_name}')
        
        df_temp['ResponseId'] = np.arange(df_temp.shape[0]).astype(int)
        df_temp.dropna(axis=0, thresh=2, inplace=True)
        

        for column in separator_list:
            if column in df_temp:
                df_temp = f.split_string_checklist(df_temp, column, ';')

        df_temp.to_csv(f'{clean_data_folder}\\{folder}\\{csv_name}', index=False)

        col_name = csv_name.lstrip('df_').rstrip('.csv')
        df_temp = f.table_stack(df_temp, id_cols[0], col_name)

        # In some cases, these boolean checklist dataframes can have a majority of rows where only one column is set to True, with
        # dozens set to false. In such cases, we end up with nearly 230k rows and dozens of columns that convey data that could just
        # as easily be represented with more rows, but only two columns: one to list ResponseId (which will no longer be unique
        # per row) and one to list the occurences of answers as strings.

        # If working strictly inside Python, we could use a dictionary to store the different possible answers, and have our
        # second column list only a numeric identifier that correspond to the answer, but such a simplification
        # makes the data harder to configure in external programs to work with.

        # As this simplification does not necessarily make the dataframes faster or easier to work with, we store these in a 
        # separate folder with separate .csv files so that we can pick and choose which variant we use depending
        # on whichever one is more convenient for the program we use them with
        if not os.path.exists(f'{clean_data_folder}\\{folder}\\stacked'):
            os.makedirs(f'{clean_data_folder}\\{folder}\\stacked')
        
        df_temp.to_csv(f'{clean_data_folder}\\{folder}\\stacked\\{csv_name}', index=False)