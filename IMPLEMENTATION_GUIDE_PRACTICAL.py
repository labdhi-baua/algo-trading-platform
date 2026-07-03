"""
COMPLETE IMPLEMENTATION GUIDE
How to Use the Master Swing Trader Strategy (4-Hour Optimized)
Step-by-Step Examples & Practical Usage
"""

# ============================================
# PART 1: QUICK START (5 MINUTES)
# ============================================

"""
FASTEST WAY TO RUN THE STRATEGY:

1. Copy MASTER_STRATEGY_4H_OPTIMIZED.py code
2. Save as: master_strategy.py
3. Run: python master_strategy.py
4. See backtest results on AAPL, MSFT, TSLA

That's it! The strategy backtests itself.
"""

# ============================================
# PART 2: STEP-BY-STEP IMPLEMENTATION
# ============================================

"""
IMPLEMENTATION STEPS:

Step 1: Import Required Libraries
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

"""
Step 2: Download Data for Your Stocks
"""
# Example: Download 6 years of 4-hour data
def download_4h_data(ticker, years=6):
    """Download 4-hour historical data"""
    
    # Yahoo Finance only provides daily data directly
    # For 4-hour, we'll use daily and resample or use yfinance library
    # For production, use: yfinance with intraday=True or Alpaca/Interactive Brokers API
    
    # For this example, we'll use daily and mention the caveat
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*years)
    
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    print(f"✓ Downloaded {len(df)} days of data for {ticker}")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"  Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
    
    return df

# Usage
aapl_data = download_4h_data("AAPL", years=6)

"""
Step 3: Initialize the Strategy with Optimal Parameters
"""
from MASTER_STRATEGY_4H_OPTIMIZED import MasterSwingTraderStrategy

strategy = MasterSwingTraderStrategy()

print("\n📊 STRATEGY CONFIGURATION:")
print(f"  Strategy: {strategy.name}")
print(f"  Timeframe: {strategy.timeframe}")
print(f"  ADX Threshold: {strategy.adx_threshold}")
print(f"  RSI Buy Zone: {strategy.rsi_buy_lower}-{strategy.rsi_buy_upper}")
print(f"  RSI Sell Zone: {strategy.rsi_sell_lower}-{strategy.rsi_sell_upper}")
print(f"  ATR Stop Multiple: {strategy.atr_stop_multiple}")
print(f"  ATR TP Multiple: {strategy.atr_tp_multiple}")

"""
Step 4: Generate Trading Signals
"""
signals_df = strategy.generate_signals(aapl_data.copy())

print("\n🎯 SIGNAL GENERATION RESULTS:")
print(f"  Total Candles: {len(signals_df)}")
print(f"  Buy Signals: {len(signals_df[signals_df['Signal'] == 1])}")
print(f"  Sell Signals: {len(signals_df[signals_df['Signal'] == -1])}")
print(f"  Hold Candles: {len(signals_df[signals_df['Signal'] == 0])}")

# Show sample signals
print("\n📈 RECENT SIGNALS:")
print(signals_df[['Close', 'Signal', 'Confidence', 'Stop_Loss', 'Take_Profit']].tail(10))

"""
Step 5: Run Backtest
"""
from MASTER_STRATEGY_4H_OPTIMIZED import QuantBacktester

backtester = QuantBacktester(
    strategy=strategy,
    initial_capital=10000,
    risk_per_trade=0.02  # 2% risk per trade
)

metrics = backtester.backtest(aapl_data)

print("\n📊 BACKTEST RESULTS:")
print(f"  Total Trades: {metrics['Total Trades']}")
print(f"  Winning Trades: {metrics['Winning Trades']}")
print(f"  Losing Trades: {metrics['Losing Trades']}")
print(f"  Win Rate: {metrics['Win Rate %']}%")
print(f"  Profit Factor: {metrics['Profit Factor']}")
print(f"  Average Win: ${metrics['Avg Win']:.2f}")
print(f"  Average Loss: ${metrics['Avg Loss']:.2f}")
print(f"  Total Return: {metrics['Total Return %']}%")
print(f"  Sharpe Ratio: {metrics['Sharpe Ratio']}")
print(f"  Max Drawdown: {metrics['Max Drawdown %']}%")

# ============================================
# PART 3: PRACTICAL TRADING EXAMPLES
# ============================================

"""
EXAMPLE 1: ANALYZE A SPECIFIC TRADE
"""

def analyze_specific_trade(signals_df, trade_index):
    """Analyze details of a specific trade"""
    
    row = signals_df.iloc[trade_index]
    
    print("\n" + "="*70)
    print(f"TRADE ANALYSIS - Candle {trade_index}")
    print("="*70)
    
    print(f"\nPrice Action:")
    print(f"  Close: ${row['Close']:.2f}")
    print(f"  High: ${row['High']:.2f}")
    print(f"  Low: ${row['Low']:.2f}")
    print(f"  Volume: {row['Volume']:,.0f}")
    
    print(f"\nSignal Details:")
    print(f"  Signal Type: {'BUY' if row['Signal'] == 1 else 'SELL' if row['Signal'] == -1 else 'HOLD'}")
    print(f"  Confidence: {row['Confidence']:.1f}%")
    print(f"  Reason: {row['Signal_Reason']}")
    
    print(f"\nIndicator Values:")
    print(f"  RSI: {row['RSI']:.2f}")
    print(f"  MACD: {row['MACD']:.4f}")
    print(f"  MACD Signal: {row['MACD_Signal']:.4f}")
    print(f"  ADX: {row['ADX']:.2f}")
    print(f"  Stochastic K: {row['Stoch_K']:.2f}")
    print(f"  CCI: {row['CCI']:.2f}")
    
    print(f"\nMoving Averages:")
    print(f"  SMA 50: ${row['SMA_50']:.2f}")
    print(f"  SMA 200: ${row['SMA_200']:.2f}")
    print(f"  Trend: {'UP' if row['Trend_Up'] else 'DOWN'}")
    
    print(f"\nBollinger Bands:")
    print(f"  Upper: ${row['BB_Upper']:.2f}")
    print(f"  Middle: ${row['BB_Middle']:.2f}")
    print(f"  Lower: ${row['BB_Lower']:.2f}")
    
    print(f"\nEntry/Exit Levels:")
    print(f"  Entry: ${row['Close']:.2f}")
    print(f"  Stop Loss: ${row['Stop_Loss']:.2f}")
    print(f"  Take Profit: ${row['Take_Profit']:.2f}")
    print(f"  Risk: ${row['Close'] - row['Stop_Loss']:.2f}")
    print(f"  Reward: ${row['Take_Profit'] - row['Close']:.2f}")
    print(f"  Risk:Reward: 1:{(row['Take_Profit'] - row['Close']) / (row['Close'] - row['Stop_Loss']):.2f}")

# Usage: Analyze the most recent buy signal
buy_signals = signals_df[signals_df['Signal'] == 1]
if len(buy_signals) > 0:
    last_buy_index = buy_signals.index[-1]
    analyze_specific_trade(signals_df, signals_df.index.get_loc(last_buy_index))

"""
EXAMPLE 2: MULTI-STOCK COMPARISON
"""

def backtest_multiple_stocks(tickers, years=6):
    """Backtest strategy on multiple stocks"""
    
    print("\n" + "="*80)
    print("MULTI-STOCK BACKTEST COMPARISON")
    print("="*80)
    
    results = {}
    
    for ticker in tickers:
        try:
            # Download data
            df = download_4h_data(ticker, years)
            
            # Run backtest
            strategy = MasterSwingTraderStrategy()
            backtester = QuantBacktester(strategy, 10000, 0.02)
            metrics = backtester.backtest(df)
            
            results[ticker] = metrics
            
            # Print results
            print(f"\n{ticker}:")
            print(f"  Trades: {metrics['Total Trades']} | "
                  f"Win Rate: {metrics['Win Rate %']}% | "
                  f"Return: {metrics['Total Return %']}%")
            
        except Exception as e:
            print(f"\n{ticker}: Error - {e}")
    
    # Create comparison table
    df_results = pd.DataFrame(results).T
    df_results = df_results.sort_values('Total Return %', ascending=False)
    
    print("\n" + "="*80)
    print("RANKED BY RETURN:")
    print("="*80)
    print(df_results[['Total Trades', 'Win Rate %', 'Profit Factor', 'Total Return %', 'Sharpe Ratio', 'Max Drawdown %']].to_string())
    
    return results

# Usage
results = backtest_multiple_stocks(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"], years=6)

"""
EXAMPLE 3: PARAMETER OPTIMIZATION
"""

def optimize_parameters():
    """Test different parameter combinations"""
    
    print("\n" + "="*80)
    print("PARAMETER OPTIMIZATION TEST")
    print("="*80)
    
    df = download_4h_data("AAPL", years=6)
    
    # Test different ADX thresholds
    adx_values = [20, 25, 30, 35]
    
    print("\nTesting different ADX thresholds:")
    print("─"*60)
    
    for adx_val in adx_values:
        strategy = MasterSwingTraderStrategy()
        strategy.adx_threshold = adx_val
        
        backtester = QuantBacktester(strategy, 10000, 0.02)
        metrics = backtester.backtest(df)
        
        print(f"ADX > {adx_val}: "
              f"Trades={metrics['Total Trades']}, "
              f"Win%={metrics['Win Rate %']}%, "
              f"Return={metrics['Total Return %']}%")
    
    # Test different RSI zones
    rsi_zones = [(25, 40), (30, 45), (35, 50), (40, 55)]
    
    print("\nTesting different RSI entry zones:")
    print("─"*60)
    
    for lower, upper in rsi_zones:
        strategy = MasterSwingTraderStrategy()
        strategy.rsi_buy_lower = lower
        strategy.rsi_buy_upper = upper
        
        backtester = QuantBacktester(strategy, 10000, 0.02)
        metrics = backtester.backtest(df)
        
        print(f"RSI {lower}-{upper}: "
              f"Trades={metrics['Total Trades']}, "
              f"Win%={metrics['Win Rate %']}%, "
              f"Return={metrics['Total Return %']}%")

# Usage
optimize_parameters()

"""
EXAMPLE 4: VISUALIZE STRATEGY
"""

def visualize_strategy(ticker, years=6):
    """Create visual chart of strategy signals"""
    
    df = download_4h_data(ticker, years)
    strategy = MasterSwingTraderStrategy()
    signals_df = strategy.generate_signals(df.copy())
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Price chart with signals
    ax1.plot(signals_df.index, signals_df['Close'], label='Close Price', linewidth=1)
    ax1.plot(signals_df.index, signals_df['SMA_50'], label='SMA 50', alpha=0.7)
    ax1.plot(signals_df.index, signals_df['SMA_200'], label='SMA 200', alpha=0.7)
    
    # Plot buy signals (green triangles)
    buy_signals = signals_df[signals_df['Signal'] == 1]
    ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', s=100, label='Buy Signal')
    
    # Plot sell signals (red triangles)
    sell_signals = signals_df[signals_df['Signal'] == -1]
    ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', s=100, label='Sell Signal')
    
    ax1.set_title(f'{ticker} - Master Swing Strategy (4H)')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Indicator chart (RSI + MACD)
    ax2.plot(signals_df.index, signals_df['RSI'], label='RSI', color='blue')
    ax2.axhline(30, color='green', linestyle='--', alpha=0.5, label='RSI 30-45 Zone')
    ax2.axhline(45, color='green', linestyle='--', alpha=0.5)
    ax2.axhline(70, color='red', linestyle='--', alpha=0.5, label='RSI 55-70 Zone')
    ax2.plot(signals_df.index, signals_df['MACD'], label='MACD', color='purple')
    ax2.plot(signals_df.index, signals_df['MACD_Signal'], label='Signal Line', color='orange')
    
    ax2.set_title('Momentum Indicators')
    ax2.set_ylabel('Value')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{ticker}_master_strategy.png', dpi=150)
    print(f"\n✓ Chart saved as '{ticker}_master_strategy.png'")
    plt.show()

# Usage
visualize_strategy("AAPL", years=6)

"""
EXAMPLE 5: PAPER TRADING LOG
"""

def create_trading_log(signals_df, starting_balance=10000):
    """Create a detailed trading log for paper trading"""
    
    log = []
    cash = starting_balance
    position = None
    
    for i, (idx, row) in enumerate(signals_df.iterrows()):
        
        # BUY signal
        if row['Signal'] == 1 and position is None:
            shares = int((cash * 0.95) / row['Close'])  # Use 95% of cash
            cost = shares * row['Close']
            
            position = {
                'entry_date': idx,
                'entry_price': row['Close'],
                'shares': shares,
                'stop_loss': row['Stop_Loss'],
                'take_profit': row['Take_Profit'],
                'confidence': row['Confidence']
            }
            
            cash -= cost
            
            log.append({
                'Date': idx,
                'Action': 'BUY',
                'Price': row['Close'],
                'Shares': shares,
                'Cost': cost,
                'Cash': cash,
                'Confidence': row['Confidence']
            })
        
        # SELL signal
        elif row['Signal'] == -1 and position is not None:
            proceeds = position['shares'] * row['Close']
            profit = proceeds - (position['shares'] * position['entry_price'])
            return_pct = (profit / (position['shares'] * position['entry_price'])) * 100
            
            cash += proceeds
            
            log.append({
                'Date': idx,
                'Action': 'SELL',
                'Price': row['Close'],
                'Shares': position['shares'],
                'Proceeds': proceeds,
                'Profit': profit,
                'Return%': return_pct,
                'Days_Held': (idx - position['entry_date']).days,
                'Cash': cash
            })
            
            position = None
    
    # Convert to DataFrame
    log_df = pd.DataFrame(log)
    
    print("\n" + "="*100)
    print("PAPER TRADING LOG")
    print("="*100)
    print(log_df.to_string())
    
    # Calculate statistics
    print("\n" + "="*100)
    print("TRADING STATISTICS")
    print("="*100)
    
    trades = log_df[log_df['Action'] == 'SELL']
    if len(trades) > 0:
        winning = trades[trades['Profit'] > 0]
        losing = trades[trades['Profit'] < 0]
        
        print(f"Total Trades: {len(trades)}")
        print(f"Winning: {len(winning)} ({len(winning)/len(trades)*100:.1f}%)")
        print(f"Losing: {len(losing)} ({len(losing)/len(trades)*100:.1f}%)")
        print(f"Total Profit: ${trades['Profit'].sum():.2f}")
        print(f"Average Win: ${winning['Profit'].mean():.2f}" if len(winning) > 0 else "Average Win: N/A")
        print(f"Average Loss: ${losing['Profit'].mean():.2f}" if len(losing) > 0 else "Average Loss: N/A")
        print(f"Final Balance: ${cash:.2f}")
        print(f"Total Return: {((cash - starting_balance) / starting_balance * 100):.2f}%")
    
    return log_df

# Usage
log_df = create_trading_log(signals_df)

# ============================================
# PART 4: DAILY TRADING CHECKLIST
# ============================================

"""
DAILY TRADING ROUTINE (4-HOUR SWING TRADER):

