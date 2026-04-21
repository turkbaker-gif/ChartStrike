from sqlalchemy import select

from app.db.models import SimulatedTrade


class PortfolioRiskService:
    @staticmethod
    def build_portfolio_risk(
        db,
        account_size: float,
        max_portfolio_risk_percent: float,
    ) -> dict:
        open_trades = list(
            db.execute(
                select(SimulatedTrade).where(SimulatedTrade.status == "open")
            ).scalars().all()
        )

        current_open_risk_amount = sum(float(t.risk_amount or 0) for t in open_trades)
        current_open_risk_percent = (
            (current_open_risk_amount / account_size) * 100 if account_size > 0 else 0
        )

        max_risk_amount = account_size * (max_portfolio_risk_percent / 100)
        remaining_risk_amount = max_risk_amount - current_open_risk_amount
        remaining_risk_percent = (
            (remaining_risk_amount / account_size) * 100 if account_size > 0 else 0
        )

        return {
            "account_size": round(account_size, 2),
            "max_portfolio_risk_percent": round(max_portfolio_risk_percent, 2),
            "current_open_risk_amount": round(current_open_risk_amount, 2),
            "current_open_risk_percent": round(current_open_risk_percent, 2),
            "remaining_risk_amount": round(remaining_risk_amount, 2),
            "remaining_risk_percent": round(remaining_risk_percent, 2),
            "open_trade_count": len(open_trades),
            "within_limit": current_open_risk_amount <= max_risk_amount,
        }

    @staticmethod
    def can_open_trade(
        db,
        account_size: float,
        max_portfolio_risk_percent: float,
        new_trade_risk_amount: float,
    ) -> dict:
        portfolio = PortfolioRiskService.build_portfolio_risk(
            db=db,
            account_size=account_size,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
        )

        projected_open_risk_amount = portfolio["current_open_risk_amount"] + new_trade_risk_amount
        max_risk_amount = account_size * (max_portfolio_risk_percent / 100)

        allowed = projected_open_risk_amount <= max_risk_amount

        return {
            "allowed": allowed,
            "projected_open_risk_amount": round(projected_open_risk_amount, 2),
            "max_risk_amount": round(max_risk_amount, 2),
        }