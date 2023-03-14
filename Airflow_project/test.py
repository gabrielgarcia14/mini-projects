import pandas as pd 
import random
import time
import os
from datetime import datetime
from utils import get_data, clean_data

countries = ['SPAIN', 'ENGLAND', 'ITALY', 'GERMANY', 'FRANCE', 'PORTUGAL', 'NETHERLANDS', 'COLOMBIA']
codes = ['esp', 'eng', 'ita', 'ger', 'fra', 'por', 'ned', 'col']

list_df = []
for country, code in zip(countries, codes):
    df = get_data(country, code)
    df = clean_data(df)
    list_df.append(df)
    print(f"finished {country} \n")

df = pd.concat(list_df, axis = 0)
#df = get_data(dict_leagues)
#df = clean_data(list_df)
print(df)