import efinance as ef
import pandas as pd

# Test with Tencent (00700.HK)
symbol = "00700"
print(f"Fetching historical data for {symbol}.HK...")

try:
    df = ef.stock.get_quote_history(symbol, klt=101)  # 101 = daily K-line
    if df.empty:
        print("No data returned.")
    else:
        print(f"Success! Retrieved {len(df)} rows.")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nColumn names:", df.columns.tolist())
except Exception as e:
    print(f"Error: {e}")