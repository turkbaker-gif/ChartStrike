import httpx
from typing import List, Dict

class EastMoneyClient:
    BASE_URL = "https://push2.eastmoney.com/api/qt/stock/get"

    @staticmethod
    def get_company_news(symbol: str, limit: int = 10) -> List[Dict]:
        """
        Fetch news from East Money for a given stock symbol.
        Symbol format: e.g., "0700" (Tencent), "9988" (Alibaba).
        """
        # Remove .HK suffix
        code = symbol.replace(".HK", "")
        params = {
            "secid": f"1.{code}",  # 1 for Shanghai/HK? Actually for HK use "116.{code}"? We'll use dynamic detection.
            "fields": "title,date,url,summary",
            "num": limit,
        }
        # For HK stocks, East Money uses "116.{code}" (where 116 is HK market code)
        if symbol.endswith(".HK"):
            params["secid"] = f"116.{code}"
        else:
            params["secid"] = f"1.{code}"   # for A-shares, but we focus on HK now

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get("https://np-api.eastmoney.com/stock/news", params=params)
                if response.status_code != 200:
                    return []
                data = response.json()
        except Exception:
            return []

        items = data.get("data", {}).get("list", [])
        return [
            {
                "headline": item.get("title", ""),
                "source": "East Money",
                "published_at": item.get("date", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", ""),
            }
            for item in items
        ]