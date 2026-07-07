"""
COMPLETE FRONTEND & REAL-TIME SCHEDULER IMPLEMENTATION
For Master Strategy Paper Trading Website
"""

# ============================================
# PART 4: STEP 3 - REAL-TIME SIGNAL SCHEDULER
# ============================================

"""
STEP 3: Create Scheduler for Automatic Signal Generation

Location: src/scheduler/signal_scheduler.py

What to Do:
1. Run every 4 hours to check for new signals
2. Download latest 4-hour candle data
3. Generate signals automatically
4. Store in database
5. Notify user of new signals

This runs in the background while your website is open
"""

# Example: src/scheduler/signal_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalScheduler:
    """
    Automatically generates trading signals every 4 hours
    """
    
    def __init__(self, strategy, tickers: list, db_path: str = 'trading.db'):
        """
        Initialize scheduler
        
        Args:
            strategy: MasterStrategyIntegrated instance
            tickers: List of tickers to monitor (e.g., ['AAPL', 'MSFT', 'GOOGL'])
            db_path: Path to SQLite database
        """
        self.strategy = strategy
        self.tickers = tickers
        self.db_path = db_path
        self.scheduler = BackgroundScheduler()
        
        # Schedule jobs
        self._schedule_jobs()
    
    def _schedule_jobs(self):
        """Schedule signal generation jobs"""
        
        # Run every 4 hours at market close (4 PM EST)
        # Adjust times based on your preference
        
        # Morning check (before market open)
        self.scheduler.add_job(
            self.check_signals,
            'cron',
            hour=9,
            minute=30,
            timezone='US/Eastern',
            id='morning_signal_check'
        )
        
        # Noon check
        self.scheduler.add_job(
            self.check_signals,
            'cron',
            hour=12,
            minute=0,
            timezone='US/Eastern',
            id='noon_signal_check'
        )
        
        # Afternoon check
        self.scheduler.add_job(
            self.check_signals,
            'cron',
            hour=16,
            minute=0,
            timezone='US/Eastern',
            id='afternoon_signal_check'
        )
        
        # Evening check
        self.scheduler.add_job(
            self.check_signals,
            'cron',
            hour=20,
            minute=0,
            timezone='US/Eastern',
            id='evening_signal_check'
        )
        
        logger.info("✓ Signal scheduler jobs configured")
    
    def check_signals(self):
        """
        Check for new signals (called by scheduler)
        """
        logger.info(f"🔍 Checking signals at {datetime.now()}")
        
        for ticker in self.tickers:
            try:
                # Download data
                df = yf.download(ticker, period='2y', progress=False)
                
                # Generate signals
                signals = self.strategy.generate_signals(ticker, df)
                
                # Store and log
                for signal in signals:
                    self.strategy.store_signal(signal)
                    logger.info(
                        f"✓ {signal.signal_type} signal for {ticker} "
                        f"(Confidence: {signal.confidence}%)"
                    )
                
            except Exception as e:
                logger.error(f"✗ Error checking {ticker}: {e}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✓ Signal scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✓ Signal scheduler stopped")
    
    def is_running(self):
        """Check if scheduler is running"""
        return self.scheduler.running


# ============================================
# PART 5: FRONTEND - HTML/JAVASCRIPT
# ============================================

"""
STEP 4: Create Web Frontend

Location: templates/index.html, static/js/app.js

This is a complete dashboard showing:
- Recent signals
- Portfolio status
- Trade history
- Performance metrics
- Real-time updates
"""

# Example: templates/index.html

