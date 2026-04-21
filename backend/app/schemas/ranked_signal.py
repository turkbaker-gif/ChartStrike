from pydantic import BaseModel


class RankedSignalOut(BaseModel):
    id: str
    symbol: str
    pattern_name: str
    score: float
    verdict: str
    reason: str