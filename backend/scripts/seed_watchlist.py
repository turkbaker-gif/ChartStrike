from app.db.session import SessionLocal
from app.services.watchlist.watchlist_service import WatchlistService

INITIAL_SYMBOLS = [
    "0700.HK",  # Tencent
    "9988.HK",  # Alibaba
    "3690.HK",  # Meituan
    "1810.HK",  # Xiaomi
    "1024.HK",  # Kuaishou
]

db = SessionLocal()
try:
    for symbol in INITIAL_SYMBOLS:
        WatchlistService.add_symbol(db, symbol)
    print(f"Added {len(INITIAL_SYMBOLS)} symbols to watchlist.")
finally:
    db.close()