html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master Swing Trader - Paper Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #e0e0e0;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: rgba(20, 20, 30, 0.8);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 1px solid rgba(100, 200, 255, 0.2);
        }
        
        h1 {
            color: #64c8ff;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .status {
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }
        
        .status-item {
            background: rgba(50, 50, 70, 0.8);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #64c8ff;
        }
        
        .status-label {
            color: #a0a0a0;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .status-value {
            color: #64c8ff;
            font-size: 24px;
            font-weight: bold;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 1200px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: rgba(30, 30, 45, 0.9);
            border: 1px solid rgba(100, 200, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
        }
        
        .card h2 {
            color: #64c8ff;
            margin-bottom: 15px;
            font-size: 18px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(100, 200, 255, 0.3);
        }
        
        .signal-item {
            background: rgba(50, 50, 70, 0.6);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        
        .signal-item.sell {
            border-left-color: #f44336;
        }
        
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .signal-type {
            font-weight: bold;
            color: #4CAF50;
            font-size: 14px;
            text-transform: uppercase;
        }
        
        .signal-item.sell .signal-type {
            color: #f44336;
        }
        
        .confidence {
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .signal-details {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            font-size: 12px;
            margin-top: 10px;
        }
        
        .detail {
            background: rgba(100, 200, 255, 0.1);
            padding: 8px;
            border-radius: 4px;
        }
        
        .detail-label {
            color: #a0a0a0;
            font-size: 10px;
            text-transform: uppercase;
            margin-bottom: 3px;
        }
        
        .detail-value {
            color: #fff;
            font-weight: bold;
        }
        
        .portfolio-stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(100, 200, 255, 0.1);
        }
        
        .portfolio-stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #a0a0a0;
        }
        
        .stat-value {
            color: #64c8ff;
            font-weight: bold;
        }
        
        .stat-value.positive {
            color: #4CAF50;
        }
        
        .stat-value.negative {
            color: #f44336;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th {
            background: rgba(50, 50, 70, 0.8);
            color: #64c8ff;
            padding: 12px;
            text-align: left;
            font-size: 12px;
            text-transform: uppercase;
            border-bottom: 2px solid rgba(100, 200, 255, 0.3);
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid rgba(100, 200, 255, 0.1);
        }
        
        tr:hover {
            background: rgba(100, 200, 255, 0.05);
        }
        
        .btn {
            background: #64c8ff;
            color: #1e1e2e;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #4ab5e6;
            transform: translateY(-2px);
        }
        
        .btn.danger {
            background: #f44336;
            color: white;
        }
        
        .btn.danger:hover {
            background: #d32f2f;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #a0a0a0;
        }
        
        .spinner {
            border: 4px solid rgba(100, 200, 255, 0.2);
            border-top: 4px solid #64c8ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
            border-left: 4px solid;
        }
        
        .alert.success {
            background: rgba(76, 175, 80, 0.2);
            border-left-color: #4CAF50;
            color: #4CAF50;
        }
        
        .alert.error {
            background: rgba(244, 67, 54, 0.2);
            border-left-color: #f44336;
            color: #f44336;
        }
        
        .alert.info {
            background: rgba(100, 200, 255, 0.2);
            border-left-color: #64c8ff;
            color: #64c8ff;
        }
        
        #chart {
            height: 400px;
            margin-top: 15px;
        }
        
        .refresh-btn {
            float: right;
            padding: 8px 15px;
            background: rgba(100, 200, 255, 0.2);
            border: 1px solid #64c8ff;
            color: #64c8ff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .refresh-btn:hover {
            background: rgba(100, 200, 255, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🚀 Master Swing Trader</h1>
            <p>Paper Trading Dashboard - 4-Hour Swing Strategy</p>
            
            <div class="status">
                <div class="status-item">
                    <div class="status-label">Portfolio Value</div>
                    <div class="status-value" id="portfolioValue">$10,000.00</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Total P&L</div>
                    <div class="status-value" id="totalPnL">+$500.00</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Win Rate</div>
                    <div class="status-value" id="winRate">72.5%</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Active Signals</div>
                    <div class="status-value" id="activeSignals">3</div>
                </div>
            </div>
        </header>
        
        <!-- Alerts -->
        <div id="alertContainer"></div>
        
        <!-- Main Dashboard -->
        <div class="dashboard">
            <!-- Signals Card -->
            <div class="card">
                <h2>
                    Recent Trading Signals
                    <button class="refresh-btn" onclick="refreshSignals()">↻ Refresh</button>
                </h2>
                <div id="signalsContainer" class="loading">
                    <div class="spinner"></div>
                    <p>Loading signals...</p>
                </div>
            </div>
            
            <!-- Portfolio Card -->
            <div class="card">
                <h2>Portfolio Status</h2>
                <div id="portfolioContainer" class="loading">
                    <div class="spinner"></div>
                    <p>Loading portfolio...</p>
                </div>
            </div>
        </div>
        
        <!-- Performance Chart -->
        <div class="card">
            <h2>Performance Analytics</h2>
            <div class="dashboard">
                <div>
                    <canvas id="performanceChart"></canvas>
                </div>
                <div>
                    <canvas id="metricsChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Trade History -->
        <div class="card">
            <h2>
                Trade History
                <button class="refresh-btn" onclick="refreshTrades()">↻ Refresh</button>
            </h2>
            <div id="tradesContainer" class="loading">
                <div class="spinner"></div>
                <p>Loading trades...</p>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="/static/js/app.js"></script>
    <script src="/static/js/api.js"></script>
</body>
</html>
'''


# Example: static/js/api.js

js_api = '''
/**
 * API Client for Master Trading Strategy
 * Handles all communication with Flask backend
 */

const API_BASE = 'http://127.0.0.1:5000/api';

// ============================================
// Signal API
// ============================================

async function fetchSignals(limit = 10) {
    try {
        const response = await fetch(`${API_BASE}/signals/recent?limit=${limit}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.signals;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error fetching signals:', error);
        showAlert('Error fetching signals: ' + error.message, 'error');
        return [];
    }
}

async function generateSignals(ticker, days = 500) {
    try {
        const response = await fetch(`${API_BASE}/signals/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: ticker,
                days: days
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.signals;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error generating signals:', error);
        showAlert('Error generating signals: ' + error.message, 'error');
        return [];
    }
}

// ============================================
// Portfolio API
// ============================================

async function fetchPortfolio() {
    try {
        const response = await fetch(`${API_BASE}/portfolio`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.portfolio;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error fetching portfolio:', error);
        showAlert('Error fetching portfolio: ' + error.message, 'error');
        return null;
    }
}

// ============================================
// Trade API
// ============================================

async function executeTrade(ticker, action, entry, stop, target, quantity) {
    try {
        const response = await fetch(`${API_BASE}/trades/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: ticker,
                action: action,
                entry: entry,
                stop: stop,
                target: target,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert(`✓ Trade executed: ${action} ${quantity} ${ticker} @ ${entry}`, 'success');
            return data;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error executing trade:', error);
        showAlert('Error executing trade: ' + error.message, 'error');
        return null;
    }
}

async function fetchTradeHistory(limit = 20) {
    try {
        const response = await fetch(`${API_BASE}/trades/history?limit=${limit}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.trades;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error fetching trade history:', error);
        showAlert('Error fetching trades: ' + error.message, 'error');
        return [];
    }
}

// ============================================
// Metrics API
// ============================================

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.metrics;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error fetching metrics:', error);
        showAlert('Error fetching metrics: ' + error.message, 'error');
        return null;
    }
}

// ============================================
// Health Check
// ============================================

async function healthCheck() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        return data.status === 'success';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// ============================================
// Utility Functions
// ============================================

function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    container.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatPercent(value) {
    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
}
'''


# Example: static/js/app.js

js_app = '''
/**
 * Main Application Logic
 * Handles dashboard updates and user interactions
 */

// Refresh intervals (in milliseconds)
const SIGNAL_REFRESH_INTERVAL = 60000; // 1 minute
const PORTFOLIO_REFRESH_INTERVAL = 30000; // 30 seconds
const METRICS_REFRESH_INTERVAL = 60000; // 1 minute

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('✓ Dashboard loaded');
    initializeDashboard();
    setupAutoRefresh();
});

// ============================================
// Initialization
// ============================================

async function initializeDashboard() {
    // Check API health
    const isHealthy = await healthCheck();
    if (!isHealthy) {
        showAlert('⚠ API server not responding. Make sure Flask is running!', 'error');
        return;
    }
    
    // Load initial data
    await loadSignals();
    await loadPortfolio();
    await loadMetrics();
}

function setupAutoRefresh() {
    // Auto-refresh signals
    setInterval(async () => {
        await loadSignals();
    }, SIGNAL_REFRESH_INTERVAL);
    
    // Auto-refresh portfolio
    setInterval(async () => {
        await loadPortfolio();
    }, PORTFOLIO_REFRESH_INTERVAL);
    
    // Auto-refresh metrics
    setInterval(async () => {
        await loadMetrics();
    }, METRICS_REFRESH_INTERVAL);
}

// ============================================
// Load Signals
// ============================================

async function loadSignals() {
    const signals = await fetchSignals(10);
    displaySignals(signals);
}

function displaySignals(signals) {
    const container = document.getElementById('signalsContainer');
    
    if (!signals || signals.length === 0) {
        container.innerHTML = '<p style="color: #a0a0a0;">No signals yet</p>';
        return;
    }
    
    let html = '';
    for (const signal of signals) {
        const isSell = signal.signal_type === 'SELL';
        const confidence = signal.confidence || 0;
        
        html += `
            <div class="signal-item ${isSell ? 'sell' : ''}">
                <div class="signal-header">
                    <div>
                        <span class="signal-type">${signal.signal_type}</span>
                        <span style="color: #a0a0a0; font-size: 12px; margin-left: 10px;">
                            ${signal.ticker || 'N/A'}
                        </span>
                    </div>
                    <span class="confidence">${confidence.toFixed(0)}%</span>
                </div>
                
                <div class="signal-details">
                    <div class="detail">
                        <div class="detail-label">Entry</div>
                        <div class="detail-value">$${(signal.entry_price || 0).toFixed(2)}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Stop</div>
                        <div class="detail-value">$${(signal.stop_loss || 0).toFixed(2)}</div>
                    </div>
                    <div class="detail">
                        <div class="detail-label">Target</div>
                        <div class="detail-value">$${(signal.take_profit || 0).toFixed(2)}</div>
                    </div>
                </div>
                
                <div style="color: #a0a0a0; font-size: 11px; margin-top: 8px;">
                    ${signal.reason || 'Generated by Master Strategy'}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function refreshSignals() {
    document.getElementById('signalsContainer').innerHTML = 
        '<div class="loading"><div class="spinner"></div><p>Refreshing...</p></div>';
    loadSignals();
}

// ============================================
// Load Portfolio
// ============================================

async function loadPortfolio() {
    const portfolio = await fetchPortfolio();
    displayPortfolio(portfolio);
}

function displayPortfolio(portfolio) {
    const container = document.getElementById('portfolioContainer');
    
    if (!portfolio) {
        container.innerHTML = '<p style="color: #a0a0a0;">Unable to load portfolio</p>';
        return;
    }
    
    const cash = portfolio.cash || 0;
    const totalValue = portfolio.total_value || 0;
    const totalReturn = portfolio.total_return || 0;
    const totalReturnPct = portfolio.total_return_pct || 0;
    const positions = portfolio.positions || [];
    
    // Update header stats
    document.getElementById('portfolioValue').textContent = formatCurrency(totalValue);
    document.getElementById('totalPnL').textContent = formatCurrency(totalReturn);
    
    // Build positions table
    let html = '<table><thead><tr>';
    html += '<th>Ticker</th>';
    html += '<th>Qty</th>';
    html += '<th>Entry</th>';
    html += '<th>Current</th>';
    html += '<th>P&L</th>';
    html += '<th>%</th>';
    html += '</tr></thead><tbody>';
    
    if (positions.length > 0) {
        for (const pos of positions) {
            const pnlClass = (pos.unrealized_pl || 0) >= 0 ? 'positive' : 'negative';
            html += `<tr>
                <td>${pos.ticker}</td>
                <td>${pos.quantity}</td>
                <td>${formatCurrency(pos.entry)}</td>
                <td>${formatCurrency(pos.current)}</td>
                <td class="stat-value ${pnlClass}">${formatCurrency(pos.unrealized_pl || 0)}</td>
                <td class="stat-value ${pnlClass}">${formatPercent(pos.unrealized_pl_pct || 0)}</td>
            </tr>`;
        }
    } else {
        html += '<tr><td colspan="6" style="text-align: center; color: #a0a0a0;">No open positions</td></tr>';
    }
    
    html += '</tbody></table>';
    
    // Add portfolio stats
    html += '<div style="margin-top: 20px;">';
    html += `<div class="portfolio-stat">
        <span class="stat-label">Cash Available</span>
        <span class="stat-value">${formatCurrency(cash)}</span>
    </div>`;
    html += `<div class="portfolio-stat">
        <span class="stat-label">Total Value</span>
        <span class="stat-value">${formatCurrency(totalValue)}</span>
    </div>`;
    html += `<div class="portfolio-stat">
        <span class="stat-label">Total Return</span>
        <span class="stat-value ${totalReturnPct >= 0 ? 'positive' : 'negative'}">
            ${formatCurrency(totalReturn)} (${formatPercent(totalReturnPct)})
        </span>
    </div>`;
    html += '</div>';
    
    container.innerHTML = html;
}

// ============================================
// Load Metrics
// ============================================

async function loadMetrics() {
    const metrics = await fetchMetrics();
    displayMetrics(metrics);
    updateMetricsChart(metrics);
}

function displayMetrics(metrics) {
    if (!metrics) return;
    
    document.getElementById('winRate').textContent = 
        metrics.win_rate ? metrics.win_rate.toFixed(1) + '%' : 'N/A';
    document.getElementById('activeSignals').textContent = 
        metrics.total_trades || '0';
}

function updateMetricsChart(metrics) {
    if (!metrics) return;
    
    const ctx = document.getElementById('metricsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Win Rate', 'Profit Factor', 'Sharpe Ratio', 'Max Drawdown'],
            datasets: [{
                label: 'Metrics',
                data: [
                    metrics.win_rate || 0,
                    (metrics.profit_factor || 0) * 10,
                    (metrics.sharpe_ratio || 0) * 10,
                    Math.abs(metrics.max_drawdown || 0)
                ],
                backgroundColor: [
                    'rgba(76, 175, 80, 0.6)',
                    'rgba(100, 200, 255, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                    'rgba(244, 67, 54, 0.6)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#a0a0a0'
                    },
                    grid: {
                        color: 'rgba(100, 200, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0a0a0'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// ============================================
// Load Trades
// ============================================

async function loadTrades() {
    const trades = await fetchTradeHistory(20);
    displayTrades(trades);
}

function displayTrades(trades) {
    const container = document.getElementById('tradesContainer');
    
    if (!trades || trades.length === 0) {
        container.innerHTML = '<p style="color: #a0a0a0;">No closed trades yet</p>';
        return;
    }
    
    let html = '<table><thead><tr>';
    html += '<th>Ticker</th>';
    html += '<th>Entry</th>';
    html += '<th>Exit</th>';
    html += '<th>Qty</th>';
    html += '<th>Profit</th>';
    html += '<th>Return %</th>';
    html += '<th>Days</th>';
    html += '</tr></thead><tbody>';
    
    for (const trade of trades) {
        const profitClass = (trade.profit || 0) >= 0 ? 'positive' : 'negative';
        html += `<tr>
            <td>${trade.ticker}</td>
            <td>${formatCurrency(trade.entry)}</td>
            <td>${formatCurrency(trade.exit)}</td>
            <td>${trade.quantity}</td>
            <td class="stat-value ${profitClass}">${formatCurrency(trade.profit || 0)}</td>
            <td class="stat-value ${profitClass}">${formatPercent(trade.profit_pct || 0)}</td>
            <td>${trade.days_held || 0}</td>
        </tr>`;
    }
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function refreshTrades() {
    document.getElementById('tradesContainer').innerHTML = 
        '<div class="loading"><div class="spinner"></div><p>Refreshing...</p></div>';
    loadTrades();
}
'''

print("✓ Frontend HTML and JavaScript created")
print("\nSave the following files:")
print("  1. templates/index.html")
print("  2. static/js/api.js")
print("  3. static/js/app.js")