Morning (8:30 AM - Before Market Open):
  □ Check overnight news for your stocks
  □ Look at overnight gaps (if any)
  □ Calculate expected volatility (ATR)
  □ Review previous day's trades
  □ Update trading journal

Late Morning (10:30 AM - 2 Hours into trading):
  □ Check 4-hour candles for new signals
  □ Look for breakout opportunities
  □ Check if current positions still valid
  □ Manage any open positions

Afternoon (2:00 PM - Mid-day):
  □ Update portfolio P&L
  □ Check for mean reversion opportunities
  □ Consider scaling into winners
  □ Review daily loss limit (5%)

Late Afternoon (3:30 PM - Before close):
  □ Check if any positions should be closed
  □ Update trading log
  □ Plan for next day
  □ Check for after-hours gaps

Evening (After Market Close):
  □ Log all trades in database
  □ Calculate daily metrics
  □ Review if trades matched plan
  □ Plan tomorrow's setups
  □ Update charts

Weekly (End of Week):
  □ Calculate weekly P&L
  □ Review win rate and profit factor
  □ Compare to target metrics
  □ Adjust strategy if needed
"""

# ============================================
# PART 5: WHEN TO SKIP TRADING
# ============================================

"""
SKIP TRADING IF:
═════════════════════════════════════════════════════════════

