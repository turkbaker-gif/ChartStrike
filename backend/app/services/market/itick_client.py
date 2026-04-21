import httpx
from typing import Optional
from app.core.config import settings

class ITickClient:
    BASE_URL = "https://api.itick.org"

    # ------------------------------------------------------------------
    # 内部辅助：根据后缀解析出 (region, formatted_code)
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_symbol(symbol: str) -> tuple[str, str]:
        """
        将 ChartStrike 内部代码转换为 iTick 所需的 region 和纯数字代码。
        例如:
            '00700.HK'  -> ('hk', '700')
            '600519.SH' -> ('sh', '600519')
            '000001.SZ' -> ('sz', '1')
        """
        if symbol.endswith(".HK"):
            region = "hk"
            code = symbol[:-3]
        elif symbol.endswith(".SH"):
            region = "sh"
            code = symbol[:-3]
        elif symbol.endswith(".SZ"):
            region = "sz"
            code = symbol[:-3]
        else:
            region = "hk"
            code = symbol

        if code.isdigit():
            code = str(int(code))
        return region, code

    # ------------------------------------------------------------------
    # 认证头
    # ------------------------------------------------------------------
    @staticmethod
    def _get_headers() -> dict:
        return {
            "accept": "application/json",
            "token": settings.itick_api_token,
        }

    # ------------------------------------------------------------------
    # 股票实时报价（单只）
    # ------------------------------------------------------------------
    @staticmethod
    def get_quote(symbol: str) -> Optional[dict]:
        try:
            region, code = ITickClient._parse_symbol(symbol)
            url = f"{ITickClient.BASE_URL}/stock/quote"
            params = {
                "region": region.upper(),
                "code": code,
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    url,
                    params=params,
                    headers=ITickClient._get_headers()
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") != 0:
                    print(f"iTick quote error for {symbol}: {data.get('msg')}")
                    return None

                result = data.get("data", {})
                if not result:
                    return None

                price = result.get("ld")
                if price is None:
                    return None

                return {
                    "symbol": symbol,
                    "price": float(price),
                    "open": float(result.get("o", price)),
                    "high": float(result.get("h", price)),
                    "low": float(result.get("l", price)),
                    "previous_close": float(result.get("p", price)),
                    "volume": int(result.get("v", 0) or 0),
                    "change": float(result.get("ch", 0)),
                    "percent_change": float(result.get("chp", 0)),
                    "timestamp": result.get("t", ""),
                }
        except Exception as e:
            print(f"iTick quote request failed for {symbol}: {e}")
            return None

    # ------------------------------------------------------------------
    # 股票K线（单只）
    # ------------------------------------------------------------------
    @staticmethod
    def get_kline(symbol: str, interval: str = "1m", limit: int = 100) -> list[dict]:
        ktype_map = {
            "1m": 1,
            "5m": 2,
            "15m": 3,
            "30m": 4,
            "1h": 5,
            "1d": 8,
        }
        ktype = ktype_map.get(interval, 1)

        try:
            region, code = ITickClient._parse_symbol(symbol)
            url = f"{ITickClient.BASE_URL}/stock/kline"
            params = {
                "region": region.upper(),
                "code": code,
                "kType": ktype,
                "limit": limit,
            }

            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    url,
                    params=params,
                    headers=ITickClient._get_headers()
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") != 0:
                    print(f"iTick kline error for {symbol}: {data.get('msg')}")
                    return []

                items = data.get("data", [])
                if not isinstance(items, list):
                    return []

                candles = []
                for item in items:
                    candles.append({
                        "timestamp": item.get("t", ""),
                        "open": float(item.get("o", 0)),
                        "high": float(item.get("h", 0)),
                        "low": float(item.get("l", 0)),
                        "close": float(item.get("c", 0)),
                        "volume": int(item.get("v", 0) or 0),
                    })
                candles.sort(key=lambda x: x["timestamp"])
                return candles
        except Exception as e:
            print(f"iTick kline request failed for {symbol}: {e}")
            return []

    # ------------------------------------------------------------------
    # 批量股票报价（最多10只）
    # ------------------------------------------------------------------
    @staticmethod
    def get_batch_quotes(symbols: list[str]) -> dict[str, dict]:
        """
        Fetch quotes for up to 10 symbols per batch.
        Official endpoint: /stock/quotes
        """
        if not symbols:
            return {}

        batches = {}
        for sym in symbols:
            region, code = ITickClient._parse_symbol(sym)
            region = region.upper()
            if region not in batches:
                batches[region] = []
            batches[region].append((sym, code))

        all_results = {}
        for region, sym_codes in batches.items():
            for i in range(0, len(sym_codes), 10):
                chunk = sym_codes[i:i+10]
                codes = [c for _, c in chunk]
                params = {
                    "region": region,
                    "codes": ",".join(codes),
                }
                try:
                    url = f"{ITickClient.BASE_URL}/stock/quotes"
                    with httpx.Client(timeout=15.0) as client:
                        response = client.get(url, params=params, headers=ITickClient._get_headers())
                        response.raise_for_status()
                        data = response.json()
                        if data.get("code") != 0:
                            print(f"iTick batch quote error: {data.get('msg')}")
                            continue
                        # Response: data is a dict keyed by symbol code
                        for code, item in data.get("data", {}).items():
                            original = next((sym for sym, c in chunk if c == code), code)
                            all_results[original] = {
                                "price": float(item.get("ld", 0)),
                                "open": float(item.get("o", 0)),
                                "high": float(item.get("h", 0)),
                                "low": float(item.get("l", 0)),
                                "previous_close": float(item.get("p", 0)),
                                "volume": int(item.get("v", 0) or 0),
                                "change": float(item.get("ch", 0)),
                                "percent_change": float(item.get("chp", 0)),
                            }
                except Exception as e:
                    print(f"iTick batch quote failed for region {region}: {e}")
        return all_results

    # ------------------------------------------------------------------
    # 批量股票K线（最多10只）
    # ------------------------------------------------------------------
    @staticmethod
    def get_batch_klines(symbols: list[str], interval: str = "5m", limit: int = 50) -> dict[str, list[dict]]:
        """
        Fetch klines for up to 10 symbols per batch.
        Official endpoint: /stock/klines
        """
        if not symbols:
            return {}

        ktype_map = {"1m": 1, "5m": 2, "15m": 3, "30m": 4, "1h": 5, "1d": 8}
        ktype = ktype_map.get(interval, 2)

        batches = {}
        for sym in symbols:
            region, code = ITickClient._parse_symbol(sym)
            region = region.upper()
            if region not in batches:
                batches[region] = []
            batches[region].append((sym, code))

        all_results = {}
        for region, sym_codes in batches.items():
            for i in range(0, len(sym_codes), 10):
                chunk = sym_codes[i:i+10]
                codes = [c for _, c in chunk]
                params = {
                    "region": region,
                    "codes": ",".join(codes),
                    "kType": ktype,
                    "limit": limit,
                }
                try:
                    url = f"{ITickClient.BASE_URL}/stock/klines"
                    with httpx.Client(timeout=20.0) as client:
                        response = client.get(url, params=params, headers=ITickClient._get_headers())
                        response.raise_for_status()
                        data = response.json()
                        if data.get("code") != 0:
                            print(f"iTick batch kline error: {data.get('msg')}")
                            continue
                        # Response: data is a dict keyed by symbol code
                        for code, klines in data.get("data", {}).items():
                            original = next((sym for sym, c in chunk if c == code), code)
                            candles = []
                            for k in klines:
                                candles.append({
                                    "timestamp": k.get("t", ""),
                                    "open": float(k.get("o", 0)),
                                    "high": float(k.get("h", 0)),
                                    "low": float(k.get("l", 0)),
                                    "close": float(k.get("c", 0)),
                                    "volume": int(k.get("v", 0) or 0),
                                })
                            all_results[original] = candles
                except Exception as e:
                    print(f"iTick batch kline failed for region {region}: {e}")
        return all_results

    # ------------------------------------------------------------------
    # 单只指数报价
    # ------------------------------------------------------------------
    @staticmethod
    def get_index_quote(code: str) -> Optional[dict]:
        try:
            url = f"{ITickClient.BASE_URL}/indices/quote"
            params = {
                "region": "GB",
                "code": code,
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params, headers=ITickClient._get_headers())
                response.raise_for_status()
                data = response.json()

                if data.get("code") != 0:
                    print(f"iTick index quote error for {code}: {data.get('msg')}")
                    return None

                result = data.get("data", {})
                if not result:
                    return None

                return {
                    "symbol": code,
                    "price": float(result.get("ld", 0)),
                    "open": float(result.get("o", 0)),
                    "high": float(result.get("h", 0)),
                    "low": float(result.get("l", 0)),
                    "previous_close": float(result.get("p", 0)),
                    "change": float(result.get("ch", 0)),
                    "percent_change": float(result.get("chp", 0)),
                    "timestamp": result.get("t", ""),
                }
        except Exception as e:
            print(f"iTick index quote request failed for {code}: {e}")
            return None

    # ------------------------------------------------------------------
    # 批量指数报价
    # ------------------------------------------------------------------
    @staticmethod
    def get_batch_index_quotes(codes: list[str]) -> dict[str, dict]:
        """
        Fetch quotes for multiple indices in one batch request.
        Official endpoint: /indices/quotes
        """
        if not codes:
            return {}

        try:
            url = f"{ITickClient.BASE_URL}/indices/quotes"
            params = {
                "region": "GB",
                "codes": ",".join(codes),
            }

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params, headers=ITickClient._get_headers())
                response.raise_for_status()
                data = response.json()

                if data.get("code") != 0:
                    print(f"iTick batch index quote error: {data.get('msg')}")
                    return {}

                result = {}
                # Response: data is a dict keyed by index code
                for code, item in data.get("data", {}).items():
                    result[code] = {
                        "price": float(item.get("ld", 0)),
                        "open": float(item.get("o", 0)),
                        "high": float(item.get("h", 0)),
                        "low": float(item.get("l", 0)),
                        "previous_close": float(item.get("p", 0)),
                        "change": float(item.get("ch", 0)),
                        "percent_change": float(item.get("chp", 0)),
                        "timestamp": item.get("t", ""),
                    }
                return result
        except Exception as e:
            print(f"iTick batch index quote request failed: {e}")
            return {}