from pydantic import BaseModel
from app.schemas.simulated_trade import SimulatedTradeOut


class TradeDashboardSummaryOut(BaseModel):
    total_trades: int
    open_trades: int
    closed_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    average_r: float | None = None


class TradeDashboardOut(BaseModel):
    summary: TradeDashboardSummaryOut
    open_trades: list[SimulatedTradeOut]
    closed_trades: list[SimulatedTradeOut]