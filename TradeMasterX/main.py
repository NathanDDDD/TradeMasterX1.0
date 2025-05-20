"""
main.py
Entry point for TradeMasterX. Starts the system loop and loads the master bot.
"""

import os
import sys
import argparse
import logging
from core.master_bot import MasterBot
from ai_assistant import TradingAssistant

def ensure_directories():
    """Ensure required directories exist."""
    directories = ['logs', 'commands', 'data', 'web']
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory)
    
    # Create data directory for each supported coin
    # Default coins to create directories for
    default_coins = ['bitcoin', 'ethereum', 'litecoin', 'dogecoin', 'cardano']
    for coin in default_coins:
        coin_dir = os.path.join('data', coin)
        if not os.path.exists(coin_dir):
            print(f"Creating coin directory: {coin_dir}")
            os.makedirs(coin_dir)
            
    # Ensure control.txt exists
    control_path = os.path.join('commands', 'control.txt')
    if not os.path.exists(control_path):
        with open(control_path, 'w') as f:
            f.write('RUN\n')
            
def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='TradeMasterX - AI-powered crypto trading system')
    
    # Add arguments
    parser.add_argument('--assistant', action='store_true', help='Run the trading assistant instead of the trading system')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization of trading history')
    parser.add_argument('--train', action='store_true', help='Train the prediction model with available data')
    parser.add_argument('--dashboard', action='store_true', help='Generate a performance dashboard')
    parser.add_argument('--days', type=int, default=7, help='Number of days to simulate (default: 7)')
    parser.add_argument('--real-data', action='store_true', help='Use real-time data feeds instead of simulated data')
    parser.add_argument('--web-interface', action='store_true', help='Start the web interface dashboard')
    parser.add_argument('--coins', type=str, default='bitcoin,ethereum,litecoin', 
                        help='Comma-separated list of cryptocurrencies to trade (default: bitcoin,ethereum,litecoin)')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Set the logging level')
    parser.add_argument('--skip-migration', action='store_true', 
                        help='Skip database migration - use when you want to start with a fresh database')
    
    return parser.parse_args()

def main():
    """Main system loop. Loads MasterBot or assistant based on arguments."""
    args = parse_arguments()
    
    try:        # Ensure directories exist
        ensure_directories()
        
        # Migrate database if needed
        if not args.skip_migration:
            try:
                print("Checking database schema and migrating if needed...")
                from migrate_database import migrate_database
                migrate_database()
            except Exception as e:
                logging.error(f"Error during database migration: {str(e)}")
                print(f"Error during database migration: {str(e)}")
                print("Continuing anyway - this might cause issues if database is in old format.")
        
        if args.dashboard:
            print("Generating performance dashboard...")
            import dashboard
            dashboard.create_performance_dashboard(dashboard.load_data())
            return 0
            
        if args.visualize:
            print("Generating trade visualization...")
            import visualize_trades
            visualize_trades.visualize_trades()
            return 0
            
        if args.train:
            print("Training prediction model...")
            import train_prediction_model
            train_prediction_model.train_and_evaluate()
            return 0
            
        if args.assistant:
            print("Starting TradeMasterX Assistant...")
            assistant = TradingAssistant()
            assistant.run_cli()
            return 0
            
        if args.web_interface:
            print("Starting TradeMasterX Web Interface...")
            try:
                from web.app import app
                app.run(debug=True, host='0.0.0.0', port=5000)
                return 0
            except ImportError:
                print("Error: Web interface not available. Please check the web/app.py file.")
                return 1
            
        # Default: run the trading system
        print("Starting TradeMasterX Trading System...")
        print("Initializing MasterBot...")
        
        # Convert string arguments to appropriate types
        config = {
            'use_real_data': args.real_data,
            'coins': args.coins.split(','),
            'days': args.days,
            'log_level': args.log_level
        }
        
        master_bot = MasterBot(config)
        
        print("Running MasterBot (Press Ctrl+C to stop)...")
        master_bot.run()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
