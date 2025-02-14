# Script for fetching data from IBKR (change variables depending on the info you need)

import pandas as pd
from ib_insync import *
import datetime
import time

# Variables
csv_filename = "data/SPY_1D.csv"
BAR_SIZE = "1 day"
SYMBOL = "SPY"
START_YEAR = 1980

# Connect to IB TWS/Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7496 for live trading

# Define the contract 
contract = Stock(SYMBOL, 'SMART', 'USD')

# Define start and end dates
end_date = datetime.datetime.now()  # Current date
start_date = datetime.datetime(START_YEAR, 1, 1).date()  # Convert start_date to date

# Convert end_date to datetime.date for proper comparison
end_date = end_date.date()

# Storage for historical data
all_data = []

# Loop to request data in chunks
while end_date > start_date:
    # Convert datetime to IB format (YYYYMMDD HH:MM:SS)
    end_date_str = end_date.strftime('%Y%m%d %H:%M:%S')

    print(f"Fetching data until {end_date_str}...")

    # Request historical data
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_date_str,
        durationStr='365 D',  # Fetch 1 month per request
        barSizeSetting=BAR_SIZE,  # Adjust interval if needed
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )

    if not bars:
        print("No more data available.")
        break

    # Store retrieved data
    all_data.extend(bars)

    # Update end_date to fetch the previous chunk (convert bars[0].date to date)
    end_date = bars[0].date  # This is already a datetime.date object

    # Pause to avoid IB's rate limits
    time.sleep(2)

# Convert to Pandas DataFrame
df = pd.DataFrame(all_data)

# Convert timestamp to datetime
df['date'] = pd.to_datetime(df['date'])

# Save to CSV
df.to_csv(csv_filename, index=False)

# Print first few rows and confirm
print(f"Data saved to {csv_filename}")
print(df.head())

# Disconnect from IB
ib.disconnect()
