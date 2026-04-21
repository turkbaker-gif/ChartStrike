import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str
    watchlist_symbols: str = ""  # fallback if DB is empty

    eodhd_api_key: str | None = None
    eodhd_interval: str = "1m"
    eodhd_outputsize: int = 30
    market_poll_seconds: int = 60

    # OpenAI is now optional (we use DeepSeek)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    # DeepSeek settings
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    autopilot_scan_seconds: int = 60

    itick_api_token: str | None = None

    news_lookback_days: int = 3
    gdelt_timespan: str = "7d"
    symbol_news_map_raw: str | None = None
    
    hk_preopen_min_gain: float = 3.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def watchlist(self) -> list[str]:
        return [s.strip() for s in self.watchlist_symbols.split(",") if s.strip()]

    @property
    def symbol_news_map(self) -> dict:
        if not self.symbol_news_map_raw:
            return {}
        try:
            return json.loads(self.symbol_news_map_raw)
        except Exception:
            return {}


settings = Settings()