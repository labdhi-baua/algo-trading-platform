import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class Trade:
    """Represents a single trade"""
    trade_id: int
    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: int
    entry_signal: str  # e.g., "RSI_OVERSOLD"
    stop_loss: float
    take_profit: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_signal: Optional[str] = None
    unrealized_pnl: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED_OUT

    @property
    def profit_loss_amount(self) -> float:
        """Calculate P&L in dollars"""
        if self.status == "OPEN":
            return 0
        return (self.exit_price - self.entry_price) * self.quantity

    @property
    def profit_loss_percent(self) -> float:
        """Calculate P&L in percentage"""
        if self.status == "OPEN":
            return 0
        return ((self.exit_price - self.entry_price) / self.entry_price) * 100

    @property
    def holding_days(self) -> int:
        """Days position was held"""
        end_date = self.exit_date or datetime.now()
        return (end_date - self.entry_date).days