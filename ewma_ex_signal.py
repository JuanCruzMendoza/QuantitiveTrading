import pandas as pd

def generate_ewma_signal(series, short_span=20, long_span=50):
    """
    Generate a trading signal based on EWMA crossover.
    
    Parameters:
        series (pd.Series): The series of prices (e.g., closing prices).
        short_span (int): Span for the short-term EWMA.
        long_span (int): Span for the long-term EWMA.
        
    Returns:
        str: 'BUY' if short EWMA > long EWMA, 'SELL' otherwise.
    """
    series = pd.Series(series)
    ewma_short = series.ewm(span=short_span, adjust=False).mean()
    ewma_long = series.ewm(span=long_span, adjust=False).mean()
    if ewma_short.iloc[-1] > ewma_long.iloc[-1]:
        return 'BUY'
    else:
        return 'SELL'
