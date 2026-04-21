import time
from app.core.config import settings
from app.services.news.eastmoney_client import EastMoneyClient
from app.services.news.google_news_rss_client import GoogleNewsRSSClient   # optional fallback
from app.services.news.hkex_rss_client import HKEXRSSClient   # you already have this

class NewsService:
    _cache = {}
    _cache_ttl = 60

    @staticmethod
    def map_symbol_for_news(symbol: str) -> str:
        # Keep mapping logic (maybe use ticker only)
        return symbol.replace(".HK", "")

    @staticmethod
    def get_recent_news(symbol: str) -> tuple[str, list[dict]]:
        provider_symbol = NewsService.map_symbol_for_news(symbol)
        cache_key = provider_symbol
        now = time.time()

        cached = NewsService._cache.get(cache_key)
        if cached and (now - cached["ts"] < NewsService._cache_ttl):
            return provider_symbol, cached["data"]

        # Try East Money first
        headlines = EastMoneyClient.get_company_news(symbol)
        if headlines:
            normalized = headlines[:10]
            NewsService._cache[cache_key] = {"ts": now, "data": normalized}
            return provider_symbol, normalized

        # Fallback to HKEX RSS
        from app.services.news.hkex_rss_client import HKEXRSSClient
        headlines = HKEXRSSClient.get_announcements(symbol)
        if headlines:
            normalized = headlines[:10]
            NewsService._cache[cache_key] = {"ts": now, "data": normalized}
            return provider_symbol, normalized

        # Fallback to Google News RSS (if still allowed)
        headlines = GoogleNewsRSSClient.get_search_results(provider_symbol, when="7d", limit=10)
        normalized = [
            {
                "headline": item.get("title", ""),
                "source": item.get("source", "Google News"),
                "published_at": item.get("published_at", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary"),
            }
            for item in headlines
        ]
        NewsService._cache[cache_key] = {"ts": now, "data": normalized}
        return provider_symbol, normalized