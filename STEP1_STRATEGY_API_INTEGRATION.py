"""
COMPLETE INTEGRATION GUIDE
Merging Master Trading Strategy with Your Paper Trading Website
Full End-to-End Architecture & Implementation
"""

# ============================================
# PART 1: SYSTEM ARCHITECTURE OVERVIEW
# ============================================

"""
YOUR CURRENT SETUP (What You've Already Built):
═════════════════════════════════════════════════════════════

You Have:
  ✓ src/indicators/ (technical indicators)
  ✓ src/risk_management/ (position sizing, stops)
  ✓ src/paper_trading/ (portfolio, trades, database)
  ✓ GitHub repository (version control)

Missing:
  ✗ Strategy generation (buy/sell signals)
  ✗ Website integration
  ✗ Real-time signal detection
  ✗ Web interface for paper trading
  ✗ API for frontend communication
  ✗ Database to store signals

NEW INTEGRATED ARCHITECTURE:
═════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                     MASTER STRATEGY SYSTEM                  │
│                  (What We're Adding Now)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    SIGNAL GENERATOR                         │
│  • Calculates indicators every 4 hours                      │
│  • Generates buy/sell signals with confidence               │
│  • Stores signals in database                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            YOUR EXISTING COMPONENTS (Already Built)         │
├─────────────────────────────────────────────────────────────┤
│  • Technical Indicators (RSI, MACD, Bollinger, etc)         │
│  • Risk Management (Position sizing, stops, limits)         │
│  • Paper Trading Engine (Portfolio, Trade execution)        │
│  • Database (SQLite storing trades, portfolio)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    WEB LAYER (Flask/Django)                 │
│  • API endpoints for strategy signals                       │
│  • Portfolio management endpoints                           │
│  • Trade execution endpoints                                │
│  • Real-time dashboard data                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React/HTML)                     │
│  • Chart visualization (TradingView Lightweight Charts)     │
│  • Signal alerts and notifications                          │
│  • Portfolio dashboard                                      │
│  • Trade log and history                                    │
│  • Performance analytics                                    │
└─────────────────────────────────────────────────────────────┘


INTEGRATION WORKFLOW:
═════════════════════════════════════════════════════════════

1. DATA LAYER (Market Data)
   └→ yfinance downloads 4H data every 4 hours
   
2. STRATEGY LAYER (Signal Generation)
   └→ Master Strategy analyzes data
   └→ Generates signals with confidence scores
   └→ Stores in database (signals table)
   
3. EXECUTION LAYER (Paper Trading)
   └→ Checks signals from database
   └→ Executes trades in paper account
   └→ Updates portfolio in database
   
4. API LAYER (Web Communication)
   └→ Exposes signals via REST API
   └→ Exposes portfolio via REST API
   └→ Exposes trades via REST API
   
5. FRONTEND LAYER (User Interface)
   └→ Displays signals in real-time
   └→ Shows portfolio dashboard
   └→ Shows trade history
   └→ Displays performance metrics

DATABASE SCHEMA:
═════════════════════════════════════════════════════════════

Tables:
  • signals - Buy/sell signals with timestamps
  • trades - Executed trades (entry/exit)
  • portfolio - Current positions and values
  • daily_values - Historical portfolio performance
  • indicators - Calculated indicator values
"""

# ============================================
# PART 2: STEP 1 - ADD STRATEGY LAYER
# ============================================

"""
STEP 1: Integrate Master Strategy into Your Project

Location: src/strategies/master_strategy.py

What to Do:
1. Copy SwingTradeIndicators class from master code
2. Copy MasterSwingTraderStrategy class from master code
3. Modify to integrate with your existing indicators
4. Create database tables for signals
"""

# Example: src/strategies/master_strategy.py

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import sqlite3

# Import your existing indicator classes
# from src.indicators.trend import MovingAverage, ADX
# from src.indicators.momentum import RSI, MACD
# from src.risk_management.position_sizer import PositionSizer

class TradeSignal:
    """Signal generated by master strategy"""
    def __init__(self, 
                 ticker: str,
                 timestamp: datetime,
                 signal_type: str,  # BUY, SELL, HOLD
                 confidence: float,
                 entry_price: float,
                 stop_loss: float,
                 take_profit: float,
                 reason: str,
                 indicators_aligned: List[str]):
        self.ticker = ticker
        self.timestamp = timestamp
        self.signal_type = signal_type
        self.confidence = confidence
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.reason = reason
        self.indicators_aligned = indicators_aligned
    
    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'reason': self.reason,
            'indicators': ','.join(self.indicators_aligned)
        }


