from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.hk_patterns.hk_preopen_scanner import HKPreopenScanner


class HKDynamicWatchlistService:
    @staticmethod
    def _get_all_hk_symbols(db: Session) -> list[str]:
        """Fetch all distinct HK symbols from the stock_prices table."""
        query = text("""
            SELECT DISTINCT symbol
            FROM stock_prices
            WHERE symbol LIKE '%.HK'
            ORDER BY symbol
        """)
        result = db.execute(query)
        return [row[0] for row in result.fetchall()]

    @staticmethod
    def build_preopen_watchlist(db: Session, min_percent_gain: float = 5.0) -> list[dict]:
        symbols = HKDynamicWatchlistService._get_all_hk_symbols(db)
        
        scan_results = HKPreopenScanner.scan_watchlist(
            db,
            symbols,
            min_percent_gain=min_percent_gain,
        )

        qualified = [item for item in scan_results if item.get("qualified")]
        qualified.sort(key=lambda x: float(x.get("percent_change", 0)), reverse=True)
        return qualified