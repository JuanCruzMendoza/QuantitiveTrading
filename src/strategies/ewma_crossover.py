import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class EWMACrossover(Strategy):
    fast_period = 10  # Period for fast EWMA
    slow_period = 50  # Period for slow EWMA

    def init(self):
        # Calculate fast and slow EWMAs on close prices
        close = self.data.Close.s
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