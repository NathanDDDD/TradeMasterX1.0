# TradeMasterX Machine Learning Prediction Model

## Overview
TradeMasterX uses a machine learning model to predict price movements and generate trading signals. The model is based on a Random Forest classifier that analyzes 21 technical features derived from price data.

## Features Generated
The prediction model uses the following 21 features:

1. **Price Changes**:
   - `price_change`: Percentage change in price
   - `price_change_1d`: 1-day price change
   - `price_change_2d`: 2-day price change
   - `price_change_3d`: 3-day price change
   - `price_change_5d`: 5-day price change

2. **Moving Averages**:
   - `ma_5`: 5-period moving average
   - `ma_10`: 10-period moving average
   - `ma_15`: 15-period moving average
   - `ma_20`: 20-period moving average

3. **Moving Average Crossovers**:
   - `ma_5_10_ratio`: Ratio of 5-period to 10-period MA
   - `ma_10_20_ratio`: Ratio of 10-period to 20-period MA

4. **Volatility Measures**:
   - `volatility_5`: 5-period standard deviation
   - `volatility_10`: 10-period standard deviation

5. **Rate of Change**:
   - `roc_5`: 5-period rate of change
   - `roc_10`: 10-period rate of change

6. **Technical Indicators**:
   - `rsi`: Relative Strength Index
   - `macd`: Moving Average Convergence Divergence
   - `macd_signal`: MACD signal line
   - `macd_hist`: MACD histogram

7. **Price-MA Relationships**:
   - `price_ma_5_delta`: Percentage difference between price and 5-period MA
   - `price_ma_10_delta`: Percentage difference between price and 10-period MA

## Model Structure
- **Algorithm**: Random Forest Classifier
- **Training**: Uses historical price data with labeled BUY/SELL/HOLD targets
- **Preprocessing**: Features are standardized using StandardScaler
- **Storage**: Model and scaler are saved as a dictionary in pickle format

## Usage

### Prediction Process
1. The `PredictionBot` loads the trained model and scaler
2. For each prediction:
   - Latest price data is fetched
   - 21 features are generated
   - Features are scaled using the trained scaler
   - Model predicts probability of price increase
   - Signal is generated based on probability thresholds

### Retraining the Model
To retrain the model with the latest data:

```powershell
python train_prediction_model.py
```

This will:
1. Load the latest price history
2. Generate features
3. Create target labels
4. Train a new Random Forest model
5. Save the model and scaler for use by `PredictionBot`

## Troubleshooting

### Common Issues
- **NotFittedError**: Make sure both model and scaler are properly trained
- **Feature Mismatch**: Ensure the same 21 features are used in both training and prediction
- **Missing Data**: The model requires at least 26 data points to generate all features

### Performance Improvement
To improve model performance:
1. Add more price history data
2. Tune hyperparameters in `train_prediction_model.py`
3. Add new features or modify existing ones
4. Try different ML algorithms

## Future Enhancements
- Hyperparameter optimization
- Feature selection to identify most predictive variables
- Ensemble with other model types
- Deep learning approaches for sequence modeling
- Incorporation of sentiment data as features