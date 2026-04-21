from pydantic import BaseModel


class AIReviewOut(BaseModel):
    signal_id: str
    symbol: str
    pattern_name: str
    verdict: str
    setup_quality: str
    analysis: str
    key_risks: list[str]
    what_to_wait_for: list[str]