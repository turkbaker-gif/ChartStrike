from datetime import datetime, timedelta
import random

from app.db.session import SessionLocal
from app.db.models import Candle

db = SessionLocal()

symbol = "0700.HK"

start = datetime.utcnow() - timedelta(minutes=25)

price = 490

for i in range(21):

    ts = start + timedelta(minutes=i)

    open_p = price

    close_p = price + random.uniform(-1, 1)

    high = max(open_p, close_p) + random.uniform(0, 1)

    low = min(open_p, close_p) - random.uniform(0, 1)

    volume = 1000000 + random.uniform(-200000, 200000)

    db.add(
        Candle(
            symbol=symbol,
            timeframe="1m",
            ts=ts,
            open=open_p,
            high=high,
            low=low,
            close=close_p,
            volume=volume
        )
    )

    price = close_p

db.commit()

print("Seeded candles")