import time
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

import pricemap

import plotly.graph_objects as go
import numpy as np
import chart_studio
import chart_studio.plotly as py

from apscheduler.schedulers.blocking import BlockingScheduler

user_name = "ricardo.delacruz"
api_key = "20Ilxq1trhOcXgRcwYdZ"
chart_studio.tools.set_credentials_file(username=user_name, api_key=api_key)

def create_fig(retailers, skus, title, price_evolution_data):   
    ## create traces
    fig = go.Figure()

    ## navigate for each retail and sku
    for retail, sku in zip(retailers, skus):
        ## select the sku and retail
        query = price_evolution_data.loc[(price_evolution_data['sku'] == sku) & (price_evolution_data['retail'] == retail)]
        price = query["price_float"] ## get the price
        date = query["date_time"] ## get the date
        
        fig.add_trace(go.Scatter(x=date.values,
                                 y=price.values,                                
                                 name=retail))
        
    fig.update_traces(mode='lines+markers')
    fig.update_layout(title={
                            'text': title,
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})
    
    return fig

sched = BlockingScheduler()
@sched.scheduled_job('cron', minute='01', hour='13,23')
def update_prices():

    #Lee los archivos .csv
    price_evolution_data = pd.read_csv("price_evolution.csv")
    retail_data = pd.read_csv("retail_data_final.csv")

    #Se aplica get_price_retail de pricemap.py a los datos de retail_data (EL código demora)
    df = pd.DataFrame(columns=price_evolution_data.columns)
    df["sku"], df["price"],df["price_tienda"],df["price_tarjeta"], df["retail"], df["date"], df["time"]= zip(*retail_data.apply(lambda x: pricemap.get_price_retail(x["uri"], x["retail"], x["sku"]), axis=1))

    #Se guardan/actualizan en .csv los datos dentro de price_evolution_data
    price_evolution_data = pd.concat([price_evolution_data, df], axis=0, ignore_index=True)
    price_evolution_data.to_csv("price_evolution.csv", index=False)

    ##Guarda en variable solo los datos de la ultima semana (GRAFICO EN 1 SEMANA)
    seven_days_ago = pricemap.get_time(today=False)
    price_evolution_data = price_evolution_data.loc[price_evolution_data['date'] >= seven_days_ago[0]]   

    #Se limpia los datos y se pasan al formato indicado
    price_evolution_data["price_float"] = price_evolution_data["price"].apply(lambda x: float(str(x).replace(',','')) if(x is not None) else "None")
    price_evolution_data["date_time"] = price_evolution_data[["date", "time"]].apply(lambda row: " ".join(row.values), axis=1)

sched.start()
