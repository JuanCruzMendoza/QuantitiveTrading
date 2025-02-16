from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG # Data example
import pandas as pd
import matplotlib.pyplot as plt
import os

class BacktestInOutSample:
    def __init__(self, data, strategy, splitRatio=0.7, cash=10000, commission=0.001):
        self.daa = data
        self.strategy = strategy
        self.splitRatio = splitRatio
        self.cash = cash
        self.commission = commission

        os.makedirs(f'{self.strategy.__name__}-Results-BacktestInOut', exist_ok=True)
        self.ruta = 'SmaCross-Results-BacktestInOut'

        # Split data
        splitIndex = int(len(data) * splitRatio)
        self.dataSample = data.iloc[:splitIndex]
        self.dataOutSample = data.iloc[splitIndex:]

        self.dfMetrics = None

    def saveResults(self, results, flag):
        # Extraer las métricas
        metrics = {
            "Equity Final [$]": results["Equity Final [$]"],
            "Equity Peak [$]": results["Equity Peak [$]"],
            "Return [%]": results["Return [%]"],
            "Return (Ann.) [%]": results["Return (Ann.) [%]"],
            "Volatility (Ann.) [%]": results["Volatility (Ann.) [%]"],
            "Sharpe Ratio": results["Sharpe Ratio"],
            "Sortino Ratio": results["Sortino Ratio"],
            "Max. Drawdown [%]": results["Max. Drawdown [%]"],
            "# Trades": results["# Trades"],
            "Win Rate [%]": results["Win Rate [%]"]
        }

        if flag:
            self.dfMetrics = pd.DataFrame(metrics, index=["Resultados - sample"])
        else:
            dfNewRow = pd.DataFrame(metrics, index=["Resultados - out-sample"])
            df = pd.concat([self.dfMetrics, dfNewRow])
            print(df)
            fig, ax = plt.subplots(figsize=(8, 4))  # Tamaño ajustable
            ax.axis("tight")
            ax.axis("off")  # Ocultar ejes
            table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, 
                            cellLoc="center", loc="center")
            plt.savefig(f"{self.ruta}/ResultadosMetricsBacktest - {self.strategy.__name__}.png", bbox_inches="tight", dpi=300)


        dfTimeSeries = results._equity_curve
        numSeries = len(dfTimeSeries.columns)  # Cantidad de series a graficar

        fig, axes = plt.subplots(numSeries, 1, figsize=(10, 2 * numSeries), sharex=True)

        if numSeries == 1:  # Si solo hay una serie, `axes` no es una lista
            axes = [axes]

        # Graficar cada serie en un subplot diferente
        for ax, column in zip(axes, dfTimeSeries.columns):
            ax.plot(dfTimeSeries.index, dfTimeSeries[column], label=column)
            ax.set_ylabel(column)
            ax.legend(loc="best")
            ax.grid(True)

        if flag:
            plt.suptitle(f"Evolución de las Series In-Sample - {self.strategy.__name__}")
            plt.xlabel("Tiempo")
            plt.tight_layout()
            plt.savefig(f"{self.ruta}/ResultadosSeriesBacktest In-Sample - {self.strategy.__name__}.png", bbox_inches="tight", dpi=300)
        else:
            plt.suptitle(f"Evolución de las Series Out-Sample - {self.strategy.__name__}")
            plt.xlabel("Tiempo")
            plt.tight_layout()
            plt.savefig(f"{self.ruta}/ResultadosSeriesBacktest Out-Sample - {self.strategy.__name__}.png", bbox_inches="tight", dpi=300)

    def runBacktest(self):
        # Iteramos una vez para muestra y para para fuera de muestra
        for i in range(0,2):
            dataToUse = self.dataSample if i == 0 else self.dataOutSample
            if i == 0:
                ### LLAMO AL OPTIMIZADOR ###
                # Le paso la estrategia y la data
                pass
            bt = Backtest(dataToUse, self.strategy, cash=self.cash, commission=self.commission)
            results = bt.run()
            self.saveResults(results, True if i == 0 else False)
        return results


# Ejemplo de estrategia simple
class SmaCross(Strategy):
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, 10)
        self.sma2 = self.I(SMA, self.data.Close, 20)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Cargar datos de ejemplo y ejecutar el backtest
backtest = BacktestInOutSample(GOOG, SmaCross)
print(GOOG)
print("Resultados:")
print(backtest.runBacktest())
