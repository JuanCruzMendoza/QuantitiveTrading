import pandas as pd
import numpy as np
from backtesting import Backtest

def monte_carlo_data_permutation(csv_path, strategy_used, n_simulations=100, bt_kwargs=None, log_filename='results_df.log'):
    """
    Perform Monte Carlo simulations by resampling with replacement the prices returns in percentage, 
    creating synthetic data with it, and backtesting the strategy.
    Besides, it saves the results to a log file.

    Note that this method breaks all market patterns and correlations, 
    and it is not suitable for strategies that rely on specific market conditions or patterns.

    Parameters:
        csv_path: Path to the CSV file containing historical price data.
        strategy_used: Strategy class to be used in the backtest.
        n_simulations: Number of Monte Carlo simulations to run.
        bt_kwargs (dict): Parameters for the backtest (commission, spread, margin).
        log_file: File to save the results of the simulations.
    """

    df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')

    # Generate daily returns in percentage of prices
    returns = df['Close'].pct_change().dropna().values
    n_returns = len(returns)
    n_days = len(df)
    initial_price = df['Close'].iloc[0]

    # Metrics
    metrics = ['Return [%]', "Return (Ann.) [%]", 'Sharpe Ratio', 'Max. Drawdown [%]', '# Trades', "Win Rate [%]",
               "Exposure Time [%]", "Volatility (Ann.) [%]"]

    # For storing results
    results_df = pd.DataFrame(columns=metrics)

    for _ in range(n_simulations):
        # Resample of returns with replacement
        simulated_returns = np.random.choice(returns, size=n_returns, replace=True)
        
        # Generate synthetic prices based on the resampled returns
        growth_factors = np.insert(1 + simulated_returns, 0, 1)
        synthetic_prices = initial_price * np.cumprod(growth_factors)
        
        synthetic_df = pd.DataFrame({
            'Open': synthetic_prices,
            'High': synthetic_prices,
            'Low': synthetic_prices,
            'Close': synthetic_prices,
            'Volume': df['Volume'].values
        }, index=df.index)
        
        # Backtest with the synthetic data
        bt = Backtest(synthetic_df, strategy_used, **(bt_kwargs or {}))
        stats = bt.run()
        
        # Metrics
        row = {metric: stats[metric] for metric in metrics}
        results_df = pd.concat([results_df, pd.DataFrame([row])], ignore_index=True)

    results_df['# Trades'] = results_df['# Trades'].astype(int)

    # Summary of the simulations
    summary = results_df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).round(2)

    # Results of the original backtest
    original_bt = Backtest(df, strategy_used, **(bt_kwargs or {}))
    original_stats = original_bt.run()

    # Saving results to log file
    with open(log_filename, 'w') as f:
        f.write("Original Backtest Results:\n")
        f.write(original_stats.to_string() + "\n\n")
        f.write("Monte Carlo Simulation Summary:\n")
        f.write(summary.to_string() + "\n\n")

    return results_df