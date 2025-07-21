#%%
from ib_insync import *

# Connect to IB TWS/Gateway
ib = IB()
ib.connect('127.0.0.1', 7497)  # Use 7496 for live trading

# Define the contract (Example: Apple stock)
contract = Stock('AAPL', 'SMART', 'USD')

# Create a market order to buy 10 shares
order = MarketOrder('BUY', 10)

# Place the trade
trade = ib.placeOrder(contract, order)

# Wait for order status update
ib.sleep(2)

# Print order status
print(trade)

# Disconnect
ib.disconnect()