class MasterStrategyIntegrated:
    """
    Master Strategy integrated with your existing infrastructure
    Generates signals for paper trading
    """
    
    def __init__(self, 
                 db_path: str = 'trading.db',
                 indicators_module=None,
                 risk_management_module=None):
        self.db_path = db_path
        self.indicators = indicators_module
        self.risk_mgmt = risk_management_module
        
        # Strategy parameters (optimized for 4-hour)
        self.adx_threshold = 25
        self.rsi_buy_lower = 30
        self.rsi_buy_upper = 45
        self.rsi_sell_lower = 55
        self.rsi_sell_upper = 70
        self.atr_stop_multiple = 2.0
        self.atr_tp_multiple = 3.0
        self.volume_ratio_min = 1.0
        
        self._init_database()
    
    def _init_database(self):
        """Create signals table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY,
                ticker TEXT,
                timestamp DATETIME,
                signal_type TEXT,
                confidence REAL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                reason TEXT,
                indicators TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                actioned INTEGER DEFAULT 0,
                UNIQUE(ticker, timestamp, signal_type)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_signals(self, ticker: str, df: pd.DataFrame) -> List[TradeSignal]:
        """
        Generate trading signals for a stock
        
        Args:
            ticker: Stock symbol
            df: DataFrame with OHLCV data
        
        Returns:
            List of TradeSignal objects
        """
        signals = []
        
        # Calculate all indicators
        df = self._calculate_all_indicators(df)
        
        # Generate signals for most recent candle
        if len(df) < 200:
            return signals
        
        i = len(df) - 1
        signal = self._evaluate_candle(df, i, ticker)
        
        if signal and signal.signal_type != 'HOLD':
            signals.append(signal)
        
        return signals
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators (your existing modules)"""
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # Moving Averages
        df['SMA_50'] = close.rolling(50).mean()
        df['SMA_200'] = close.rolling(200).mean()
        
        # Momentum
        df['RSI'] = self._calculate_rsi(close, 14)
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = \
            self._calculate_macd(close, 12, 26, 9)
        
        # Volatility
        df['ATR'] = self._calculate_atr(high, low, close, 14)
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = \
            self._calculate_bollinger_bands(close, 20, 2.0)
        
        # Trend Strength
        df['ADX'] = self._calculate_adx(high, low, close, 14)
        
        # Other indicators
        df['Stoch_K'], df['Stoch_D'] = \
            self._calculate_stochastic(high, low, close, 14, 3, 3)
        df['CCI'] = self._calculate_cci(high, low, close, 20)
        
        # Volume
        df['Volume_SMA'] = volume.rolling(20).mean()
        
        # Support/Resistance
        df['Resistance'] = high.rolling(20).max()
        df['Support'] = low.rolling(20).min()
        
        return df
    
    def _evaluate_candle(self, df: pd.DataFrame, i: int, ticker: str) -> TradeSignal:
        """Evaluate single candle for buy/sell signals"""
        
        close = df['Close'].iloc[i]
        sma50 = df['SMA_50'].iloc[i]
        sma200 = df['SMA_200'].iloc[i]
        adx = df['ADX'].iloc[i]
        rsi = df['RSI'].iloc[i]
        macd = df['MACD'].iloc[i]
        macd_signal = df['MACD_Signal'].iloc[i]
        atr = df['ATR'].iloc[i]
        volume = df['Volume'].iloc[i]
        volume_sma = df['Volume_SMA'].iloc[i]
        
        # Trend Analysis
        trend_up = sma50 > sma200
        trend_strong = adx > self.adx_threshold
        
        # Volume Check
        if volume < volume_sma * self.volume_ratio_min:
            return None
        
        # BUY Signal Logic
        buy_signals = []
        buy_confidence = 0
        
        if not trend_up or not trend_strong:
            return None
        
        # Signal 1: MA Filter
        if trend_up and close > sma50:
            buy_signals.append('MA_ABOVE_50')
            buy_confidence += 20
        
        # Signal 2: RSI
        if self.rsi_buy_lower < rsi < self.rsi_buy_upper:
            buy_signals.append('RSI_MOMENTUM_ZONE')
            buy_confidence += 25
        
        # Signal 3: MACD
        if macd > macd_signal:
            buy_signals.append('MACD_ABOVE_SIGNAL')
            buy_confidence += 20
        
        # Generate Signal
        if len(buy_signals) >= 3 and buy_confidence >= 50:
            stop_loss = close - (self.atr_stop_multiple * atr)
            take_profit = close + (self.atr_tp_multiple * atr)
            
            return TradeSignal(
                ticker=ticker,
                timestamp=df.index[i],
                signal_type='BUY',
                confidence=min(buy_confidence, 100),
                entry_price=close,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=f'Signals: {", ".join(buy_signals)}',
                indicators_aligned=buy_signals
            )
        
        return None
    
    def store_signal(self, signal: TradeSignal):
        """Store signal in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        signal_dict = signal.to_dict()
        
        try:
            cursor.execute('''
                INSERT INTO signals 
                (ticker, timestamp, signal_type, confidence, entry_price, 
                 stop_loss, take_profit, reason, indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_dict['ticker'],
                signal_dict['timestamp'],
                signal_dict['signal_type'],
                signal_dict['confidence'],
                signal_dict['entry_price'],
                signal_dict['stop_loss'],
                signal_dict['take_profit'],
                signal_dict['reason'],
                signal_dict['indicators']
            ))
            
            conn.commit()
            print(f"✓ Signal stored for {signal.ticker}")
            
        except sqlite3.IntegrityError:
            print(f"⚠ Signal already exists for {signal.ticker} at {signal.timestamp}")
        
        conn.close()
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM signals 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        signals = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return signals
    
    # Helper indicator methods (from master strategy)
    def _calculate_rsi(self, data, period=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, data, fast=12, slow=26, signal=9):
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def _calculate_atr(self, high, low, close, period=14):
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def _calculate_bollinger_bands(self, data, period=20, std_dev=2.0):
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower
    
    def _calculate_adx(self, high, low, close, period=14):
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
        minus_di = 100 * minus_dm.rolling(window=period).mean() / atr
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def _calculate_stochastic(self, high, low, close, k_period=14, k_smooth=3, d_smooth=3):
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        k_percent = k_percent.rolling(window=k_smooth).mean()
        d_percent = k_percent.rolling(window=d_smooth).mean()
        
        return k_percent, d_percent
    
    def _calculate_cci(self, high, low, close, period=20):
        tp = (high + low + close) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        return (tp - sma) / (0.015 * mad)


# ============================================
# PART 3: STEP 2 - CREATE WEB API LAYER
# ============================================

"""
STEP 2: Build Flask API to Connect Website to Strategy

