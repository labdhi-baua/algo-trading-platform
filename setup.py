# setup.py
import os
import sqlite3
from pathlib import Path

# Clean requirements list embedded directly to fix the script bug
requirements = """# Web Framework
Flask==2.3.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.0

# Data & Finance
pandas>=2.0.0
numpy>=1.26.0
yfinance>=0.2.0

# Scheduling
APScheduler==3.10.0

# Database
SQLAlchemy==2.0.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0

# Logging
colorlog>=6.7.0

# Development
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
"""


def setup_project():
    print("\n" + "=" * 80)
    print("MASTER STRATEGY PAPER TRADING - SETUP SCRIPT")
    print("=" * 80)

    # ===== CREATE DIRECTORIES =====
    print("\n📁 Creating directories...")
    dirs = [
        'src/indicators',
        'src/risk_management',
        'src/paper_trading',
        'src/strategies',
        'src/scheduler',
        'src/api',  # Added to prevent Flask import crashes
        'templates',
        'static/js',
        'static/css',
        'config',
        'logs'
    ]

    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name}/")

    # ===== CREATE __init__.py FILES =====
    print("\n📄 Creating Python package files...")
    init_files = [
        'src/__init__.py',
        'src/indicators/__init__.py',
        'src/risk_management/__init__.py',
        'src/paper_trading/__init__.py',
        'src/strategies/__init__.py',
        'src/scheduler/__init__.py',
        'src/api/__init__.py',  # Added
    ]

    for file_name in init_files:
        Path(file_name).touch()
        print(f"  ✓ {file_name}")

    # ===== CREATE MAIN APP.PY =====
    print("\n🚀 Creating app.py...")
    create_app_file()
    print("  ✓ app.py")

    # ===== CREATE REQUIREMENTS.TXT =====
    print("\n📦 Creating requirements.txt...")
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("  ✓ requirements.txt")

    # ===== CREATE DATABASE =====
    print("\n🗄️  Creating database schema...")
    create_database()
    print("  ✓ trading.db")

    # ===== CREATE CONFIG =====
    print("\n⚙️  Creating configuration...")
    create_config()
    print("  ✓ config/config.py")

    # ===== CREATE .ENV =====
    print("\n⚙️  Creating environment file...")
    create_env_file()
    print("  ✓ .env")

    print("\n" + "=" * 80)
    print("✅ AUTOMATED SETUP COMPLETE!")
    print("=" * 80)


def create_app_file():
    app_code = '''from flask import Flask, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import API blueprints
from src.api.signals import signals_bp
from src.api.portfolio import portfolio_bp
from src.api.trades import trades_bp
from src.api.metrics import metrics_bp

app.register_blueprint(signals_bp, url_prefix='/api/signals')
app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
app.register_blueprint(trades_bp, url_prefix='/api/trades')
app.register_blueprint(metrics_bp, url_prefix='/api/metrics')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    from datetime import datetime
    return {
        'status': 'success',
        'message': 'Trading API is running',
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
'''
    with open('app.py', 'w') as f:
        f.write(app_code)


def create_database():
    conn = sqlite3.connect('trading.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            entry_date DATETIME NOT NULL,
            exit_date DATETIME,
            entry_price REAL NOT NULL,
            exit_price REAL,
            quantity INTEGER NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            profit REAL,
            profit_pct REAL,
            days_held INTEGER,
            status TEXT DEFAULT 'open',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            entry_price REAL NOT NULL,
            current_price REAL,
            unrealized_pl REAL,
            unrealized_pl_pct REAL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_values (
            id INTEGER PRIMARY KEY,
            date DATETIME NOT NULL,
            portfolio_value REAL NOT NULL,
            cash REAL NOT NULL,
            total_return REAL,
            total_return_pct REAL,
            UNIQUE(date)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            adx REAL,
            atr REAL,
            stoch_k REAL,
            stoch_d REAL,
            UNIQUE(ticker, timestamp)
        )
    ''')
    conn.commit()
    conn.close()


def create_config():
    config_code = '''import os
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
'''
    with open('config/config.py', 'w') as f:
        f.write(config_code)


def create_env_file():
    env_content = '''FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///trading.db
INITIAL_CAPITAL=10000
RISK_PER_TRADE=0.02
ADX_THRESHOLD=25
RSI_BUY_LOWER=30
RSI_BUY_UPPER=45
RSI_SELL_LOWER=55
RSI_SELL_UPPER=70
SCHEDULER_ENABLED=True
MONITORED_TICKERS=AAPL,MSFT,GOOGL,AMZN,TSLA
'''
    with open('.env', 'w') as f:
        f.write(env_content)


if __name__ == '__main__':
    setup_project()