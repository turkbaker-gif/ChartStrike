from app.services.news.news_service import NewsService
from app.services.research.catalyst_ai_service import CatalystAIService


class CatalystService:
    COMPANY_KEYWORDS = [
        "earnings",
        "results",
        "revenue",
        "profit",
        "guidance",
        "buyback",
        "dividend",
        "acquisition",
        "merger",
        "partnership",
        "approval",
        "launch",
        "contract",
        "stake",
        "filing",
    ]

    MACRO_KEYWORDS = [
        "inflation",
        "rates",
        "interest rate",
        "central bank",
        "stimulus",
        "tariff",
        "policy",
        "gdp",
        "cpi",
        "yuan",
        "renminbi",
        "fed",
        "pbo",
    ]

    SECTOR_KEYWORDS = [
        "sector",
        "industry",
        "peers",
        "chip",
        "semiconductor",
        "tech",
        "property",
        "banking",
        "consumer",
        "internet",
        "ev",
        "ecommerce",
        "gaming",
    ]

    @staticmethod
    def classify_from_headlines(headlines: list[dict]) -> tuple[str, str]:
        if not headlines:
            return (
                "unclear",
                "No recent external headlines were found, so catalyst confidence is low.",
            )

        text_blob = " ".join(
            f"{h.get('headline', '')} {h.get('summary', '') or ''}".lower()
            for h in headlines
        )

        if any(keyword in text_blob for keyword in CatalystService.COMPANY_KEYWORDS):
            return (
                "company_news",
                "Recent headlines suggest a company-specific catalyst may be driving the move.",
            )

        if any(keyword in text_blob for keyword in CatalystService.MACRO_KEYWORDS):
            return (
                "macro",
                "Recent headlines suggest a broader macro driver may be influencing price action.",
            )

        if any(keyword in text_blob for keyword in CatalystService.SECTOR_KEYWORDS):
            return (
                "sector_news",
                "Recent headlines suggest a sector-wide theme may be contributing to the move.",
            )

        return (
            "technical_or_unclear",
            "Recent headlines do not clearly point to a strong company or macro catalyst.",
        )

    @staticmethod
    def confidence_from_count_and_type(
        headline_count: int,
        catalyst_type: str,
    ) -> str:
        if headline_count == 0:
            return "low"

        if headline_count >= 3 and catalyst_type in {
            "company_news",
            "macro",
            "sector_news",
        }:
            return "high"

        if headline_count >= 1:
            return "medium"

        return "low"

    @staticmethod
    def build(symbol: str, pattern_context: dict | None = None) -> dict:
        provider_symbol, headlines = NewsService.get_recent_news(symbol)

        catalyst_type, summary = CatalystService.classify_from_headlines(headlines)
        confidence = CatalystService.confidence_from_count_and_type(
            len(headlines),
            catalyst_type,
        )

        # Convert pattern_context dict to a readable string if provided
        context_str = None
        if pattern_context:
            context_str = f"Pattern: {pattern_context.get('pattern_name', 'unknown')}, "
            context_str += f"Stage: {pattern_context.get('stage', 'unknown')}, "
            context_str += f"Confidence Boost: {pattern_context.get('confidence_boost', 0)}"

        ai_interpretation = CatalystAIService.build_interpretation(
            symbol=symbol,
            catalyst_type=catalyst_type,
            confidence=confidence,
            headlines=headlines,
            pattern_context=context_str,
        )

        return {
            "symbol": symbol,
            "provider_symbol": provider_symbol,
            "catalyst_type": catalyst_type,
            "summary": summary,
            "confidence": confidence,
            "headline_count": len(headlines),
            "ai_interpretation": ai_interpretation,
            "headlines": headlines,
        }