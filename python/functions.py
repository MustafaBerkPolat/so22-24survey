import pandas as pd
import os
import requests
import urllib.request
import zipfile



##################################################
def download_data(link, folder, filename):
# This function is used to fetch the dataset used for this project from the internet 
# and download it to the specified folder with the specified filename
    
    downloaded_file = folder + "\\" + filename
    urllib.request.urlretrieve(link, downloaded_file)   
    print(f'File downloaded from {link} under {downloaded_file}')
##################################################





##################################################
def read_zip(folder, csv_file):
# This function is to retrieve the dataset used for this project from within the downloaded zip file
    with zipfile.ZipFile(folder) as z:
       with z.open(csv_file) as f:
          df = pd.read_csv(f)
    return df
##################################################





##################################################
def columns_bucket(df, main_col_list, filter_col_list, id_col):
# This function filters the dataframe df by a list of columns filter_col_list, and one additional column (or column list) id_col, and removes
# the list of columns from a list of columns main_col_list, and returns the filtered dataframe and the main column list minus removed
# column list

    removed_col_list = [x for x in main_col_list if x not in filter_col_list]

    if type(id_col) == str:
        filter_col_list.append(id_col)
    elif type(id_col) == list:
        for i in id_col:
            filter_col_list.append(i)
    df_filtered = df[filter_col_list]

    return (df_filtered, removed_col_list)
##################################################





##################################################
def detect_separator(df, x=50, separator=";"):
# This function checks a dataframe's columns' first x rows for whether they contain a separator character, typically
# a semicolon, and then returns a list of columns that have this separator character within the first x rows.
# A high x value can make this very slow, but a low x value can gloss over columns in certain edge cases that do use
# a separator character to handle strings as a checklist of entries that possess a characteristic.
    
    first_x_rows = df.head(x)

    separator_list = []
    for column in first_x_rows.columns:
        contains_separator = first_x_rows[column].apply(lambda y: separator in str(y)).any()
        if contains_separator:
            separator_list.append(column)

    return separator_list
##################################################





##################################################
def table_stack(df, id_col, col_name):
# This function is a simple stacking task to help automate the compression of a multitude of boolean columns into one column that counts the occurence of
# that column alongside the index column. This is much more effective than storing dozens of boolean columns, as we have a lot of rows that have only one
# boolean value and a ton of redundant Falses.

    df_temp = df.set_index(id_col).stack().reset_index()
    
    df_temp.columns = [id_col, col_name, 'bool_val_tmp']
    
    df_stacked = df_temp[df_temp['bool_val_tmp']==1]
    
    return df_stacked.drop(labels='bool_val_tmp', axis=1)
##################################################





##################################################
def split_string_checklist(df, column_name, separator=';', identifier='null'):
# This function takes a string column of a dataframe and splits this column into multiple boolean columns based on
# the occurence of a separator character, most typically a semicolon, and outputs a new dataframe containing these new
# bool columns
# The identifier input, if not left to its default value of 'null', adds a prefix before the column names to help identify shared column
# names between dataframes

# Making array from columns and discarding repeat entries to make it easier to work with
    arr = df[column_name].unique()

# Splitting values and making nested list with them
    nested_lists = [str(i).split(separator) for i in arr]


# Getting all the unique values from list (getting the new column names)
    split_values = set()
    
    for sublist in nested_lists:
        split_values.update(sublist)
    split_values = sorted(split_values)

    
    pairs = []
    names= []
    simple_names = []


# Making new df with boolean, isinstance to avoid null/nan values
    new_df = pd.DataFrame(df[column_name])
    for column in split_values:
        new_df[column] = df[column_name].apply(
            lambda x: column in x if isinstance(x, (list, str)) else False).astype(int)

    
# Replacing null values with True bool and non-null values with False bool for selected column for future analysis
    df_temp = pd.DataFrame(df)
    df_temp[column_name] = df_temp[column_name].apply(lambda x: True if pd.isnull(x) else False)

    
# Combining 'duplicate' columns with different notations into one column, since not every name is consistently formatted across years
# eg. 'Couch DB' is spelled as 'CouchDB' in one year
    for col in split_values:
        names.append(col)
        simple_names.append(col.replace(" ", "").replace("-", "").replace("_", "").lower())

    for i,name in enumerate(names):
        pairs.append([name, names[simple_names.index(simple_names[i])]])

    
    for col in pairs:
        if col[0] != col[1]:
            new_df[col[1]] = new_df[[col[0], col[1]]].any(axis=1).astype(int)

# Dropping the now unnecessary duplicate columns, and renaming the remaining column to include the optional identifier string
# at the start of the column names. This is useful as multiple dataframes can have columns that have the same name but represent
# different things (like the 'WantToWorkWith' and 'HaveWorkedWith' dataframes in this project)
    for col in pairs:
        if col[0] != col[1]:
            if col[0] in new_df.columns:
                new_df.drop(col[0], axis=1, inplace=True)
        else:
            if identifier != 'null':
                new_col = identifier + '-' + col[1]
                new_df[new_col] = new_df[col[1]]
                new_df.drop(col[1], axis=1, inplace=True)

        
# Combining new df with old one
    df_combined = pd.concat([df_temp*1, new_df], axis=1)
    df_combined.drop(column_name, axis=1, inplace=True)

    if 'nan' in df_combined.columns:
        df_combined.drop('nan', axis=1, inplace=True)

    
    return df_combined
##################################################




