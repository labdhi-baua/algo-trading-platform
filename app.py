from flask import Flask, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv

from src.scheduler.signal_schedular import SignalScheduler

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
