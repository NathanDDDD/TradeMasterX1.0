"""
train_prediction_model.py
Script to train an advanced ML model for price prediction.
"""
import os
import pandas as pd
import numpy as np
import pickle
import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Import notification system if available
try:
    from notification_system import notify
except ImportError:
    # Fallback if notification system is not available
    def notify(level, message, force=False):
        print(f"[{level}] {message}")

def load_price_history():
    """Load price history from CSV file."""
    price_file = os.path.join('data', 'price_history.csv')
    
    if not os.path.exists(price_file):
        print(f"Error: Price history file not found at {price_file}")
        return None
    
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(price_file)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        print(f"Error loading price history: {str(e)}")
        return None

def load_trade_history():
    """Load trade history from CSV file."""
    trade_file = os.path.join('logs', 'trade_history.csv')
    
    if not os.path.exists(trade_file):
        print(f"Error: Trade history file not found at {trade_file}")
        return None
    
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(trade_file)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except Exception as e:
        print(f"Error loading trade history: {str(e)}")
        return None

def create_features(df):
    """Create features for the prediction model."""
    # Make a copy to avoid modifying the original
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
    
    # Avoid division by zero
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

def create_target(df, forecast_periods=1, threshold_pct=0.5):
    """Create target variable for price movement prediction."""
    # Calculate future price change
    df['future_price_change'] = df['price'].shift(-forecast_periods) / df['price'] - 1
    
    # Create categorical target based on threshold
    df['target'] = 0  # Default to HOLD
    df.loc[df['future_price_change'] > threshold_pct/100, 'target'] = 1  # BUY
    df.loc[df['future_price_change'] < -threshold_pct/100, 'target'] = -1  # SELL
    
    return df

def train_and_evaluate():
    """Train an ML model and evaluate its performance."""
    # Load price history
    df = load_price_history()
    if df is None:
        notify('ERROR', "Failed to load price history for training.")
        return False
    
    # Need at least 30 data points
    if len(df) < 30:
        notify('WARNING', f"Not enough price history for training. Have {len(df)} points, need at least 30.")
        return False
    
    print(f"Loaded {len(df)} price data points.")
    
    # Create features
    df = create_features(df)
    
    # Create target (predict price movement 1 day in advance)
    df = create_target(df, forecast_periods=1, threshold_pct=0.5)
    
    # Drop missing values
    df = df.dropna()
    
    # Feature columns
    feature_columns = [
        'price_change', 'price_change_1d', 'price_change_2d', 'price_change_3d',
        'price_change_5d', 'ma_5', 'ma_10', 'ma_15', 'ma_20', 'ma_5_10_ratio',
        'ma_10_20_ratio', 'volatility_5', 'volatility_10', 'roc_5', 'roc_10',
        'rsi', 'macd', 'macd_signal', 'macd_hist',
        'price_ma_5_delta', 'price_ma_10_delta'
    ]
    
    # Split into features and target
    X = df[feature_columns].values
    y = df['target'].values
    
    # Handle class imbalance if needed
    class_counts = np.bincount(y + 1)  # Add 1 to handle -1 class
    print(f"Class distribution: SELL: {class_counts[0]}, HOLD: {class_counts[1]}, BUY: {class_counts[2]}")
    
    # Split into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train model with hyperparameter tuning
    print("Training model with hyperparameter tuning...")
    
    # Define parameter grid for GridSearchCV
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.05, 0.1, 0.2]
    }
    
    # Create and train model
    base_model = GradientBoostingClassifier(random_state=42)
    grid_search = GridSearchCV(base_model, param_grid, cv=3, scoring='f1_weighted')
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_model = grid_search.best_estimator_
    print(f"Best parameters: {grid_search.best_params_}")
    
    # Evaluate on test set
    y_pred = best_model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    # Print metrics
    print(f"Model Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Plot confusion matrix
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['SELL', 'HOLD', 'BUY'],
                yticklabels=['SELL', 'HOLD', 'BUY'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig('prediction_model_confusion_matrix.png')
    
    # Feature importance
    feature_importance = best_model.feature_importances_
    sorted_idx = np.argsort(feature_importance)
    plt.figure(figsize=(10, 12))
    plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx])
    plt.yticks(range(len(sorted_idx)), [feature_columns[i] for i in sorted_idx])
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig('prediction_model_feature_importance.png')
    
    # Save model and scaler
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'feature_columns': feature_columns,
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        },
        'training_date': datetime.datetime.now().isoformat()
    }
    
    with open('prediction_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Model saved to prediction_model.pkl")
    notify('INFO', f"Prediction model trained with F1 score: {f1:.4f}")
    
    return True

if __name__ == "__main__":
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Train and evaluate the model
    train_and_evaluate()
