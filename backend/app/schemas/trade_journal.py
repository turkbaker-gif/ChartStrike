from datetime import datetime
from pydantic import BaseModel


class TradeJournalOut(BaseModel):
    signal_id: str
    symbol: str
    decision: str | None = None
    outcome: str | None = None
    notes: str | None = None
    lesson: str | None = None
    updated_at: datetime | None = None


class TradeJournalUpdateIn(BaseModel):
    decision: str | None = None
    outcome: str | None = None
    notes: str | None = None
    lesson: str | None = None