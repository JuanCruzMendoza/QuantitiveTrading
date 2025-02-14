import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Estrategia de muestra
class EWMACrossover(Strategy):
    fast_period = 20  # Período de la EWMA rápida
    slow_period = 50  # Período de la EWMA lenta

    def init(self):
        # Calcula la EWMA rápida y lenta sobre el precio de cierre
        close = self.data.Close.s
        self.fast_ewma = self.I(lambda x: x.ewm(span=self.fast_period, adjust=False).mean(), close)
        self.slow_ewma = self.I(lambda x: x.ewm(span=self.slow_period, adjust=False).mean(), close)

    def next(self):
        # Señal de compra: la EWMA rápida cruza por encima de la lenta
        if crossover(self.fast_ewma, self.slow_ewma):
            # Abre una posición larga si no se tiene ya
            if not self.position:
                self.buy()
        # Señal de salida: la EWMA lenta cruza por encima de la rápida
        elif crossover(self.slow_ewma, self.fast_ewma):
            if self.position:
                self.position.close()