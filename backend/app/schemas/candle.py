from datetime import datetime
from pydantic import BaseModel


class CandleOut(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float

    class Config:
        from_attributes = True