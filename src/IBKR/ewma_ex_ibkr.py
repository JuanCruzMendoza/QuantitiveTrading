import time
import pandas as pd
from ib_insync import *
from IBKR.ewma_ex_signal import generate_ewma_signal


# Connect to IBKR
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Define AAPL contract
contract = Stock('AAPL', 'SMART', 'USD')

class EWMACrossoverLive:
    short_span = 20
    long_span = 50
    position_size = 10  # Number of shares per trade

    def __init__(self, contract):
        self.contract = contract
        self.position = 0  # Track current position (for simulation)

    def fetch_data(self):
        # Fetch recent historical data (e.g., last 2 months of daily bars)
        bars = ib.reqHistoricalData(
            self.contract,
            endDateTime='',
            durationStr='2 M',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        df = pd.DataFrame(bars)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def run(self):
        while True:
            df = self.fetch_data()
            # Use the common signal generator on the latest closing prices
            signal = generate_ewma_signal(df['close'], self.short_span, self.long_span)
            current_price = df['close'].iloc[-1]
            print(f"Latest signal: {signal} at price {current_price}")

            # Place orders based on signal
            if signal == 'BUY':
                print("Placing BUY order")
                order = MarketOrder('BUY', self.position_size)
                ib.placeOrder(self.contract, order)
                self.position += self.position_size
            elif signal == 'SELL':
                print("Placing SELL order")
                order = MarketOrder('SELL', self.position_size)
                ib.placeOrder(self.contract, order)
                self.position -= self.position_size

            # Wait for a minute before the next check (adjust as needed)
            time.sleep(60)

# Create an instance of the live strategy and run it
live_strategy = EWMACrossoverLive(contract)

# Uncomment the next line to start live trading
live_strategy.run()

# When done, disconnect from IBKR
ib.disconnect()
