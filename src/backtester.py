import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, stock_a_prices, stock_b_prices, z_score):
        self.a = stock_a_prices
        self.b = stock_b_prices
        self.z = z_score

    def run_strategy(self, entry_threshold=2.0, exit_threshold=0.5):
        """
        Logic: 
        Short the spread if Z > 2 (Sell A, Buy B)
        Long the spread if Z < -2 (Buy A, Sell B)
        """
        df = pd.DataFrame({'a': self.a, 'b': self.b, 'z': self.z})
        
        # Initialize with NaN so forward-fill (ffill) works properly to hold positions
        df['position'] = np.nan
        
        # Simple signal logic
        df.loc[df['z'] > entry_threshold, 'position'] = -1    # Short spread
        df.loc[df['z'] < -entry_threshold, 'position'] = 1    # Long spread
        df.loc[abs(df['z']) < exit_threshold, 'position'] = 0 # Exit
        
        # Forward fill positions to stay in the trade, then fill remaining NaNs with 0 (flat)
        df['position'] = df['position'].ffill().fillna(0)
        
        # Calculate Returns (simplified)
        df['spread_return'] = (df['a'].pct_change() - df['b'].pct_change())
        df['strategy_return'] = df['position'].shift(1) * df['spread_return']
        df['cumulative_return'] = df['strategy_return'].cumsum()
        
        return df