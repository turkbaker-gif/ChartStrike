from pydantic import BaseModel


class ResearchOut(BaseModel):
    signal_id: str
    symbol: str
    research_summary: str
    catalyst_type: str
    key_drivers: list[str]
    evidence: list[str]
    next_checks: list[str]