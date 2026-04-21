from datetime import datetime, timezone
import httpx


class YahooClient:
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

    @staticmethod
    def map_symbol(symbol: str) -> str:
        """
        Internal symbol format already matches Yahoo for HK names:
        0700.HK, 9988.HK, 3690.HK
        """
        return symbol

    @classmethod
    def _get_chart_data(
        cls,
        symbol: str,
        range_value: str,
        interval: str,
    ) -> dict | None:
        mapped_symbol = cls.map_symbol(symbol)
        params = {
            "range": range_value,
            "interval": interval,
            "includePrePost": "false",
            "events": "div,splits",
        }

        try:
            with httpx.Client(timeout=20.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get(f"{cls.BASE_URL}/{mapped_symbol}", params=params)

                if response.status_code != 200:
                    print(f"Yahoo chart HTTP error for {mapped_symbol}: {response.text}")
                    return None

                data = response.json()
        except Exception as e:
            print(f"Yahoo chart request failed for {mapped_symbol}: {e}")
            return None

        if not isinstance(data, dict):
            return None

        chart = data.get("chart", {})
        error = chart.get("error")
        if error:
            print(f"Yahoo chart API error for {mapped_symbol}: {error}")
            return None

        results = chart.get("result", [])
        if not results or not isinstance(results, list):
            return None

        return results[0]

    @classmethod
    def get_quote(cls, symbol: str) -> dict | None:
        result = cls._get_chart_data(symbol=symbol, range_value="1d", interval="1m")
        if not result:
            return None

        meta = result.get("meta", {}) or {}
        indicators = result.get("indicators", {}) or {}
        quote_list = indicators.get("quote", []) or []
        quote_block = quote_list[0] if quote_list else {}

        timestamps = result.get("timestamp", []) or []
        closes = quote_block.get("close", []) or []

        latest_close = None
        for value in reversed(closes):
            if value is not None:
                latest_close = float(value)
                break

        price = latest_close
        if price is None:
            regular_market_price = meta.get("regularMarketPrice")
            if regular_market_price is not None:
                price = float(regular_market_price)

        if price is None:
            return None

        return {
            "symbol": symbol,
            "price": float(price),
            "open": float(meta.get("regularMarketOpen") or 0),
            "high": float(meta.get("regularMarketDayHigh") or 0),
            "low": float(meta.get("regularMarketDayLow") or 0),
            "previous_close": float(meta.get("previousClose") or 0),
            "change": round(float(price) - float(meta.get("previousClose") or 0), 4),
            "percent_change": round(
                (
                    (float(price) - float(meta.get("previousClose") or 0))
                    / float(meta.get("previousClose") or 1)
                )
                * 100,
                4,
            ) if float(meta.get("previousClose") or 0) != 0 else 0,
            "volume": float(meta.get("regularMarketVolume") or 0),
            "currency": meta.get("currency"),
            "exchange": meta.get("fullExchangeName") or meta.get("exchangeName"),
            "regular_market_time": meta.get("regularMarketTime"),
        }

    @classmethod
    def get_time_series(
        cls,
        symbol: str,
        interval: str = "1m",
        range_value: str = "5d",
    ) -> list[dict]:
        yahoo_interval = interval
        if interval == "1min":
            yahoo_interval = "1m"

        result = cls._get_chart_data(symbol=symbol, range_value=range_value, interval=yahoo_interval)
        if not result:
            return []

        timestamps = result.get("timestamp", []) or []
        indicators = result.get("indicators", {}) or {}
        quote_list = indicators.get("quote", []) or []
        if not quote_list:
            return []

        quote_block = quote_list[0]
        opens = quote_block.get("open", []) or []
        highs = quote_block.get("high", []) or []
        lows = quote_block.get("low", []) or []
        closes = quote_block.get("close", []) or []
        volumes = quote_block.get("volume", []) or []

        rows = []
        for i, ts in enumerate(timestamps):
            try:
                o = opens[i]
                h = highs[i]
                l = lows[i]
                c = closes[i]
                v = volumes[i] if i < len(volumes) else 0
            except IndexError:
                continue

            if None in (o, h, l, c):
                continue

            dt = datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)

            rows.append(
                {
                    "datetime": dt.isoformat(sep=" "),
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": float(v or 0),
                }
            )

        return rows