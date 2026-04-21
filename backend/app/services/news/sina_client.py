import httpx
from typing import List, Dict

class SinaClient:
    @staticmethod
    def get_company_news(symbol: str, limit: int = 10) -> List[Dict]:
        code = symbol.replace(".HK", "")
        # Sina uses symbol like "hk0070"
        sina_symbol = f"hk{code}"
        url = f"https://finance.sina.com.cn/stock/stock_news/{sina_symbol}.shtml"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code != 200:
                    return []
                # Parse HTML – this is a placeholder; you'd need BeautifulSoup.
                # For now, we'll return empty; implement later with lxml.
                return []
        except Exception:
            return []