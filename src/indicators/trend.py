import pandas as pd
import numpy as np
from src.indicators.base import calculate_true_range


def calculate_sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(period).mean()


def calculate_ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    # Using your shared utility from base.py
    atr = calculate_true_range(high, low, close).rolling(window=period).mean()

    plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
    minus_di = 100 * minus_dm.rolling(window=period).mean() / atr

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.rolling(window=period).mean()


def get_support_resistance(high: pd.Series, low: pd.Series, period: int = 20):
    resistance = high.rolling(period).max()
    support = low.rolling(period).min()
    return support, resistance