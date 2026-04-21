from sqlalchemy.orm import Session
from app.services.market.data_service import LocalDataService


class HKPreopenScanner:
    @staticmethod
    def scan_symbol(db: Session, symbol: str, min_percent_gain: float = 5.0) -> dict:
        """Check if the most recent daily close shows a strong gain (>min_percent_gain%)."""
        candles = LocalDataService.get_recent_candles(db, symbol, limit=2)
        if len(candles) < 2:
            return {"symbol": symbol, "qualified": False, "reason": "not_enough_data"}

        prev_close = float(candles[-2]['close'])
        current_close = float(candles[-1]['close'])
        if prev_close <= 0:
            return {"symbol": symbol, "qualified": False, "reason": "invalid_prev_close"}

        percent_change = ((current_close - prev_close) / prev_close) * 100
        return {
            "symbol": symbol,
            "previous_close": round(prev_close, 4),
            "reference_price": round(current_close, 4),
            "percent_change": round(percent_change, 2),
            "qualified": percent_change >= min_percent_gain,
        }

    @staticmethod
    def scan_watchlist(db: Session, symbols: list[str], min_percent_gain: float = 5.0) -> list[dict]:
        """Scan a list of symbols and return results for each."""
        results = []
        for symbol in symbols:
            result = HKPreopenScanner.scan_symbol(db, symbol, min_percent_gain)
            results.append(result)
        return results