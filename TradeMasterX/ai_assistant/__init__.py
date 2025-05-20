"""
ai_assistant/__init__.py
Terminal-based assistant for TradeMasterX.
Reads logs, shows system status, and allows control of the trading system.
"""
import os
import time
import datetime
import csv
from collections import Counter

class TradingAssistant:
    """Terminal-based assistant for monitoring and controlling TradeMasterX."""
    
    def __init__(self):
        self.logs_dir = 'logs'
        self.system_log = os.path.join(self.logs_dir, 'system.log')
        self.trades_log = os.path.join(self.logs_dir, 'trades.log')
        self.trades_csv = os.path.join(self.logs_dir, 'trade_history.csv')
        self.control_file = os.path.join('commands', 'control.txt')
    
    def get_system_status(self):
        """Read the control file and return system status."""
        if not os.path.exists(self.control_file):
            return "UNKNOWN"
        
        with open(self.control_file, 'r') as f:
            status = f.read().strip().upper()
        
        return status
    
    def set_system_status(self, status):
        """Set the system status by writing to the control file."""
        if status not in ['RUN', 'PAUSE']:
            raise ValueError("Status must be 'RUN' or 'PAUSE'")
        
        with open(self.control_file, 'w') as f:
            f.write(f"{status}\n")
        
        return f"System status set to: {status}"
    
    def get_recent_logs(self, num_lines=10):
        """Get the most recent log entries."""
        if not os.path.exists(self.system_log):
            return ["No logs found."]
        
        try:
            with open(self.system_log, 'r') as f:
                lines = f.readlines()
            
            return lines[-num_lines:]
        except Exception as e:
            return [f"Error reading logs: {str(e)}"]
    
    def get_recent_trades(self, num_trades=5):
        """Get the most recent trades."""
        if not os.path.exists(self.trades_log):
            return ["No trades found."]
        
        try:
            with open(self.trades_log, 'r') as f:
                lines = f.readlines()
            
            return lines[-num_trades:]
        except Exception as e:
            return [f"Error reading trades: {str(e)}"]
    
    def get_trade_summary(self):
        """Get a summary of all trades."""
        if not os.path.exists(self.trades_csv):
            return "No trade history found."
        
        try:
            trades = []
            with open(self.trades_csv, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    trades.append(row[1])  # Action column
            
            counter = Counter(trades)
            
            summary = "Trade Summary:\n"
            summary += f"Total Trades: {len(trades)}\n"
            for action, count in counter.items():
                summary += f"  {action}: {count}\n"
            
            return summary
        except Exception as e:
            return f"Error generating trade summary: {str(e)}"
    
    def run_cli(self):
        """Run the command-line interface for the assistant."""
        print("TradeMasterX Assistant")
        print("=====================")
        
        while True:
            print("\nAvailable commands:")
            print("1. Show system status")
            print("2. Toggle system (RUN/PAUSE)")
            print("3. Show recent logs")
            print("4. Show recent trades")
            print("5. Show trade summary")
            print("6. Exit")
            
            choice = input("\nEnter command (1-6): ")
            
            if choice == '1':
                status = self.get_system_status()
                print(f"System Status: {status}")
            
            elif choice == '2':
                current = self.get_system_status()
                new_status = "PAUSE" if current == "RUN" else "RUN"
                result = self.set_system_status(new_status)
                print(result)
            
            elif choice == '3':
                logs = self.get_recent_logs()
                print("\nRecent Logs:")
                for log in logs:
                    print(log.strip())
            
            elif choice == '4':
                trades = self.get_recent_trades()
                print("\nRecent Trades:")
                for trade in trades:
                    print(trade.strip())
            
            elif choice == '5':
                summary = self.get_trade_summary()
                print(f"\n{summary}")
            
            elif choice == '6':
                print("Exiting assistant...")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
            
            time.sleep(1)

if __name__ == "__main__":
    # Run the assistant if this file is executed directly
    assistant = TradingAssistant()
    assistant.run_cli()
