import pandas as pd
import matplotlib.pyplot as plt
import os
from src.scraper import scrape_tickers_SP_500
from src.data_manager import DataManager
from src.analytics import Analytics
from src.backtester import Backtester

def main():
    # Ensure plots folder exists
    os.makedirs('plots', exist_ok=True)

    # 1. Scrape Tickers
    print("--- Phase 1: Scraping ---")
    tickers_df = scrape_tickers_SP_500()
    
    # 2. Download Data
    tickers = tickers_df['Ticker'].to_list()
    print(f"--- Phase 2: Loading or Downloading S&P 500 Data ---")
    dm = DataManager()
    prices = dm.get_data(tickers)
    
    # 3. Analytics: Find the best Pairs
    print("--- Phase 3: Finding Cointegrated Pairs ---")
    high_corr_pairs = Analytics.get_top_correlated(prices, threshold=0.85)
    cointegrated_results = Analytics.test_cointegration(prices, high_corr_pairs)
    
    if not cointegrated_results:
        print("No cointegrated pairs found. Try lowering the correlation threshold!")
        return

    # Grab up to the top 5 pairs
    top_5_pairs = cointegrated_results[:5]
    print(f"\nFound {len(cointegrated_results)} cointegrated pairs. Testing the top {len(top_5_pairs)}...\n")

    # Loop through the top 5 pairs
    for i, pair_data in enumerate(top_5_pairs, 1):
        stock_a, stock_b = pair_data['pair']
        p_val = pair_data['p_value']
        
        print(f"--- Pair {i}: {stock_a} vs {stock_b} (p-value: {p_val:.4f}) ---")

        # 4. Generate Signals (Z-Score)
        spread = prices[stock_a] / prices[stock_b]
        z_score = Analytics.calculate_zscore(spread, window=21)

        # 5. Backtest
        bt = Backtester(prices[stock_a], prices[stock_b], z_score)
        
        # Backtester now returns a full DataFrame
        df_backtest = bt.run_strategy(entry_threshold=2.0, exit_threshold=0.5)

        # 6. Performance Summary
        cumulative_returns = df_backtest['cumulative_return'].fillna(0)
        final_return = cumulative_returns.iloc[-1] if not cumulative_returns.empty else 0
        print(f"Final Strategy Return: {final_return:.2%}\n")

        # --- 7. Plotting and Saving ---
        # Create a figure with 2 subplots (Prices + Signals on top, Returns on bottom)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Subplot 1: Normalized Prices & Trading Signals
        # Normalizing prices to a base of 100 allows easy visual comparison
        norm_a = df_backtest['a'] / df_backtest['a'].iloc[0] * 100
        norm_b = df_backtest['b'] / df_backtest['b'].iloc[0] * 100
        
        ax1.plot(norm_a.index, norm_a, label=f'{stock_a} Price', alpha=0.7)
        ax1.plot(norm_b.index, norm_b, label=f'{stock_b} Price', alpha=0.7)
        
        # Extract signal trigger points
        position_changes = df_backtest['position'].diff()
        
        long_signals = df_backtest[position_changes == 1]   # Shifted to Long Spread (Buy A, Sell B)
        short_signals = df_backtest[position_changes == -1] # Shifted to Short Spread (Sell A, Buy B)
        exit_signals = df_backtest[(df_backtest['position'] == 0) & (position_changes != 0)] # Shifted to Flat
        
        # Plot markers on Stock A's line (as a reference point for the spread trades)
        ax1.scatter(long_signals.index, norm_a.loc[long_signals.index], marker='^', color='green', s=120, label='Long Spread', zorder=5)
        ax1.scatter(short_signals.index, norm_a.loc[short_signals.index], marker='v', color='red', s=120, label='Short Spread', zorder=5)
        ax1.scatter(exit_signals.index, norm_a.loc[exit_signals.index], marker='x', color='black', s=80, label='Exit Position', zorder=5)

        ax1.set_title(f"#{i} {stock_a} vs {stock_b} - Prices & Trade Signals")
        ax1.set_ylabel("Normalized Price")
        ax1.legend()
        ax1.grid(True)
        
        # Subplot 2: Cumulative Strategy Return
        ax2.plot(cumulative_returns.index, cumulative_returns, color='purple', label='Strategy Cumulative Return')
        ax2.set_title(f"Cumulative Strategy Return (Total: {final_return:.2%})")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Return")
        ax2.legend()
        ax2.grid(True)

        # Save Plot to folder
        plt.tight_layout()
        save_path = os.path.join("plots", f"pair_{i}_{stock_a}_{stock_b}.png")
        plt.savefig(save_path)
        plt.close() # Close to free memory and suppress popup
        
        print(f"Saved plot to {save_path}")

    print("\nAll backtests complete. Check the 'plots' folder for your graphs!")

if __name__ == "__main__":
    main()