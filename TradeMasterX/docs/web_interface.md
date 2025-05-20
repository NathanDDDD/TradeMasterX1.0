# TradeMasterX Web Interface

The TradeMasterX web interface provides a dashboard for monitoring trades and portfolio status in real time.

## Features
- View recent trades with coin, action, amount, price, and timestamp
- View current portfolio value with multi-cryptocurrency support
- Chart visualization of portfolio value over time
- REST API endpoints for integration
- Error handling and feedback for data issues

## Usage
1. Start the web server using either method:
   ```powershell
   python main.py --web-interface
   ```
   or directly:
   ```powershell
   python web/app.py
   ```
2. Open your browser to [http://localhost:5000](http://localhost:5000)
3. The dashboard will automatically update with the latest data

## Troubleshooting
- **Blank page or loading issues**: Check the Flask server console for errors
- **Missing trade data**: Ensure the database has been migrated properly
- **Chart not displaying**: Check browser console for JavaScript errors

## API Endpoints
- `/api/trades` — Returns recent trades as JSON
- `/api/portfolio` — Returns current portfolio value as JSON

## Extending the Web Interface
- Add new API endpoints to `web/app.py` as needed.
- Add or modify HTML templates in `web/templates/`.
- Add static files (CSS, JS) to `web/static/`.

## Future Enhancements
- Add user authentication
- Implement real-time trade notifications using WebSockets
- Add controls to manually execute trades
- Create more detailed charts and analytics
- Add filtering and search for trade history

---
For more details, see the main README.md or the code in `web/app.py`.
