"""
web/app.py
Basic Flask web interface for TradeMasterX.
"""
import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'trading_history.db')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/trades')
def api_trades():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 100', conn)
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/portfolio')
def api_portfolio():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query('SELECT * FROM portfolio ORDER BY timestamp DESC LIMIT 1', conn)
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test')
def test():
    return '<h2>Flask is working!</h2>'

if __name__ == '__main__':
    app.run(debug=True)
