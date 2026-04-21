from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Candle


class CandleStore:
    @staticmethod
    def _parse_timestamp(row: dict) -> datetime:
        """
        EODHD intraday data may provide:
        - 'datetime': '2026-03-09 10:31:00'
        - or date fields depending on endpoint/version

        We’ll support the common 'datetime' field first.
        """
        raw = row.get("datetime") or row.get("date")
        if not raw:
            raise ValueError(f"Missing datetime/date field in row: {row}")

        return datetime.fromisoformat(raw)

    @staticmethod
    def upsert_intraday(
        db: Session,
        symbol: str,
        timeframe: str,
        values: list[dict],
    ) -> int:
        inserted_or_updated = 0

        for row in values:
            ts = CandleStore._parse_timestamp(row)

            stmt = select(Candle).where(
                Candle.symbol == symbol,
                Candle.timeframe == timeframe,
                Candle.ts == ts,
            )
            existing = db.execute(stmt).scalar_one_or_none()

            open_price = float(row["open"])
            high_price = float(row["high"])
            low_price = float(row["low"])
            close_price = float(row["close"])
            volume = float(row.get("volume", 0) or 0)

            if existing:
                existing.open = open_price
                existing.high = high_price
                existing.low = low_price
                existing.close = close_price
                existing.volume = volume
            else:
                db.add(
                    Candle(
                        symbol=symbol,
                        timeframe=timeframe,
                        ts=ts,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=volume,
                    )
                )

            inserted_or_updated += 1

        db.commit()
        return inserted_or_updated