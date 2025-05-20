"""
bots/prediction_bot.py
PredictionBot: Uses machine learning to predict price movements and generate signals.
"""
import os
import random
import numpy as np
import pandas as pd
import pickle
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class PredictionBot:
    def __init__(self):
        """Initialize the PredictionBot with ML model."""
        self.model_path = os.path.join('prediction_model.pkl')
        self.price_history_path = os.path.join('data', 'price_history.csv')
        self.model = None
        self.scaler = StandardScaler()
        
        # Load existing model or create a new one
        self.load_or_train_model()
        
    def load_or_train_model(self):
        """Load existing model or train a new one if none exists."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                # If the file is a dict (from train_prediction_model.py), load model and scaler
                if isinstance(model_data, dict) and 'model' in model_data and 'scaler' in model_data:
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    print("Loaded existing prediction model and scaler.")
                    return True
                else:
                    # Fallback for old format
                    self.model = model_data
                    print("Loaded existing prediction model (no scaler in file).")
                    return True
            except Exception as e:
                print(f"Could not load model: {str(e)}")
                
        print("Training new prediction model...")
        return self.train_model()
    
    def train_model(self):
        """Train a simple prediction model using historical price data."""
        try:
            # Load price data
            if not os.path.exists(self.price_history_path):
                print("No price history found. Cannot train model.")
                return False
                
            # Load the data
            df = pd.read_csv(self.price_history_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Need at least 20 data points
            if len(df) < 20:
                print("Not enough price history for training.")
                return False
                
            # Create features
            df = self.create_features(df)
            
            # Create target: 1 if price goes up in next period, 0 otherwise
            df['target'] = (df['price'].shift(-1) > df['price']).astype(int)
            
            # Remove rows with NaN
            df = df.dropna()
            
            # Split features and target
            features = ['price_change', 'ma_5', 'ma_10', 'std_5', 'rsi']
            X = df[features].values
            y = df['target'].values
            
            # Scale features
            X = self.scaler.fit_transform(X)
            
            # Train model
            model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X, y)
            
            # Save model
            self.model = model
            with open(self.model_path, 'wb') as f:
                pickle.dump(model, f)
                
            print("Model trained and saved.")
            return True
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False
    
    def create_features(self, df):
        """Create features for the model (match training script)."""
        df = df.copy()
        # Price changes
        df['price_change'] = df['price'].pct_change()
        df['price_change_1d'] = df['price'].pct_change(periods=1)
        df['price_change_2d'] = df['price'].pct_change(periods=2)
        df['price_change_3d'] = df['price'].pct_change(periods=3)
        df['price_change_5d'] = df['price'].pct_change(periods=5)
        # Moving averages
        df['ma_5'] = df['price'].rolling(window=5).mean()
        df['ma_10'] = df['price'].rolling(window=10).mean()
        df['ma_15'] = df['price'].rolling(window=15).mean()
        df['ma_20'] = df['price'].rolling(window=20).mean()
        # Moving average crossovers
        df['ma_5_10_ratio'] = df['ma_5'] / df['ma_10']
        df['ma_10_20_ratio'] = df['ma_10'] / df['ma_20']
        # Volatility
        df['volatility_5'] = df['price'].rolling(window=5).std()
        df['volatility_10'] = df['price'].rolling(window=10).std()
        # Rate of change
        df['roc_5'] = (df['price'] / df['price'].shift(5) - 1) * 100
        df['roc_10'] = (df['price'] / df['price'].shift(10) - 1) * 100
        # Simple RSI (Relative Strength Index)
        delta = df['price'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        avg_loss = avg_loss.replace(0, 0.001)
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        # MACD (Moving Average Convergence Divergence)
        ema_12 = df['price'].ewm(span=12).mean()
        ema_26 = df['price'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        # Price distance from moving averages (as percentage)
        df['price_ma_5_delta'] = (df['price'] / df['ma_5'] - 1) * 100
        df['price_ma_10_delta'] = (df['price'] / df['ma_10'] - 1) * 100
        return df
    
    def predict(self, features):
        """Make predictions using the trained model."""
        if self.model is None:
            return None
            
        # Scale the features
        features = self.scaler.transform([features])
        
        # Predict probability of price increase
        probabilities = self.model.predict_proba(features)[0]
        
        # Return the probability of price increase (class 1)
        if len(probabilities) >= 2:
            return probabilities[1]
        return 0.5  # Default to 50% if something is wrong
    
    def get_latest_data(self):
        """Get the latest price data for prediction (21 features)."""
        if not os.path.exists(self.price_history_path):
            return None
        try:
            df = pd.read_csv(self.price_history_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if len(df) < 26:  # Need enough data for all features
                return None
            df = self.create_features(df)
            latest_data = df.iloc[-1]
            features = [
                latest_data['price_change'],
                latest_data['price_change_1d'],
                latest_data['price_change_2d'],
                latest_data['price_change_3d'],
                latest_data['price_change_5d'],
                latest_data['ma_5'],
                latest_data['ma_10'],
                latest_data['ma_15'],
                latest_data['ma_20'],
                latest_data['ma_5_10_ratio'],
                latest_data['ma_10_20_ratio'],
                latest_data['volatility_5'],
                latest_data['volatility_10'],
                latest_data['roc_5'],
                latest_data['roc_10'],
                latest_data['rsi'],
                latest_data['macd'],
                latest_data['macd_signal'],
                latest_data['macd_hist'],
                latest_data['price_ma_5_delta'],
                latest_data['price_ma_10_delta']
            ]
            return features
        except Exception as e:
            print(f"Error getting latest data: {str(e)}")
            return None
    
    def get_signal(self):
        """Return a trading signal based on ML prediction."""
        # If we have no model or can't load data, fall back to random
        features = self.get_latest_data()
        if self.model is None or features is None:
            return random.choice(['BUY', 'SELL', 'HOLD'])
            
        # Get prediction probability
        up_probability = self.predict(features)
        
        # Convert probability to signal
        if up_probability > 0.65:
            return 'BUY'
        elif up_probability < 0.35:
            return 'SELL'
        else:
            return 'HOLD'
