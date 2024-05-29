# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import datetime
import time
from api_requests import fetch_total_data_number, fetch_individual_data, fetch_both_data
from utils import date_to_int, int_to_date

def main():

    st.set_page_config(layout="wide")


    st.title("Sensor Data Visualization")
    sensor_id = st.selectbox("Select Sensor ID", ["151", "152"])
    sensor_name = st.selectbox("Select Sensor Name", ["temp", "hum", "both"])
    slave_address = st.selectbox("Select Slave Address", ["1", "2", "3", "4", "5", "6"])
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    day_range = (end_date - start_date).days

    if day_range > 31:
        st.warning("Please select a range within a month")
    else:
        total_data = fetch_total_data_number(sensor_name, str(start_date), str(end_date), sensor_id, slave_address)
        if start_date == end_date:
            end_date = start_date + datetime.timedelta(days=1)

        start_date_int = date_to_int(start_date)
        end_date_int = date_to_int(end_date)
        start_date_slider = st.slider("Start Date", min_value=start_date_int, max_value=end_date_int, value=start_date_int)
        end_date_slider = st.slider("End Date", min_value=start_date_int, max_value=end_date_int, value=end_date_int)
        start_date_selected = int_to_date(start_date_slider)
        end_date_selected = int_to_date(end_date_slider)

        if sensor_name == "both":
            slave_address_temp = st.selectbox("Select Slave Address For Temperature", ["1", "2", "3", "4", "5", "6"])
            slave_address_hum = st.selectbox("Select Slave Address For Humidity", ["1", "2", "3", "4", "5", "6"])

        if st.button("Fetch Data"):
            if start_date and end_date:
                start_date_selected = pd.to_datetime(start_date_selected).tz_localize(None).tz_localize('UTC')
                end_date_selected = pd.to_datetime(end_date_selected).tz_localize(None).tz_localize('UTC')

                if sensor_name != "both":
                    data = fetch_individual_data(sensor_name, str(start_date), str(end_date), sensor_id, slave_address, total_data)
                    if data:
                        display_data(data, start_date_selected, end_date_selected)
                else:
                    start_time = time.time()
                    temp_data, hum_data = fetch_both_data(str(start_date), str(end_date), slave_address_temp, slave_address_hum, total_data)
                    display_both_data(temp_data, hum_data, start_date_selected, end_date_selected)
                    end_time = time.time()
                    st.write(f"Data fetching and processing time: {end_time - start_time:.2f} seconds")


def display_data(data, start_date_selected, end_date_selected):
    st.subheader("Data Table")
    df = pd.DataFrame(data)
    df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('UTC')
    filtered_df = df[(df['created_at'] >= start_date_selected) & (df['created_at'] <= end_date_selected)]
    st.write(filtered_df)
    display_statistics(filtered_df)
    display_line_chart(filtered_df, "Sensor Data",plot_height=800, plot_width=1800)

def display_both_data(temp_data, hum_data, start_date_selected, end_date_selected):
    temp_df = pd.DataFrame(temp_data)
    temp_df = temp_df[temp_df['sensor_name'] == "temp"]
    hum_df = pd.DataFrame(hum_data)
    hum_df = hum_df[hum_df['sensor_name'] == "hum"]
    temp_df['created_at'] = pd.to_datetime(temp_df['created_at']).dt.tz_convert('UTC')
    hum_df['created_at'] = pd.to_datetime(hum_df['created_at']).dt.tz_convert('UTC')
    filtered_temp_df = temp_df[(temp_df['created_at'] >= start_date_selected) & (temp_df['created_at'] <= end_date_selected)]
    filtered_hum_df = hum_df[(hum_df['created_at'] >= start_date_selected) & (hum_df['created_at'] <= end_date_selected)]

    
    st.subheader("Temperature Data")
    st.dataframe(filtered_temp_df,width=1800)
    display_statistics(filtered_temp_df)
    display_line_chart(filtered_temp_df, "Temperature Data", plot_height=800, plot_width=1800)

    # Add spacing
    st.write("")
    st.write("")
   
    st.subheader("Humidity Data")
    st.dataframe(filtered_hum_df,width=1800)
    display_statistics(filtered_hum_df)
    display_line_chart(filtered_hum_df, "Humidity Data", plot_height=800, plot_width=1800)

def display_statistics(df):

    st.subheader("Statistical Features")
    mean_value = round(df['value'].mean(), 2)
    max_value = round(df['value'].max(), 2)
    min_value = round(df['value'].min(), 2)

    max_date_time = df.loc[df['value'] == max_value, 'created_at'].values[0]
    min_date_time = df.loc[df['value'] == min_value, 'created_at'].values[0]

    max_date_str = pd.to_datetime(max_date_time).strftime('%Y-%m-%d %H:%M:%S')
    min_date_str = pd.to_datetime(min_date_time).strftime('%Y-%m-%d %H:%M:%S')
    max_day_str = pd.to_datetime(max_date_time).strftime('%A')
    min_day_str = pd.to_datetime(min_date_time).strftime('%A')

    st.write(f"Max Value: {max_value} (Recorded on {max_day_str}, {max_date_str})")
    st.write(f"Min Value: {min_value} (Recorded on {min_day_str}, {min_date_str})")

def display_line_chart(df, title,plot_height = 800,plot_width = 1800):
    st.subheader("Line Chart")
    fig = px.line(df, x='created_at', y='value', title=title)

    fig.update_layout(height=plot_height, width=plot_width)

    max_value = df['value'].max()
    min_value = df['value'].min()
    max_date_str = pd.to_datetime(df.loc[df['value'] == max_value, 'created_at'].values[0]).strftime('%Y-%m-%d %H:%M:%S')
    min_date_str = pd.to_datetime(df.loc[df['value'] == min_value, 'created_at'].values[0]).strftime('%Y-%m-%d %H:%M:%S')

    fig.add_trace(go.Scatter(
        x=[max_date_str], y=[max_value],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Max Value'
    ))

    fig.add_trace(go.Scatter(
        x=[min_date_str], y=[min_value],
        mode='markers',
        marker=dict(color='blue', size=10),
        name='Min Value'
    ))
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()

