from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG # Data example
import pandas as pd
import matplotlib.pyplot as plt
import os

class WalkForwardStatic:
    def __init__(self, data, strategy, periods, sampleSize, cash=10000, commission=0.001):
        self.dataReIndex = data.reset_index(drop=False)
        self.periods = periods
        self.strategy = strategy
        self.sampleSize = sampleSize
        self.windowSize = int(len(self.dataReIndex)/periods)
        self.cash = cash
        self.commission = commission

        os.makedirs(f'{self.strategy.__name__}-Results-WalkForward', exist_ok=True)
        self.ruta = 'SmaCross-Results-WalkForward'
        os.makedirs(f'{self.ruta}/{self.strategy.__name__}-Curves Returns WalkForward', exist_ok=True)
        self.rutaReturns = 'SmaCross-Results-WalkForward/SmaCross-Curves Returns WalkForward'

    def splitData(self):
        periods = []
        start = 0
        end = self.windowSize

        for period in range(0, self.periods):
            periods.append(self.dataReIndex[start:end].reset_index(drop=False))
            start = periods[period].index[-1]
            end = start + self.windowSize

        dataSample = []
        dataOuSample = []
        for data in periods:
            splitIndex = int(len(data) * self.sampleSize)
            self.dataSample = data.iloc[:splitIndex]
            dataSample.append(self.dataSample)
            self.dataOutSample = data.iloc[splitIndex:]
            dataOuSample.append(self.dataOutSample)

        return dataSample, dataOuSample
    
    def saveResults(self, results, returns):
        fig, ax = plt.subplots(figsize=(20, 12))  # Crea la figura y el eje
    
        ax.axis("tight")  # Ajusta la tabla al espacio disponible
        ax.axis("off")  # Oculta los ejes
        
        # Crea la tabla en Matplotlib con los datos del DataFrame
        table = ax.table(cellText=results.values,  # Datos
                        colLabels=results.columns,  # Nombres de columnas
                        cellLoc="center",  # Alineación de las celdas
                        loc="center")  # Ubicación en el gráfico
        
        table.auto_set_font_size(False)
        table.set_fontsize(5)  # Ajusta el tamaño de fuente
        plt.draw()
        plt.savefig(f"{self.ruta}/Results WalkForward - {self.strategy.__name__}.png", bbox_inches="tight", dpi=300)
        plt.close()

        results.to_csv(f'{self.ruta}/Results CVS')
        count = 0
        for sample, outSample in returns:
            count += 1
            fig, axes = plt.subplots(2, 1, figsize=(8, 6))
            # Graficar en el primer subplot
            axes[0].plot(sample.index, sample, color='blue')
            axes[0].set_title("Returns Sample Period")
            axes[0].grid()

            # Graficar en el segundo subplot
            axes[1].plot(outSample.index, outSample, color='red')
            axes[1].set_title("Reurns Out Sample Period")
            axes[1].grid()

            plt.tight_layout()
            plt.savefig(f"{self.rutaReturns}/Returns period {count}.png")
        plt.close(fig)
            
    def run(self):
        curveReturns = []
        dataSample, dataOutSample = self.splitData()
        dfMetrics = None
        metrics = {
                "Equity Final [$]": None,
                "Equity Peak [$]": None,
                "Return [%]": None,
                "Return (Ann.) [%]": None,
                "Volatility (Ann.) [%]": None,
                "Sharpe Ratio": None,
                "Sortino Ratio": None,
                "Max. Drawdown [%]": None,
                "# Trades": None,
                "Win Rate [%]": None
            }

        dfMetrics = pd.DataFrame(metrics, columns=['Equity Final [$]', 'Equity Peak [$]', 'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 'Max. Drawdown [%]', '# Trades', 'Win Rate [%]', 'muestra/no muestra'])

        for periodo in range(len(dataSample)):
            # Crear un nuevo diccionario en cada iteración
            metrics = {
                "Equity Final [$]": None,
                "Equity Peak [$]": None,
                "Return [%]": None,
                "Return (Ann.) [%]": None,
                "Volatility (Ann.) [%]": None,
                "Sharpe Ratio": None,
                "Sortino Ratio": None,
                "Max. Drawdown [%]": None,
                "# Trades": None,
                "Win Rate [%]": None,
                "muestra/no muestra": None
            }

            # Evaluamos el periodo dentro de muestra
            bt = Backtest(dataSample[periodo].set_index('index'), self.strategy, cash=self.cash, commission=self.commission)
            resultsSample = bt.run()

            # Cargamos las métricas en un diccionario nuevo
            metrics["Equity Final [$]"] = resultsSample["Equity Final [$]"]
            metrics["Equity Peak [$]"] = resultsSample["Equity Peak [$]"]
            metrics["Return [%]"] = resultsSample["Return [%]"]
            metrics["Return (Ann.) [%]"] = resultsSample["Return (Ann.) [%]"]
            metrics["Volatility (Ann.) [%]"] = resultsSample["Volatility (Ann.) [%]"]
            metrics["Sharpe Ratio"] = resultsSample["Sharpe Ratio"]
            metrics["Sortino Ratio"] = resultsSample["Sortino Ratio"]
            metrics["Max. Drawdown [%]"] = resultsSample["Max. Drawdown [%]"]
            metrics["# Trades"] = resultsSample["# Trades"]
            metrics["Win Rate [%]"] = resultsSample["Win Rate [%]"]
            metrics['muestra/no muestra'] = 'Sample'

            if dfMetrics is None or dfMetrics.empty:
                dfMetrics = pd.DataFrame([metrics])  # Si está vacío, inicializa con `metrics`
            else:
                dfMetrics = pd.concat([dfMetrics, pd.DataFrame([metrics])], ignore_index=False)

            # Crear un nuevo diccionario para la muestra fuera de muestra
            metrics = {
                "Equity Final [$]": None,
                "Equity Peak [$]": None,
                "Return [%]": None,
                "Return (Ann.) [%]": None,
                "Volatility (Ann.) [%]": None,
                "Sharpe Ratio": None,
                "Sortino Ratio": None,
                "Max. Drawdown [%]": None,
                "# Trades": None,
                "Win Rate [%]": None,
                "muestra/no muestra": None
            }

            # Evaluamos el periodo fuera de muestra
            bt = Backtest(dataOutSample[periodo].set_index('index'), self.strategy, cash=self.cash, commission=self.commission)
            resultsOutSample = bt.run()

            # Cargamos las métricas en un diccionario nuevo
            metrics["Equity Final [$]"] = resultsOutSample["Equity Final [$]"]
            metrics["Equity Peak [$]"] = resultsOutSample["Equity Peak [$]"]
            metrics["Return [%]"] = resultsOutSample["Return [%]"]
            metrics["Return (Ann.) [%]"] = resultsOutSample["Return (Ann.) [%]"]
            metrics["Volatility (Ann.) [%]"] = resultsOutSample["Volatility (Ann.) [%]"]
            metrics["Sharpe Ratio"] = resultsOutSample["Sharpe Ratio"]
            metrics["Sortino Ratio"] = resultsOutSample["Sortino Ratio"]
            metrics["Max. Drawdown [%]"] = resultsOutSample["Max. Drawdown [%]"]
            metrics["# Trades"] = resultsOutSample["# Trades"]
            metrics["Win Rate [%]"] = resultsOutSample["Win Rate [%]"]
            metrics['muestra/no muestra'] = 'Out sample'

            if dfMetrics is None or dfMetrics.empty:
                dfMetrics = pd.DataFrame([metrics])  # Si está vacío, inicializa con `metrics`
            else:
                dfMetrics = pd.concat([dfMetrics, pd.DataFrame([metrics])], ignore_index=False)

            curveReturns.append((resultsSample._equity_curve['Equity'], resultsOutSample._equity_curve['Equity']))

        self.saveResults(dfMetrics, curveReturns)


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

walkforward = WalkForwardStatic(GOOG, SmaCross, 6, 0.7)
walkforward.run()


