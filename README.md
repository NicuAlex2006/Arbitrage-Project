# Pairs Trading Arbitrage Bot

A robust, automated Python framework for discovering and backtesting statistical arbitrage (pairs trading) strategies using S&P 500 equity data. This project automates the entire pipeline from ticker discovery to generating trade logs and performance visualizations.

## 🚀 Key Features

* **Automated Ticker Discovery**: Dynamically scrapes the current list of S&P 500 companies from Wikipedia, handling various table formats and SSL configurations.
* **Intelligent Data Management**: Fetches historical close prices via Yahoo Finance and caches them locally in CSV format to minimize API calls.
* **Statistical Analysis Pipeline**: 
    * **Correlation Filtering**: Identifies highly correlated asset pairs (default threshold > 0.85) while automatically excluding dual-class shares of the same company (e.g., GOOG/GOOGL).
    * **Cointegration Testing**: Uses the Engle-Granger two-step method to find pairs with mean-reverting spreads.
    * **Z-Score Signaling**: Calculates rolling standard deviations to determine entry and exit points.
* **Strategy Backtester**: Simulates a "Long/Short Spread" strategy with configurable entry (Z > 2.0) and exit (Z < 0.5) thresholds.
* **Performance Reporting**: 
    * Generates dual-axis price charts with trade markers.
    * Produces cumulative return plots for each pair.
    * Exports detailed `trade_logs.csv` including entry/exit dates and individual trade returns.

## 🛠 Installation

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/yourusername/Arbitrage-Project.git](https://github.com/yourusername/Arbitrage-Project.git)
    cd Arbitrage-Project
    ```

2.  **Install Dependencies**:
    Ensure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The primary dependencies include `pandas`, `numpy`, `yfinance`, `statsmodels`, `matplotlib`, and `requests`.*

## 📂 Project Structure

```text
├── main.py              # Orchestrates the scraping, analysis, and backtesting
├── src/
│   ├── scraper.py       # Scrapes S&P 500 tickers from Wikipedia
│   ├── data_manager.py  # Handles CSV storage and Yahoo Finance downloads
│   ├── analytics.py     # Statistical tools: Cointegration, Correlation, Z-Score
│   └── backtester.py    # Logic for strategy execution and return calculation
├── data/                # Local storage for downloaded market data
├── plots/               # Generated strategy charts and trade logs
└── requirements.txt     # List of required Python packages