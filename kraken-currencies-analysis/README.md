# Analysis of Currencies with Kraken

## Project Overview
This project aims to retrieve and analyze the exchange rate data of currency pairs using the **Kraken API**. The data is visualized through an interactive **Streamlit** interface, where users can select different currency pairs and adjust time intervals for analysis. Additionally, **Bollinger Bands** are implemented to identify buy and sell signals based on price volatility and trading volume.

## Features
- **Real-time exchange rate data retrieval** from Kraken's API
- **Bollinger Bands implementation** to detect potential entry and exit points
- **Interactive Streamlit interface** for selecting currency pairs and time intervals
- **Graphical representation of price trends**
- **Data cleaning and processing** using Pandas and NumPy

## Technologies Used
- **Python 3.8+**
- **Streamlit** (for UI visualization)
- **krakenex** (for API communication with Kraken)
- **pykrakenapi** (for structured data retrieval)
- **Pandas** (for data manipulation)
- **NumPy** (for statistical calculations)
- **Matplotlib** (for graphical representation)

## Installation and Execution
### Prerequisites
Ensure you have **Python 3.8 or later** installed on your system.

### Installation
Clone this repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
Execute the following command to launch the Streamlit interface:
```bash
streamlit run Project_Kraken.py
```
This will open a browser window where you can select a currency pair and visualize its trends.

## Implementation Details
### Data Retrieval
- The **Kraken API** is used to fetch Open, High, Low, Close (**OHLC**) price data.
- Users can select currency pairs interactively using a dropdown menu.
- Different time intervals are available for detailed trend analysis.

### Bollinger Bands Calculation
- The **Simple Moving Average (SMA)** is calculated over a user-defined period.
- The **standard deviation** of prices is computed to determine price volatility.
- Upper and lower bands are set at **SMA ± (2 * standard deviation)**.
- Buy signals are generated when the price crosses below the lower band.
- Sell signals are generated when the price crosses above the upper band.

### Visualization
- Price trends and Bollinger Bands are plotted using **Matplotlib**.
- Buy and sell signals are marked with **green and red markers**.
- A data table displays the last 50 time intervals for validation.

## Error Handling
- API errors are managed using `try-except` blocks to prevent crashes.
- Invalid API responses are detected and handled gracefully.
- Streamlit displays error messages when data retrieval fails.

## Conclusion
This project integrates financial data analysis and interactive visualization to provide a **real-time currency market monitoring tool**. The combination of **Bollinger Bands and volume analysis** offers a structured approach to identifying trading opportunities.

Future enhancements may include:
- Additional technical indicators (MACD, RSI)
- Integration with machine learning models for predictive analysis
- Expansion to support multiple cryptocurrency exchanges

## Author
**Prudencio Ceada Morales**


