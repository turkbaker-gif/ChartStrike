from datetime import datetime
from pydantic import BaseModel


class SimulatedTradeOut(BaseModel):
    id: str
    signal_id: str
    symbol: str
    status: str
    outcome: str | None = None
    entry_price: float
    stop_price: float
    target_1: float | None = None
    target_2: float | None = None
    position_size_shares: int
    risk_amount: float
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    exit_price: float | None = None
    pnl_amount: float | None = None
    pnl_r_multiple: float | None = None

    class Config:
        from_attributes = True


class CreateSimulatedTradeIn(BaseModel):
    account_size: float
    risk_percent: float
    max_portfolio_risk_percent: float