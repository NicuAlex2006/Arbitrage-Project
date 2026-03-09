import yfinance as yf
import pandas as pd
import os

class DataManager:
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        self.file_path = os.path.join(self.data_folder, 'sp500_prices.csv')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

    def get_data(self, tickers, start="2023-01-01", end="2026-01-01"):
        """Loads local data if it exists, otherwise downloads it."""
        if os.path.exists(self.file_path):
            print("Local data found. Loading from CSV instead of downloading...")
            return self.load_local_data()
        else:
            print("Local data not found. Downloading from Yahoo Finance...")
            return self.download_and_save(tickers, start, end)

    def download_and_save(self, tickers, start="2023-01-01", end="2026-01-01"):
        """Downloads close prices and saves to CSV."""
        if isinstance(tickers, pd.Series):
            tickers = tickers.tolist()
        
        print(f"Downloading data for {len(tickers)} tickers...")
        data = yf.download(tickers, start=start, end=end)['Close']
        
        # Clean: Remove tickers with more than 10% missing values
        data = data.dropna(thresh=len(data) * 0.9, axis=1)
        data = data.ffill() # Fill minor gaps
        
        data.to_csv(self.file_path)
        return data

    def load_local_data(self):
        """Loads data from the local CSV file."""
        return pd.read_csv(self.file_path, index_col=0, parse_dates=True)