import time
import sqlite3
import pandas as pd
import yfinance as yf
from pathlib import Path

# --- Configuration ---
DB_PATH = "chartstrike.db"
HK_LIST_FILE = Path(__file__).parent / "hk_stock_list.csv"
REQUEST_DELAY = 2.5       # seconds between requests (increased)
MIN_ROWS_REQUIRED = 100   # skip symbols with less than 100 days of data
START_DATE = "2020-01-01"

# --- Logging failures ---
FAILED_LOG = Path(__file__).parent / "failed_hk_symbols.txt"

def log_failure(symbol, reason):
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{symbol}: {reason}\n")

# --- Database Helpers ---
def get_db_connection():
    return sqlite3.connect(DB_PATH)

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
    print("Database ready.")

def symbol_already_processed(symbol):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM stock_prices WHERE symbol = ? LIMIT 1", (symbol,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def backfill_symbol_history(symbol):
    """Fetch historical data with validation."""
    if symbol_already_processed(symbol):
        print(f"  {symbol} already in DB. Skipping.")
        return 0

    try:
        print(f"  Processing {symbol}...", end="", flush=True)
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=START_DATE, interval="1d")
        
        # Validate data
        if df.empty:
            reason = "no data returned"
            print(f" {reason}")
            log_failure(symbol, reason)
            return 0
        
        if len(df) < MIN_ROWS_REQUIRED:
            reason = f"only {len(df)} rows (< {MIN_ROWS_REQUIRED})"
            print(f" {reason}")
            log_failure(symbol, reason)
            return 0
        
        # Clean and prepare
        df = df.reset_index()
        df['Date'] = df['Date'].dt.date.astype(str)
        df = df.rename(columns={
            'Date': 'date', 'Open': 'open', 'High': 'high',
            'Low': 'low', 'Close': 'close', 'Volume': 'volume'
        })
        df['symbol'] = symbol
        df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Insert into DB
        conn = get_db_connection()
        df.to_sql('stock_prices', conn, if_exists='append', index=False)
        conn.close()
        print(f" inserted {len(df)} rows.")
        return len(df)
        
    except Exception as e:
        reason = f"exception: {e}"
        print(f" failed: {reason}")
        log_failure(symbol, reason)
        return 0

# --- Main ---
if __name__ == "__main__":
    # Clear old failure log
    if FAILED_LOG.exists():
        FAILED_LOG.unlink()
    
    setup_database()
    
    if not HK_LIST_FILE.exists():
        print(f"ERROR: {HK_LIST_FILE} not found.")
        exit(1)
    
    df = pd.read_csv(HK_LIST_FILE, dtype=str)
    symbols = df['symbol'].tolist()
    print(f"Loaded {len(symbols)} HK symbols.\n")
    
    total_rows = 0
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}]", end="")
        rows_inserted = backfill_symbol_history(symbol)
        total_rows += rows_inserted
        time.sleep(REQUEST_DELAY)
    
    print(f"\n--- Backfill Complete ---")
    print(f"Total new rows inserted: {total_rows}")
    print(f"Failures logged to: {FAILED_LOG}")