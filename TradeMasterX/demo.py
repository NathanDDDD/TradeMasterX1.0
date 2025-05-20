#!/usr/bin/env python3
"""
demo.py
Demonstration script for TradeMasterX system features.
"""
import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

def clear_screen():
    """Clear terminal screen based on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print demo header."""
    clear_screen()
    print("=" * 80)
    print("                        TRADEMASTERX DEMONSTRATION                       ")
    print("=" * 80)
    print("\nThis script will demonstrate the key features of TradeMasterX\n")

def run_command(command, wait_time=3):
    """Run a command and wait for specified time."""
    print(f"\n> Running: {command}")
    try:
        process = subprocess.Popen(command, shell=True)
        time.sleep(wait_time)  # Give process time to start and display output
        return process
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def kill_process(process):
    """Kill process if it's still running."""
    if process and process.poll() is None:
        try:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
        except Exception as e:
            print(f"Error killing process: {e}")

def demo_trading_system():
    """Demonstrate the basic trading system."""
    print("\n\n=== BASIC TRADING SYSTEM DEMO ===")
    print("Running TradeMasterX for 15 seconds with simulated data...")
    process = run_command("python main.py", wait_time=15)
    kill_process(process)
    input("\nPress Enter to continue...")

def demo_real_data():
    """Demonstrate trading with real data."""
    print("\n\n=== REAL-TIME DATA DEMO ===")
    print("Running TradeMasterX with real-time market data for 15 seconds...")
    print("(Note: This requires internet connection)")
    process = run_command("python main.py --real-data --coins bitcoin,ethereum", wait_time=15)
    kill_process(process)
    input("\nPress Enter to continue...")

def demo_visualization():
    """Demonstrate trade visualization."""
    print("\n\n=== TRADE VISUALIZATION DEMO ===")
    print("Generating trade visualization...")
    run_command("python main.py --visualize", wait_time=5)
    input("\nPress Enter to continue...")

def demo_dashboard():
    """Demonstrate performance dashboard."""
    print("\n\n=== PERFORMANCE DASHBOARD DEMO ===")
    print("Generating performance dashboard...")
    run_command("python main.py --dashboard", wait_time=5)
    input("\nPress Enter to continue...")

def demo_web_interface():
    """Demonstrate web interface."""
    print("\n\n=== WEB INTERFACE DEMO ===")
    print("Starting web interface. Open http://localhost:5000 in your browser.")
    print("Press Ctrl+C when finished viewing...")
    
    try:
        process = run_command("python main.py --web-interface", wait_time=1)
        print("\nWeb interface started! Press Enter when you've finished exploring...")
        input()
        kill_process(process)
    except KeyboardInterrupt:
        print("\nWeb interface demo interrupted.")
    
    input("\nPress Enter to continue...")

def demo_multiple_coins():
    """Demonstrate trading with multiple coins."""
    print("\n\n=== MULTI-CRYPTOCURRENCY TRADING DEMO ===")
    print("Running TradeMasterX with multiple cryptocurrencies...")
    process = run_command("python main.py --coins bitcoin,ethereum,litecoin,ripple,dogecoin", wait_time=15)
    kill_process(process)
    input("\nPress Enter to continue...")

def demo_train_model():
    """Demonstrate model training."""
    print("\n\n=== PREDICTION MODEL TRAINING DEMO ===")
    print("Training the prediction model...")
    run_command("python main.py --train", wait_time=10)
    input("\nPress Enter to continue...")

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='TradeMasterX Demo')
    parser.add_argument('--all', action='store_true', help='Run all demos')
    parser.add_argument('--trading', action='store_true', help='Demo basic trading system')
    parser.add_argument('--real-data', action='store_true', help='Demo real-time data')
    parser.add_argument('--visualization', action='store_true', help='Demo trade visualization')
    parser.add_argument('--dashboard', action='store_true', help='Demo performance dashboard')
    parser.add_argument('--web', action='store_true', help='Demo web interface')
    parser.add_argument('--multi-coins', action='store_true', help='Demo multi-cryptocurrency trading')
    parser.add_argument('--training', action='store_true', help='Demo model training')
    
    args = parser.parse_args()
    all_demos = not any(vars(args).values()) or args.all
    
    print_header()
    
    try:
        if all_demos or args.trading:
            demo_trading_system()
        
        if all_demos or args.visualization:
            demo_visualization()
        
        if all_demos or args.dashboard:
            demo_dashboard()
            
        if all_demos or args.multi_coins:
            demo_multiple_coins()
            
        if all_demos or args.training:
            demo_train_model()
            
        if all_demos or args.real_data:
            demo_real_data()
            
        if all_demos or args.web:
            demo_web_interface()
            
        print("\n\n=== DEMO COMPLETE ===")
        print("Thank you for exploring TradeMasterX!")
        print("For more information, please refer to the README.md file.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Exiting...")
    
    print("\nExiting demo...")

if __name__ == "__main__":
    main()
