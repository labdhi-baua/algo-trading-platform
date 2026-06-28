"""
Advanced Trading Strategies
Implements 10+ trading strategies using technical indicators
"""

import pandas as pd
import numpy as np
from typing import Tuple
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Base class for all strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.signals = None
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals
        Returns: Series with values 1 (buy), 0 (hold), -1 (sell)
        """
        pass
    
    def validate_data(self, df: pd.DataFrame):
        """Validate DataFrame has required columns"""
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required):
            raise ValueError(f"DataFrame must contain columns: {required}")


# ============= TREND-FOLLOWING STRATEGIES =============

class MovingAverageCrossover(BaseStrategy):
    """Buy when fast MA crosses above slow MA"""
    
    def __init__(self, fast: int = 20, slow: int = 50):
        super().__init__(f"MA Crossover ({fast}/{slow})")
        self.fast = fast
        self.slow = slow
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        self.validate_data(df)
        
        fast_ma = df['Close'].rolling(self.fast).mean()
        slow_ma = df['Close'].rolling(self.slow).mean()
        
        signals = pd.Series(0, index=df.index)
        signals[fast_ma > slow_ma] = 1
        signals[fast_ma < slow_ma] = -1
        
        return signals


class ADXTrendFilter(BaseStrategy):
    """Only trade when ADX shows strong trend"""
    
    def __init__(self, adx_threshold: float = 25):
        super().__init__(f"ADX Trend Filter (>{adx_threshold})")
        self.adx_threshold = adx_threshold
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        # Calculate ADX
        adx = TechnicalIndicators.adx(df['High'], df['Low'], df['Close'])
        
        # Strong uptrend/downtrend when ADX is high
        ema_fast = df['Close'].ewm(span=12).mean()
        ema_slow = df['Close'].ewm(span=26).mean()
        
        signals = pd.Series(0, index=df.index)
        signals[(adx > self.adx_threshold) & (ema_fast > ema_slow)] = 1
        signals[(adx > self.adx_threshold) & (ema_fast < ema_slow)] = -1
        
        return signals


# ============= MOMENTUM STRATEGIES =============

class RSIStrategy(BaseStrategy):
    """Buy when RSI oversold, sell when overbought"""
    
    def __init__(self, oversold: int = 30, overbought: int = 70):
        super().__init__(f"RSI Strategy ({oversold}/{overbought})")
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        rsi = TechnicalIndicators.rsi(df['Close'])
        
        signals = pd.Series(0, index=df.index)
        signals[rsi < self.oversold] = 1      # Buy oversold
        signals[rsi > self.overbought] = -1   # Sell overbought
        
        return signals


class MACDStrategy(BaseStrategy):
    """Buy when MACD crosses above signal line"""
    
    def __init__(self):
        super().__init__("MACD Strategy")
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        macd, signal, histogram = TechnicalIndicators.macd(df['Close'])
        
        signals = pd.Series(0, index=df.index)
        # Buy when MACD crosses above signal
        signals[macd > signal] = 1
        # Sell when MACD crosses below signal
        signals[macd < signal] = -1
        
        return signals


class CCIStrategy(BaseStrategy):
    """Trade based on CCI levels"""
    
    def __init__(self, upper: int = 100, lower: int = -100):
        super().__init__(f"CCI Strategy ({upper}/{lower})")
        self.upper = upper
        self.lower = lower
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        cci = TechnicalIndicators.cci(df['High'], df['Low'], df['Close'])
        
        signals = pd.Series(0, index=df.index)
        signals[cci > self.upper] = 1     # Strong uptrend
        signals[cci < self.lower] = -1    # Strong downtrend
        
        return signals


# ============= MEAN REVERSION STRATEGIES =============

class BollingerBandStrategy(BaseStrategy):
    """Buy at lower band (oversold), sell at upper band (overbought)"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(f"Bollinger Bands ({period}/{std_dev})")
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        upper, middle, lower = TechnicalIndicators.bollinger_bands(
            df['Close'], self.period, self.std_dev
        )
        
        signals = pd.Series(0, index=df.index)
        signals[df['Close'] < lower] = 1      # Buy oversold
        signals[df['Close'] > upper] = -1     # Sell overbought
        
        return signals


class MeanReversionZScore(BaseStrategy):
    """Trade based on Z-score distance from mean"""
    
    def __init__(self, period: int = 20, threshold: float = 2.0):
        super().__init__(f"Z-Score Mean Reversion ({period}/{threshold})")
        self.period = period
        self.threshold = threshold
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        self.validate_data(df)
        
        close = df['Close']
        sma = close.rolling(self.period).mean()
        std = close.rolling(self.period).std()
        
        z_score = (close - sma) / std
        
        signals = pd.Series(0, index=df.index)
        signals[z_score < -self.threshold] = 1    # Oversold
        signals[z_score > self.threshold] = -1    # Overbought
        
        return signals


# ============= BREAKOUT STRATEGIES =============

class DonchianBreakout(BaseStrategy):
    """Buy on breakout above highest high, sell on breakdown"""
    
    def __init__(self, period: int = 20):
        super().__init__(f"Donchian Breakout ({period})")
        self.period = period
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        upper, lower = TechnicalIndicators.donchian_channels(
            df['High'], df['Low'], self.period
        )
        
        signals = pd.Series(0, index=df.index)
        # Buy above upper channel (breakout)
        signals[df['Close'] > upper.shift(1)] = 1
        # Sell below lower channel (breakdown)
        signals[df['Close'] < lower.shift(1)] = -1
        
        return signals


# ============= COMBINATION STRATEGIES (MOST POWERFUL) =============

