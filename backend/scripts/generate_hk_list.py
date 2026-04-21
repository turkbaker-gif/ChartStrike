import akshare as ak

# Fetch current main board equities (no warrants/CBBCs)
df = ak.stock_hk_main_board_spot_em()

# Keep only the stock code and format as .HK
df['symbol'] = df['代码'].astype(str) + '.HK'

# Save to CSV in the same folder
df[['symbol']].to_csv('hk_stock_list.csv', index=False)

print(f"✅ Generated hk_stock_list.csv with {len(df)} symbols.")