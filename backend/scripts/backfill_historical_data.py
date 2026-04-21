import time
import sqlite3
import requests
import pandas as pd
import akshare as ak
import yfinance as yf
from requests.adapters import HTTPAdapter, Retry
from io import StringIO

# --- Configuration ---
DB_PATH = "chartstrike.db"
CN_FALLBACK_URL = "https://raw.githubusercontent.com/huobiapi/StockList/main/a_stock_list.csv"
REQUEST_DELAY = 5.0  # seconds between symbols (increased)
MAX_RETRIES = 3
BACKOFF_FACTOR = 2.0  # multiplier for delay between retries

# --- Setup a requests session with retries ---
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- Helper Functions ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def setup_database():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol_date ON stock_prices (symbol, date);")
    conn.commit()
    conn.close()
    print("Database table 'stock_prices' is ready.")

def fetch_hk_universe():
    print("Fetching HK Stock Connect universe...")
    try:
        df = ak.stock_hk_ggt_components_em()
        hk_symbols = [f"{code}.HK" for code in df['代码'].tolist()]
        print(f"Fetched {len(hk_symbols)} liquid HK symbols (Stock Connect).")
        return hk_symbols
    except Exception as e:
        print(f"Error fetching HK list: {e}")
        return []

def fetch_cn_universe():
    print("Fetching full CN A-share universe...")
    for attempt in range(3):
        try:
            df = ak.stock_info_a_code_name()
            cn_symbols = [f"{code}.{exchange}" for code, exchange in zip(df['code'], df['exchange'])]
            print(f"Fetched {len(cn_symbols)} CN symbols via akshare.")
            return cn_symbols
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    print("  akshare failed. Falling back to community-maintained CSV...")
    try:
        response = session.get(CN_FALLBACK_URL, timeout=30)
        df = pd.read_csv(StringIO(response.text), dtype=str)
        if 'symbol' in df.columns and 'exchange' in df.columns:
            cn_symbols = [f"{row['symbol']}.{row['exchange']}" for _, row in df.iterrows()]
            print(f"Fetched {len(cn_symbols)} CN symbols via fallback CSV.")
            return cn_symbols
        else:
            print("  Fallback CSV format unexpected.")
            return []
    except Exception as e:
        print(f"  Fallback also failed: {e}")
        return []

def symbol_already_processed(symbol):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM stock_prices WHERE symbol = ? LIMIT 1", (symbol,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def backfill_symbol_history(symbol, start_date="20200101"):
    """
    Fetch historical data with retries and fallback to yfinance if akshare fails.
    """
    if symbol_already_processed(symbol):
        print(f"  {symbol} already in DB. Skipping.")
        return 0

    # Try akshare with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            print(f"  Processing {symbol} (akshare)...", end="", flush=True)
            if symbol.endswith(".HK"):
                akshare_symbol = symbol.replace(".HK", "")
                df = ak.stock_hk_hist(symbol=akshare_symbol, period="daily",
                                     start_date=start_date, adjust="qfq")
            else:
                akshare_symbol = symbol.split('.')[0]
                df = ak.stock_zh_a_hist(symbol=akshare_symbol, period="daily",
                                        start_date=start_date, adjust="qfq")
            if not df.empty:
                # Success with akshare
                return _insert_data(symbol, df)
            else:
                print(" no data.")
                return 0
        except Exception as e:
            wait = BACKOFF_FACTOR ** attempt
            print(f" attempt {attempt+1} failed ({e}), waiting {wait:.1f}s...", end="", flush=True)
            time.sleep(wait)
    
    # If all akshare attempts fail, try yfinance as fallback (for HK only)
    if symbol.endswith(".HK"):
        print(f"  Falling back to yfinance for {symbol}...", end="", flush=True)
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, interval="1d")
            if df.empty:
                print(" no data.")
                return 0
            df = df.reset_index()
            df['Date'] = df['Date'].dt.date
            df = df.rename(columns={
                'Date': 'date', 'Open': 'open', 'High': 'high',
                'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            })
            df['symbol'] = symbol
            df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
            return _insert_data(symbol, df)
        except Exception as e:
            print(f" yfinance fallback failed: {e}")
            return 0
    else:
        print(f"  All attempts failed for {symbol}.")
        return 0

def _insert_data(symbol, df):
    conn = get_db_connection()
    df.to_sql('stock_prices', conn, if_exists='append', index=False)
    conn.close()
    print(f" inserted {len(df)} rows.")
    return len(df)

# --- Main Execution ---
if __name__ == "__main__":
    setup_database()
    
    hk_symbols = fetch_hk_universe()
    cn_symbols = fetch_cn_universe()
    all_symbols = hk_symbols + cn_symbols
    
    print(f"\nStarting backfill for {len(all_symbols)} total symbols...")
    print("(Existing symbols will be skipped)\n")
    
    total_rows = 0
    for i, symbol in enumerate(all_symbols):
        print(f"[{i+1}/{len(all_symbols)}]", end="")
        rows_inserted = backfill_symbol_history(symbol)
        total_rows += rows_inserted
        time.sleep(REQUEST_DELAY)
    
    print(f"\n--- Backfill Complete ---")
    print(f"Total new rows inserted: {total_rows}")