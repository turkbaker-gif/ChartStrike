import time
import sqlite3
import pandas as pd
import yfinance as yf
from pathlib import Path

# --- Configuration ---
DB_PATH = "chartstrike.db"
HK_LIST_FILE = Path(__file__).parent / "hk_stock_list.csv"  # expects CSV with 'symbol' column
REQUEST_DELAY = 1.5  # seconds between symbols (yfinance is lenient)
MAX_RETRIES = 2
START_DATE = "2020-01-01"

# --- Helper Functions ---
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

def load_hk_universe():
    """Load symbols from the CSV file."""
    if not HK_LIST_FILE.exists():
        print(f"ERROR: {HK_LIST_FILE} not found. Generate it first.")
        return []
    df = pd.read_csv(HK_LIST_FILE, dtype=str)
    symbols = df['symbol'].tolist()
    print(f"Loaded {len(symbols)} HK symbols from {HK_LIST_FILE.name}")
    return symbols

def symbol_already_processed(symbol):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM stock_prices WHERE symbol = ? LIMIT 1", (symbol,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def backfill_symbol_history(symbol):
    """Fetch historical data for a single symbol using yfinance."""
    if symbol_already_processed(symbol):
        print(f"  {symbol} already in DB. Skipping.")
        return 0

    for attempt in range(MAX_RETRIES + 1):
        try:
            print(f"  Processing {symbol}...", end="", flush=True)
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=START_DATE, interval="1d")
            
            if df.empty:
                print(" no data.")
                return 0
            
            df = df.reset_index()
            df['Date'] = df['Date'].dt.date.astype(str)  # ensure string for SQLite
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
            if attempt == MAX_RETRIES:
                print(f" failed: {e}")
                return 0
            else:
                print(f" retry...", end="", flush=True)
                time.sleep(3)

    return 0

# --- Main ---
if __name__ == "__main__":
    setup_database()
    symbols = load_hk_universe()
    if not symbols:
        exit(1)
    
    print(f"\nStarting backfill for {len(symbols)} HK symbols...")
    print("(Existing symbols will be skipped)\n")
    
    total_rows = 0
    for i, symbol in enumerate(symbols):
        print(f"[{i+1}/{len(symbols)}]", end="")
        rows_inserted = backfill_symbol_history(symbol)
        total_rows += rows_inserted
        time.sleep(REQUEST_DELAY)
    
    print(f"\n--- Backfill Complete ---")
    print(f"Total new rows inserted: {total_rows}")