import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from statsforecast import StatsForecast
from statsforecast.models import SeasonalNaive
from statsforecast.models import AutoARIMA
import matplotlib.pyplot as plt
from neuralforecast import NeuralForecast
from neuralforecast.models import NBEATS

st.balloons()
st.header("Ticker Forecaster is :blue[Born] :sunglasses:")

st.subheader("This is not an app providing investing advise 🏴")
st.divider()
st.write("""
The Bull Run App is a dynamic financial application designed to help \n
investors and traders navigate and capitalize on bullish market trends. 
Whether you're a seasoned investor or new to trading, the app provides tools, insights,\n
and analytics to support profitable decision-making \nduring market upswings.
""")

def fetch_historical_data(product_id, days, granularity):
    base_url = "https://api.exchange.coinbase.com"
    endpoint = f"/products/{product_id}/candles"
    
    # Prepare date ranges
    end_date = datetime.utcnow()  # Current time in UTC
    start_date = end_date - timedelta(days=days)  # Start date
    delta = timedelta(days=200)  # Maximum range per request (adjust if needed)
    
    all_data = []
    current_start = start_date
    
    while current_start < end_date:
        current_end = min(current_start + delta, end_date)
        params = {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
            "granularity": granularity
        }
        
        response = requests.get(base_url + endpoint, params=params)
        
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
        
        current_start = current_end  # Move to the next chunk
    
    # Convert to DataFrame
    columns = ["time", "low", "high", "open", "close", "volume"]
    df = pd.DataFrame(all_data, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert timestamp to datetime
    df = df.sort_values(by='time')  # Sort by time ascending
    return df

# Parameters
product_id = "ETH-USD"  # Replace with desired pair
days = 1000
granularity = 86400  # 1-day candles


product_id = st.text_input("Movie title", "ETH-USD")
# Fetch data
data = fetch_historical_data(product_id, days, granularity)

# Display and save data
# print(data)
# data.to_csv("btc_usd_300days.csv", index=False)
st.text("Choose Your Ticker.")
st.dataframe(data.style.highlight_max(axis=0))

st.write("Preprocessing the Timeseries")
# Prepare the data
data = data.reset_index()  # Ensure 'time' is reset if it was the index
data = data.rename(columns={'time': 'ds', 'open': 'y'})  # Rename columns for compatibility
data['ds'] = pd.to_datetime(data['ds'])  # Ensure 'ds' is datetime
data['unique_id'] = 'series_1'  # Add 'unique_id' column for single series

# Prepare dataset
fcst_data = data[['unique_id', 'ds', 'y']]

# Define the model
input_size = 300  # Set the input size (e.g., 30 historical steps)
horizon = 150  # Forecast 30 steps ahead

nf = NeuralForecast(
    models=[
        NBEATS(input_size=input_size, h=horizon, max_steps=200),  # Specify input_size and forecast horizon
    ],
    freq='D'  # Specify the frequency of your data
)

# Fit the model
nf.fit(fcst_data)
st.write("endpoint2")
st.write("Fitting the Model...")
# Forecast
forecast = nf.predict()
st.write("Predicting the Future Value...")

# Inspect the forecasted data
# print(forecast.head())


st.write("Plotting the Future Value...")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(fcst_data['ds'], fcst_data['y'], label='Historical Open', color='blue')
ax.plot(forecast['ds'], forecast['NBEATS'], label='Forecast', color='red')
ax.legend()
ax.set_title('Open Price Forecast with N-BEATS')
ax.set_xlabel('Date')
ax.set_ylabel('Open Price')

# st.write("endpoint3")
# Display the plot in Streamlit
st.pyplot(fig)
st.dataframe(fcst_data[["ds","y"]].style.highlight_max(axis=0))
