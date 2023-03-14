import pandas as pd 
import random
import time
import os
from datetime import datetime
import hashlib


def id_generator(team):

    return hashlib.md5(f"{team}".encode()).hexdigest()[:10]

def get_data(league, code):

    tiempo = [1, 2, 3]

    url = f'https://www.espn.com.co/futbol/posiciones/_/liga/{code}.1'
    time.sleep(random.choice(tiempo))
    # Create a dataframe with the tables from the URL
    df = pd.read_html(url)
    # df is a list with two dataframes. One with the names of the footbal teams, and the another with the statistics from the team
    # Rename the column of the first df
    df[0].rename(columns={df[0].columns[0] : 'FOOTBALL_TEAM'}, inplace=True)
    # join both dfs into a new one
    df = pd.concat([df[0], df[1]], axis = 1)
    # assign the country
    df['COUNTRY'] = league

    return df

def clean_data(df):

    #df = pd.concat(list_df, axis = 0)
    # Clean the football team column. 
    df['FOOTBALL_TEAM'] = df['FOOTBALL_TEAM'].apply(lambda x: x[5:] if x[:2].isnumeric() == True else x[4:])

    df.insert(loc = 0,
          column = 'ID',
          value = df.apply(lambda row: id_generator(row['COUNTRY'] + row['FOOTBALL_TEAM']), axis = 1)
          )

    df['CREATED_TIME'] = datetime.now().strftime('%Y-%m-%d')

    return df