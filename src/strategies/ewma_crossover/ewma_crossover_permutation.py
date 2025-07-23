import sys
from pathlib import Path
# Add the root directory to the system path
# This allows importing modules from the src directory
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

# Or we can execute the script from the root directory with -m option

from src.strategies.ewma_crossover.ewma_crossover import EWMACrossover, VolTargetEWMACrossover
from src.robustness_tests.monte_carlo_data_permutation import monte_carlo_data_permutation

bt_params = {'cash':100000, 'commission': 0.01, 'margin': 1.0, 'spread': 0.002}

monte_carlo_data_permutation(
    csv_path='data/SPY_1D.csv',
    strategy_used=VolTargetEWMACrossover,
    n_simulations=10,
    bt_kwargs=bt_params,
    log_filename='src/strategies/ewma_crossover/monte_carlo_permutation.log')