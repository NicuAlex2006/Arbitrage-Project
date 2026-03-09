import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint

class Analytics:
    # Known dual-class shares in the S&P 500
    SAME_COMPANY_PAIRS = [
        {'GOOG', 'GOOGL'},
        {'FOX', 'FOXA'},
        {'NWS', 'NWSA'},
        {'UA', 'UAA'},
        {'BRK.A', 'BRK.B'},
        {'BF.A', 'BF.B'}
    ]

    @staticmethod
    def get_top_correlated(data, threshold=0.85, exclude_same_company=True):
        """Filters pairs that move together."""
        corr = data.corr()
        
        # Get upper triangle only to avoid duplicates
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        pairs = upper.unstack().dropna()
        
        # Filter by threshold to get high correlations
        high_corr = pairs[pairs > threshold].sort_values(ascending=False)

        # Filter out dual-class shares of the same company
        if exclude_same_company:
            def is_same_company(pair):
                stock_a, stock_b = pair
                for company_set in Analytics.SAME_COMPANY_PAIRS:
                    if stock_a in company_set and stock_b in company_set:
                        return True
                return False
            
            # Apply the filter mapping the boolean function over the MultiIndex
            high_corr = high_corr[~high_corr.index.map(is_same_company)]
            
        return high_corr

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