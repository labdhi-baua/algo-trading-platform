"""
Technical Indicators Calculator
Implements 20+ technical analysis indicators
"""

import pandas as pd
import numpy as np
from typing import Tuple

class TechnicalIndicators:
    """Calculate all technical indicators"""
    
    @staticmethod
    def simple_moving_average(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average (SMA)"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def exponential_moving_average(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average (EMA) - gives more weight to recent data"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (RSI)
        - Measures momentum (0-100)
        - < 30 = Oversold (good entry point)
        - > 70 = Overbought (good exit point)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence (MACD)
        Returns: (MACD line, Signal line, Histogram)
        
        Buy signal: MACD crosses above signal line
        Sell signal: MACD crosses below signal line
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, 
                       std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        Returns: (Upper Band, Middle Band, Lower Band)
        
        Price touches upper band = overbought (sell signal)
        Price touches lower band = oversold (buy signal)
        """
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> pd.Series:
        """
        Average True Range (ATR)
        Measures volatility
        
        Use case: Set stop losses based on recent volatility
        Stop loss = Entry - (ATR * 2)
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> pd.Series:
        """
        Average Directional Index (ADX)
        Measures trend strength (0-100)
        
        < 20 = Weak trend (avoid trading)
        20-50 = Strong trend (good for trend trading)
        > 50 = Very strong trend
        """
        # Directional Movements
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate directional indicators
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
        minus_di = 100 * minus_dm.rolling(window=period).mean() / atr
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14, smooth: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator
        Similar to RSI but more sensitive
        
        < 20 = Oversold (buy signal)
        > 80 = Overbought (sell signal)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d_percent = k_percent.rolling(window=smooth).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def cci(high: pd.Series, low: pd.Series, close: pd.Series, 
           period: int = 20) -> pd.Series:
        """
        Commodity Channel Index (CCI)
        Identifies cyclical trends and reversals
        
        > 100 = Strong uptrend
        < -100 = Strong downtrend
        """
        tp = (high + low + close) / 3  # Typical Price
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On-Balance Volume (OBV)
        Cumulative buying/selling pressure
        
        Rising OBV confirms uptrend
        Falling OBV confirms downtrend
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def roc(data: pd.Series, period: int = 12) -> pd.Series:
        """
        Rate of Change (ROC)
        Measures momentum
        
        > 0 = Uptrend
        < 0 = Downtrend
        """
        return ((data - data.shift(period)) / data.shift(period)) * 100
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> pd.Series:
        """
        Williams %R
        Similar to Stochastic but inverted
        
        -80 to 0 range
        > -20 = Overbought (sell)
        < -80 = Oversold (buy)
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr
    
    @staticmethod
    def donchian_channels(high: pd.Series, low: pd.Series, 
                         period: int = 20) -> Tuple[pd.Series, pd.Series]:
        """
        Donchian Channels - Breakout levels
        
        Returns: (Upper channel, Lower channel)
        
        Price breaks above upper = Breakout (buy signal)
        Price breaks below lower = Breakdown (sell signal)
        """
        upper = high.rolling(window=period).max()
        lower = low.rolling(window=period).min()
        return upper, lower
    
    @staticmethod
    def ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> dict:
        """
        Ichimoku Cloud
        Japanese indicator combining trend, support/resistance, momentum
        
        Returns dict with all components
        """
        # Conversion line (Tenkan-sen)
        conversion = (high.rolling(9).max() + low.rolling(9).min()) / 2
        
        # Base line (Kijun-sen)
        baseline = (high.rolling(26).max() + low.rolling(26).min()) / 2
        
        # Leading span A (Senkou A)
        senkou_a = ((conversion + baseline) / 2).shift(26)
        
        # Leading span B (Senkou B)
        senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        
        # Lagging span (Chikou)
        chikou = close.shift(-26)
        
        return {
            'conversion': conversion,
            'baseline': baseline,
            'senkou_a': senkou_a,
            'senkou_b': senkou_b,
            'chikou': chikou
        }
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators and add to DataFrame
        
        Expected DataFrame columns: 'Open', 'High', 'Low', 'Close', 'Volume'
        """
        # Trend indicators
        df['SMA_20'] = TechnicalIndicators.simple_moving_average(df['Close'], 20)
        df['SMA_50'] = TechnicalIndicators.simple_moving_average(df['Close'], 50)
        df['SMA_200'] = TechnicalIndicators.simple_moving_average(df['Close'], 200)
        df['EMA_12'] = TechnicalIndicators.exponential_moving_average(df['Close'], 12)
        df['EMA_26'] = TechnicalIndicators.exponential_moving_average(df['Close'], 26)
        df['ADX'] = TechnicalIndicators.adx(df['High'], df['Low'], df['Close'])
        
        # Momentum indicators
        df['RSI'] = TechnicalIndicators.rsi(df['Close'])
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = TechnicalIndicators.macd(df['Close'])
        df['Stochastic_K'], df['Stochastic_D'] = TechnicalIndicators.stochastic(
            df['High'], df['Low'], df['Close']
        )
        df['CCI'] = TechnicalIndicators.cci(df['High'], df['Low'], df['Close'])
        df['ROC'] = TechnicalIndicators.roc(df['Close'])
        df['Williams_R'] = TechnicalIndicators.williams_r(df['High'], df['Low'], df['Close'])
        
        # Volatility indicators
        df['Upper_BB'], df['Middle_BB'], df['Lower_BB'] = TechnicalIndicators.bollinger_bands(
            df['Close']
        )
        df['ATR'] = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        df['OBV'] = TechnicalIndicators.obv(df['Close'], df['Volume'])
        
        # Breakout indicators
        df['Donchian_High'], df['Donchian_Low'] = TechnicalIndicators.donchian_channels(
            df['High'], df['Low']
        )
        
        # Ichimoku
        ichimoku = TechnicalIndicators.ichimoku(df['High'], df['Low'], df['Close'])
        for key, value in ichimoku.items():
            df[f'Ichimoku_{key}'] = value
        
        return df


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Download sample data
    df = yf.download("AAPL", start="2023-01-01", end="2024-01-01", progress=False)
    
    # Calculate all indicators
    df = TechnicalIndicators.calculate_all_indicators(df)
    
    # Display results
    print("Sample Data with Indicators:")
    print(df[['Close', 'RSI', 'MACD', 'ADX', 'Upper_BB', 'Lower_BB']].tail(10))
    print(f"\nTotal indicators calculated: {len([col for col in df.columns if col.isupper()])}")
