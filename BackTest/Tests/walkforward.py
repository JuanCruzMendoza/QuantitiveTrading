from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG # Data example
import pandas as pd
import matplotlib.pyplot as plt
import os

class WalkForward:
    def __init__(self, data, strategy, periods, sampleWindows, outSampleWindows, cash=10000, commission=0.001):
        self.data = data
        self.data.index = pd.to_datetime(self.data.index)
        self.strategy = strategy
        self.periods = periods
        self.cash = cash
        self.commission = commission

        self.startSample, self.endSample = sampleWindows
        startOut, endOut = outSampleWindows

        self.sampleWindows = self.data.loc[self.endSample:].index[0] - self.data.loc[self.startSample:].index[0]
        self.outSampleWindows = self.data.loc[endOut:].index[0] - self.data.loc[startOut:].index[0]

    def run(self):
        ### ARREGLAR ###
        startSample = self.data.loc[self.data.index[0]:].index[0]
        endSample = self.data.loc[startSample + self.sampleWindows:].index[0]
        startOutSample = endSample
        endOutSample = self.data.loc[startOutSample + self.outSampleWindows:].index[0]
        ### ARREGLAR ###

        for period in range(self.periods):
            dataSample = self.data[startSample:endSample]
            dataOutSample = self.data[startOutSample:endOutSample]
            '''
            Llamo al optimizador.
                - Le paso data Sample
                - Le paso strategy
            '''
            startSample = startOutSample
            endSample = startSample + self.sampleWindows

            startOutSample = endSample
            endOutSample = startOutSample + self.outSampleWindows

            print('Datta dentro de muestra: \n', dataSample)
            print('Data fuera de muestra: \n', dataOutSample)

class SmaCross(Strategy):
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, 10)
        self.sma2 = self.I(SMA, self.data.Close, 20)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()
print(GOOG)
walkforward = WalkForward(GOOG, SmaCross, 6, (pd.to_datetime('2004-08-19'), pd.to_datetime('2005-08-19')), (pd.to_datetime('2005-08-19'), pd.to_datetime(GOOG.index[-1])))
walkforward.run()