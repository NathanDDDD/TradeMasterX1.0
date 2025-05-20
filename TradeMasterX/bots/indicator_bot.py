"""
bots/indicator_bot.py
IndicatorBot: Analyzes price data using moving averages to generate trading signals.
"""
import random
import datetime
import os
import csv
import time
import json
import logging

# For real-time data
try:
    import requests
except ImportError:
    requests = None

class IndicatorBot:
    def __init__(self, use_real_data=False):
        """Initialize the IndicatorBot with price history and moving average settings.
        
        Args:
            use_real_data (bool): If True, fetch real cryptocurrency price data from API
        """
        self.price_history = []
        self.short_window = 5  # Short moving average window
        self.long_window = 10  # Long moving average window
        self.history_file = os.path.join('data', 'price_history.csv')
        self.use_real_data = use_real_data
        
        # Create a simulated price history if none exists
        if not self._load_price_history():
            self._generate_price_history()
    
    def _load_price_history(self):
        """Load price history from CSV file. Returns True if successful."""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        if not os.path.exists(self.history_file):
            return False
            
        try:
            with open(self.history_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    timestamp, price = row
                    self.price_history.append(float(price))
            return True
        except Exception:
            return False
    
    def _generate_price_history(self):
        """Generate simulated price history if no real data is available."""
        # Start with a base price
        price = 10000.0  # Starting price ($10,000)
        
        # Create a realistic price series with some trend and volatility
        for _ in range(100):  # Generate 100 data points
            # Add some random movement (-2% to +2%)
            change = random.uniform(-0.02, 0.02)
            price = price * (1 + change)
            self.price_history.append(price)
            
        # Save the generated data
        self._save_price_history()
    
    def _save_price_history(self):
        """Save price history to CSV file."""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        with open(self.history_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'price'])
              # Generate timestamps starting from 100 days ago
            base_date = datetime.datetime.now() - datetime.timedelta(days=100)
            for i, price in enumerate(self.price_history):
                date = base_date + datetime.timedelta(days=i)
                writer.writerow([date.isoformat(), price])
    
    def _calculate_moving_average(self, window):
        """Calculate moving average for the given window size."""
        if len(self.price_history) < window:
            return None
        
        return sum(self.price_history[-window:]) / window
    
    def _update_price(self, coin='bitcoin'):
        """Add a new price point based on real data or simulation.
        
        Args:
            coin (str): The cryptocurrency to fetch price data for
        """
        if self.use_real_data and requests is not None:
            # Use real API to fetch cryptocurrency price
            try:
                # Use CoinGecko API (free, no API key needed)
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if coin in data and 'usd' in data[coin]:
                        new_price = float(data[coin]['usd'])
                        logging.info(f"Fetched real price data for {coin}: ${new_price}")
                    else:
                        # Fallback to simulation if data format is unexpected
                        logging.warning(f"Unexpected data format from API: {data}")
                        return self._simulate_price_update()
                else:
                    # API rate limit or other error, fall back to simulation
                    logging.warning(f"API request failed with status {response.status_code}")
                    return self._simulate_price_update()
                    
            except Exception as e:
                # Any error in the API request, fall back to simulation
                logging.error(f"Error fetching real price data: {e}")
                return self._simulate_price_update()
        else:
            # Use simulated price data
            return self._simulate_price_update()
            
        # Add the new price to history
        self.price_history.append(new_price)
        
        # Keep only the most recent 100 prices
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
            
        # Update the saved history
        self._save_price_history()
        
    def _simulate_price_update(self):
        """Simulate a price update based on the previous trend with some noise."""
        if not self.price_history:
            self.price_history.append(10000.0)  # Start at $10,000 if no history
            return
        
        last_price = self.price_history[-1]
        # Add some random movement (-1.5% to +1.5%)
        change = random.uniform(-0.015, 0.015)
        new_price = last_price * (1 + change)
        
        # Add the new price to history
        self.price_history.append(new_price)
        
        # Keep only the most recent 100 prices
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
            
        # Update the saved history
        self._save_price_history()
    
    def get_signal(self):
        """Generate a signal based on moving average crossover strategy."""
        # Update the price data first
        self._update_price()
        
        # Calculate moving averages
        short_ma = self._calculate_moving_average(self.short_window)
        long_ma = self._calculate_moving_average(self.long_window)
        
        # If we don't have enough data for both MAs, return HOLD
        if short_ma is None or long_ma is None:
            return "HOLD"
        
        # Check for crossover
        if short_ma > long_ma:
            # Short-term MA above long-term MA is bullish
            return "BUY"
        elif short_ma < long_ma:
            # Short-term MA below long-term MA is bearish
            return "SELL"
        else:
            # No significant difference
            return "HOLD"
