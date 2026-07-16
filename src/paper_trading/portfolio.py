import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
from src.paper_trading.paper_trader import Trade
from src.paper_trading.database import PaperTradingDatabase


class VirtualPortfolio:
    """Manages virtual portfolio of paper trades"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, List[Trade]] = {}  # symbol -> list of open trades
        self.closed_trades: List[Trade] = []
        self.database = PaperTradingDatabase()
        self.daily_values = []
        self.trade_counter = 0

    def open_position(self, symbol: str, quantity: int,
                      entry_price: float, entry_signal: str,
                      stop_loss: float, take_profit: float) -> Trade:
        """
        Open a new position

        Example:
            portfolio.open_position(
                symbol="AAPL",
                quantity=10,
                entry_price=150.00,
                entry_signal="RSI_OVERSOLD",
                stop_loss=145.00,
                take_profit=160.00
            )
        """

        trade_cost = quantity * entry_price
        if trade_cost > self.cash:
            raise ValueError(f"Insufficient cash. Need ${trade_cost}, have ${self.cash}")

        trade = Trade(
            trade_id=self.trade_counter,
            symbol=symbol,
            entry_date=datetime.now(),
            entry_price=entry_price,
            quantity=quantity,
            entry_signal=entry_signal,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        self.trade_counter += 1
        self.cash -= trade_cost

        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)

        # Save to database
        self.database.add_trade(trade)

        return trade

    def close_position(self, symbol: str, exit_price: float,
                       exit_signal: str, trade_index: int = 0):

        if symbol not in self.positions or len(self.positions[symbol]) <= trade_index:
            raise ValueError(f"No position found for {symbol}")

        trade = self.positions[symbol][trade_index]
        proceeds = trade.quantity * exit_price

        trade.exit_date = datetime.now()
        trade.exit_price = exit_price
        trade.exit_signal = exit_signal
        trade.status = "CLOSED"

        self.cash += proceeds
        self.closed_trades.append(trade)

        # Update database
        self.database.close_trade(
            trade.trade_id,
            exit_price,
            trade.exit_date,
            exit_signal
        )

        # Remove from open positions
        self.positions[symbol].pop(trade_index)
        if not self.positions[symbol]:
            del self.positions[symbol]

    def update_position_prices(self, price_data: Dict[str, float]):
        """Update current prices for open positions (for unrealized P&L)"""
        for symbol, trades in self.positions.items():
            if symbol in price_data:
                current_price = price_data[symbol]
                for trade in trades:
                    trade.unrealized_pnl = (current_price - trade.entry_price) * trade.quantity

    def get_portfolio_value(self, price_data: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        self.update_position_prices(price_data)

        open_equity = sum(
            sum(trade.quantity * price_data.get(symbol, trade.entry_price)
                for trade in trades)
            for symbol, trades in self.positions.items()
        )

        # realized_pnl = sum(trade.profit_loss_amount for trade in self.closed_trades)

        return self.cash + open_equity

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'profit_factor': 0,
                'average_win': 0,
                'average_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            }

        winning_trades = [t for t in self.closed_trades if t.profit_loss_amount > 0]
        losing_trades = [t for t in self.closed_trades if t.profit_loss_amount < 0]

        total_wins = sum(t.profit_loss_amount for t in winning_trades)
        total_losses = abs(sum(t.profit_loss_amount for t in losing_trades))

        return {
            'total_trades': len(self.closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.closed_trades) * 100,
            'total_return': (self.get_portfolio_value({}) - self.initial_capital) / self.initial_capital * 100,
            'profit_factor': total_wins / total_losses if total_losses > 0 else 0,
            'average_win': total_wins / len(winning_trades) if winning_trades else 0,
            'average_loss': total_losses / len(losing_trades) if losing_trades else 0,
            'largest_win': max([t.profit_loss_amount for t in winning_trades]) if winning_trades else 0,
            'largest_loss': min([t.profit_loss_amount for t in losing_trades]) if losing_trades else 0
        }

    def print_summary(self, price_data: Dict[str, float] = None):
        """Print portfolio summary"""
        if price_data is None:
            price_data = {}

        print("\n" + "=" * 60)
        print("PAPER TRADING PORTFOLIO SUMMARY")
        print("=" * 60)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Current Cash: ${self.cash:,.2f}")
        print(f"Portfolio Value: ${self.get_portfolio_value(price_data):,.2f}")

        metrics = self.get_performance_metrics()
        print(f"\nTotal Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Average Win: ${metrics['average_win']:,.2f}")
        print(f"Average Loss: ${metrics['average_loss']:,.2f}")
        print(f"Total Return: {metrics['total_return']:.2f}%")
        print("=" * 60)

    def get_open_positions_summary(self) -> pd.DataFrame:
        """Get summary of open positions"""
        data = []
        for symbol, trades in self.positions.items():
            for trade in trades:
                data.append({
                    'Symbol': symbol,
                    'Entry Price': f"${trade.entry_price:.2f}",
                    'Quantity': trade.quantity,
                    'Entry Date': trade.entry_date.strftime('%Y-%m-%d %H:%M'),
                    'Entry Signal': trade.entry_signal,
                    'Stop Loss': f"${trade.stop_loss:.2f}",
                    'Take Profit': f"${trade.take_profit:.2f}"
                })

        return pd.DataFrame(data) if data else pd.DataFrame()

    def get_closed_trades_summary(self) -> pd.DataFrame:
        """Get summary of closed trades"""
        data = []
        for trade in self.closed_trades:
            data.append({
                'Symbol': trade.symbol,
                'Entry': f"${trade.entry_price:.2f}",
                'Exit': f"${trade.exit_price:.2f}",
                'Qty': trade.quantity,
                'P&L': f"${trade.profit_loss_amount:,.2f}",
                'Return': f"{trade.profit_loss_percent:.2f}%",
                'Days': trade.holding_days,
                'Entry Signal': trade.entry_signal,
                'Exit Signal': trade.exit_signal
            })

        return pd.DataFrame(data) if data else pd.DataFrame()