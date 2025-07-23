import pandas as pd
import numpy as np
from backtesting import Backtest

def walk_forward_optimization(
    csv_path,
    strategy,
    initial_cash=10_000,
    n_periods=5,
    test_pct=0.2,
    output_csv='wfo_results.csv',
    opt_kwargs=None,
    bt_kwargs=None
):
    """
    The function does walk-forward optimization with n_periods of training and testing.
    It saves the results to a CSV file.

    strategy: backtesting.py strategy sub class.
    test_pct: percentage of the out of sample data in each period.
    opt_kwargs (dict): parameters for the optimization, ranges of each parameter.
    bt_kwargs (dict): parameters for the backtest (comission, spread, margin)
    
    """
    df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
    N = len(df)
    results = []

    # Size of each period
    period_len = N // n_periods

    for i in range(n_periods):
        start = i * period_len
        end = start + period_len
        if end > N:
            end = N
        segment = df.iloc[start:end]
        test_size = int(len(segment) * test_pct)
        train_df = segment.iloc[:-test_size]
        test_df = segment.iloc[-test_size:]

        # Optimize on in-sample
        bt_train = Backtest(
            data=train_df,
            strategy=strategy,
            cash=initial_cash,
            **(bt_kwargs or {})
        )
        stats_train = bt_train.optimize(**(opt_kwargs or {}), 
                                        method="grid",
                                        max_tries=1000) 
        
        # Backtest on out-of-sample using best params
        best_params = stats_train['_strategy']._params
        bt_test = Backtest(
            test_df,
            strategy=strategy,
            cash=initial_cash,
            **(bt_kwargs or {})
        )

        ## **kwargs are read as parameters for the strategy
        stats_test = bt_test.run(**best_params)

        # Collect metrics
        res = {
            'period': i+1,
            'start': segment.index[-1],
            'end': segment.index[0],
            'Return [%]': stats_test['Return [%]'],
            'Sharpe': stats_test['Sharpe Ratio'],
            'MaxDrawdown [%]': stats_test['Max. Drawdown [%]'],
            '# Trades': stats_test['# Trades'],
            'WinRate [%]': stats_test['Win Rate [%]'],
            'Best Params': best_params
        }
        results.append(res)

    pd.DataFrame(results).to_csv(output_csv, mode="w", index=False)
    print(f"Saved walk-forward results to {output_csv}")
    return pd.DataFrame(results)

