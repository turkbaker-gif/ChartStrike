from pydantic import BaseModel


class PortfolioRiskOut(BaseModel):
    account_size: float
    max_portfolio_risk_percent: float
    current_open_risk_amount: float
    current_open_risk_percent: float
    remaining_risk_amount: float
    remaining_risk_percent: float
    open_trade_count: int
    within_limit: bool