import requests
import pandas as pd
import certifi
import io

def scrape_tickers_SP_500():
    # Prefer reading directly from the Wikipedia URL (may raise SSL errors on some setups)
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    # Try direct read_html from URL first
    try:
        df_list = pd.re
        df = df_list[0]
    except Exception:
        # Try fetching the page using requests with certifi's CA bundle (secure)
        try:
            headers = {'User-Agent': 'python-requests/2.0'}
            resp = requests.get(url, headers=headers, timeout=15, verify=certifi.where())
            resp.raise_for_status()
            # Pass bytes to pandas so lxml doesn't treat the string as a filename
            df_list = pd.read_html(io.BytesIO(resp.content))
            df = df_list[0]
        except Exception:
            # Last resort: use wikipedia package HTML (wrap in StringIO for pandas)
            import wikipedia as wp
            html = wp.page('List of S&P 500 companies').html()
            df_list = pd.read_html(io.StringIO(html))
            df = df_list[0]
    # Now select only company name and ticker columns (robust to column name variations)
    cols_low = [str(c).lower() for c in df.columns.astype(str)]
    company_candidates = ['security','company','company name','name','firm']
    ticker_candidates = ['symbol','ticker','ticker symbol']
    company_col = None
    ticker_col = None
    for orig, low in zip(df.columns, cols_low):
        if any(k in low for k in company_candidates) and company_col is None:
            company_col = orig
        if any(k in low for k in ticker_candidates) and ticker_col is None:
            ticker_col = orig
    # Fallback heuristics
    if company_col is None:
        for orig in df.columns:
            if df[orig].dtype == object:
                company_col = orig
                break
    if ticker_col is None:
        for orig in df.columns:
            non_null = df[orig].dropna().astype(str)
            if len(non_null) == 0:
                continue
            sample = non_null.iloc[0]
            if 1 <= len(sample) <= 6 and sample.upper() == sample:
                ticker_col = orig
                break
    if ticker_col is None:
        ticker_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    out = df[[company_col, ticker_col]].copy()
    out.columns = ['Company', 'Ticker']
    out['Company'] = out['Company'].astype(str).str.replace(r'\[.*?\]', '', regex=True).str.strip()
    out['Ticker'] = out['Ticker'].astype(str).str.strip()
    return out