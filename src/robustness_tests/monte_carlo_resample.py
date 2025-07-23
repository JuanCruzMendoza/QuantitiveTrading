import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from backtesting import Backtest

def monte_carlo_resample(csv_path, strategy, n_simulations=100, initial_capital=100000, bt_kwargs=None, 
                              log_filename= "monte_carlo_resample.log", plot_file="monte_carlo_resample.png", trading_days=252, risk_free_rate=0.04):

    """
    Perform Monte Carlo resampling on backtest trades with replacement to analyze strategy robustness.
    Then, it plots the equity curves of the simulations along with confidence intervals.

    Parameters:
    - csv_path: Path to the CSV file containing historical data.
    - strategy: The trading strategy to be backtested (in backtesting.py format).
    - n_simulations: Number of Monte Carlo simulations to run.
    - bt_kwargs: Additional keyword arguments for the Backtest class (commission, margin, etc.)
    """

    data = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')

    ### Initial backtest
    bt = Backtest(data, strategy, cash=initial_capital, **(bt_kwargs or {}))
    results = bt.run()

    # Get trades from the backtest results (assumes a 'PnL' column exists)
    trades = results._trades

    ### Monte Carlo simulation: resample trades with replacement and calculate metrics
    metrics_list = []
    equity_curves= []

    for i in range(n_simulations):
        # Sample with replacement from the trades dataframe
        sampled_trades = trades.sample(n=len(trades), replace=True)

        # Compute metrics based on the trade outcomes:
        total_pnl = sampled_trades['PnL'].sum()
        avg_trade = sampled_trades['PnL'].mean()
        std_trade = sampled_trades['PnL'].std()
        win_rate = (sampled_trades['PnL'] > 0).mean()  # fraction of winning trades

        # Simulate an equity curve based on cumulative PnL.
        # Starting with the same initial capital used in the backtest.
        equity_curve = initial_capital + sampled_trades['PnL'].cumsum()
        equity_curves.append(equity_curve.values)

        # Calculate drawdown pct
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (running_max - equity_curve) / running_max
        max_drawdown_pct = drawdown.max() * 100  # Convert to percentage

        # Calculate sharpe ratio
        daily_returns = equity_curve.pct_change().dropna()
        annualized_return = daily_returns.mean() * trading_days
        annualized_volatility = daily_returns.std() * np.sqrt(trading_days)
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

    with open(log_filename, 'w') as log_file:
        log_file.write("Monte Carlo Resampling Results:\n")
        log_file.write(metrics_df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).round(2).to_string())

    ### Plotting

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
    
    # Plot line for initial capital
    plt.axhline(y=initial_capital, color='red', linestyle='--', label='Initial Capital')

    plt.title('Monte Carlo Simulations of Equity Curves')
    plt.xlabel('Trade Number')
    plt.ylabel('Equity ($)')
    plt.legend()
    plt.grid()
    plt.show()

    # Save the plot
    plt.savefig(plot_file, dpi=300)