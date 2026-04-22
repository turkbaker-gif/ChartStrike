from sqlalchemy.orm import Session
from app.services.market.data_service import LocalDataService
from app.services.market.itick_client import ITickClient


class HKPreopenScanner:
    @staticmethod
    def scan_watchlist(symbols: list[str], min_percent_gain: float = 5.0) -> list[dict]:
        """
        Scans a list of symbols for pre-open momentum using a SINGLE batch API call.
        """
        if not symbols:
            return []

        # 1. Fetch all quotes in a SINGLE batch request
        batch_quotes = ITickClient.get_batch_quotes(symbols)

        results = []
        for symbol in symbols:
            quote = batch_quotes.get(symbol)

            # Default result if quote is missing or invalid
            if not quote:
                results.append({
                    "symbol": symbol,
                    "qualified": False,
                    "reason": "no_quote",
                })
                continue

            previous_close = float(quote.get("previous_close") or 0)
            current_price = float(quote.get("price") or 0)

            if previous_close <= 0 or current_price <= 0:
                results.append({
                    "symbol": symbol,
                    "qualified": False,
                    "reason": "invalid_price_data",
                })
                continue

            percent_change = ((current_price - previous_close) / previous_close) * 100

            results.append({
                "symbol": symbol,
                "previous_close": previous_close,
                "reference_price": current_price,
                "percent_change": round(percent_change, 2),
                "qualified": percent_change >= min_percent_gain,
            })

        return results