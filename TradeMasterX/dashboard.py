"""
dashboard.py
Creates a simple dashboard to visualize trading performance.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from matplotlib.gridspec import GridSpec

def load_data():
    """Load trading data from various sources."""
    data = {
        'price_history': None,
        'trades': None,
        'portfolio': None
    }
    
    # Load price history
    price_file = os.path.join('data', 'price_history.csv')
    if os.path.exists(price_file):
        try:
            data['price_history'] = pd.read_csv(price_file)
            data['price_history']['timestamp'] = pd.to_datetime(data['price_history']['timestamp'])
        except Exception as e:
            print(f"Error loading price history: {str(e)}")
    
    # Load trade history from database
    db_file = os.path.join('trading_history.db')
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            data['trades'] = pd.read_sql('SELECT * FROM trades', conn)
            data['portfolio'] = pd.read_sql('SELECT * FROM portfolio', conn)
            
            # Convert timestamps
            data['trades']['timestamp'] = pd.to_datetime(data['trades']['timestamp'])
            data['portfolio']['timestamp'] = pd.to_datetime(data['portfolio']['timestamp'])
            
            conn.close()
        except Exception as e:
            print(f"Error loading from database: {str(e)}")
            
            # Fallback to CSV
            trade_file = os.path.join('logs', 'trade_history.csv')
            if os.path.exists(trade_file):
                try:
                    data['trades'] = pd.read_csv(trade_file)
                    data['trades']['timestamp'] = pd.to_datetime(data['trades']['timestamp'])
                except Exception as e:
                    print(f"Error loading trade history: {str(e)}")
    
    return data

def create_performance_dashboard(data):
    """Create a comprehensive performance dashboard."""
    if not data['price_history'] is not None and not data['trades'] is not None:
        print("Not enough data available to create dashboard.")
        return
    
    # Create figure layout
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 2, figure=fig)
    
    # Plot 1: Price chart with buy/sell markers
    ax1 = fig.add_subplot(gs[0, :])
    
    if data['price_history'] is not None:
        ax1.plot(data['price_history']['timestamp'], data['price_history']['price'], label='Price', color='blue', alpha=0.7)
        
        # Format x-axis for dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        
        # Add buy/sell markers if trade data exists
        if data['trades'] is not None:
            buy_trades = data['trades'][data['trades']['action'] == 'BUY']
            sell_trades = data['trades'][data['trades']['action'] == 'SELL']
            
            # For each trade, find closest price point
            for _, trade in buy_trades.iterrows():
                trade_time = trade['timestamp']
                price = trade['price']
                ax1.scatter(trade_time, price, color='green', marker='^', s=100, label='_Buy')
            
            for _, trade in sell_trades.iterrows():
                trade_time = trade['timestamp']
                price = trade['price']
                ax1.scatter(trade_time, price, color='red', marker='v', s=100, label='_Sell')
        
        # Add legend with unique entries
        handles, labels = ax1.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        ax1.legend(*zip(*unique))
    
    ax1.set_title('Price Movement with Trade Signals')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price ($)')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Portfolio value over time
    ax2 = fig.add_subplot(gs[1, 0])
    
    if data['portfolio'] is not None:
        ax2.plot(data['portfolio']['timestamp'], data['portfolio']['value'], color='purple', marker='o', markersize=3)
        ax2.set_title('Portfolio Value Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Value ($)')
        ax2.grid(True, alpha=0.3)
    
    # Plot 3: Asset allocation over time
    ax3 = fig.add_subplot(gs[1, 1])
    
    if data['portfolio'] is not None:
        # Create stacked area chart for cash and crypto
        ax3.fill_between(data['portfolio']['timestamp'], 0, data['portfolio']['cash'], label='Cash', alpha=0.7, color='green')
        
        crypto_value = data['portfolio']['crypto'] * data['portfolio']['value'] / (data['portfolio']['cash'] + data['portfolio']['crypto'])
        ax3.fill_between(data['portfolio']['timestamp'], data['portfolio']['cash'], data['portfolio']['value'], label='Crypto', alpha=0.7, color='orange')
        
        ax3.set_title('Asset Allocation')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Value ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Plot 4: Trade distribution by action
    ax4 = fig.add_subplot(gs[2, 0])
    
    if data['trades'] is not None:
        trade_counts = data['trades']['action'].value_counts()
        ax4.bar(trade_counts.index, trade_counts.values, color=['green', 'red'])
        ax4.set_title('Trade Distribution by Action')
        ax4.set_xlabel('Action')
        ax4.set_ylabel('Count')
        for i, v in enumerate(trade_counts):
            ax4.text(i, v + 0.1, str(v), ha='center')
    
    # Plot 5: Profit/Loss distribution
    ax5 = fig.add_subplot(gs[2, 1])
    
    if data['portfolio'] is not None:
        # Calculate daily returns
        data['portfolio']['daily_return'] = data['portfolio']['value'].pct_change() * 100
        data['portfolio'] = data['portfolio'].dropna()
        
        sns.histplot(data['portfolio']['daily_return'], bins=20, kde=True, ax=ax5)
        ax5.set_title('Distribution of Daily Returns (%)')
        ax5.set_xlabel('Daily Return (%)')
        ax5.set_ylabel('Frequency')
        ax5.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('trading_dashboard.png', dpi=300, bbox_inches='tight')
    print("Dashboard saved as trading_dashboard.png")

if __name__ == "__main__":
    data = load_data()
    create_performance_dashboard(data)
