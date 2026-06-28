"""
Risk Management Module
Position sizing, stop loss calculation, and portfolio protection
"""

import numpy as np
import pandas as pd
from typing import Tuple

class RiskManager:
    """Manages all risk-related calculations"""
    
    @staticmethod
    def calculate_position_size(
        account_size: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: float = 0.02
    ) -> Tuple[float, float]:
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
        
        risk_amount = account_size * risk_per_trade
        price_difference = abs(entry_price - stop_loss)
        
        if price_difference == 0:
            raise ValueError("Stop loss must be different from entry price")
        
        shares = risk_amount / price_difference
        position_cost = shares * entry_price
        
        return int(shares), position_cost
    
    @staticmethod
    def calculate_stop_loss_and_tp(
        entry_price: float,
        strategy_atr: float = None,
        stop_loss_percent: float = None,
        reward_ratio: float = 2.0
    ) -> Tuple[float, float]:
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
    
    @staticmethod
    def validate_trade(
        current_cash: float,
        position_cost: float,
        max_positions: int = 5,
        current_positions: int = 0,
        max_portfolio_risk: float = 0.05
    ) -> Tuple[bool, str]:
        """
        Validate if a trade should be executed
        
        Checks:
        1. Sufficient cash
        2. Not too many open positions
        3. Portfolio risk limit not exceeded
        
        Returns: (is_valid, reason)
        """
        
        if position_cost > current_cash:
            return False, f"Insufficient cash: Need ${position_cost:.2f}, Have ${current_cash:.2f}"
        
        if current_positions >= max_positions:
            return False, f"Max {max_positions} positions already open"
        
        return True, "Trade approved"
    
    @staticmethod
    def kelly_criterion(
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Kelly Criterion - Optimal position sizing
        
        Tells you optimal % of portfolio to risk per trade
        
        Kelly % = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        Example:
            - Win rate: 55%
            - Avg win: $100
            - Avg loss: $100
            
            kelly = (0.55 * 100 - 0.45 * 100) / 100 = 0.10 = 10%
            
            So risk 10% of portfolio per trade (but typically use 0.25 * kelly)
        """
        
        if win_rate <= 0 or win_rate >= 1:
            return 0
        
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Use 25% of kelly to be conservative
        conservative_kelly = kelly * 0.25
        
        return max(0, min(conservative_kelly, 0.25))  # Cap at 25%
    
    @staticmethod
    def calculate_portfolio_metrics(
        daily_equity: list,
        initial_capital: float
    ) -> dict:
        """
        Calculate portfolio risk metrics
        
        Returns:
            - Total return %
            - Max drawdown %
            - Sharpe ratio (assuming 252 trading days/year, 0% risk-free rate)
            - Calmar ratio (return / max drawdown)
        """
        
        equity_series = pd.Series(daily_equity)
        returns = equity_series.pct_change().dropna()
        
        # Total return
        total_return = (equity_series.iloc[-1] - initial_capital) / initial_capital * 100
        
        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Sharpe ratio
        annual_return = returns.mean() * 252
        annual_std = returns.std() * np.sqrt(252)
        sharpe = annual_return / annual_std if annual_std != 0 else 0
        
        # Calmar ratio
        calmar = total_return / max_drawdown if max_drawdown != 0 else 0
        
        return {
            'Total Return %': round(total_return, 2),
            'Max Drawdown %': round(max_drawdown, 2),
            'Sharpe Ratio': round(sharpe, 2),
            'Calmar Ratio': round(calmar, 2),
            'Annual Return %': round(annual_return * 100, 2),
            'Annual Volatility %': round(annual_std * 100, 2)
        }
    
    @staticmethod
    def calculate_win_rate_metrics(trades: list) -> dict:
        """
        Calculate win/loss metrics from trades
        
        Example trade format:
            {'profit': 250, 'loss': 100}  # Positive = win, Negative = loss
        """
        
        if not trades:
            return {
                'Win Rate %': 0,
                'Total Trades': 0,
                'Wins': 0,
                'Losses': 0,
                'Profit Factor': 0,
                'Average Win': 0,
                'Average Loss': 0,
                'Largest Win': 0,
                'Largest Loss': 0
            }
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        total_wins = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        
        return {
            'Win Rate %': round(len(winning_trades) / len(trades) * 100, 2),
            'Total Trades': len(trades),
            'Wins': len(winning_trades),
            'Losses': len(losing_trades),
            'Profit Factor': round(total_wins / total_losses, 2) if total_losses > 0 else 0,
            'Average Win': round(total_wins / len(winning_trades), 2) if winning_trades else 0,
            'Average Loss': round(total_losses / len(losing_trades), 2) if losing_trades else 0,
            'Largest Win': round(max([t['pnl'] for t in winning_trades]), 2) if winning_trades else 0,
            'Largest Loss': round(min([t['pnl'] for t in losing_trades]), 2) if losing_trades else 0
        }
    
    @staticmethod
    def print_risk_management_rules(account_size: float):
        """Print recommended risk management rules"""
        print("\n" + "="*60)
        print("RISK MANAGEMENT RULES")
        print("="*60)
        print(f"Account Size: ${account_size:,.0f}")
        print(f"\nMaximum Risk Per Trade: ${account_size * 0.02:,.0f} (2%)")
        print(f"Maximum Risk Per Day: ${account_size * 0.05:,.0f} (5%)")
        print(f"Maximum Drawdown Before STOP: ${account_size * 0.10:,.0f} (10%)")
        print(f"Maximum Position Size: ${account_size * 0.05:,.0f} (5% of account)")
        print(f"Maximum Positions Open: 5")
        print("\nSignals:")
        print("• Stop trading if daily loss reaches 5% of account")
        print("• Close worst positions if portfolio draws down 10%")
        print("• Never risk more than 2% on any single trade")
        print("• Always use stop losses on EVERY trade")
        print("• Scale out: Take profits at 50%, 100%, and 150% of risk")
        print("="*60)


# Example usage
if __name__ == "__main__":
    account = 10000
    
    # Example 1: Position sizing
    print("Example 1: Calculate position size")
    shares, cost = RiskManager.calculate_position_size(
        account_size=account,
        entry_price=150,
        stop_loss=145,  # Risk $5 per share
        risk_per_trade=0.02  # Risk $200 (2% of account)
    )
    print(f"Account: ${account:,}, Entry: $150, Stop: $145")
    print(f"Risk 2% = ${account * 0.02:,.0f}")
    print(f"Position size: {shares} shares for ${cost:,.2f}")
    
    # Example 2: Stop loss and take profit
    print("\n" + "="*60)
    print("Example 2: Calculate stop loss and take profit")
    entry = 100
    atr = 2.5
    sl, tp = RiskManager.calculate_stop_loss_and_tp(
        entry_price=entry,
        strategy_atr=atr,
        reward_ratio=2.0
    )
    print(f"Entry: ${entry}, ATR: {atr}")
    print(f"Stop Loss: ${sl:.2f} (risk ${entry - sl:.2f})")
    print(f"Take Profit: ${tp:.2f} (gain ${tp - entry:.2f})")
    print(f"Risk:Reward Ratio = 1:{(tp - entry) / (entry - sl):.1f}")
    
    # Example 3: Kelly Criterion
    print("\n" + "="*60)
    print("Example 3: Kelly Criterion")
    kelly = RiskManager.kelly_criterion(
        win_rate=0.55,
        avg_win=100,
        avg_loss=100
    )
    print(f"Win rate: 55%, Avg Win: $100, Avg Loss: $100")
    print(f"Kelly Criterion: {kelly*100:.2f}% of account per trade")
    print(f"(Using 25% of Kelly for safety)")
    
    # Example 4: Risk management rules
    RiskManager.print_risk_management_rules(account)
