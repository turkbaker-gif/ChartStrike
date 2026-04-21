import httpx

from app.core.config import settings


class TwelveDataClient:
    BASE_URL = "https://api.twelvedata.com"

    @staticmethod
    def map_symbol(symbol: str) -> tuple[str, str | None, str | None]:
        """
        Internal -> Twelve Data symbol + exchange + mic_code
        0700.HK -> ("0700", "HKEX", "XHKG")
        """
        if symbol.endswith(".HK"):
            return symbol.replace(".HK", ""), "HKEX", "XHKG"
        return symbol, None, None

    @classmethod
    def get_quote(cls, symbol: str) -> dict | None:
        if not settings.twelvedata_api_key:
            return None

        mapped_symbol, exchange, mic_code = cls.map_symbol(symbol)

        candidates = [
            {"symbol": mapped_symbol, "apikey": settings.twelvedata_api_key},
            {
                "symbol": mapped_symbol,
                "exchange": exchange,
                "apikey": settings.twelvedata_api_key,
            } if exchange else None,
            {
                "symbol": mapped_symbol,
                "mic_code": mic_code,
                "apikey": settings.twelvedata_api_key,
            } if mic_code else None,
            {
                "symbol": mapped_symbol,
                "exchange": exchange,
                "mic_code": mic_code,
                "country": "Hong Kong",
                "apikey": settings.twelvedata_api_key,
            } if exchange and mic_code else None,
        ]

        for params in [c for c in candidates if c]:
            try:
                with httpx.Client(timeout=15.0) as client:
                    response = client.get(f"{cls.BASE_URL}/quote", params=params)

                    if response.status_code != 200:
                        print(f"TwelveData quote HTTP error for {params}: {response.text}")
                        continue

                    data = response.json()

            except Exception as e:
                print(f"TwelveData quote request failed for {params}: {e}")
                continue

            if not isinstance(data, dict):
                continue

            if data.get("status") == "error":
                print(f"TwelveData quote API error for {params}: {data}")
                continue

            return data

        return None

    @classmethod
    def get_time_series(
        cls,
        symbol: str,
        interval: str = "1min",
        outputsize: int = 100,
    ) -> list[dict]:
        if not settings.twelvedata_api_key:
            return []

        mapped_symbol, exchange, mic_code = cls.map_symbol(symbol)

        candidates = [
            {
                "symbol": mapped_symbol,
                "interval": interval,
                "outputsize": outputsize,
                "format": "JSON",
                "apikey": settings.twelvedata_api_key,
            },
            {
                "symbol": mapped_symbol,
                "exchange": exchange,
                "interval": interval,
                "outputsize": outputsize,
                "format": "JSON",
                "apikey": settings.twelvedata_api_key,
            } if exchange else None,
            {
                "symbol": mapped_symbol,
                "mic_code": mic_code,
                "interval": interval,
                "outputsize": outputsize,
                "format": "JSON",
                "apikey": settings.twelvedata_api_key,
            } if mic_code else None,
            {
                "symbol": mapped_symbol,
                "exchange": exchange,
                "mic_code": mic_code,
                "country": "Hong Kong",
                "interval": interval,
                "outputsize": outputsize,
                "format": "JSON",
                "apikey": settings.twelvedata_api_key,
            } if exchange and mic_code else None,
        ]

        for params in [c for c in candidates if c]:
            try:
                with httpx.Client(timeout=20.0) as client:
                    response = client.get(f"{cls.BASE_URL}/time_series", params=params)

                    if response.status_code != 200:
                        print(f"TwelveData time_series HTTP error for {params}: {response.text}")
                        continue

                    data = response.json()

            except Exception as e:
                print(f"TwelveData time_series request failed for {params}: {e}")
                continue

            if not isinstance(data, dict):
                continue

            if data.get("status") == "error":
                print(f"TwelveData time_series API error for {params}: {data}")
                continue

            values = data.get("values", [])
            if not isinstance(values, list):
                continue

            values.reverse()
            return values

        return []