from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candle
from app.services.market.itick_client import ITickClient


class MarketDataService:
    @staticmethod
    def refresh_candles_for_symbol(db: Session, symbol: str, interval: str = "1m", outputsize: int = 100):
        """
        Fetch intraday candles from iTick and upsert into database.
        """
        # iTick uses 'limit' instead of outputsize; we'll request a bit more and slice
        raw_candles = ITickClient.get_time_series(
            symbol=symbol,
            interval=interval,   # e.g., "1m", "5m"
            limit=outputsize     # request exactly the number we need
        )

        if not raw_candles:
            return {"symbol": symbol, "inserted": 0, "updated": 0, "status": "no_data"}

        inserted = 0
        updated = 0

        for item in raw_candles:
            ts_str = item.get("datetime")
            if not ts_str:
                continue

            try:
                ts = datetime.fromisoformat(ts_str)
            except Exception:
                continue

            stmt = select(Candle).where(
                Candle.symbol == symbol,
                Candle.timeframe == interval,
                Candle.ts == ts,
            )
            existing = db.execute(stmt).scalar_one_or_none()

            open_v = float(item["open"])
            high_v = float(item["high"])
            low_v = float(item["low"])
            close_v = float(item["close"])
            volume_v = float(item.get("volume", 0) or 0)

            if existing:
                changed = False
                if float(existing.open) != open_v:
                    existing.open = open_v
                    changed = True
                if float(existing.high) != high_v:
                    existing.high = high_v
                    changed = True
                if float(existing.low) != low_v:
                    existing.low = low_v
                    changed = True
                if float(existing.close) != close_v:
                    existing.close = close_v
                    changed = True
                if float(existing.volume or 0) != volume_v:
                    existing.volume = volume_v
                    changed = True

                if changed:
                    updated += 1
                continue

            candle = Candle(
                symbol=symbol,
                timeframe=interval,
                ts=ts,
                open=open_v,
                high=high_v,
                low=low_v,
                close=close_v,
                volume=volume_v,
            )
            db.add(candle)
            inserted += 1

        db.commit()

        return {
            "symbol": symbol,
            "inserted": inserted,
            "updated": updated,
            "status": "ok",
        }

    def get_candles_for_symbol(db: Session, symbol: str, interval: str = "1m", limit: int = 100) -> list[dict]:
        """
        Retrieve recent candles from the database for a given symbol and interval.
        Returns a list of dicts with keys: datetime, open, high, low, close, volume.
        """
        stmt = select(Candle).where(
            Candle.symbol == symbol,
            Candle.timeframe == interval
            ).order_by(Candle.ts.desc()).limit(limit)

        candles = db.execute(stmt).scalars().all()
        candles.reverse()  # oldest first

        return [
        {
            "datetime": c.ts.isoformat(),
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": float(c.volume),
        }
        for c in candles
    ]