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