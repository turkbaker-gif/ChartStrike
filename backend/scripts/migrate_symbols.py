import sqlite3
import re

DB_PATH = "chartstrike.db"

def normalize_to_itick(symbol):
    """Convert '06166.HK' to '6166.HK'"""
    match = re.match(r"0*(\d+\.HK)", symbol)
    if match:
        return match.group(1)
    return symbol

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Create the mapping table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS symbol_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol_itick TEXT UNIQUE NOT NULL,
        symbol_local TEXT UNIQUE,
        name TEXT,
        exchange TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 2. Get all distinct HK symbols from your stock_prices table
cur.execute("SELECT DISTINCT symbol FROM stock_prices WHERE symbol LIKE '%.HK'")
local_symbols = [row[0] for row in cur.fetchall()]

print(f"Found {len(local_symbols)} unique HK symbols in stock_prices.")

for local_sym in local_symbols:
    itick_sym = normalize_to_itick(local_sym)
    
    # Insert or ignore into the mapping table
    cur.execute(
        "INSERT OR IGNORE INTO symbol_mapping (symbol_itick, symbol_local) VALUES (?, ?)",
        (itick_sym, local_sym)
    )
    
    # If the local format is already the iTick format, we still want to record it
    if local_sym != itick_sym:
        cur.execute(
            "INSERT OR IGNORE INTO symbol_mapping (symbol_itick, symbol_local) VALUES (?, ?)",
            (local_sym, local_sym)
        )

conn.commit()
conn.close()
print("Symbol mapping table populated.")