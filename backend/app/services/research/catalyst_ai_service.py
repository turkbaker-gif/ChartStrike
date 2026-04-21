from openai import OpenAI
from app.core.config import settings


class CatalystAIService:
    @staticmethod
    def build_interpretation(
        symbol: str,
        catalyst_type: str,
        confidence: str,
        headlines: list[dict],
        pattern_context: str | None = None,
    ) -> str | None:
        if not settings.deepseek_api_key:
            return None

        if not headlines:
            return (
                f"No external headlines were available for {symbol}, so there is not "
                "enough evidence to form a strong catalyst view."
            )

        headline_text = "\n".join(
            [
                f"- {item.get('headline', '')} | {item.get('source', '')} | {item.get('summary', '') or ''}"
                for item in headlines[:8]
            ]
        )

        context_line = ""
        if pattern_context:
            context_line = f"\nPattern context: {pattern_context}\n"

        prompt = f"""
You are an equity trading research assistant.

Stock: {symbol}
Detected catalyst type: {catalyst_type}
Confidence: {confidence}
{context_line}
Recent headlines:
{headline_text}

Task:
Write a short, practical interpretation for a trader.

Requirements:
- Explain what may be driving the stock
- Mention whether the move appears company-specific, sector-driven, macro-driven, or unclear
- Keep it concise and useful
- Use plain English
- Maximum 90 words
"""

        try:
            client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": "You are an equity research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Catalyst AI interpretation failed: {e}")
            return None