"""
Test script to validate multi-cryptocurrency functionality.
This script tests the trade execution with multiple coins to ensure
the 'crypto' KeyError bug has been fixed.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trade_executor import TradeExecutor
from core.coin_selector import CoinSelector
import time

def test_trade_execution():
    """Test trade execution with multiple coins."""
    print("Starting multi-cryptocurrency trade test...")
    
    # Test coins
    coins = ['bitcoin', 'ethereum', 'litecoin', 'cardano', 'dogecoin']
    
    # Initialize trade executor with multiple coins
    trade_executor = TradeExecutor(coins=coins)
    
    # Initialize coin selector
    coin_selector = CoinSelector(coins=coins)
    
    print(f"Initial portfolio: {trade_executor.portfolio}")
    
    # Execute BUY trades for each coin
    for coin in coins:
        print(f"\nTesting BUY trade for {coin}...")
        try:
            result = trade_executor.execute_trade('BUY', coin)
            print(f"Trade result: {result}")
            print(f"Updated portfolio: {trade_executor.portfolio}")
            time.sleep(1)  # Wait a bit between trades
        except KeyError as e:
            print(f"ERROR: KeyError occurred when trading {coin}: {str(e)}")
            return False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {str(e)}")
            return False
    
    # Execute SELL trades for each coin
    for coin in coins:
        print(f"\nTesting SELL trade for {coin}...")
        try:
            result = trade_executor.execute_trade('SELL', coin)
            print(f"Trade result: {result}")
            print(f"Updated portfolio: {trade_executor.portfolio}")
            time.sleep(1)  # Wait a bit between trades
        except KeyError as e:
            print(f"ERROR: KeyError occurred when trading {coin}: {str(e)}")
            return False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred: {str(e)}")
            return False
    
    # Test coin selector
    print("\nTesting coin selector...")
    for i in range(10):
        selected_coin = coin_selector.select_coin()
        print(f"Round {i+1}: Selected {selected_coin}")
        time.sleep(0.2)
    
    print("\nAll tests passed successfully!")
    return True

if __name__ == "__main__":
    # Ensure the necessary directories exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Open a log file to capture output
    with open('multi_coin_test_log.txt', 'w') as log_file:
        # Redirect stdout to the log file
        original_stdout = sys.stdout
        sys.stdout = log_file
        
        try:
            # Run the test
            success = test_trade_execution()
            
            # Write final status
            print(f"\nTEST {'PASSED' if success else 'FAILED'}")
        finally:
            # Restore stdout
            sys.stdout = original_stdout
    
    # Print a short summary to console
    print("Test completed. See multi_coin_test_log.txt for details.")
    print(f"Test {'passed' if success else 'failed'}")
    
    sys.exit(0 if success else 1)
