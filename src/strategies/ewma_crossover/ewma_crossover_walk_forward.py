import sys
from pathlib import Path
# Add the root directory to the system path
# This allows importing modules from the src directory
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

# Or we can execute the script from the root directory with -m option

from src.strategies.ewma_crossover.ewma_crossover import VolTargetEWMACrossover
from src.optimization.walk_forward import walk_forward_optimization

opt_params = {'fast_period': range(10, 50, 5), 
               "medium_period": range(15, 100, 5),
              'slow_period': range(30, 200, 10),
              "constraint": lambda p: p.fast_period < p.medium_period and p.medium_period < p.slow_period}

bt_params = {'commission': 0.01, 'margin': 1.0, 'spread': 0.002}

walk_forward_optimization(csv_path='data/SPY_1D.csv',
                          strategy=VolTargetEWMACrossover,
                          initial_cash=100000,
                          n_periods=10,
                          test_pct=0.3,
                          output_csv='src/strategies/ewma_crossover/walk_ewmavol_results.csv',
                          opt_kwargs= opt_params,
                          bt_kwargs=bt_params)
