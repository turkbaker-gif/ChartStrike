from __future__ import annotations

from typing import Any
import httpx

from app.core.config import settings


class EODHDClient:
    BASE_URL = "https://eodhd.com/api"

    def __init__(self) -> None:
        self.api_key = settings.eodhd_api_key

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        response = httpx.get(
            f"{self.BASE_URL}/{path}",
            params=params,
            timeout=20.0,
        )
        response.raise_for_status()

        data = response.json()

        # EODHD sometimes returns dict-style errors
        if isinstance(data, dict) and data.get("error"):
            raise ValueError(f"EODHD error: {data}")

        return data

    def fetch_intraday(
        self,
        symbol: str,
        interval: str | None = None,
        outputsize: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch recent intraday candles.

        EODHD intraday endpoint uses:
        /intraday/{symbol}
        with interval, api_token, fmt=json
        """
        params = {
            "api_token": self.api_key,
            "fmt": "json",
            "interval": interval or settings.eodhd_interval,
        }

        # EODHD intraday uses either a record count or date filters depending on endpoint behavior.
        # We’ll fetch recent data and trim locally.
        data = self._get(f"intraday/{symbol}", params)

        if not isinstance(data, list) or not data:
            raise ValueError(f"EODHD returned no intraday data for '{symbol}': {data}")

        # Keep only the most recent N rows
        return data[-(outputsize or settings.eodhd_outputsize):]

    def validate_symbol(self, symbol: str) -> str:
        """
        For MVP, just trust symbols in SYMBOL.EXCHANGE form.
        Example: 0700.HK
        """
        if "." not in symbol:
            raise ValueError(
                f"Invalid EODHD symbol '{symbol}'. Expected format like 0700.HK"
            )
        return symbol