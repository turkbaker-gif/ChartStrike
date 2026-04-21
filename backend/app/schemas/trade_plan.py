from pydantic import BaseModel


class TradePlanOut(BaseModel):
    signal_id: str
    symbol: str
    account_size: float
    risk_percent: float
    risk_amount: float
    entry_price: float
    stop_price: float
    target_1: float | None = None
    target_2: float | None = None
    risk_per_share: float
    position_size_shares: int
    position_value: float
    max_loss: float
    reward_target_1: float | None = None
    reward_target_2: float | None = None
    rr_target_1: float | None = None
    rr_target_2: float | None = None