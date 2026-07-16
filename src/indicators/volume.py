import pandas as pd

def calculate_volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculates the Simple Moving Average of Volume."""
    return volume.rolling(window=period).mean()

def calculate_volume_ratio(volume: pd.Series, volume_sma: pd.Series) -> pd.Series:
    """Calculates the ratio of current volume to its moving average."""
    # We use .replace(0, 1) or handle inf to avoid DivisionByZero errors
    return volume / volume_sma.replace(0, 1)