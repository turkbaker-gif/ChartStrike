import time
from fastapi import APIRouter
from app.services.news.gdelt_client import GDELTClient

router = APIRouter()

# Simple in-memory cache
_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 120  # seconds (2 minutes)
}


@router.get("/market-news")
def get_market_news(limit: int = 20):
    """
    Fetch market-moving business and geopolitical headlines with caching.
    """
    now = time.time()
    if _cache["data"] is not None and (now - _cache["timestamp"]) < _cache["ttl"]:
        return _cache["data"]

    query = '(business OR markets OR stocks OR economy OR "central bank" OR fed OR geopolitics OR war OR trade OR tariffs)'
    articles = GDELTClient.get_article_list(query=query, max_records=limit)

    result = []
    for art in articles:
        title = art.get("title", "").strip()
        if not title:
            continue
        result.append({
            "title": title,
            "source": art.get("source", {}).get("title", "Unknown") if isinstance(art.get("source"), dict) else art.get("domain", "Unknown"),
            "url": art.get("url", ""),
            "published_at": art.get("published", "") or art.get("seendate", ""),
            "summary": art.get("content", "")[:300] if art.get("content") else None,
        })

    response = {"articles": result[:limit]}
    _cache["data"] = response
    _cache["timestamp"] = now
    return response