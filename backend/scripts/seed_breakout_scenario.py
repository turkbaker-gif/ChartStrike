from datetime import datetime, timedelta, UTC
import random

from app.db.session import SessionLocal
from app.db.models import Candle

db = SessionLocal()

symbol = "0700.HK"

# optional cleanup for this symbol/timeframe
db.query(Candle).filter(
    Candle.symbol == symbol,
    Candle.timeframe == "1m"
).delete()

start = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=25)
price = 490.0

# 20 normal candles
for i in range(20):
    ts = start + timedelta(minutes=i)
    open_p = price + random.uniform(-0.4, 0.4)
    close_p = open_p + random.uniform(-0.5, 0.5)
    high_p = max(open_p, close_p) + random.uniform(0.1, 0.4)
    low_p = min(open_p, close_p) - random.uniform(0.1, 0.4)
    volume = 1_000_000 + random.uniform(-100_000, 100_000)

    db.add(
        Candle(
            symbol=symbol,
            timeframe="1m",
            ts=ts,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            volume=volume,
        )
    )
    price = close_p

# breakout candle
ts = start + timedelta(minutes=20)
db.add(
    Candle(
        symbol=symbol,
        timeframe="1m",
        ts=ts,
        open=price,
        high=497.2,
        low=494.9,
        close=496.8,
        volume=2_600_000,
    )
)

db.commit()
db.close()

print("Seeded breakout scenario for 0700.HK")