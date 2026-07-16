import numpy as np
import pandas as pd
from typing import Tuple

def calculate_position_size(
        account_size: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: float = 0.02
) -> Tuple[float, float]:

    risk_amount = account_size * risk_per_trade
    price_difference = abs(entry_price - stop_loss)

    if price_difference == 0:
        raise ValueError("Stop loss must be different from entry price")

    shares = risk_amount / price_difference
    position_cost = shares * entry_price

    return int(shares), position_cost

"""
    Calculate position size using fixed risk percentage

    Args:
        account_size: Total account size
        entry_price: Entry price
        stop_loss: Stop loss price
        risk_per_trade: Maximum % of account to risk (default 2%)

    Returns:
        (shares, position_cost)

    Example:
        shares, cost = RiskManager.calculate_position_size(
            account_size=10000,
            entry_price=150,
            stop_loss=145,
            risk_per_trade=0.02  # Risk 2% of account = $200
        )
        # If entry=150, stop=145, risk=$200
        # Then position size = 200 / (150-145) = 40 shares
    """
