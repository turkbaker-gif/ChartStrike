from pydantic import BaseModel


class SignalExplanationOut(BaseModel):
    signal_id: str
    symbol: str
    pattern_name: str
    summary: str
    strengths: list[str]
    risks: list[str]
    invalidation: list[str]
    trade_plan: list[str]