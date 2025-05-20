"""
Database migration script to transition from old to new schema.
This handles the 'crypto' to multi-cryptocurrency conversion.
"""
import os
import sqlite3
import json
import sys

def migrate_database():
    """Migrate database from old schema to new schema."""
    db_path = 'trading_history.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("Database not found. No migration needed.")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        try:
            cursor.execute("SELECT * FROM coin_holdings LIMIT 1")
            print("Migration already completed. coin_holdings table exists.")
            conn.close()
            return True
        except sqlite3.OperationalError:
            # Table doesn't exist, proceed with migration
            pass
        
        print("Starting database migration...")
        
        # Create new tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            coin TEXT,
            amount REAL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolio (id)
        )
        ''')
        
        # Check if the old portfolio table has 'crypto' column
        has_crypto_column = False
        try:
            cursor.execute("SELECT crypto FROM portfolio LIMIT 1")
            has_crypto_column = True
        except:
            pass
        
        # If we have crypto data, migrate it
        if has_crypto_column:
            # Get all portfolio entries
            cursor.execute("SELECT id, crypto FROM portfolio")
            portfolio_entries = cursor.fetchall()
            
            # Migrate data - add 'bitcoin' as the default for old 'crypto' values
            for portfolio_id, crypto_amount in portfolio_entries:
                if crypto_amount is not None and crypto_amount > 0:
                    cursor.execute(
                        "INSERT INTO coin_holdings (portfolio_id, coin, amount) VALUES (?, ?, ?)",
                        (portfolio_id, 'bitcoin', crypto_amount)
                    )
            
            # Alter portfolio table: remove crypto column - SQLite doesn't support DROP COLUMN
            # So we need to recreate the table without that column
            
            # 1. Rename the old table
            cursor.execute("ALTER TABLE portfolio RENAME TO portfolio_old")
            
            # 2. Create new table without the crypto column
            cursor.execute('''
            CREATE TABLE portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cash REAL,
                value REAL
            )
            ''')
            
            # 3. Copy data from old table to new table
            cursor.execute("INSERT INTO portfolio (id, timestamp, cash, value) SELECT id, timestamp, cash, value FROM portfolio_old")
            
            # 4. Drop the old table
            cursor.execute("DROP TABLE portfolio_old")
          # Update trades table structure
        try:
            # Check if trades table exists and has portfolio_crypto column
            cursor.execute("PRAGMA table_info(trades)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'portfolio_crypto' in column_names and 'coin' not in column_names:
                print("Migrating trades table...")
                
                # Create a new trades table with updated schema
                cursor.execute('''
                CREATE TABLE trades_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    coin TEXT,
                    action TEXT,
                    price REAL,
                    amount REAL,
                    portfolio_cash REAL,
                    portfolio_value REAL
                )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                INSERT INTO trades_new (id, timestamp, coin, action, price, amount, portfolio_cash, portfolio_value)
                SELECT id, timestamp, 'bitcoin', action, price, amount, portfolio_cash, portfolio_value FROM trades
                ''')
                
                # Drop old table and rename new table
                cursor.execute("DROP TABLE trades")
                cursor.execute("ALTER TABLE trades_new RENAME TO trades")
                
                print("Trades table migration completed")
            else:
                print("Trades table already has correct schema or doesn't exist")
        except Exception as e:
            print(f"Error updating trades table: {str(e)}")
        
        conn.commit()
        
        print("Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration error: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if migrate_database():
        print("Migration successful. Database is now ready for multi-cryptocurrency support.")
        sys.exit(0)
    else:
        print("Migration failed. Please check the errors above.")
        sys.exit(1)
