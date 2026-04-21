import sqlite3
import re

DB_PATH = "chartstrike.db"

# Mapping from Chinese exchange names to standard suffixes
EXCHANGE_MAP = {
    "深圳证券交易所": "SZ",
    "上海证券交易所": "SH",
    "北京证券交易所": "BJ",
}

def convert_to_standard(symbol):
    for chinese, english in EXCHANGE_MAP.items():
        if symbol.endswith(f".{chinese}"):
            code = symbol[:-(len(chinese) + 1)]  # remove the suffix and dot
            code = code.lstrip("0") or "0"
            return f"{code}.{english}"
    return symbol

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Find all symbols with Chinese suffixes
cur.execute("""
    SELECT DISTINCT symbol FROM stock_prices
    WHERE symbol LIKE '%.深圳证券交易所'
       OR symbol LIKE '%.上海证券交易所'
       OR symbol LIKE '%.北京证券交易所'
""")
rows = cur.fetchall()

print(f"Found {len(rows)} symbols with Chinese suffixes.")

for (local_sym,) in rows:
    standard_sym = convert_to_standard(local_sym)
    itick_sym = standard_sym.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    
    # Insert into mapping table
    cur.execute("""
        INSERT OR REPLACE INTO symbol_mapping (symbol_itick, symbol_local)
        VALUES (?, ?)
    """, (itick_sym, local_sym))
    
    print(f"  Mapped: {local_sym} -> iTick: {itick_sym}, Standard: {standard_sym}")

conn.commit()
conn.close()
print("\nDone. Chinese suffixes have been mapped to standard English formats.")