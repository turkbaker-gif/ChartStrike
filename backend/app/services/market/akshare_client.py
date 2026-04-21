import akshare as ak
import pandas as pd


class AkShareClient:
    @staticmethod
    def get_realtime_quote(symbol: str) -> dict | None:
        """
        symbol: e.g., '600036' (Shanghai) or '000858' (Shenzhen)
        Returns normalized quote dict or None.
        """
        try:
            df = ak.stock_zh_a_spot_em()  # real-time snapshot of all A-shares
        except Exception as e:
            print(f"AkShare spot request failed: {e}")
            return None

        row = df[df["代码"] == symbol]
        if row.empty:
            return None

        row = row.iloc[0]
        return {
            "symbol": symbol,
            "price": float(row["最新价"]),
            "open": float(row["今开"]),
            "high": float(row["最高"]),
            "low": float(row["最低"]),
            "previous_close": float(row["昨收"]),
            "change": float(row["涨跌额"]),
            "percent_change": float(row["涨跌幅"]),
            "volume": float(row["成交量"]),
            "currency": "CNY",
            "exchange": "SHSE" if symbol.startswith("6") else "SZSE",
        }

    @staticmethod
    def get_time_series(symbol: str, period: str = "daily", adjust: str = "") -> list[dict]:
        """
        Fetch historical daily data (intraday not free/easy).
        Returns list of candle dicts with 'datetime', 'open', 'high', 'low', 'close', 'volume'.
        """
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date="20240101",
                end_date="20500101",
                adjust=adjust,
            )
        except Exception as e:
            print(f"AkShare history request failed for {symbol}: {e}")
            return []

        if df.empty:
            return []

        candles = []
        for _, row in df.iterrows():
            candles.append({
                "datetime": row["日期"].strftime("%Y-%m-%d"),
                "open": float(row["开盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "close": float(row["收盘"]),
                "volume": float(row["成交量"]),
            })
        return candles