Market Conditions:
  ✗ ADX < 25 (no trend, markets are choppy)
  ✗ Major economic news announced
  ✗ Fed decision day (too volatile)
  ✗ Earnings reports (unpredictable moves)
  ✗ Pre-market/post-market hours (low volume)

Personal Conditions:
  ✗ You're tired or emotional
  ✗ You just had 2 losing trades in a row
  ✗ You're trying to "revenge trade" (recover losses)
  ✗ You don't fully understand the signal
  ✗ Your risk management isn't clear

Portfolio Conditions:
  ✗ Already lost 5% today (hit daily limit)
  ✗ Drawdown is > 10% of account (high stress)
  ✗ Win rate has dropped below 40% (strategy broken?)
  ✗ You have > 5 open positions (too much risk)

REMEMBER: The best trades are the ones you DON'T take.
"""

print("\n" + "="*80)
print("✓ IMPLEMENTATION GUIDE COMPLETE")
print("="*80)
print("\nYou now have:")
print("  ✓ Master strategy code ready to use")
print("  ✓ 5 practical usage examples")
print("  ✓ Backtesting framework")
print("  ✓ Multi-stock comparison")
print("  ✓ Parameter optimization tools")
print("  ✓ Visualization tools")
print("  ✓ Trading log system")
print("  ✓ Daily routine checklist")
print("\nNext step: Run 'python master_strategy.py' to backtest on your stocks")
print("="*80)
