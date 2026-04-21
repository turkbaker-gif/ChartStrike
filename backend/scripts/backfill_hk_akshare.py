import time
import sqlite3
import pandas as pd
import akshare as ak
from pathlib import Path
import random

# --- Configuration ---
DB_PATH = "chartstrike.db"
REQUEST_DELAY = 30.0          # seconds between requests (conservative)
MAX_RETRIES = 5
BACKOFF_FACTOR = 5.0
START_DATE = "20200101"

# --- Logging failures ---
FAILED_LOG = Path(__file__).parent / "failed_hk_akshare.txt"

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

def get_liquid_hk_universe():
    """
    Build a high-quality HK universe using Stock Connect + top Main Board stocks.
    Returns a list of symbols formatted as 'XXXXX.HK'
    """
    print("Building liquid HK universe...")
    symbols = set()
    
    # 1. Stock Connect (most liquid)
    try:
        df_ggt = ak.stock_hk_ggt_components_em()
        symbols.update([f"{code}.HK" for code in df_ggt['代码'].tolist()])
        print(f"  Stock Connect: {len(df_ggt)} symbols")
    except Exception as e:
        print(f"  Stock Connect failed: {e}")
    
    # 2. Top Main Board by market cap (fallback)
    try:
        df_main = ak.stock_hk_main_board_spot_em()
        # Sort by market cap (if column exists) or just take top 500
        if '市值' in df_main.columns:
            df_main = df_main.sort_values('市值', ascending=False)
        top_n = min(800, len(df_main))
        symbols.update([f"{code}.HK" for code in df_main['代码'].head(top_n).tolist()])
        print(f"  Added top {top_n} Main Board stocks")
    except Exception as e:
        print(f"  Main Board fetch failed: {e}")
    
    symbols = sorted(list(symbols))
    print(f"Total liquid HK universe: {len(symbols)} symbols")
    return symbols

def backfill_symbol_history(symbol):
    """Fetch historical data with exponential backoff and retries."""
    if symbol_already_processed(symbol):
        print(f"  {symbol} already in DB. Skipping.")
        return 0

    akshare_symbol = symbol.replace(".HK", "")
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            print(f"  Processing {symbol} (attempt {attempt+1})...", end="", flush=True)
            df = ak.stock_hk_hist(symbol=akshare_symbol, period="daily",
                                 start_date=START_DATE, adjust="qfq")
            
            if df.empty:
                reason = "no data returned"
                print(f" {reason}")
                log_failure(symbol, reason)
                return 0
            
            # Standardize columns
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume'
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
            if attempt == MAX_RETRIES:
                reason = f"failed after {MAX_RETRIES+1} attempts: {e}"
                print(f" {reason}")
                log_failure(symbol, reason)
                return 0
            else:
                wait = BACKOFF_FACTOR ** attempt + random.uniform(0, 1)
                print(f" error, waiting {wait:.1f}s...", end="", flush=True)
                time.sleep(wait)
    
    return 0

# --- Main ---
if __name__ == "__main__":
    # Clear old failure log
    if FAILED_LOG.exists():
        FAILED_LOG.unlink()
    
    setup_database()
    
    symbols = get_liquid_hk_universe()
    if not symbols:
        print("ERROR: Could not build HK universe.")
        exit(1)
    
    print(f"\nStarting backfill for {len(symbols)} liquid HK symbols...")
    print("(Existing symbols will be skipped)\n")
    
    total_rows = 0
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}]", end="")
        rows_inserted = backfill_symbol_history(symbol)
        total_rows += rows_inserted
        time.sleep(REQUEST_DELAY)
    
    print(f"\n--- Backfill Complete ---")
    print(f"Total new rows inserted: {total_rows}")
    print(f"Failures logged to: {FAILED_LOG}")