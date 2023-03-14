"""
# Create, clean, and populate a table of football leagues across the globe 

SUMMARY:
--------
* DAG Name:
    FOOTBALL_LEAGUES
* Owner:
    Gabriel García
* Description:
    Dag runs on demand
"""
import json
from datetime import datetime, timedelta
import os
from airflow.models import Variable
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
import pandas as pd
from utils import get_data, clean_data

default_arguments = {   'owner': 'Gabogar',
                        'email': 'garciagabo1@gmail.com',
                        'retries': 1 ,
                        'retry_delay': timedelta(minutes=5)}

with DAG('FOOTBALL_LEAGUES',
         default_args = default_arguments,
         description='Extracting Data Football League' ,
         start_date = datetime(2023, 2, 26),
         schedule_interval = None,
         tags = ['leagues_data'],
         catchup=False) as dag :

         params_info = Variable.get("feature_info", deserialize_json=True)
         #df = pd.read_csv('/usr/local/airflow/df_ligas.csv')
         #df_team = pd.read_csv('/usr/local/airflow/team_table.csv')
         countries = ['SPAIN', 'ENGLAND', 'ITALY', 'GERMANY', 'FRANCE', 'PORTUGAL', 'NETHERLANDS', 'COLOMBIA']
         codes = ['esp', 'eng', 'ita', 'ger', 'fra', 'por', 'ned', 'col']
         
         def extract_info(countries, codes,**kwargs):
            list_df = []
            for country, code in zip(countries, codes):
                df = get_data(country, code)
                df = clean_data(df)
                list_df.append(df)
                print(f"finished {country} \n")
            df_final = pd.concat(list_df, axis = 0)
            df_final.to_csv('./premier_positions.csv', index=False)


         extract_data = PythonOperator(task_id='EXTRACT_FOOTBALL_DATA',
                                    provide_context=True,
                                    python_callable=extract_info,
                                    op_kwargs={"countries":countries,"codes":codes})
        
         delete_stage = SnowflakeOperator(

                    task_id='delete_data_stage',
                    sql='./queries/delete_stage.sql',
                    snowflake_conn_id='demo_snow',
                    warehouse=params_info["DWH"],
                    database=params_info["DB"],
                    role=params_info["ROLE"],
                    params=params_info
                    )
         
         create_stage = SnowflakeOperator(

                    task_id='create_data_stage',
                    sql='./queries/create_stage.sql',
                    snowflake_conn_id='demo_snow',
                    warehouse=params_info["DWH"],
                    database=params_info["DB"],
                    role=params_info["ROLE"],
                    params=params_info
                    )
         
         upload_stage = SnowflakeOperator(

                    task_id='upload_data_stage',
                    sql='./queries/upload_stage.sql',
                    snowflake_conn_id='demo_snow',
                    warehouse=params_info["DWH"],
                    database=params_info["DB"],
                    role=params_info["ROLE"],
                    params=params_info
                    )
         
         ingest_table = SnowflakeOperator(

                    task_id='ingest_table',
                    sql='./queries/upload_table.sql',
                    snowflake_conn_id='demo_snow',
                    warehouse=params_info["DWH"],
                    database=params_info["DB"],
                    role=params_info["ROLE"],
                    params=params_info
                    )

         extract_data >> delete_stage >> create_stage >> upload_stage >> ingest_table