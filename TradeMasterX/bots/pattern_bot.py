"""
bots/pattern_bot.py
PatternBot: Identifies candlestick patterns in price data to generate signals.
"""
import os
import pandas as pd
import numpy as np

class PatternBot:
    def __init__(self, use_real_data=False):
        """Initialize PatternBot with pattern detection capabilities.
        
        Args:
            use_real_data (bool): If True, attempt to fetch real data
        """
        self.price_history_path = os.path.join('data', 'price_history.csv')
        self.min_pattern_size = 5  # Minimum data points needed for pattern detection
        self.use_real_data = use_real_data
        
    def _load_price_data(self):
        """Load price history from CSV file."""
        if not os.path.exists(self.price_history_path):
            return None
            
        try:
            df = pd.read_csv(self.price_history_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading price data: {str(e)}")
            return None
    
    def _detect_double_bottom(self, prices):
        """Detect double bottom pattern (W-shape) - bullish reversal pattern."""
        if len(prices) < 15:
            return False
            
        # Take the last 15 prices for pattern detection
        window = prices[-15:].copy()
        
        # Normalize prices for easier pattern detection
        normalized = (window - window.min()) / (window.max() - window.min())
        
        # Calculate rolling minimum with window size 5
        rolling_min = normalized.rolling(window=5).min().dropna()
        
        # Find local minima indices
        local_minima = []
        for i in range(1, len(rolling_min) - 1):
            if rolling_min.iloc[i-1] > rolling_min.iloc[i] < rolling_min.iloc[i+1]:
                local_minima.append(i + 4)  # +4 because of rolling window offset
        
        # Need at least 2 minima for double bottom
        if len(local_minima) < 2:
            return False
        
        # Check if the last two minima are within 20% of each other's value
        # and separated by at least 3 data points
        last_min1 = local_minima[-1]
        last_min2 = local_minima[-2]
        
        if last_min1 - last_min2 >= 3:
            price1 = normalized.iloc[last_min1]
            price2 = normalized.iloc[last_min2]
            
            # Check if prices are close (within 15%)
            if abs(price1 - price2) < 0.15:
                # Check if we've started moving up from the second minimum
                if normalized.iloc[-1] > normalized.iloc[last_min1]:
                    return True
        
        return False
    
    def _detect_double_top(self, prices):
        """Detect double top pattern (M-shape) - bearish reversal pattern."""
        if len(prices) < 15:
            return False
            
        # Take the last 15 prices for pattern detection
        window = prices[-15:].copy()
        
        # Normalize prices for easier pattern detection
        normalized = (window - window.min()) / (window.max() - window.min())
        
        # Calculate rolling maximum with window size 5
        rolling_max = normalized.rolling(window=5).max().dropna()
        
        # Find local maxima indices
        local_maxima = []
        for i in range(1, len(rolling_max) - 1):
            if rolling_max.iloc[i-1] < rolling_max.iloc[i] > rolling_max.iloc[i+1]:
                local_maxima.append(i + 4)  # +4 because of rolling window offset
        
        # Need at least 2 maxima for double top
        if len(local_maxima) < 2:
            return False
        
        # Check if the last two maxima are within 20% of each other's value
        # and separated by at least 3 data points
        last_max1 = local_maxima[-1]
        last_max2 = local_maxima[-2]
        
        if last_max1 - last_max2 >= 3:
            price1 = normalized.iloc[last_max1]
            price2 = normalized.iloc[last_max2]
            
            # Check if prices are close (within 15%)
            if abs(price1 - price2) < 0.15:
                # Check if we've started moving down from the second maximum
                if normalized.iloc[-1] < normalized.iloc[last_max1]:
                    return True
        
        return False

    def _detect_head_and_shoulders(self, prices):
        """Detect head and shoulders pattern - bearish reversal pattern."""
        if len(prices) < 20:
            return False
            
        window = prices[-20:].copy()
        normalized = (window - window.min()) / (window.max() - window.min())
        
        # Calculate rolling maximum with window size 3
        rolling_max = normalized.rolling(window=3).max().dropna()
        
        # Find local maxima indices
        local_maxima = []
        for i in range(1, len(rolling_max) - 1):
            if rolling_max.iloc[i-1] < rolling_max.iloc[i] > rolling_max.iloc[i+1]:
                local_maxima.append(i + 2)  # +2 because of rolling window offset
        
        # Need at least 3 maxima for head and shoulders
        if len(local_maxima) < 3:
            return False
        
        # Get the last three maxima
        if len(local_maxima) >= 3:
            left = local_maxima[-3]
            head = local_maxima[-2]
            right = local_maxima[-1]
            
            left_val = normalized.iloc[left]
            head_val = normalized.iloc[head]
            right_val = normalized.iloc[right]
            
            # Head should be higher than shoulders
            if head_val > left_val and head_val > right_val:
                # Shoulders should be at similar heights (within 20%)
                if abs(left_val - right_val) < 0.2:
                    # Pattern should be recent (right shoulder near end)
                    if len(normalized) - right < 5:
                        return True
        
        return False
    
    def get_signal(self):
        """Analyze price patterns and return trading signal."""
        df = self._load_price_data()
        
        if df is None or len(df) < self.min_pattern_size:
            return 'HOLD'  # Not enough data for pattern detection
        
        prices = df['price']
        
        # Check for double bottom (bullish)
        if self._detect_double_bottom(prices):
            return 'BUY'
        
        # Check for double top (bearish)
        if self._detect_double_top(prices):
            return 'SELL'
            
        # Check for head and shoulders (bearish)
        if self._detect_head_and_shoulders(prices):
            return 'SELL'
        
        # No clear pattern detected
        return 'HOLD'
