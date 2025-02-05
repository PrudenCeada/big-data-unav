import streamlit as st
import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create a Kraken API instance
api = krakenex.API()
k = KrakenAPI(api)

# Retrieve available currency pairs
pairs_data = k.get_tradable_asset_pairs()

# Extract base and quote currencies from wsname
pairs_data[['base', 'quote']] = pairs_data['wsname'].str.split('/', expand=True)

# Trim spaces
pairs_data['base'] = pairs_data['base'].str.strip()
pairs_data['quote'] = pairs_data['quote'].str.strip()

# Create unique lists of base and quote currencies
base_currencies = pairs_data['base'].unique()
quote_currencies = pairs_data['quote'].unique()

# Application title
st.title("Currency Analysis with Kraken")

# Set default values
default_base = "ETH" if "ETH" in base_currencies else base_currencies[0]
default_quote = "EUR" if "EUR" in quote_currencies else quote_currencies[0]

# Select base and quote currency
base = st.selectbox("Select base currency:", base_currencies, index=list(base_currencies).index(default_base))
quote = st.selectbox("Select quote currency:", quote_currencies, index=list(quote_currencies).index(default_quote))

if base and quote:
    selected_pair = f"{base}{quote}"
    st.write(f"Selected pair: {base}/{quote}")

    # Get alternative pair name (altname)
    altname = pairs_data.loc[(pairs_data['base'] == base) & (pairs_data['quote'] == quote), 'altname'].values[0]

    # Select interval with discrete values
    interval_options = {
        1: "1 minute",
        5: "5 minutes",
        15: "15 minutes",
        30: "30 minutes",
        60: "1 hour",
        240: "4 hours",
        1440: "1 day",
        10080: "1 week",
        21600: "15 days"
    }
    interval_label = st.selectbox("Select interval:", list(interval_options.values()))
    interval = [key for key, value in interval_options.items() if value == interval_label][0]

    try:
        # Retrieve OHLC data
        ohlc_data, _ = k.get_ohlc_data(altname, interval=interval)

        # Set `dtime` as index if not already set
        if 'dtime' in ohlc_data.columns:
            ohlc_data.set_index('dtime', inplace=True)

        # Remove `time` column if it exists
        if 'time' in ohlc_data.columns:
            ohlc_data.drop(columns=['time'], inplace=True)

        # Rename columns for better clarity
        ohlc_data.rename(columns={
            'close': 'Closing Price',
            'Upper': 'Upper Band',
            'Lower': 'Lower Band',
            'volume': 'Volume'
        }, inplace=True)

        # Compute Bollinger Bands
        window = st.slider("Select period for Bollinger Bands:", 5, 50, 10)
        ohlc_data['SMA'] = ohlc_data['Closing Price'].rolling(window=window).mean()
        ohlc_data['Upper Band'] = ohlc_data['SMA'] + 2 * ohlc_data['Closing Price'].rolling(window=window).std()
        ohlc_data['Lower Band'] = ohlc_data['SMA'] - 2 * ohlc_data['Closing Price'].rolling(window=window).std()

        # Identify high volume periods
        ohlc_data['High Volume'] = ohlc_data['Volume'] > (
            ohlc_data['Volume'].rolling(window=window).mean() + 0.5 * ohlc_data['Volume'].rolling(window=window).std()
        )

        # Generate buy and sell signals based on Bollinger Bands and Volume
        ohlc_data['Buy Signal'] = (
            (ohlc_data['Closing Price'] < ohlc_data['Lower Band']) &
            (ohlc_data['High Volume'])
        )
        ohlc_data['Sell Signal'] = (
            (ohlc_data['Closing Price'] > ohlc_data['Upper Band']) &
            (ohlc_data['High Volume'])
        )

        # Debugging: Display generated signals
        st.write("Generated signals (last 50 records):")
        st.write(ohlc_data[['Closing Price', 'Lower Band', 'Upper Band', 'High Volume', 'Buy Signal', 'Sell Signal']].tail(50))

        # Plot the data
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(ohlc_data.index, ohlc_data['Closing Price'], label='Closing Price', color='blue')
        ax.plot(ohlc_data.index, ohlc_data['Upper Band'], label='Upper Band', color='red', linestyle='--')
        ax.plot(ohlc_data.index, ohlc_data['Lower Band'], label='Lower Band', color='green', linestyle='--')

        # Add signals
        ax.scatter(ohlc_data.index[ohlc_data['Buy Signal']],
                   ohlc_data['Closing Price'][ohlc_data['Buy Signal']], label='Buy Signal', color='green', marker='^', alpha=1)
        ax.scatter(ohlc_data.index[ohlc_data['Sell Signal']],
                   ohlc_data['Closing Price'][ohlc_data['Sell Signal']], label='Sell Signal', color='red', marker='v', alpha=1)

        ax.set_title(f"Analysis of {base}/{quote} with Bollinger Bands and Volume Optimization")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

        # Display the chart in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.write(f"Error retrieving OHLC data: {e}")
