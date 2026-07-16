import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
from src.paper_trading.paper_trader import Trade

class PaperTradingDatabase:
    """SQLite database for storing trade history"""

    def __init__(self, db_path: str = "data/paper_trades.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                entry_signal TEXT,
                stop_loss REAL NOT NULL,
                take_profit REAL NOT NULL,
                exit_date TEXT,
                exit_price REAL,
                exit_signal TEXT,
                status TEXT DEFAULT 'OPEN',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Daily portfolio values table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_values (
                date TEXT PRIMARY KEY,
                portfolio_value REAL NOT NULL,
                cash REAL NOT NULL,
                equity REAL NOT NULL,
                realized_pnl REAL,
                unrealized_pnl REAL,
                daily_return REAL
            )
        ''')

        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                date TEXT PRIMARY KEY,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                profit_factor REAL,
                average_win REAL,
                average_loss REAL
            )
        ''')

        conn.commit()
        conn.close()

    def add_trade(self, trade: Trade):
        """Add a new trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO trades 
            (symbol, entry_date, entry_price, quantity, entry_signal, 
             stop_loss, take_profit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.symbol,
            trade.entry_date.isoformat(),
            trade.entry_price,
            trade.quantity,
            trade.entry_signal,
            trade.stop_loss,
            trade.take_profit,
            trade.status
        ))

        conn.commit()
        trade.trade_id = cursor.lastrowid
        conn.close()
        return trade

    def close_trade(self, trade_id: int, exit_price: float,
                   exit_date: datetime, exit_signal: str):
        """Close an open trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE trades 
            SET exit_price = ?, exit_date = ?, exit_signal = ?, status = ?
            WHERE trade_id = ?
        ''', (exit_price, exit_date.isoformat(), exit_signal, 'CLOSED', trade_id))

        conn.commit()
        conn.close()

    def get_all_trades(self) -> List[Dict]:
        """Get all trades"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM trades ORDER BY entry_date DESC')
        columns = [description[0] for description in cursor.description]
        trades = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return trades

    def save_daily_value(self, date: str, portfolio_value: float,
                        cash: float, equity: float, realized_pnl: float,
                        unrealized_pnl: float, daily_return: float):
        """Save daily portfolio value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO daily_values 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, portfolio_value, cash, equity,
              realized_pnl, unrealized_pnl, daily_return))

        conn.commit()
        conn.close()