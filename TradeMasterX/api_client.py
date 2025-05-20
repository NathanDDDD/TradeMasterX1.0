#!/usr/bin/env python3
"""
api_client.py
A simple client for interacting with the TradeMasterX web API.
"""
import sys
import json
import time
import argparse
import requests
from datetime import datetime

class TradeMasterXClient:
    def __init__(self, base_url="http://localhost:5000"):
        """Initialize API client with base URL."""
        self.base_url = base_url
    
    def _get(self, endpoint):
        """Make a GET request to the API."""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
    
    def _post(self, endpoint, data):
        """Make a POST request to the API."""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
    
    def get_trade_history(self):
        """Get trade history from API."""
        return self._get("/api/trade-history")
    
    def get_portfolio(self):
        """Get current portfolio value."""
        return self._get("/api/portfolio")
    
    def get_signals(self):
        """Get recent bot signals."""
        return self._get("/api/signals")
    
    def get_system_status(self):
        """Get current system status (running or paused)."""
        return self._get("/api/control")
    
    def set_system_status(self, status):
        """Set system status (RUN or PAUSE)."""
        status = status.upper()
        if status not in ["RUN", "PAUSE"]:
            print("Invalid status. Use 'RUN' or 'PAUSE'.")
            return None
            
        return self._post("/api/control", {"command": status})

def display_trade_history(trades):
    """Display trade history in a formatted table."""
    if not trades:
        print("No trades found.")
        return
        
    print("\n=== RECENT TRADES ===")
    print(f"{'TIME':<20} {'TYPE':<6} {'CRYPTO':<10} {'PRICE':>10} {'AMOUNT':>10} {'VALUE':>12}")
    print("-" * 72)
    
    for trade in trades[:10]:  # Show most recent 10 trades
        timestamp = trade.get('timestamp', 'N/A')
        action = trade.get('action', 'N/A')
        crypto = trade.get('crypto', 'N/A')
        price = float(trade.get('price', 0))
        amount = float(trade.get('amount', 0))
        value = float(trade.get('value', 0))
        
        print(f"{timestamp:<20} {action:<6} {crypto:<10} ${price:>9.2f} {amount:>10.4f} ${value:>10.2f}")

def display_portfolio(portfolio):
    """Display portfolio information."""
    if not portfolio:
        print("Portfolio information not available.")
        return
    
    value = portfolio.get('portfolio_value', 0)
    timestamp = portfolio.get('timestamp', 'N/A')
    
    print("\n=== PORTFOLIO ===")
    print(f"Value: ${value:.2f}")
    print(f"Last Updated: {timestamp}")

def display_signals(signals):
    """Display recent bot signals."""
    if not signals:
        print("No signals found.")
        return
    
    print("\n=== RECENT SIGNALS ===")
    for signal in signals:
        print(f"- {signal}")

def display_system_status(status):
    """Display system status."""
    if not status or status.get('status') != 'success':
        print("System status not available.")
        return
    
    command = status.get('command', 'UNKNOWN')
    state = "RUNNING" if command == "RUN" else "PAUSED"
    
    print("\n=== SYSTEM STATUS ===")
    print(f"Status: {state}")

def monitor_loop(client, interval=5):
    """Monitor system continuously."""
    try:
        print("Starting continuous monitoring (Press Ctrl+C to stop)...")
        while True:
            clear_screen()
            print(f"=== TRADEMASTERX MONITOR === (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Get and display system status
            status = client.get_system_status()
            display_system_status(status)
            
            # Get and display portfolio
            portfolio = client.get_portfolio()
            display_portfolio(portfolio)
            
            # Get and display trade history
            trades = client.get_trade_history()
            display_trade_history(trades)
            
            # Get and display signals
            signals = client.get_signals()
            display_signals(signals)
            
            print("\nPress Ctrl+C to stop monitoring...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def clear_screen():
    """Clear terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(description="TradeMasterX API Client")
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--trades', action='store_true', help='Show recent trades')
    parser.add_argument('--portfolio', action='store_true', help='Show portfolio value')
    parser.add_argument('--signals', action='store_true', help='Show recent signals')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--set-status', choices=['run', 'pause'], help='Set system status')
    parser.add_argument('--monitor', action='store_true', help='Monitor system continuously')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring refresh interval (seconds)')
    
    args = parser.parse_args()
    client = TradeMasterXClient(base_url=args.url)
    
    # If no specific actions requested, show everything
    show_all = not (args.trades or args.portfolio or args.signals or 
                    args.status or args.set_status or args.monitor)
    
    try:
        if args.set_status:
            result = client.set_system_status(args.set_status)
            if result and result.get('status') == 'success':
                print(f"System status set to {args.set_status.upper()}")
            else:
                print("Failed to set system status")
        
        if args.monitor or show_all:
            monitor_loop(client, args.interval)
            return
            
        if args.status or show_all:
            status = client.get_system_status()
            display_system_status(status)
            
        if args.portfolio or show_all:
            portfolio = client.get_portfolio()
            display_portfolio(portfolio)
            
        if args.trades or show_all:
            trades = client.get_trade_history()
            display_trade_history(trades)
            
        if args.signals or show_all:
            signals = client.get_signals()
            display_signals(signals)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
