import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///trading.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 10000))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 0.02))
    ADX_THRESHOLD = int(os.getenv('ADX_THRESHOLD', 25))
    RSI_BUY_LOWER = int(os.getenv('RSI_BUY_LOWER', 30))
    RSI_BUY_UPPER = int(os.getenv('RSI_BUY_UPPER', 45))
    RSI_SELL_LOWER = int(os.getenv('RSI_SELL_LOWER', 55))
    RSI_SELL_UPPER = int(os.getenv('RSI_SELL_UPPER', 70))
    SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'True').lower() == 'true'
    MONITORED_TICKERS = os.getenv('MONITORED_TICKERS', 'AAPL,MSFT,GOOGL').split(',')
