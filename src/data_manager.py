import yfinance as yf
import pandas as pd
import os

class DataManager:
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

    def download_and_save(self, tickers, start="2023-01-01", end="2025-01-01"):
        """Downloads adjusted close prices and saves to CSV."""
        if isinstance(tickers, pd.Series):
            tickers = tickers.tolist()
        
        print(f"Downloading data for {len(tickers)} tickers...")
        data = yf.download(tickers, start=start, end=end)['Close']
        
        # Clean: Remove tickers with more than 10% missing values
        data = data.dropna(thresh=len(data) * 0.9, axis=1)
        data = data.ffill() # Fill minor gaps
        
        path = os.path.join(self.data_folder, 'sp500_prices.csv')
        data.to_csv(path)
        return data

    def load_local_data(self):
        path = os.path.join(self.data_folder, 'sp500_prices.csv')
        return pd.read_csv(path, index_col=0, parse_dates=True)