import numpy as np
import pandas as pd
from typing import Tuple

def calculate_stop_loss_and_tp(
        entry_price: float,
        strategy_atr: float = None,
        stop_loss_percent: float = None,
        reward_ratio: float = 2.0
) -> Tuple[float, float]:

    if strategy_atr is not None:
        # ATR-based stop loss
        stop_loss = entry_price - strategy_atr
        stop_distance = strategy_atr
    elif stop_loss_percent is not None:
        # Percentage-based stop loss
        stop_distance = entry_price * stop_loss_percent
        stop_loss = entry_price - stop_distance
    else:
        raise ValueError("Either ATR or stop_loss_percent must be provided")

    # Take profit based on reward:risk ratio
    take_profit = entry_price + (stop_distance * reward_ratio)

    return stop_loss, take_profit

"""
    Calculate stop loss and take profit levels

    Two methods:
    1. ATR-based (volatility-based)
    2. Percentage-based (fixed%)

    Example 1 - ATR based:
        sl, tp = RiskManager.calculate_stop_loss_and_tp(
            entry_price=100,
            strategy_atr=2.5,  # ATR is 2.5
            reward_ratio=2.0
        )
        # Stop = 100 - 2.5 = 97.5
        # TP = 100 + (2 * 2.5) = 105

    Example 2 - Percentage based:
        sl, tp = RiskManager.calculate_stop_loss_and_tp(
            entry_price=100,
            stop_loss_percent=0.05,  # 5% stop loss
            reward_ratio=2.0
        )
        # Stop = 95
        # TP = 110 (5% risk * 2 reward = 10% gain)
    """