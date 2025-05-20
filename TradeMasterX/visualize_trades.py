"""
visualize_trades.py
Visualizes the trading history and system performance.
"""
import os
import csv
import datetime
import matplotlib.pyplot as plt
import pandas as pd

def load_trade_history():
    """Load trade history from CSV file."""
    file_path = os.path.join('logs', 'trade_history.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: Trade history file not found at {file_path}")
        return None
    
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(file_path)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        print(f"Error loading trade history: {str(e)}")
        return None

def load_price_history():
    """Load price history from CSV file."""
    file_path = os.path.join('data', 'price_history.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: Price history file not found at {file_path}")
        return None
    
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(file_path)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        print(f"Error loading price history: {str(e)}")
        return None

def visualize_trades():
    """Visualize trades and price movements."""
    trade_df = load_trade_history()
    price_df = load_price_history()
    
    if trade_df is None or price_df is None:
        return
    
    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot 1: Price chart with buy/sell markers
    ax1.plot(price_df['timestamp'], price_df['price'], label='Price')
    
    # Add buy markers
    buy_trades = trade_df[trade_df['action'] == 'BUY']
    if not buy_trades.empty:
        # For each buy trade, find the closest price point
        for idx, trade in buy_trades.iterrows():
            # Find closest timestamp in price data
            closest_idx = (price_df['timestamp'] - trade['timestamp']).abs().idxmin()
            price_at_trade = price_df.iloc[closest_idx]['price']
            
            # Mark the buy point
            ax1.scatter(trade['timestamp'], price_at_trade, color='green', marker='^', s=100, label='Buy' if idx == buy_trades.index[0] else "")
    
    # Add sell markers
    sell_trades = trade_df[trade_df['action'] == 'SELL']
    if not sell_trades.empty:
        # For each sell trade, find the closest price point
        for idx, trade in sell_trades.iterrows():
            # Find closest timestamp in price data
            closest_idx = (price_df['timestamp'] - trade['timestamp']).abs().idxmin()
            price_at_trade = price_df.iloc[closest_idx]['price']
            
            # Mark the sell point
            ax1.scatter(trade['timestamp'], price_at_trade, color='red', marker='v', s=100, label='Sell' if idx == sell_trades.index[0] else "")
    
    ax1.set_title('Price Chart with Trade Signals')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Trade frequency histogram
    trade_counts = trade_df.groupby(['action']).size()
    ax2.bar(trade_counts.index, trade_counts.values, color=['green', 'red'])
    ax2.set_title('Trade Counts by Action')
    ax2.set_xlabel('Action')
    ax2.set_ylabel('Count')
    ax2.grid(True, axis='y')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('trading_visualization.png')
    plt.close()
    
    print(f"Visualization saved to trading_visualization.png")

if __name__ == "__main__":
    visualize_trades()
