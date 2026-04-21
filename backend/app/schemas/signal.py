from datetime import datetime
from pydantic import BaseModel


class SignalOut(BaseModel):
    id: str
    symbol: str
    pattern_name: str
    timeframe: str
    detected_at: datetime
    trigger_price: float
    entry_low: float | None = None
    entry_high: float | None = None
    stop_price: float | None = None
    target_1: float | None = None
    target_2: float | None = None
    confidence: float | None = None
    signal_state: str
    context_summary: str | None = None

    class Config:
        from_attributes = True