Location: app.py (or src/web/app.py)

What to Do:
1. Create Flask endpoints for signals
2. Create endpoints for portfolio
3. Create endpoints for trades
4. Enable CORS for frontend communication
"""

# Example: app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize strategy
from MASTER_STRATEGY_4H_OPTIMIZED import MasterSwingTraderStrategy

strategy = MasterSwingTraderStrategy(db_path='trading.db')


# ============================================
# ENDPOINT 1: Generate Signals
# ============================================

@app.route('/api/signals/generate', methods=['POST'])
def generate_signals():
    """
    Generate trading signals for a stock
    
    Request: {
        "ticker": "AAPL",
        "days": 500
    }
    
    Response: {
        "ticker": "AAPL",
        "signal": {
            "type": "BUY",
            "confidence": 75,
            "entry": 150.00,
            "stop": 145.00,
            "target": 157.50
        }
    }
    """
    try:
        data = request.json
        ticker = data.get('ticker', 'AAPL')
        days = data.get('days', 500)
        
        # Download data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        # Generate signals
        signals = strategy.generate_signals(ticker, df)
        
        # Store signals and return
        response_signals = []
        for signal in signals:
            strategy.store_signal(signal)
            response_signals.append({
                'ticker': signal.ticker,
                'type': signal.signal_type,
                'confidence': signal.confidence,
                'entry': signal.entry_price,
                'stop': signal.stop_loss,
                'target': signal.take_profit,
                'reason': signal.reason,
                'indicators': signal.indicators_aligned,
                'timestamp': signal.timestamp.isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'ticker': ticker,
            'signals': response_signals,
            'count': len(response_signals)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 2: Get Recent Signals
# ============================================

@app.route('/api/signals/recent', methods=['GET'])
def get_recent_signals():
    """
    Get recent trading signals
    
    Query params:
        limit: Number of signals to return (default: 10)
        ticker: Filter by ticker (optional)
    
    Response: {
        "signals": [
            {
                "ticker": "AAPL",
                "type": "BUY",
                "confidence": 75,
                "entry": 150.00,
                "timestamp": "2024-01-15T10:30:00"
            }
        ]
    }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        ticker = request.args.get('ticker', None)
        
        signals = strategy.get_recent_signals(limit=limit)
        
        # Filter by ticker if specified
        if ticker:
            signals = [s for s in signals if s['ticker'] == ticker]
        
        return jsonify({
            'status': 'success',
            'signals': signals,
            'count': len(signals)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 3: Execute Trade from Signal
# ============================================

@app.route('/api/trades/execute', methods=['POST'])
def execute_trade():
    """
    Execute a paper trade from signal
    
    Request: {
        "ticker": "AAPL",
        "action": "BUY",
        "entry": 150.00,
        "stop": 145.00,
        "target": 157.50,
        "quantity": 10
    }
    
    Response: {
        "trade_id": 123,
        "status": "executed",
        "ticker": "AAPL",
        "entry": 150.00,
        "quantity": 10,
        "total_cost": 1500.00
    }
    """
    try:
        data = request.json
        ticker = data.get('ticker')
        action = data.get('action')
        entry = data.get('entry')
        stop = data.get('stop')
        target = data.get('target')
        quantity = data.get('quantity')
        
        # Validate
        if not all([ticker, action, entry, stop, target, quantity]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Execute trade in paper trading engine
        # This connects to your existing paper trading module
        
        from src_paper_trading_engine import PaperTradingDatabase
        
        paper_trader = PaperTradingDatabase(db_path='trading.db')
        trade = paper_trader.open_position(
            ticker=ticker,
            entry_price=entry,
            quantity=quantity,
            stop_loss=stop,
            take_profit=target
        )
        
        return jsonify({
            'status': 'success',
            'trade_id': trade['id'],
            'ticker': ticker,
            'action': action,
            'entry': entry,
            'quantity': quantity,
            'total_cost': entry * quantity,
            'stop': stop,
            'target': target
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 4: Get Portfolio Status
# ============================================

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """
    Get current portfolio status
    
    Response: {
        "cash": 8500.00,
        "positions": [
            {
                "ticker": "AAPL",
                "quantity": 10,
                "entry": 150.00,
                "current": 152.50,
                "unrealized_pl": 250.00,
                "unrealized_pl_pct": 1.67
            }
        ],
        "total_value": 10000.00,
        "total_return": 500.00,
        "total_return_pct": 5.00
    }
    """
    try:
        from src_paper_trading_engine import VirtualPortfolio
        
        portfolio = VirtualPortfolio(db_path='trading.db')
        status = portfolio.get_portfolio_status()
        
        return jsonify({
            'status': 'success',
            'portfolio': status
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 5: Get Trade History
# ============================================

@app.route('/api/trades/history', methods=['GET'])
def get_trade_history():
    """
    Get trade history with P&L
    
    Query params:
        limit: Number of trades to return
        ticker: Filter by ticker
    
    Response: {
        "trades": [
            {
                "id": 1,
                "ticker": "AAPL",
                "entry": 150.00,
                "exit": 157.50,
                "quantity": 10,
                "profit": 75.00,
                "profit_pct": 5.00,
                "days_held": 5
            }
        ]
    }
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        ticker = request.args.get('ticker', None)
        
        from src.paper_trading.database import TradeDatabase
        
        db = TradeDatabase(db_path='trading.db')
        trades = db.get_trade_history(limit=limit)
        
        # Filter by ticker if specified
        if ticker:
            trades = [t for t in trades if t['ticker'] == ticker]
        
        return jsonify({
            'status': 'success',
            'trades': trades,
            'count': len(trades)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 6: Get Performance Metrics
# ============================================

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get trading performance metrics
    
    Response: {
        "total_trades": 45,
        "winning_trades": 32,
        "losing_trades": 13,
        "win_rate": 71.1,
        "profit_factor": 2.85,
        "avg_win": 3.2,
        "avg_loss": -1.3,
        "sharpe_ratio": 1.42,
        "max_drawdown": 6.5,
        "total_return": 16.8
    }
    """
    try:
        from src.paper_trading.metrics import MetricsCalculator
        
        metrics_calc = MetricsCalculator(db_path='trading.db')
        metrics = metrics_calc.calculate_all_metrics()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================
# ENDPOINT 7: Health Check
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Trading API is running',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Run in development mode (NOT production)
    # For personal use only, no authentication needed
    app.run(
        host='127.0.0.1',  # Only local
        port=5000,
        debug=True,
        use_reloader=True
    )
