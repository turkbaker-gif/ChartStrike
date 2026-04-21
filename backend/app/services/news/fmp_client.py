import httpx

from app.core.config import settings


class FMPClient:
    BASE_URL = "https://financialmodelingprep.com/stable/news/stock"

    @staticmethod
    def get_stock_news(symbol: str, limit: int = 10) -> list[dict]:
        if not settings.fmp_api_key:
            return []

        params = {
            "symbols": symbol,
            "limit": limit,
            "apikey": settings.fmp_api_key,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(FMPClient.BASE_URL, params=params)

                if response.status_code != 200:
                    print(f"FMP error for {symbol}: {response.text}")
                    return []

                data = response.json()

        except Exception as e:
            print(f"FMP request failed for {symbol}: {e}")
            return []

        if not isinstance(data, list):
            return []

        return data