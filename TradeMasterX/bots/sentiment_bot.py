"""
bots/sentiment_bot.py
SentimentBot: Analyzes news and social media sentiment about cryptocurrencies
to generate trading signals.
"""
import os
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class SentimentBot:
    def __init__(self):
        self.logger = logging.getLogger('SentimentBot')
        self.logger.info("Initializing SentimentBot")
        self.sentiment_cache = {}
        self.cache_time = {}
        self.cache_duration = 3600  # 1 hour cache duration
        
        # Set up data directory
        self.data_dir = os.path.join('data', 'sentiment')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Load example data for offline simulation
        self.sample_data_file = os.path.join(self.data_dir, 'sample_sentiment_data.json')
        self._ensure_sample_data()
    
    def _ensure_sample_data(self):
        """Create sample sentiment data if it doesn't exist."""
        if not os.path.exists(self.sample_data_file):
            self.logger.info("Creating sample sentiment data")
            # Generate some realistic looking sample data
            sample_data = {
                'bitcoin': self._generate_sample_sentiment_data(bias=0.6),  # Slightly positive bias
                'ethereum': self._generate_sample_sentiment_data(bias=0.55),  # Slightly positive bias
                'litecoin': self._generate_sample_sentiment_data(bias=0.5),  # Neutral
                'ripple': self._generate_sample_sentiment_data(bias=0.45),   # Slightly negative bias
                'dogecoin': self._generate_sample_sentiment_data(volatility=0.8)  # More volatile sentiment
            }
            with open(self.sample_data_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
    
    def _generate_sample_sentiment_data(self, days=30, bias=0.5, volatility=0.5):
        """Generate realistic sample sentiment data with the given bias and volatility."""
        date_range = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        
        # Generate sentiment scores with some trend and volatility
        base_scores = np.cumsum(np.random.normal(0, volatility, days)) / 10
        sentiment_scores = base_scores + bias
        
        # Clip values to be between 0 and 1
        sentiment_scores = np.clip(sentiment_scores, 0, 1)
        
        # Create sources with varying reliability
        sources = ['twitter', 'reddit', 'news', 'blogs', 'forums']
        
        data = []
        for i, date in enumerate(date_range):
            for source in sources:
                # Add some variation per source
                source_bias = np.random.normal(0, 0.1)
                score = min(max(sentiment_scores[i] + source_bias, 0), 1)
                
                data.append({
                    'date': date,
                    'source': source,
                    'sentiment_score': float(score),
                    'volume': int(np.random.randint(100, 10000)),
                    'keywords': self._get_sample_keywords(score)
                })
        
        return data
    
    def _get_sample_keywords(self, score):
        """Generate sample keywords based on sentiment score."""
        positive_words = ['bullish', 'surge', 'gains', 'rise', 'breakthrough', 'adoption', 'potential']
        negative_words = ['bearish', 'drop', 'crash', 'regulation', 'ban', 'risk', 'bubble']
        neutral_words = ['price', 'market', 'crypto', 'blockchain', 'trading', 'transaction']
        
        # Select words based on sentiment score
        keywords = []
        keywords.extend(np.random.choice(neutral_words, size=3, replace=False))
        
        if score > 0.6:  # Positive sentiment
            keywords.extend(np.random.choice(positive_words, size=2, replace=False))
        elif score < 0.4:  # Negative sentiment
            keywords.extend(np.random.choice(negative_words, size=2, replace=False))
        else:  # Neutral
            keywords.append(np.random.choice(positive_words, size=1)[0])
            keywords.append(np.random.choice(negative_words, size=1)[0])
            
        return keywords
        
    def get_sentiment_data(self, coin='bitcoin', days=7):
        """Get sentiment data for a specific coin over the last few days."""
        cache_key = f"{coin}_{days}"
        
        # Check cache first
        now = time.time()
        if cache_key in self.sentiment_cache and now - self.cache_time.get(cache_key, 0) < self.cache_duration:
            self.logger.debug(f"Using cached sentiment data for {coin}")
            return self.sentiment_cache[cache_key]
        
        try:
            # In a real implementation, we would call an API here
            # For now, we'll use our sample data
            with open(self.sample_data_file, 'r') as f:
                all_data = json.load(f)
                
            if coin not in all_data:
                self.logger.warning(f"No sentiment data available for {coin}")
                return []
                
            # Filter by date
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            filtered_data = [item for item in all_data[coin] if item['date'] >= cutoff_date]
            
            # Cache the result
            self.sentiment_cache[cache_key] = filtered_data
            self.cache_time[cache_key] = now
            
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error fetching sentiment data: {e}")
            return []
    
    def analyze_sentiment(self, coin='bitcoin'):
        """Analyze sentiment data and determine a trading signal."""
        sentiment_data = self.get_sentiment_data(coin)
        
        if not sentiment_data:
            self.logger.warning(f"No sentiment data to analyze for {coin}")
            return 'HOLD'  # Default to HOLD if no data
            
        # Calculate sentiment metrics
        df = pd.DataFrame(sentiment_data)
        avg_sentiment = df['sentiment_score'].mean()
        recent_sentiment = df[df['date'] >= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')]['sentiment_score'].mean()
        
        # Calculate sentiment change
        sentiment_change = recent_sentiment - avg_sentiment
        
        # Calculate weighted sentiment score
        volume_weighted_sentiment = (df['sentiment_score'] * df['volume']).sum() / df['volume'].sum()
        
        # Determine signal based on sentiment
        signal = 'HOLD'
        
        # Strong positive sentiment
        if volume_weighted_sentiment > 0.7 or (volume_weighted_sentiment > 0.6 and sentiment_change > 0.05):
            signal = 'BUY'
        # Strong negative sentiment
        elif volume_weighted_sentiment < 0.3 or (volume_weighted_sentiment < 0.4 and sentiment_change < -0.05):
            signal = 'SELL'
            
        self.logger.info(f"Sentiment analysis for {coin}: {signal} (score: {volume_weighted_sentiment:.2f}, change: {sentiment_change:.2f})")
        return signal
    
    def get_signal(self, coin='bitcoin'):
        """Return a trading signal based on sentiment analysis."""
        return self.analyze_sentiment(coin)
