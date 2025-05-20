"""
core/trade_executor.py
Simulates trades, logs them to trades.log and trade_history.csv, and sends notifications.
"""
import os
import csv
import datetime
import sqlite3
import sys
import json

# Add parent directory to path to allow imports from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import notification system - will be available when running as part of the main system
try:
    from notification_system import notify
except ImportError:
    # Fallback if notification system is not available
    def notify(level, message, force=False):
        print(f"[{level}] {message}")

class TradeExecutor:
    def __init__(self, coins=['bitcoin'], use_real_data=False):
        """Initialize trade executor with portfolio tracking and logging.
        
        Args:
            coins (list): List of cryptocurrencies to trade
            use_real_data (bool): Whether to use real market data
        """
        self.trades_log = os.path.join('logs', 'trades.log')
        self.history_csv = os.path.join('logs', 'trade_history.csv')
        self.db_path = os.path.join('trading_history.db')
        
        # Initialize portfolio with cash and each supported coin
        self.portfolio = {'cash': 10000.0}  # Start with $10,000
        for coin in coins:
            self.portfolio[coin] = 0.0
            
        self.current_prices = {coin: 10000.0 for coin in coins}  # Default prices
        self.default_coin = coins[0]  # First coin is the default
        self.coins = coins
        self.use_real_data = use_real_data
        
        # Set up API for real data if enabled
        if use_real_data:
            try:
                import requests
                self.requests = requests
            except ImportError:
                self.use_real_data = False
                notify('WARNING', 'Requests library not available. Falling back to simulated data.')
                self.requests = None
        else:
            self.requests = None
        
        # Ensure directories exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Ensure CSV has headers
        if not os.path.exists(self.history_csv):
            with open(self.history_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'coin', 'price', 'amount', 'portfolio_value'])
                
        # Initialize database
        self._init_database()
        
        # Load portfolio if it exists
        self._load_portfolio()
        
        # Get current price
        self._update_current_price()

    def _init_database(self):
        """Initialize SQLite database for more robust storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                coin TEXT,
                action TEXT,
                price REAL,
                amount REAL,
                portfolio_cash REAL,
                portfolio_value REAL
            )
            ''')
            
            # Create portfolio table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cash REAL,
                value REAL
            )
            ''')
            
            # Create coin_holdings table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER,
                coin TEXT,
                amount REAL,
                FOREIGN KEY (portfolio_id) REFERENCES portfolio (id)
            )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            notify('ERROR', f"Database initialization error: {str(e)}")
    
    def _load_portfolio(self):
        """Load the latest portfolio state from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the latest portfolio entry for cash
            cursor.execute('SELECT cash FROM portfolio ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            
            if result:
                self.portfolio['cash'] = result[0]
                
            # Check if coin_holdings table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coin_holdings'")
            if cursor.fetchone():
                # Get coin holdings
                cursor.execute('SELECT coin, amount FROM coin_holdings WHERE portfolio_id = (SELECT MAX(id) FROM portfolio)')
                coin_holdings = cursor.fetchall()
                
                for coin, amount in coin_holdings:
                    if coin in self.portfolio:
                        self.portfolio[coin] = amount
            
            conn.close()
        except Exception as e:
            notify('WARNING', f"Could not load portfolio: {str(e)}")
    
    def _update_current_price(self):
        """Get the current price for all coins from API or CSV files."""
        # Use real data if enabled
        if self.use_real_data and self.requests:
            try:
                for coin in self.coins:
                    # Try to get real price from CoinGecko API
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
                    response = self.requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if coin in data and 'usd' in data[coin]:
                            self.current_prices[coin] = data[coin]['usd']
                return
            except Exception as e:
                notify('WARNING', f"Failed to get real-time price data: {str(e)}. Using historical/simulated data.")
                pass
        
        # Fallback to CSV files
        for coin in self.coins:
            price_history_path = os.path.join('data', f'{coin}_price_history.csv')
            if os.path.exists(price_history_path):
                try:
                    with open(price_history_path, 'r') as f:
                        reader = csv.reader(f)
                        next(reader)  # Skip header
                        
                        # Get the last line (most recent price)
                        last_row = None
                        for row in reader:
                            last_row = row
                        
                        # Update price if we have data
                        if last_row and len(last_row) >= 2:
                            self.current_prices[coin] = float(last_row[1])
                except Exception:
                    # If we can't read the file, keep the default price
                    pass

    def _save_portfolio(self):
        """Save the current portfolio state to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate total portfolio value (cash + all coin values)
            portfolio_value = self.portfolio['cash']
            for coin in self.coins:
                if coin in self.portfolio and coin in self.current_prices:
                    portfolio_value += (self.portfolio[coin] * self.current_prices[coin])
            
            # Insert into portfolio table
            cursor.execute(
                'INSERT INTO portfolio (timestamp, cash, value) VALUES (?, ?, ?)',
                (datetime.datetime.now().isoformat(), self.portfolio['cash'], portfolio_value)
            )
            
            # Get the ID of the inserted portfolio entry
            portfolio_id = cursor.lastrowid
            
            # Insert coin holdings
            for coin in self.coins:
                if coin in self.portfolio:
                    cursor.execute(
                        'INSERT INTO coin_holdings (portfolio_id, coin, amount) VALUES (?, ?, ?)',
                        (portfolio_id, coin, self.portfolio[coin])
                    )
            
            conn.commit()
            conn.close()
            
            # Save to a JSON file as backup
            with open(os.path.join('data', 'portfolio.json'), 'w') as f:
                portfolio_data = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'cash': self.portfolio['cash'],
                    'coins': {coin: self.portfolio[coin] for coin in self.coins if coin in self.portfolio},
                    'value': portfolio_value
                }
                json.dump(portfolio_data, f, indent=4)
                
        except Exception as e:
            notify('ERROR', f"Failed to save portfolio: {str(e)}")

    def execute_trade(self, action, coin=None):
        """Simulate a trade and log it for a specific coin.
        
        Args:
            action (str): 'BUY' or 'SELL'
            coin (str, optional): Specific coin to trade. If None, uses default_coin.
        """
        # Use specified coin or default
        coin = coin or self.default_coin
        if coin not in self.coins:
            notify('ERROR', f"Cannot trade unknown coin: {coin}")
            return None
            
        timestamp = datetime.datetime.now().isoformat()
        
        # Update current prices before executing trade
        self._update_current_price()
        
        # Get current price for this coin
        current_price = self.current_prices[coin]
        
        # Execute the trade (update portfolio)
        trade_amount = 0.0
        if action == 'BUY':
            # Use 20% of cash for each buy
            cash_to_spend = self.portfolio['cash'] * 0.2
            trade_amount = cash_to_spend / current_price
            
            self.portfolio['cash'] -= cash_to_spend
            self.portfolio[coin] += trade_amount
            
        elif action == 'SELL':
            # Sell 50% of coin holdings
            trade_amount = self.portfolio[coin] * 0.5
            cash_gained = trade_amount * current_price
            
            self.portfolio['cash'] += cash_gained
            self.portfolio[coin] -= trade_amount
        
        # Calculate portfolio value
        portfolio_value = self.portfolio['cash']
        for c in self.coins:
            portfolio_value += (self.portfolio[c] * self.current_prices[c])
        
        # Log to text file
        with open(self.trades_log, 'a') as f:
            log_message = f"{timestamp}: {action} {coin} {trade_amount:.6f} at ${current_price:.2f}, Portfolio: ${portfolio_value:.2f}\n"
            f.write(log_message)
        
        # Log to CSV
        with open(self.history_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, action, coin, current_price, trade_amount, portfolio_value])
        
        # Log to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO trades (timestamp, coin, action, price, amount, portfolio_cash, portfolio_value) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (timestamp, coin, action, current_price, trade_amount, self.portfolio['cash'], portfolio_value)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            notify('ERROR', f"Database error: {str(e)}")
        
        # Save portfolio state
        self._save_portfolio()
        
        # Send notification
        trade_summary = f"Trade executed: {action} {coin} {trade_amount:.6f} at ${current_price:.2f}, Portfolio: ${portfolio_value:.2f}"
        notify('TRADE', trade_summary)
        
        return {
            'timestamp': timestamp,
            'coin': coin,
            'action': action,
            'price': current_price,
            'amount': trade_amount,
            'portfolio': self.portfolio,
            'portfolio_value': portfolio_value
        }