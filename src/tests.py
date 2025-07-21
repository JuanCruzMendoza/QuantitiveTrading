import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load data
data = pd.read_csv(
    "data/SPY_1D.csv",
    parse_dates=['Date'],
    index_col='Date',
    usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
)

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

# Run backtest
bt = Backtest(data, EWMACrossover, cash=10000, commission=0.002)
results = bt.run()

# Get trades from the backtest results
trades = results._trades

# Monte Carlo simulation: resample trades with replacement and calculate metrics
n_iter = 1000  # number of Monte Carlo iterations
metrics_list = []
equity_curves = []

# Risk-free rate (annual)
risk_free_rate = 0.01  # 1%

# Number of trading days in a year
trading_days_per_year = 252

for i in range(n_iter):
    # Sample with replacement from the trades dataframe
    sampled_trades = trades.sample(n=len(trades), replace=True)

    # Simulate an equity curve based on cumulative PnL
    initial_capital = 10000
    equity_curve = initial_capital + sampled_trades['PnL'].cumsum()
    equity_curves.append(equity_curve.values)

# Convert equity curves list to a DataFrame for easier manipulation
equity_curves_df = pd.DataFrame(equity_curves).T

# Calculate average equity curve and confidence intervals
average_equity = equity_curves_df.mean(axis=1)
confidence_interval = equity_curves_df.quantile([0.025, 0.975], axis=1)

# Plotting the equity curves
plt.figure(figsize=(12, 6))

# Plot a subset of individual equity curves for clarity
subset_size = 100  # Number of simulations to plot
for i in range(subset_size):
    plt.plot(equity_curves_df.iloc[:, i], color='gray', alpha=0.3)

# Plot average equity curve
plt.plot(average_equity, color='blue', label='Average Equity Curve', linewidth=2)

# Plot confidence intervals
plt.fill_between(average_equity.index, confidence_interval.loc[0.025], confidence_interval.loc[0.975],
                 color='blue', alpha=0.2, label='95% Confidence Interval')

plt.title('Monte Carlo Simulations of Equity Curves')
plt.xlabel('Trade Number')
plt.ylabel('Equity ($)')
plt.legend()
plt.show()
