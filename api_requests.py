# api_requests.py
import requests
import pandas as pd

API_URL = "https://bontonfoods.aqualinkbd.com/apiV2/datatables"

def fetch_total_data_number(sensor_name, start_date, end_date, sensor_id, slave_address):
    params = {
        "sensor_name": sensor_name,
        "startdate": start_date,
        "enddate": end_date,
        "sensor_id": sensor_id,
        "slave_address": slave_address,
    }
    response = requests.post(API_URL, data=params)
    total_data = response.json()["total"]
    return total_data

def fetch_individual_data(sensor_name, start_date, end_date, sensor_id, slave_address, dataview):
    params = {
        "sensor_name": sensor_name,
        "startdate": start_date,
        "enddate": end_date,
        "sensor_id": sensor_id,
        "slave_address": slave_address,
        "page": 0,
        "dataview": dataview,
    }
    response = requests.post(API_URL, data=params)
    if response.status_code == 200:
        data = response.json()["data"]
        return data
    else:
        return None

def fetch_both_data(start_date, end_date, slave_address_temp, slave_address_hum, dataview):
    
    temp_data = fetch_individual_data("temp",start_date,end_date,151,slave_address_temp,dataview)
    hum_data = fetch_individual_data("hum",start_date,end_date,152,slave_address_hum,dataview)
    

    print(len(temp_data),len(hum_data))

    return temp_data, hum_data
