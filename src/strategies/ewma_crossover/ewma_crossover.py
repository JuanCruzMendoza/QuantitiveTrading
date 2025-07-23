import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

"""
Notes to remember for future strategies:
 - The `I()` method is used to register indicators in the strategy.
 - If order's size >= 1, it buys that many shares
   If size_frac < 1, it will buy a fraction of the current equity (if we want 100%, we write size_frac=0.999)
   Still, it is buying shares, and not fractions of shares (can be changed)
"""

class EWMACrossover(Strategy):
    fast_period = 10  # Period for fast EWMA
    slow_period = 50  # Period for slow EWMA

    def init(self):
        # Calculate fast and slow EWMAs on close prices
        close = self.data.Close.s # Needs to be a Series for I() to work
        self.fast_ewma = self.I(lambda x: x.ewm(span=self.fast_period, adjust=False).mean(), close)
        self.slow_ewma = self.I(lambda x: x.ewm(span=self.slow_period, adjust=False).mean(), close)

    def next(self):
        # Buy when fast EWMA crosses above slow EWMA
        if crossover(self.fast_ewma, self.slow_ewma):
            if not self.position:
                self.buy()
        # Exit when slow EWMA crosses above fast EWMA
        elif crossover(self.slow_ewma, self.fast_ewma):
            if self.position:
                self.position.close()



class VolTargetEWMACrossover(Strategy):
    # An EWMA crossover strategy with volatility targeting (meaning, it changes the position size based on volatility)
    fast_period = 10
    slow_period = 50
    vol_window = 20         # days to estimate vol
    annual_target = 0.15    # 15% annualized volatility target

    def init(self):
        close = self.data.Close.s # Needs to be a Series for I() to work
        # EWMAs
        self.fast_ewma = self.I(lambda x: x.ewm(span=self.fast_period, adjust=False).mean(), close)
        self.slow_ewma = self.I(lambda x: x.ewm(span=self.slow_period, adjust=False).mean(), close)
        # Calculate daily return and rolling volatility
        returns = np.log(close / close.shift(1))
        self.vol = self.I(lambda x: x.rolling(self.vol_window).std(), returns)

    def next(self):
        if len(self.vol) < self.vol_window or self.vol[-1] == 0:
            return  # wait for vol data

        # Convert daily vol -> annualized
        daily_vol = self.vol[-1]
        annual_vol = daily_vol * np.sqrt(252)

        # Determine fraction of capital to deploy today
        size_frac = self.annual_target / annual_vol
        size_frac = min(size_frac, 0.999)  # cap at 100% of equity

        if crossover(self.fast_ewma, self.slow_ewma):
            if not self.position:

                self.buy(size=size_frac)

        elif crossover(self.slow_ewma, self.fast_ewma):
            if self.position:
                self.position.close()