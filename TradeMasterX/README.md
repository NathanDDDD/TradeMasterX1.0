# TradeMasterX

An AI-powered cryptocurrency trading system built from scratch.

## Overview

TradeMasterX is a modular trading system with five specialized bots:
- **IndicatorBot**: Analyzes price movements using technical indicators (moving averages)
- **PatternBot**: Identifies chart patterns (double top/bottom recognition)
- **SignalBot**: Interprets market signals
- **SentimentBot**: Analyzes social media and news sentiment about cryptocurrencies
- **PredictionBot**: Makes price predictions using machine learning

The system collects signals from all bots, makes trades based on consensus (when 3+ bots agree), and logs all activity for future analysis and learning. It supports both simulated data and real-time market data.

## Features

- **Modular Bot Architecture**: Each bot specializes in a different analysis approach
- **Consensus-Based Trading**: Trades only when 3+ bots agree (BUY/SELL)
- **Comprehensive Logging**: All signals and trades are logged in standardized formats
- **Terminal Assistant**: Control and monitor the system via a simple CLI
- **Trade Visualization**: Generate charts showing trade history and performance
- **Performance Dashboard**: Interactive dashboard for system performance
- **Sentiment Analysis**: Analyzes social media and news sentiment
- **Machine Learning Predictions**: Uses 21-feature ML model for price movement prediction
- **Real-Time Data Support**: Option to use real market data from APIs
- **Web Interface**: Web-based dashboard for monitoring and controlling the system
- **Portfolio Tracking**: Tracks portfolio value and trade history in a database
- **Multi-Cryptocurrency Support**: Trade multiple cryptocurrencies simultaneously
- **Notification System**: Get alerts on important system events and trades

## Getting Started

### Requirements

```
pip install -r requirements.txt
```

### Running the System

```
# Run the trading system with simulated data
python main.py

# Run with real-time market data
python main.py --real-data

# Specify which cryptocurrencies to trade (comma-separated, no spaces)
python main.py --coins bitcoin,ethereum,dogecoin

# Skip database migration (useful when starting fresh)
python main.py --skip-migration

# Run the assistant interface
python main.py --assistant

# Start the web interface dashboard
python main.py --web-interface

# Generate trade visualization
python main.py --visualize

# Generate performance dashboard
python main.py --dashboard

# Train the prediction model with latest data
python main.py --train

# Set the logging level
python main.py --log-level DEBUG
```

## Quickstart

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Run the trading system:**
   ```powershell
   python main.py
   ```
3. **Start the web dashboard:**
   ```powershell
   python main.py --web-interface
   # Then open http://localhost:5000 in your browser
   ```
4. **Run tests and demo:**
   ```powershell
   python test_multi_coin.py
   python demo.py
   ```

## System Control

The system can be paused/resumed by:
1. Using the assistant (`python main.py --assistant`)
2. Editing `commands/control.txt` (set to "PAUSE" or "RUN")
3. Using the web interface (`python main.py --web-interface`)
4. Making API calls to the control endpoint when web interface is running

## Advanced Features

### Web Interface

TradeMasterX includes a web-based dashboard for monitoring and controlling the system:

```
python main.py --web-interface
```

Then open http://localhost:5000 in your browser to access the dashboard.

### Database Migration

The system includes a database migration tool to ensure multi-cryptocurrency support:

```
python migrate_database.py
```

This is automatically run when you start the system, but can be bypassed with `--skip-migration`.

### Logging System

TradeMasterX uses a comprehensive logging system with standardized formats:

- `logs/trades.log`: All trades with timestamp, action, coin, amount, price, and portfolio value
- `logs/system.log`: System-level events, errors, and bot activity
- `logs/notifications.log`: Important notifications and alerts
- `logs/trade_history.csv`: CSV format of all trades for easy analysis

You can view these logs directly or through the web interface.

### API Client

We provide a command-line API client for interacting with the running system:

```
# Monitor the system continuously
python api_client.py --monitor

# Get current portfolio status
python api_client.py --portfolio

# Pause the system
python api_client.py --set-status pause

# Resume the system
python api_client.py --set-status run
```

### Error Handling

The system includes advanced error handling with logging, notifications, and recovery mechanisms. Configure error handling in `errors.json`.

### Demo Script

Try the complete demo script to explore all features:

```
python demo.py
```

## Directory Structure

```
TradeMasterX/
├── main.py
├── README.md
├── requirements.txt
├── core/
├── bots/
├── ai_assistant/
├── logs/
├── commands/
├── config/
├── data/
├── docs/
├── web/
│   ├── app.py
│   ├── static/
│   └── templates/
```

- All logs and data are written to the `logs/` and `data/` directories.
- The web interface is in `web/` and can be extended as needed.
- For more details, see the `docs/` directory.

## Project Structure

- **main.py**: Entry point
- **core/**: Core system components
  - **master_bot.py**: Coordinates bots and trading
  - **trade_executor.py**: Handles trade execution and logging
- **bots/**: Trading bot modules
  - **indicator_bot.py**: Technical indicators analysis
  - **pattern_bot.py**: Chart pattern recognition
  - **signal_bot.py**: Market signal analysis
  - **sentiment_bot.py**: Sentiment analysis
  - **prediction_bot.py**: ML-based predictions
- **ai_assistant/**: Interactive CLI assistant
- **logs/**: System logs and trade history
- **commands/**: Control files
- **data/**: Price data and other inputs

## Adding New Features

The system is designed to be modular and extensible. To add new functionality:
1. Enhance existing bots or add new bot types
2. Modify the consensus algorithm in `master_bot.py`
3. Enhance the assistant with new commands

## Future Development

- Implement real API connections to exchanges
- Advanced portfolio optimization and risk management
- Add more ML models and feature generation techniques
- Incorporate live news and social media streams for sentiment analysis
- Develop mobile app interface
- Add user authentication and multiple user accounts
- Implement backtesting on historical data

## Troubleshooting

### Common Issues

- **Database Errors**: If you see database-related errors, try running the migration script:
  ```
  python migrate_database.py
  ```

- **Web Interface Not Loading**: Make sure Flask is running and check browser console for errors
  ```
  python web/app.py
  ```

- **Machine Learning Issues**: If the prediction model has errors, retrain it:
  ```
  python train_prediction_model.py
  ```

For more help, check logs in the `logs/` directory or open an issue.
