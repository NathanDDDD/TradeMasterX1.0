"""
core/coin_selector.py
Utility for selecting which coin to trade based on various strategies.
"""
import random
import time

class CoinSelector:
    def __init__(self, coins=['bitcoin'], strategy='round_robin'):
        """Initialize the coin selector with a list of available coins.
        
        Args:
            coins (list): List of available cryptocurrencies
            strategy (str): Selection strategy - 'round_robin', 'random', 'weighted'
        """
        self.coins = coins
        self.strategy = strategy
        self.current_index = 0
        self.last_selection = None
        self.last_selection_time = 0
        
        # Performance tracking (could be used for weighted selection)
        self.performance = {coin: 1.0 for coin in coins}  # Default equal weights
    
    def select_coin(self):
        """Select a coin for trading based on the chosen strategy.
        
        Returns:
            str: The selected coin symbol/name
        """
        if not self.coins:
            return None
            
        # Implement cool-down to avoid rapidly trading the same coin
        current_time = time.time()
        if self.last_selection and current_time - self.last_selection_time < 10:
            # If last selection was recent, use a different coin
            remaining_coins = [c for c in self.coins if c != self.last_selection]
            if not remaining_coins:
                return self.coins[0]  # Default to first if no alternative
            selected = self.select_from_list(remaining_coins)
        else:
            selected = self.select_from_list(self.coins)
            
        # Update tracking
        self.last_selection = selected
        self.last_selection_time = current_time
        
        return selected
        
    def select_from_list(self, coin_list):
        """Select a coin from the given list based on strategy.
        
        Args:
            coin_list (list): List of coins to select from
            
        Returns:
            str: Selected coin
        """
        if self.strategy == 'round_robin':
            selected = coin_list[self.current_index % len(coin_list)]
            self.current_index += 1
            return selected
            
        elif self.strategy == 'random':
            return random.choice(coin_list)
            
        elif self.strategy == 'weighted':
            # Get weights for the coins in the list
            weights = [self.performance.get(coin, 1.0) for coin in coin_list]
            # Normalize weights
            total = sum(weights)
            if total == 0:
                return random.choice(coin_list)
            norm_weights = [w/total for w in weights]
            
            # Use weighted random choice
            r = random.random()
            cumulative = 0
            for i, w in enumerate(norm_weights):
                cumulative += w
                if r <= cumulative:
                    return coin_list[i]
            
            # Fallback
            return coin_list[-1]
        
        # Default to first coin if invalid strategy
        return coin_list[0]
        
    def update_performance(self, coin, performance_value):
        """Update the performance score for a coin.
        
        Args:
            coin (str): Coin to update
            performance_value (float): New performance value
        """
        if coin in self.performance:
            # Exponential moving average to smooth performance changes
            self.performance[coin] = 0.7 * self.performance[coin] + 0.3 * performance_value
