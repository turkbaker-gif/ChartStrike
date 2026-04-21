from pydantic import BaseModel


class SignalStatusOut(BaseModel):
    signal_id: str
    symbol: str
    latest_price: float | None
    status: str
    distance_to_entry_pct: float | None = None
    distance_to_stop_pct: float | None = None
    distance_to_target_1_pct: float | None = None
    distance_to_target_2_pct: float | None = None
    summary: str