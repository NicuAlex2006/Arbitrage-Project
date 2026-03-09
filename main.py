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

    # Master list to hold our trade logs across all pairs
    all_trades = []

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
        df_backtest = bt.run_strategy(entry_threshold=2.0, exit_threshold=0.5)

        # 6. Performance Summary
        cumulative_returns = df_backtest['cumulative_return'].fillna(0)
        final_return = cumulative_returns.iloc[-1] if not cumulative_returns.empty else 0
        print(f"Final Strategy Return: {final_return:.2%}")

        # --- 7. Extract Trade Logs ---
        current_trade = None
        # Use shift to easily compare the current day's position to the previous day
        df_backtest['prev_position'] = df_backtest['position'].shift(1).fillna(0)
        
        for date, row in df_backtest.iterrows():
            pos = row['position']
            prev_pos = row['prev_position']
            
            if pos != prev_pos:
                # Closing an active trade
                if prev_pos != 0 and current_trade is not None:
                    current_trade['Exit Date'] = date.strftime('%Y-%m-%d')
                    # Profit is the difference in cumulative return from entry to exit
                    current_trade['Trade Return'] = row['cumulative_return'] - current_trade['_entry_cum_ret']
                    all_trades.append(current_trade)
                    current_trade = None
                    
                # Opening a new trade
                if pos != 0:
                    current_trade = {
                        'Pair Rank': f"#{i}",
                        'Pair': f"{stock_a} vs {stock_b}",
                        'Type': 'Long Spread' if pos == 1 else 'Short Spread',
                        'Entry Date': date.strftime('%Y-%m-%d'),
                        '_entry_cum_ret': row['cumulative_return'] # Hidden field used for calculation
                    }
                    
        # If the backtest ends while a trade is still open, log it as open
        if current_trade is not None:
            current_trade['Exit Date'] = 'Open (End of Data)'
            current_trade['Trade Return'] = df_backtest['cumulative_return'].iloc[-1] - current_trade['_entry_cum_ret']
            all_trades.append(current_trade)

        # --- 8. Plotting and Saving ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        norm_a = df_backtest['a'] / df_backtest['a'].iloc[0] * 100
        norm_b = df_backtest['b'] / df_backtest['b'].iloc[0] * 100
        
        ax1.plot(norm_a.index, norm_a, label=f'{stock_a} Price', alpha=0.7)
        ax1.plot(norm_b.index, norm_b, label=f'{stock_b} Price', alpha=0.7)
        
        position_changes = df_backtest['position'].diff()
        
        long_signals = df_backtest[position_changes == 1]
        short_signals = df_backtest[position_changes == -1]
        exit_signals = df_backtest[(df_backtest['position'] == 0) & (position_changes != 0)]
        
        ax1.scatter(long_signals.index, norm_a.loc[long_signals.index], marker='^', color='green', s=120, label='Long Spread', zorder=5)
        ax1.scatter(short_signals.index, norm_a.loc[short_signals.index], marker='v', color='red', s=120, label='Short Spread', zorder=5)
        ax1.scatter(exit_signals.index, norm_a.loc[exit_signals.index], marker='x', color='black', s=80, label='Exit Position', zorder=5)

        ax1.set_title(f"#{i} {stock_a} vs {stock_b} - Prices & Trade Signals")
        ax1.set_ylabel("Normalized Price")
        ax1.legend()
        ax1.grid(True)
        
        ax2.plot(cumulative_returns.index, cumulative_returns, color='purple', label='Strategy Cumulative Return')
        ax2.set_title(f"Cumulative Strategy Return (Total: {final_return:.2%})")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Return")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        save_path = os.path.join("plots", f"pair_{i}_{stock_a}_{stock_b}.png")
        plt.savefig(save_path)
        plt.close()
        print(f"Saved plot to {save_path}\n")

    # --- 9. Save Trade Logs to CSV ---
    if all_trades:
        trades_df = pd.DataFrame(all_trades)
        # Drop the temporary calculation column
        trades_df = trades_df.drop(columns=['_entry_cum_ret'])
        
        # Format the return column as a human-readable percentage
        trades_df['Trade Return'] = trades_df['Trade Return'].apply(lambda x: f"{x:.2%}")
        
        csv_path = os.path.join("plots", "trade_logs.csv")
        trades_df.to_csv(csv_path, index=False)
        print(f"Successfully saved trade logs to '{csv_path}'!")
    else:
        print("No trades were executed during this period.")

if __name__ == "__main__":
    main()