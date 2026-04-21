from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.services.patterns.breakout_20d import Breakout20DPattern
from app.services.recommendations.signal_service import SignalService


class PatternRunner:
    def __init__(self):
        self.pattern = Breakout20DPattern()

    def run_for_symbol(self, db: Session, symbol: str) -> dict:
        # Fetch 25 most recent daily candles from local DB
        query = text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE symbol = :symbol
            ORDER BY date DESC
            LIMIT 25
        """)
        result = db.execute(query, {"symbol": symbol})
        rows = result.fetchall()

        if len(rows) < 21:
            return {"symbol": symbol, "status": "not_enough_data"}

        # Convert to list of dicts (oldest first for feature computation)
        candles = [
            {
                "date": row[0],
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
            }
            for row in reversed(rows)
        ]

        features = self._compute_features(candles)
        result = self.pattern.evaluate(symbol, features)

        if result["triggered"]:
            # Check for recent duplicate to avoid spam
            existing = db.query(Signal).filter(
                Signal.symbol == symbol,
                Signal.pattern_name == result["pattern_name"]
            ).order_by(Signal.detected_at.desc()).first()

            if existing:
                return {"symbol": symbol, "status": "duplicate_skipped", "signal_id": existing.id}

            signal = SignalService.create_signal_from_pattern(
                db, symbol, result, features
            )
            return {"symbol": symbol, "status": "triggered", "signal_id": signal.id}

        return {"symbol": symbol, "status": "no_trigger"}

    def _compute_features(self, candles: list[dict]) -> dict:
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        volumes = [c['volume'] for c in candles]

        return {
            "current_close": closes[-1],
            "high_20": max(highs[-21:-1]),
            "avg_volume_20": sum(volumes[-21:-1]) / 20,
            "current_volume": volumes[-1],
            "relative_volume": volumes[-1] / (sum(volumes[-21:-1]) / 20),
            "ma20": sum(closes[-21:-1]) / 20,
            "avg_range_20": sum(highs[i] - candles[i]['low'] for i in range(-21, -1)) / 20,
        }