import json
from openai import OpenAI

from app.core.config import settings


class AIClient:
    def __init__(self) -> None:
        # Use DeepSeek if configured, otherwise fall back to OpenAI
        if settings.deepseek_api_key:
            self.client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            self.model = settings.deepseek_model
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model

    def review_signal(self, prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a cautious trading signal reviewer. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        text = response.choices[0].message.content
        if not text:
            raise ValueError("AI returned empty output")

        # Strip markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI JSON output: {text}") from e