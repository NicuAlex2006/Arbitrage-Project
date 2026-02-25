import pandas as pd
from src.scraper import scrape_tickers_SP_500
from src.data_manager import DataManager
from src.analytics import Analytics
from src.backtester import Backtester

def main():
    # 1. Scrape Tickers
    print("--- Phase 1: Scraping ---")
    tickers_df = scrape_tickers_SP_500()
    
    # 2. Download Data
    tickers = tickers_df['Ticker'].to_list()
    print(f"--- Phase 2: Downloading S&P 500 Data ---")
    dm = DataManager()
    prices = dm.download_and_save(tickers_df['Ticker'])
    
    # 3. Analytics: Find the best Pair
    print("--- Phase 3: Finding Cointegrated Pairs ---")
    # Filter by correlation first (Coarse Filter)
    high_corr_pairs = Analytics.get_top_correlated(prices, threshold=0.90)
    
    # Filter by Cointegration (The "Quant" Filter)
    cointegrated_results = Analytics.test_cointegration(prices, high_corr_pairs)
    
    if not cointegrated_results:
        print("No cointegrated pairs found in this sector. Try another!")
        return

    # Pick the top pair (lowest p-value)
    best_pair = cointegrated_results[0]
    stock_a, stock_b = best_pair['pair']
    print(f"Selected Pair: {stock_a} and {stock_b} (p-value: {best_pair['p_value']:.4f})")

    # 4. Generate Signals (Z-Score)
    print("--- Phase 4: Generating Signals ---")
    # We define the spread as Stock A / Stock B (Ratio) or A - B
    spread = prices[stock_a] / prices[stock_b]
    z_score = Analytics.calculate_zscore(spread, window=21)

    # 5. Backtest
    print("--- Phase 5: Backtesting Strategy ---")
    bt = Backtester(prices[stock_a], prices[stock_b], z_score)
    cumulative_returns = bt.run_strategy(entry_threshold=2.0, exit_threshold=0.5)

    # 6. Performance Summary
    final_return = cumulative_returns.iloc[-1]
    print(f"Final Strategy Return: {final_return:.2%}")

    # Plotting (Optional but recommended)
    cumulative_returns.plot(title=f"Pairs Trading: {stock_a} vs {stock_b}")

if __name__ == "__main__":
    main()