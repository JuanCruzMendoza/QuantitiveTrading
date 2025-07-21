import pandas as pd
import numpy as np
from backtesting import Backtest

# Select strategy
from src.strategies.ewma_crossover import EWMACrossover
strategy_used = EWMACrossover

# Modify strategy parameters
strategy_used.slow_period = 50
strategy_used.fast_period = 15

# Cargar datos históricos
df = pd.read_csv(
    "data/SPY_1D.csv",
    parse_dates=['Date'],
    index_col='Date',
    usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
)

def monte_carlo_reshuffle(df, n_simulations=100, initial_balance=10000, commission=0.002):

    # Generar retornos diarios para las simulaciones
    returns = df['Close'].pct_change().dropna().values
    n_returns = len(returns)
    n_days = len(df)
    initial_price = df['Close'].iloc[0]

    # Almacenar resultados de simulaciones
    monte_carlo_results = []

    for _ in range(n_simulations):
        # Muestreo con reemplazo de retornos
        simulated_returns = np.random.choice(returns, size=n_returns, replace=True)
        
        # Generar precios sintéticos vectorizados
        growth_factors = np.insert(1 + simulated_returns, 0, 1)
        synthetic_prices = initial_price * np.cumprod(growth_factors)
        
        # Crear DataFrame sintético
        synthetic_df = pd.DataFrame({
            'Open': synthetic_prices,
            'High': synthetic_prices,
            'Low': synthetic_prices,
            'Close': synthetic_prices,
            'Volume': df['Volume'].values
        }, index=df.index)
        
        # Ejecutar backtest en datos sintéticos
        bt = Backtest(synthetic_df, strategy_used, cash=initial_balance, commission=commission)
        stats = bt.run()
        
        # Guardar métricas clave
        monte_carlo_results.append({
            'Retorno (%)': stats['Return [%]'],
            'Sharpe': stats['Sharpe Ratio'],
            'Drawdown (%)': stats['Max. Drawdown [%]'],
            'Operaciones': stats['# Trades']
        })

    # Convertir resultados a DataFrame
    results_df = pd.DataFrame(monte_carlo_results)

    # Mostrar análisis estadístico
    print("\nResumen estadístico de las simulaciones:")
    print(results_df.describe())

    # Resultados de la simulación original (opcional)
    original_bt = Backtest(df, strategy_used, cash=initial_balance, commission=commission)
    original_stats = original_bt.run()
    print("\nResultado en datos reales:")
    print(f"Retorno: {original_stats['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {original_stats['Sharpe Ratio']:.2f}")


monte_carlo_reshuffle(df)
