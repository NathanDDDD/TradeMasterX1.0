"""
bots/signal_bot.py
SignalBot: Generates a random signal for demonstration.
"""
import random
class SignalBot:
    def get_signal(self):
        """Return a random signal: BUY, SELL, or HOLD."""
        return random.choice(['BUY', 'SELL', 'HOLD'])
