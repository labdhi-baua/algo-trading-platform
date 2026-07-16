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