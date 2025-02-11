import pandas as pd
import os
import requests
import zipfile
import functions as f
import numpy as np

################################################################




### Defining folder paths for downloaded and cleaned data, as well as links for the surveys

raw_data_folder = r"INSERT DOWNLOAD FOLDER DIRECTORY HERE"
clean_data_folder = r"INSERT CLEAN DATA STORAGE DIRECTORY HERE"

if not os.path.exists(raw_data_folder):
    os.makedirs(raw_data_folder)

if not os.path.exists(clean_data_folder):
    os.makedirs(clean_data_folder)

survey_2022 = "https://info.stackoverflowsolutions.com/rs/719-EMH-566/images/stack-overflow-developer-survey-2022.zip"
survey_2023 = "https://cdn.stackoverflow.co/files/jo7n4k8s/production/49915bfd46d0902c3564fd9a06b509d08a20488c.zip/stack-overflow-developer-survey-2023.zip"
survey_2024 = "https://cdn.sanity.io/files/jo7n4k8s/production/262f04c41d99fea692e0125c342e446782233fe4.zip/stack-overflow-developer-survey-2024.zip"

links_list = [survey_2022, survey_2023, survey_2024]



### Downloading the survey data and opening them with Pandas

# By using rsplit, we can get the filename as it is stored in the StackOverflow servers to assign to our downloaded zips

for i in links_list:
    f.download_data(i, raw_data_folder, i.rsplit('/',1)[1])


