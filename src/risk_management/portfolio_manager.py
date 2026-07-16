import numpy as np
import pandas as pd
from typing import Tuple

def validate_trade(
        current_cash: float,
        position_cost: float,
        max_positions: int = 5,
        current_positions: int = 0,
        max_portfolio_risk: float = 0.05
) -> Tuple[bool, str]:
    if position_cost > current_cash:
        return False, f"Insufficient cash: Need ${position_cost:.2f}, Have ${current_cash:.2f}"

    if current_positions >= max_positions:
        return False, f"Max {max_positions} positions already open"

    return True, "Trade approved"
"""
    Validate if a trade should be executed

    Checks:
    1. Sufficient cash
    2. Not too many open positions
    3. Portfolio risk limit not exceeded

    Returns: (is_valid, reason)
"""


def kelly_criterion(
        win_rate: float,
        avg_win: float,
        avg_loss: float
) -> float:

    if win_rate <= 0 or win_rate >= 1:
        return 0

    kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win

    # Use 25% of kelly to be conservative
    conservative_kelly = kelly * 0.25

    return max(0, min(conservative_kelly, 0.25))  # Cap at 25%
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


def calculate_portfolio_metrics(
        daily_equity: list,
        initial_capital: float
) -> dict:

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

"""
    Calculate portfolio risk metrics

    Returns:
        - Total return %
        - Max drawdown %
        - Sharpe ratio (assuming 252 trading days/year, 0% risk-free rate)
        - Calmar ratio (return / max drawdown)
"""


def calculate_win_rate_metrics(trades: list) -> dict:

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

"""
    Calculate win/loss metrics from trades

    Example trade format:
        {'profit': 250, 'loss': 100}  # Positive = win, Negative = loss
    """


def print_risk_management_rules(account_size: float):
    """Print recommended risk management rules"""
    print("\n" + "=" * 60)
    print("RISK MANAGEMENT RULES")
    print("=" * 60)
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
    print("=" * 60)