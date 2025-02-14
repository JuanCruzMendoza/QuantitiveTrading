#%%
import pandas as pd
from backtesting import Backtest, Strategy
from ewma_ex_signal import generate_ewma_signal

# Load historical data from CSV
df = pd.read_csv("data/AAPL_1D.csv")

df.columns = [col.lower().capitalize() for col in df.columns]

# Convert the date column to datetime and set it as the index
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# Ensure the DataFrame contains the required columns
df = df[['Open', 'High', 'Low', 'Close', 'Volume']]




#%%

class EWMACrossoverBacktest(Strategy):
    short_span = 20
    long_span = 50

    def init(self):
        # Se requiere definir el método init, aunque no se use nada en él.
        pass

    def next(self):
        signal = generate_ewma_signal(self.data.Close, self.short_span, self.long_span)
        if signal == 'BUY' and self.position.size <= 0:
            if self.position:
                self.position.close()
            self.buy()
        elif signal == 'SELL' and self.position.size >= 0:
            if self.position:
                self.position.close()
            self.sell()

# Create and run the backtest (if you upgraded backtesting.py, you can add shorting=True)
bt = Backtest(df, EWMACrossoverBacktest, cash=10_000, commission=0.002)
results = bt.run()
print(results)
bt.plot()
