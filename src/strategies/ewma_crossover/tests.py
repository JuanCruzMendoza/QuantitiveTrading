import sys
from pathlib import Path
# Add the root directory to the system path
# This allows importing modules from the src directory
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

# Or we can execute the script from the root directory with -m option

from src.strategies.ewma_crossover.ewma_crossover import VolTargetEWMACrossover
from backtesting import Backtest
import pandas as pd

# Backtest
strategy = VolTargetEWMACrossover
# Define the parameters for the backtest
bt_params = {'commission': 0.01, 'margin': 1.0, 'spread': 0.002}

# Parameters for the strategy
strategy.fast_period = 20
strategy.medium_period = 50
strategy.slow_period = 100

data = pd.read_csv('data/SPY_1D.csv', index_col='Date', parse_dates=True)

# Run the backtest
bt = Backtest(data, strategy=VolTargetEWMACrossover, cash=100000, commission=0.01, margin=1.0, spread=0.002)
results = bt.run()
print(results)