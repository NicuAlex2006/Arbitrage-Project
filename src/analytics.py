import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint

class Analytics:
    @staticmethod
    def get_top_correlated(data, threshold=0.90):
        """Filters pairs that move together."""
        corr = data.corr()
        # Get upper triangle only to avoid duplicates
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        pairs = upper.unstack().dropna()
        return pairs[pairs > threshold].sort_values(ascending=False)

    @staticmethod
    def test_cointegration(data, pair_list):
        """Tests if the spread between pairs is stationary (mean-reverting)."""
        results = []
        for (stock_b, stock_a) in pair_list.index:
            score, p_value, _ = coint(data[stock_a], data[stock_b])
            if p_value < 0.05:
                results.append({'pair': (stock_a, stock_b), 'p_value': p_value})
        return results

    @staticmethod
    def calculate_zscore(series, window=21):
        """Calculates how many standard deviations the spread is from its mean."""
        mean = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        return (series - mean) / std