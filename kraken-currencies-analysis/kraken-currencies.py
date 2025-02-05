import streamlit as st
import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Crear una instancia de la API de Kraken
api = krakenex.API()
k = KrakenAPI(api)

# Obtener los pares de divisas disponibles
pairs_data = k.get_tradable_asset_pairs()

# Extraer base y quote a partir de wsname
pairs_data[['base', 'quote']] = pairs_data['wsname'].str.split('/', expand=True)

# Limpiar espacios
pairs_data['base'] = pairs_data['base'].str.strip()
pairs_data['quote'] = pairs_data['quote'].str.strip()

# Crear listas únicas de divisas base y de cotización
base_currencies = pairs_data['base'].unique()
quote_currencies = pairs_data['quote'].unique()

# Título de la aplicación
st.title("Análisis de Divisas con Kraken")

# Establecer valores predeterminados
default_base = "ETH" if "ETH" in base_currencies else base_currencies[0]
default_quote = "EUR" if "EUR" in quote_currencies else quote_currencies[0]

# Seleccionar la divisa base y cotización
base = st.selectbox("Seleccionar divisa base:", base_currencies, index=list(base_currencies).index(default_base))
quote = st.selectbox("Seleccionar divisa de cotización:", quote_currencies, index=list(quote_currencies).index(default_quote))

if base and quote:
    selected_pair = f"{base}{quote}"
    st.write(f"Par seleccionado: {base}/{quote}")

    # Obtener el nombre alternativo del par (altname)
    altname = pairs_data.loc[(pairs_data['base'] == base) & (pairs_data['quote'] == quote), 'altname'].values[0]

    # Seleccionar el intervalo con valores discretos
    interval_options = {
        1: "1 minuto",
        5: "5 minutos",
        15: "15 minutos",
        30: "30 minutos",
        60: "1 hora",
        240: "4 horas",
        1440: "1 día",
        10080: "1 semana",
        21600: "15 días"
    }
    interval_label = st.selectbox("Selecciona el intervalo:", list(interval_options.values()))
    interval = [key for key, value in interval_options.items() if value == interval_label][0]

    try:
        # Obtener datos OHLC
        ohlc_data, _ = k.get_ohlc_data(altname, interval=interval)

        # Establecer `dtime` como índice si no lo está ya
        if 'dtime' in ohlc_data.columns:
            ohlc_data.set_index('dtime', inplace=True)

        # Eliminar la columna `time` si existe
        if 'time' in ohlc_data.columns:
            ohlc_data.drop(columns=['time'], inplace=True)

        # Renombrar columnas para una mejor comprensión
        ohlc_data.rename(columns={
            'close': 'Precio de Cierre',
            'Upper': 'Banda Superior',
            'Lower': 'Banda Inferior',
            'volume': 'Volumen'
        }, inplace=True)

        # Calcular Bandas de Bollinger
        window = st.slider("Selecciona el período para las Bandas de Bollinger:", 5, 50, 10)
        ohlc_data['SMA'] = ohlc_data['Precio de Cierre'].rolling(window=window).mean()
        ohlc_data['Banda Superior'] = ohlc_data['SMA'] + 2 * ohlc_data['Precio de Cierre'].rolling(window=window).std()
        ohlc_data['Banda Inferior'] = ohlc_data['SMA'] - 2 * ohlc_data['Precio de Cierre'].rolling(window=window).std()

        # Calcular si el volumen es alto
        ohlc_data['Volumen Alto'] = ohlc_data['Volumen'] > (
            ohlc_data['Volumen'].rolling(window=window).mean() + 0.5 * ohlc_data['Volumen'].rolling(window=window).std()
        )

        # Generar señales basadas en Bandas y Volumen
        ohlc_data['Señal de Compra'] = (
            (ohlc_data['Precio de Cierre'] < ohlc_data['Banda Inferior']) &
            (ohlc_data['Volumen Alto'])
        )
        ohlc_data['Señal de Venta'] = (
            (ohlc_data['Precio de Cierre'] > ohlc_data['Banda Superior']) &
            (ohlc_data['Volumen Alto'])
        )

        # Depuración: Verificar señales generadas
        st.write("Señales generadas (últimos 50 registros):")
        st.write(ohlc_data[['Precio de Cierre', 'Banda Inferior', 'Banda Superior', 'Volumen Alto', 'Señal de Compra', 'Señal de Venta']].tail(50))

        # Graficar los datos
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(ohlc_data.index, ohlc_data['Precio de Cierre'], label='Precio de Cierre', color='blue')
        ax.plot(ohlc_data.index, ohlc_data['Banda Superior'], label='Banda Superior', color='red', linestyle='--')
        ax.plot(ohlc_data.index, ohlc_data['Banda Inferior'], label='Banda Inferior', color='green', linestyle='--')

        # Añadir señales
        ax.scatter(ohlc_data.index[ohlc_data['Señal de Compra']],
                   ohlc_data['Precio de Cierre'][ohlc_data['Señal de Compra']], label='Señal de Compra', color='green', marker='^', alpha=1)
        ax.scatter(ohlc_data.index[ohlc_data['Señal de Venta']],
                   ohlc_data['Precio de Cierre'][ohlc_data['Señal de Venta']], label='Señal de Venta', color='red', marker='v', alpha=1)

        ax.set_title(f"Análisis de {base}/{quote} con Bandas de Bollinger y Volumen Optimizado")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Precio")
        ax.legend()
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.write(f"Error al obtener los datos OHLC: {e}")
