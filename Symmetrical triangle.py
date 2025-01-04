"""
Created on Sun Dec 29 17:25:37 2024

@author: Deepak Dalal
"""

import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# Set date range for stock data retrieval
end_date = dt.date.today()  # Today's date as the end date
start_date = end_date - dt.timedelta(days=500)  # 500 days prior as the start date

# List of Nifty 500 stocks for pattern analysis
stocks = ['ABB.NS','ADANIENSOL.NS','ADANIENT.NS','ADANIGREEN.NS','ADANIPORTS.NS','ADANIPOWER.NS','ATGL.NS','AMBUJACEM.NS',
          'APOLLOHOSP.NS','ASIANPAINT.NS','AXISBANK.NS','BAJAJ-AUTO.NS','BAJFINANCE.NS','BAJAJFINSV.NS','BAJAJHLDNG.NS',
          'BANKBARODA.NS','BEL.NS','BHEL.NS','BPCL.NS','BHARTIARTL.NS','BOSCHLTD.NS','CANBK.NS','CHOLAFIN.NS',
          'CIPLA.NS','COALINDIA.NS','DLF.NS','DABUR.NS','DIVISLAB.NS','DRREDDY.NS','EICHERMOT.NS','GAIL.NS','GODREJCP.NS',
          'GRASIM.NS','HCLTECH.NS','HDFCBANK.NS','HDFCLIFE.NS','HAVELLS.NS','HEROMOTOCO.NS','HINDALCO.NS','HAL.NS',
          'HINDUNILVR.NS','ICICIBANK.NS','ICICIGI.NS','ICICIPRULI.NS','ITC.NS','IOC.NS','IRCTC.NS','IRFC.NS']

# Initialize lists to store trendline points
above_tradline_points = []
below_tradline_points = []

# Loop through each stock for analysis
for stock in stocks:
    # Download historical data for the stock
    data = yf.download(stock, start=start_date, end=end_date, interval="1D")
    data = np.round(data, 2)  # Round values to 2 decimal places

    # Identify the highest value and its corresponding date
    High = data["High"].max()
    High_date = data["High"].idxmax()
    High_position = data.index.get_loc(High_date)

    # Calculate positions for the trendline
    a = len(data) - High_position  # Relative position from the end of the data
    b = 1  # Most recent position

    # Extract relevant values for calculations
    y1 = data["High"].iloc[-a]
    y2 = data["High"].iloc[-b]

    # Calculate the slope and intercept for the upper trendline
    x1_num = (data.index[-a] - data.index[0]).days
    x2_num = (data.index[-b] - data.index[0]).days
    slope = (y2 - y1) / (x2_num - x1_num)
    intercept = y1 - (slope * x1_num)

    # Add a trendline column to the DataFrame
    data["Trendline"] = slope * ((data.index - data.index[0]).days) + intercept

    # Determine points above the trendline
    above_tradline = np.where(data["High"] > data["Trendline"], 1, 0)
    total_above_treadline_points = above_tradline.sum()

    # Identify the lowest value and its corresponding date
    Low = data["Low"].min()
    Low_date = data["Low"].idxmin()
    Low_position = data.index.get_loc(Low_date)

    # Calculate positions for the lower trendline
    c = len(data) - Low_position
    y01 = data["Low"].iloc[-c]
    y02 = data["Low"].iloc[-b]

    # Calculate the slope and intercept for the lower trendline
    x01_num = (data.index[-c] - data.index[0]).days
    x02_num = (data.index[-b] - data.index[0]).days
    slope = (y02 - y01) / (x02_num - x01_num)
    intercept = y01 - (slope * x01_num)

    # Add a lower trendline column to the DataFrame
    data["Trendline"] = slope * ((data.index - data.index[0]).days) + intercept

    # Determine points below the trendline
    below_tradline = np.where(data["Low"] < data["Trendline"], 1, 0)
    total_below_treadline_points = below_tradline.sum()

    # Check the count of points below the trendline
    if total_below_treadline_points < 5:
        print(f"{stock} has less than 5 points below the trendline.")

    # Append points count to respective lists
    above_tradline_points.append(total_above_treadline_points)
    below_tradline_points.append(total_below_treadline_points)

# Create Pandas Series for the above and below trendline data
above_tradline_series = pd.Series(above_tradline_points, index=stocks)
below_tradline_series = pd.Series(below_tradline_points, index=stocks)

# Sort stocks by trendline points
above_tradlines = above_tradline_series.sort_values(ascending=True)
below_tradlines = below_tradline_series.sort_values(ascending=True)

# Get the top stocks for analysis
values = above_tradlines.index
values1 = below_tradlines.index

best_stock_above = values[1:20]
best_stock_below = values1[1:20]

# Find the first common stock between the two lists
first_common_stock = []
for stock in best_stock_above:
    if stock in best_stock_below:
        first_common_stock.append(stock)
        break

print(first_common_stock)

# Download historical data for the first common stock
stocks_data = yf.download(first_common_stock, start=start_date, end=end_date, interval="1D")

# Calculate trendlines for the first common stock
High = stocks_data["High"].max()
High_date = stocks_data["High"].idxmax()
High_position = stocks_data.index.get_loc(High_date)

Low = stocks_data["Low"].min()
Low_date = stocks_data["Low"].idxmin()
Low_position = stocks_data.index.get_loc(Low_date)

x = len(stocks_data) - High_position
y = len(stocks_data) - Low_position
b = 1

# Define trendline points for plotting
trendline_points = [[(stocks_data.index[-y], stocks_data["Low"].iloc[-y]),
                     (stocks_data.index[-b], stocks_data["Low"].iloc[-b])],
                    [(stocks_data.index[-x], stocks_data["High"].iloc[-x]),
                     (stocks_data.index[-b], stocks_data["High"].iloc[-b])]]

# Configure and plot the candlestick chart with trendlines
fig = plt.figure(figsize=(16, 10))
mpf.plot(stocks_data, type='candle', style='charles', alines=trendline_points, volume=False, 
         title=f'{first_common_stock} Stock with Symmetrical Triangle')

# Display the plot
plt.show()
