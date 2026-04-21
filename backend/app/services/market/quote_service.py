from app.services.market.itick_client import ITickClient
from app.services.market.data_service import LocalDataService
from app.db.session import SessionLocal

class QuoteService:
    @staticmethod
    def get_latest_quote(symbol: str) -> dict | None:
        # Try iTick first
        quote = ITickClient.get_quote(symbol)
        if quote:
            return quote

        # Fall back to latest daily close from local DB
        db = SessionLocal()
        try:
            price = LocalDataService.get_latest_price(db, symbol)
            if price:
                return {
                    "symbol": symbol,
                    "price": price,
                    "source": "local_daily_close",
                }
        finally:
            db.close()

        return None