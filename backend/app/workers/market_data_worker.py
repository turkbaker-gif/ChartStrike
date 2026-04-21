from __future__ import annotations

import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.market.eodhd_client import EODHDClient
from app.services.market.candle_store import CandleStore


class MarketDataWorker:
    def __init__(self) -> None:
        self.client = EODHDClient()

    def fetch_and_store_symbol(self, db: Session, symbol: str) -> dict:
        resolved_symbol = self.client.validate_symbol(symbol)

        values = self.client.fetch_intraday(
            symbol=resolved_symbol,
            interval=settings.eodhd_interval,
            outputsize=settings.eodhd_outputsize,
        )

        count = CandleStore.upsert_intraday(
            db=db,
            symbol=resolved_symbol,
            timeframe=settings.eodhd_interval,
            values=values,
        )

        return {
            "symbol": resolved_symbol,
            "status": "ok",
            "candles_processed": count,
        }

    def run_once(self) -> list[dict]:
        db = SessionLocal()
        try:
            results = []
            for symbol in settings.watchlist:
                try:
                    result = self.fetch_and_store_symbol(db, symbol)
                except Exception as e:
                    result = {"symbol": symbol, "status": "error", "error": str(e)}
                results.append(result)
            return results
        finally:
            db.close()

    def run_forever(self) -> None:
        while True:
            results = self.run_once()
            print(results, flush=True)
            time.sleep(settings.market_poll_seconds)