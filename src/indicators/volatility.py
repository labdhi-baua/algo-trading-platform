import pandas as pd
import numpy as np
from src.indicators.base import calculate_true_range

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """ATR: Volatility for stop placement"""
    return calculate_true_range(high, low, close).rolling(window=period).mean()

def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Bollinger Bands: Mean reversion levels"""
    sma = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower