#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from ewma_crossover import EWMACrossover

# Data de muestra
data = pd.read_csv(
    "data/SPY_1D.csv",
    parse_dates=['Date'],
    index_col='Date',
    usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
)

def monte_carlo_resample_func(data, strategy, n_simulations=100, initial_balance=10000, commision=0.002, trading_days=252, risk_free_rate=0.04):
    bt = Backtest(data, strategy, cash=initial_balance, commission=commision)
    results = bt.run()

    # Get trades from the backtest results (assumes a 'PnL' column exists)
    trades = results._trades

    # Monte Carlo simulation: resample trades with replacement and calculate metrics
    n_iter = n_simulations  # number of Monte Carlo iterations
    metrics_list = []
    equity_curves= []

    for i in range(n_iter):
        # Sample with replacement from the trades dataframe
        sampled_trades = trades.sample(n=len(trades), replace=True)

        # Compute metrics based on the trade outcomes:
        total_pnl = sampled_trades['PnL'].sum()
        avg_trade = sampled_trades['PnL'].mean()
        std_trade = sampled_trades['PnL'].std()
        win_rate = (sampled_trades['PnL'] > 0).mean()  # fraction of winning trades

        # Simulate an equity curve based on cumulative PnL.
        # Starting with the same initial capital used in the backtest.
        initial_capital = 10000
        equity_curve = initial_capital + sampled_trades['PnL'].cumsum()
        equity_curves.append(equity_curve.values)

        # Calculate drawdown
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (running_max - equity_curve) / running_max
        max_drawdown_pct = drawdown.max() * 100  # Convert to percentage

        # Calculate daily returns from the equity curve
        daily_returns = equity_curve.pct_change().dropna()

        # Annualized return
        annualized_return = daily_returns.mean() * trading_days

        # Annualized volatility
        annualized_volatility = daily_returns.std() * np.sqrt(trading_days)

        # Sharpe ratio calculation
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

        metrics_list.append({
            'total_pnl': total_pnl,
            'avg_trade': avg_trade,
            'std_trade': std_trade,
            'win_rate': win_rate,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio
        })

    # Save the simulation metrics into a DataFrame
    metrics_df = pd.DataFrame(metrics_list)

    # General metrics of all simulations
    print(metrics_df.describe())

    # We plot based on confidence interval of 95%
    equity_curves_df = pd.DataFrame(equity_curves).T

    average_equity = equity_curves_df.mean(axis=1)
    confidence_interval = equity_curves_df.quantile([0.025, 0.975], axis=1)

    # Plotting the equity curves
    plt.figure(figsize=(12, 6))

    for i in range(n_simulations):
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

monte_carlo_resample_func(data, EWMACrossover)