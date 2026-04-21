from datetime import date, timedelta
import httpx

from app.core.config import settings


class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1/company-news"

    @staticmethod
    def get_company_news(symbol: str, days_back: int = 3) -> list[dict]:
        if not settings.finnhub_api_key:
            return []

        today = date.today()
        start_date = today - timedelta(days=days_back)

        params = {
            "symbol": symbol,
            "from": start_date.isoformat(),
            "to": today.isoformat(),
            "token": settings.finnhub_api_key,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(FinnhubClient.BASE_URL, params=params)

                if response.status_code != 200:
                    print(f"Finnhub error for {symbol}: {response.text}")
                    return []

                data = response.json()

        except Exception as e:
            print(f"Finnhub request failed: {e}")
            return []

        if not isinstance(data, list):
            return []

        return data