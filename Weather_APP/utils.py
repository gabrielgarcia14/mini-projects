import pandas as pd
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SSID,TWILIO_AUTH_TOKEN,PHONE_NUMBER
from datetime import datetime
import requests
from requests import Request, Session
import json

def get_date():

    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")

    return input_date

def request_wapi(api_key, query):

    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=no&alerts=no'

    try :
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)

    return response

def get_forecast(response, i):
    place = f"{response['location']['name']}-{response['location']['region']}-{response['location']['country']}"
    date_forecast = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hour_forecast = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condition = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temp_c = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    will_rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    return place, date_forecast, hour_forecast, condition, temp_c, will_rain, prob_rain

def create_df(data):

    cols = ['place', 'date_forecast', 'hour_forecast', 'condition', 'temp_c', 'will_rain', 'prob_rain']
    df = pd.DataFrame(data, columns=cols)
    df['prob_rain_%'] = df.prob_rain.apply(lambda x: str(x) + '%')
    df = df.sort_values(by = 'hour_forecast', ascending = True)

    df_rain = df[df['will_rain'] == 1][['hour_forecast', 'condition', 'prob_rain_%']].reset_index(drop = True)
    df_rain.set_index('hour_forecast', inplace = True)

    return df_rain

def send_message(TWILIO_ACCOUNT_SSID, TWILIO_AUTH_TOKEN, city, date, df):

    account_sid = TWILIO_ACCOUNT_SSID
    auth_token = TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    body_message = f"Take Care!! In {city} at {date} there's a high probability to rain at:\n\n\
    {str(df)}"

    message = client.messages \
                    .create(
                        body = body_message,
                        from_ = PHONE_NUMBER,
                        to='+573502695238'
                    )

    return message.sid
