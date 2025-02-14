from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Replace these with your Alpaca API credentials (paper)
API_KEY = "PK95Z978MFTJA6C4G5Q6"
API_SECRET = "TrXgyPgDQgdNhgiaVdCoThz6EArGcPI3vts0efIo"

# Initialize Alpaca Trading Client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

# Preparing market order
market_order_data = MarketOrderRequest(
    symbol="BTC/USD",
    qty=0.001,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC
)

# Market order execution
market_order = trading_client.submit_order(
    order_data=market_order_data
)

# Preparing limit order
limit_order_data = LimitOrderRequest(
    symbol="BTC/USD",
    limit_price=17000,
    qty=0.001,
    side=OrderSide.SELL,
    time_in_force=TimeInForce.GTC
)

# Limit order execution
limit_order = trading_client.submit_order(
    order_data=limit_order_data
)
