import os
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SSID, TWILIO_AUTH_TOKEN, PHONE_NUMBER,WEATHER_API_KEY
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
from utils import request_wapi, get_forecast, create_df, send_message, get_date
import json

city = 'Villavicencio'
api_key = WEATHER_API_KEY
input_date= get_date()
response = request_wapi(api_key, city)
datos = []
for i in tqdm(range(24),colour = 'green'):
    datos.append(get_forecast(response,i))
df_rain = create_df(datos)
# Send Message
message_id = send_message(TWILIO_ACCOUNT_SSID,TWILIO_AUTH_TOKEN, city, input_date, df_rain)

print('Mensaje Enviado con exito ' + message_id)

