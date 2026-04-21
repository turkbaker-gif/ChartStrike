from pydantic import BaseModel


class NewsItemOut(BaseModel):
    headline: str
    source: str
    published_at: str
    url: str
    summary: str | None = None


class CatalystOut(BaseModel):
    symbol: str
    provider_symbol: str
    catalyst_type: str
    summary: str
    confidence: str
    headline_count: int
    ai_interpretation: str | None = None
    headlines: list[NewsItemOut]