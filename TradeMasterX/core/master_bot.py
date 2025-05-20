"""
core/master_bot.py
Loads and runs all bots, aggregates signals, and coordinates trade execution.
"""
from core.trade_executor import TradeExecutor
from core.coin_selector import CoinSelector
from bots.indicator_bot import IndicatorBot
from bots.pattern_bot import PatternBot
from bots.signal_bot import SignalBot
from bots.sentiment_bot import SentimentBot
from bots.prediction_bot import PredictionBot
import os
import csv
import time
import sys
import logging

# Import notification system if available
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from notification_system import notify
except ImportError:
    # Fallback if notification system is not available
    def notify(level, message, force=False):
        print(f"[{level}] {message}")

class MasterBot:
    def __init__(self, config=None):
        """Initialize all bots and trade executor.
        
        Args:
            config (dict): Configuration dictionary with parameters:
                - use_real_data (bool): Whether to use real-time data feeds
                - coins (list): List of cryptocurrencies to trade
                - days (int): Number of days to simulate
                - log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        # Set default configuration
        self.config = {
            'use_real_data': False,
            'coins': ['bitcoin', 'ethereum', 'litecoin'],
            'days': 7,
            'log_level': 'INFO'
        }
        
        # Update with provided configuration
        if config:
            self.config.update(config)
            
        # Configure logging
        log_level = getattr(logging, self.config['log_level'])
        logging.basicConfig(
            filename=os.path.join('logs', 'system.log'),
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize bots with configuration
        self.bots = [
            IndicatorBot(use_real_data=self.config['use_real_data']),
            PatternBot(use_real_data=self.config['use_real_data']),
            SignalBot(),
            SentimentBot(),
            PredictionBot()
        ]
        
        # Initialize trade executor with configuration
        self.trade_executor = TradeExecutor(
            coins=self.config['coins'],
            use_real_data=self.config['use_real_data']
        )
        
        # Initialize coin selector
        self.coin_selector = CoinSelector(
            coins=self.config['coins'],
            strategy='round_robin'  # Start with round robin by default
        )
        
        self.log_path = os.path.join('logs', 'system.log')
        self.control_path = os.path.join('commands', 'control.txt')
        
        # Log initialization
        coins_str = ', '.join(self.config['coins'])
        data_type = 'REAL-TIME' if self.config['use_real_data'] else 'SIMULATED'
        notify('INFO', f'MasterBot initialized with 5 bots, trading {coins_str} with {data_type} data')

    def log(self, message):
        """Log system activity to system.log."""
        with open(self.log_path, 'a') as f:
            f.write(message + '\n')

    def check_control(self):
        """Check control.txt for pause/resume commands."""
        if not os.path.exists(self.control_path):
            return 'RUN'
        with open(self.control_path, 'r') as f:
            cmd = f.read().strip().upper()
        return cmd if cmd in ['PAUSE', 'RUN'] else 'RUN'
        
    def run(self):
        """Main loop: run bots, aggregate signals, and execute trades if consensus."""
        print("MasterBot is running. Press Ctrl+C to stop.")
        notify('INFO', 'MasterBot starting trading operations')
        
        try:
            while True:
                try:
                    if self.check_control() == 'PAUSE':
                        message = 'System paused by control.txt'
                        print(message)
                        self.log(message)
                        time.sleep(2)
                        continue
                        
                    # Get signals from all bots
                    signals = [bot.get_signal() for bot in self.bots]
                    bot_names = ['Indicator', 'Pattern', 'Signal', 'Sentiment', 'Prediction']
                    
                    # Log detailed signal information
                    signal_detail = ", ".join([f"{bot_names[i]}: {signals[i]}" for i in range(len(signals))])
                    message = f"Signals: {signals} [{signal_detail}]"
                    print(message)
                    self.log(message)
                    
                    # Count consensus
                    trade_executed = False
                    for direction in ['BUY', 'SELL']:
                        if signals.count(direction) >= 3:
                            # Use coin selector to choose which coin to trade
                            selected_coin = self.coin_selector.select_coin()
                            
                            # Execute trade and get trade details
                            trade_result = self.trade_executor.execute_trade(direction, selected_coin)
                            
                            # Format a detailed message
                            message = f"Trade executed: {direction} {selected_coin} (consensus: {signals.count(direction)}/5)"
                            
                            # Add portfolio details if available
                            if isinstance(trade_result, dict) and 'portfolio_value' in trade_result:
                                message += f", Portfolio: ${trade_result['portfolio_value']:.2f}"
                                
                                # Update coin performance if trade was successful
                                if 'portfolio' in trade_result and selected_coin in trade_result['portfolio']:
                                    # Simple performance metric: more holdings is better
                                    performance = trade_result['portfolio'][selected_coin]
                                    self.coin_selector.update_performance(selected_coin, performance)
                            
                            print(message)
                            self.log(message)
                            notify('TRADE', message)
                            trade_executed = True
                            break
                    
                    if not trade_executed:
                        print("No consensus reached. No trade executed.")
                    
                    # Wait before next cycle
                    time.sleep(2)
                    
                except Exception as e:
                    error_message = f"Error in main loop: {str(e)}"
                    print(error_message)
                    self.log(error_message)
                    notify('ERROR', error_message)
                    
                    import traceback
                    traceback_text = traceback.format_exc()
                    print(traceback_text)
                    self.log(traceback_text)
                    time.sleep(5)  # Wait before retrying
                    
        except KeyboardInterrupt:
            print("\nMasterBot stopped by user.")
            self.log("MasterBot stopped by user.")
            notify('INFO', 'MasterBot stopped by user')
