"""
# Create, clean, and populate a table of football leagues across the globe,
using TaskGroup to parallelize extraction by country. 

SUMMARY:
--------
* DAG Name:
    FOOTBALL_LEAGUES_CHALLENGE
* Owner:
    Gabriel García
* Description:
    DAG runs Monday and Thursday at 7:00 UTC
"""
import json
from datetime import datetime, timedelta
import os
from airflow.models import Variable
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
from airflow.utils.task_group import TaskGroup
import pandas as pd
from utils import get_data, clean_data

default_arguments = {   'owner': 'Gabogar',
                        'email': 'garciagabo1@gmail.com',
                        'retries': 1 ,
                        'retry_delay': timedelta(minutes=5)}


with DAG('FOOTBALL_LEAGUES_CHALLENGE',
         default_args = default_arguments,
         description='Extracting Data Football League' ,
         start_date = datetime(2023, 2, 26),
         schedule_interval = "0 7 * * 1,4",
         tags = ['leagues_data'],
         catchup=False
         ) as dag :


         params_info = Variable.get("feature_info", deserialize_json=True)

         countries = ['SPAIN', 'ENGLAND', 'ITALY', 'GERMANY', 'FRANCE', 'PORTUGAL', 'NETHERLANDS', 'COLOMBIA']
         codes = ['esp', 'eng', 'ita', 'ger', 'fra', 'por', 'ned', 'col']

         def extract_info(country, code, **kwargs):
            df = get_data(country, code)
            df = clean_data(df)
            df.to_csv(f"./{code}.csv", index=False)
        
         with TaskGroup(group_id="extract_data") as extract_data_group:
            for country, code in zip(countries, codes):
                extract_data = PythonOperator(
                    task_id=f"extract_data_{code}",
                    python_callable=extract_info,
                    op_kwargs={"country": country, "code": code},
                )

         merge_data = PythonOperator(   
            task_id="merge_data",
            python_callable=lambda: pd.concat(
                [pd.read_csv(f"./{code}.csv") for code in codes]
            ).to_csv("./premier_positions.csv", index=False)
                )
            
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

         extract_data_group >> merge_data >> delete_stage >> create_stage >> upload_stage >> ingest_table