class TripleScreenStrategy(BaseStrategy):
    """
    Triple Screen Strategy - Three-timeframe analysis
    1. Daily chart: Identify major trend
    2. 4-hour chart: Find pullback opportunities
    3. 1-hour chart: Find exact entry point
    
    This simulates using 1-hour data with indicator ratios
    """
    
    def __init__(self):
        super().__init__("Triple Screen (Daily+4H+1H)")
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        # Screen 1: Daily trend (using 50-200 MA on 1-hour = simulates daily)
        daily_ma_fast = df['Close'].rolling(50).mean()
        daily_ma_slow = df['Close'].rolling(200).mean()
        daily_trend = daily_ma_fast > daily_ma_slow
        
        # Screen 2: 4-hour chart (MACD on 1-hour)
        macd, signal, _ = TechnicalIndicators.macd(df['Close'])
        macd_bullish = macd > signal
        
        # Screen 3: 1-hour entry (RSI)
        rsi = TechnicalIndicators.rsi(df['Close'])
        rsi_oversold = rsi < 30
        rsi_overbought = rsi > 70
        
        signals = pd.Series(0, index=df.index)
        # Buy: Uptrend + Bullish MACD + RSI oversold (good entry)
        signals[(daily_trend) & (macd_bullish) & (rsi_oversold)] = 1
        # Sell: Downtrend or RSI overbought
        signals[(~daily_trend) | (rsi_overbought)] = -1
        
        return signals


class TrendFollowingWithConfirmation(BaseStrategy):
    """
    Multiple confirmation: Trend + Momentum + Volatility
    1. Trend: EMA crossover (direction)
    2. Momentum: MACD or RSI (strength)
    3. Volume: OBV (confirmation)
    """
    
    def __init__(self):
        super().__init__("Trend + Momentum + Volume")
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        from src_technical_indicators import TechnicalIndicators
        self.validate_data(df)
        
        # Trend confirmation
        ema_fast = df['Close'].ewm(span=12).mean()
        ema_slow = df['Close'].ewm(span=26).mean()
        trend_bullish = ema_fast > ema_slow
        
        # Momentum confirmation
        macd, signal, _ = TechnicalIndicators.macd(df['Close'])
        momentum_bullish = macd > signal
        
        # Volume confirmation
        obv = TechnicalIndicators.obv(df['Close'], df['Volume'])
        volume_bullish = obv > obv.shift(1)
        
        signals = pd.Series(0, index=df.index)
        # Buy: All three conditions met
        signals[(trend_bullish) & (momentum_bullish) & (volume_bullish)] = 1
        # Sell: Trend breaks or momentum turns negative
        signals[(~trend_bullish) | (~momentum_bullish)] = -1
        
        return signals


class SupportResistanceStrategy(BaseStrategy):
    """
    Trade support and resistance levels
    Buy at support with volume confirmation
    Sell at resistance
    """
    
    def __init__(self, lookback: int = 20):
        super().__init__(f"Support/Resistance ({lookback})")
        self.lookback = lookback
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        self.validate_data(df)
        
        # Calculate support and resistance
        resistance = df['High'].rolling(self.lookback).max()
        support = df['Low'].rolling(self.lookback).min()
        
        signals = pd.Series(0, index=df.index)
        
        # Buy near support with confirmation (close near low)
        near_support = df['Close'] < (support + 0.02 * (resistance - support))
        volume_confirm = df['Volume'] > df['Volume'].rolling(20).mean()
        signals[near_support & volume_confirm] = 1
        
        # Sell at resistance
        signals[df['Close'] > resistance.shift(1)] = -1
        
        return signals


# ============= STRATEGY ANALYZER =============

class StrategyAnalyzer:
    """Analyze and compare multiple strategies"""
    
    @staticmethod
    def backtest_all_strategies(df: pd.DataFrame, initial_capital: float = 10000) -> dict:
        """
        Test all strategies and return results
        """
        strategies = [
            MovingAverageCrossover(20, 50),
            MovingAverageCrossover(12, 26),
            ADXTrendFilter(25),
            RSIStrategy(30, 70),
            MACDStrategy(),
            CCIStrategy(),
            BollingerBandStrategy(),
            MeanReversionZScore(),
            DonchianBreakout(),
            TripleScreenStrategy(),
            TrendFollowingWithConfirmation(),
            SupportResistanceStrategy()
        ]
        
        results = {}
        
        for strategy in strategies:
            signals = strategy.generate_signals(df.copy())
            
            # Simple backtest calculation
            returns = df['Close'].pct_change()
            strategy_returns = returns * signals.shift(1)
            
            cumulative_return = (1 + strategy_returns).cumprod() - 1
            total_return = cumulative_return.iloc[-1] * 100
            
            win_trades = len(signals[signals == 1])
            lose_trades = len(signals[signals == -1])
            
            results[strategy.name] = {
                'Total Return %': round(total_return, 2),
                'Buy Signals': win_trades,
                'Sell Signals': lose_trades,
                'Sharpe Ratio': round(strategy_returns.mean() / strategy_returns.std() * np.sqrt(252), 2)
            }
        
        return results


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Download data
    df = yf.download("AAPL", start="2023-01-01", end="2024-01-01", progress=False)
    
    # Test single strategy
    strategy = TripleScreenStrategy()
    signals = strategy.generate_signals(df)
    print(f"Strategy: {strategy.name}")
    print(f"Buy signals: {len(signals[signals == 1])}")
    print(f"Sell signals: {len(signals[signals == -1])}")
    
    # Compare all strategies
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    results = StrategyAnalyzer.backtest_all_strategies(df)
    
    results_df = pd.DataFrame(results).T
    print(results_df.sort_values('Total Return %', ascending=False))
