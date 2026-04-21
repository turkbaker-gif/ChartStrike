import time
import sqlite3
import pandas as pd
import efinance as ef
from pathlib import Path

# --- Configuration ---
DB_PATH = "chartstrike.db"
REQUEST_DELAY = 1.5          # seconds (efinance is quite tolerant)
MAX_RETRIES = 3
MIN_ROWS_REQUIRED = 100      # skip delisted/illiquid stocks
START_DATE = "2020-01-01"

FAILED_LOG = Path(__file__).parent / "failed_efinance.txt"

def log_failure(symbol, reason):
    with open(FAILED_LOG, "a", encoding="utf-8") as f:
        f.write(f"{symbol}: {reason}\n")

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

def get_hk_universe():
    """Use Stock Connect list for liquid HK stocks."""
    try:
        import akshare as ak
        df = ak.stock_hk_ggt_components_em()
        symbols = [f"{code}.HK" for code in df['代码'].tolist()]
        print(f"Fetched {len(symbols)} liquid HK symbols (Stock Connect).")
        return symbols
    except Exception as e:
        print(f"Error fetching HK universe: {e}")
        return []

def get_cn_universe():
    """
    Fetch a filtered list of liquid China A-shares.
    We'll use CSI 300 constituents for quality.
    """
    try:
        import akshare as ak
        # CSI 300 index constituents
        df = ak.index_stock_cons_csindex("000300")
        symbols = [f"{code}.{exchange}" for code, exchange in zip(df['成分券代码'], df['交易所'])]
        print(f"Fetched {len(symbols)} liquid CN symbols (CSI 300).")
        return symbols
    except Exception as e:
        print(f"Error fetching CN universe: {e}")
        return []

def backfill_symbol_history(symbol):
    """Fetch historical data using efinance."""
    if symbol_already_processed(symbol):
        print(f"  {symbol} already in DB. Skipping.")
        return 0

    # efinance expects plain numeric code (no .HK/.SH suffix)
    efinance_symbol = symbol.split('.')[0]

    for attempt in range(MAX_RETRIES + 1):
        try:
            print(f"  Processing {symbol}...", end="", flush=True)
            df = ef.stock.get_quote_history(efinance_symbol, klt=101)  # 101 = daily

            if df.empty:
                reason = "no data returned"
                print(f" {reason}")
                log_failure(symbol, reason)
                return 0

            # Rename and standardize columns
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })
            df['symbol'] = symbol
            df = df[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']]

            # Filter by start date
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] >= pd.to_datetime(START_DATE)]
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')

            if len(df) < MIN_ROWS_REQUIRED:
                reason = f"only {len(df)} rows (< {MIN_ROWS_REQUIRED})"
                print(f" {reason}")
                log_failure(symbol, reason)
                return 0

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
                wait = (2 ** attempt) + 1
                print(f" retry in {wait}s...", end="", flush=True)
                time.sleep(wait)

    return 0

# --- Main ---
if __name__ == "__main__":
    if FAILED_LOG.exists():
        FAILED_LOG.unlink()

    setup_database()

    # Build universe
    hk_symbols = get_hk_universe()
    cn_symbols = get_cn_universe()
    all_symbols = hk_symbols + cn_symbols

    if not all_symbols:
        print("No symbols to process. Exiting.")
        exit(1)

    print(f"\nStarting backfill for {len(all_symbols)} total symbols (HK: {len(hk_symbols)}, CN: {len(cn_symbols)})")
    print("(Existing symbols will be skipped)\n")

    total_rows = 0
    for i, symbol in enumerate(all_symbols):
        print(f"[{i+1}/{len(all_symbols)}]", end="")
        rows_inserted = backfill_symbol_history(symbol)
        total_rows += rows_inserted
        time.sleep(REQUEST_DELAY)

    print(f"\n--- Backfill Complete ---")
    print(f"Total new rows inserted: {total_rows}")
    print(f"Failures logged to: {FAILED_LOG}")