from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal, SimulatedTrade
from app.services.tracking.trade_plan_service import TradePlanService
from app.services.portfolio.portfolio_risk_service import PortfolioRiskService


class SimulatedTradeService:
    @staticmethod
    def get_by_id(db: Session, trade_id: str) -> SimulatedTrade | None:
        stmt = select(SimulatedTrade).where(SimulatedTrade.id == trade_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_by_signal_id(db: Session, signal_id: str) -> SimulatedTrade | None:
        stmt = select(SimulatedTrade).where(SimulatedTrade.signal_id == signal_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_all(db: Session) -> list[SimulatedTrade]:
        stmt = select(SimulatedTrade).order_by(SimulatedTrade.created_at.desc())
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def list_open_trades(db: Session) -> list[SimulatedTrade]:
        stmt = (
            select(SimulatedTrade)
            .where(SimulatedTrade.status == "open")
            .order_by(SimulatedTrade.created_at.desc())
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create_from_signal(
        db: Session,
        signal: Signal,
        account_size: float,
        risk_percent: float,
        max_portfolio_risk_percent: float,
    ) -> SimulatedTrade:
        existing_trade = SimulatedTradeService.get_by_signal_id(db, signal.id)
        if existing_trade:
            raise ValueError("A simulated trade already exists for this signal")

        trade_plan = TradePlanService.build_trade_plan(
            signal=signal,
            account_size=account_size,
            risk_percent=risk_percent,
        )

        risk_check = PortfolioRiskService.can_open_trade(
            db=db,
            account_size=account_size,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            new_trade_risk_amount=trade_plan["risk_amount"],
        )

        if not risk_check["allowed"]:
            raise ValueError(
                "Opening this trade would exceed your max portfolio risk limit"
            )

        trade = SimulatedTrade(
            signal_id=signal.id,
            symbol=signal.symbol,
            status="open",
            outcome="open",
            entry_price=trade_plan["entry_price"],
            stop_price=trade_plan["stop_price"],
            target_1=trade_plan["target_1"],
            target_2=trade_plan["target_2"],
            position_size_shares=trade_plan["position_size_shares"],
            risk_amount=trade_plan["risk_amount"],
            opened_at=datetime.utcnow(),
        )

        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def close_trade(
        db: Session,
        trade: SimulatedTrade,
        exit_price: float,
        outcome: str,
        status: str,
    ) -> SimulatedTrade:
        entry_price = float(trade.entry_price)
        shares = int(trade.position_size_shares)
        risk_amount = float(trade.risk_amount)

        pnl_amount = (exit_price - entry_price) * shares
        pnl_r_multiple = pnl_amount / risk_amount if risk_amount > 0 else None

        trade.exit_price = exit_price
        trade.outcome = outcome
        trade.status = status
        trade.closed_at = datetime.utcnow()
        trade.pnl_amount = round(pnl_amount, 2)
        trade.pnl_r_multiple = round(pnl_r_multiple, 2) if pnl_r_multiple is not None else None
        trade.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def to_dict(trade: SimulatedTrade) -> dict:
        return {
            "id": trade.id,
            "signal_id": trade.signal_id,
            "symbol": trade.symbol,
            "status": trade.status,
            "outcome": trade.outcome,
            "entry_price": float(trade.entry_price),
            "stop_price": float(trade.stop_price),
            "target_1": float(trade.target_1) if trade.target_1 is not None else None,
            "target_2": float(trade.target_2) if trade.target_2 is not None else None,
            "position_size_shares": trade.position_size_shares,
            "risk_amount": float(trade.risk_amount),
            "opened_at": trade.opened_at,
            "closed_at": trade.closed_at,
            "exit_price": float(trade.exit_price) if trade.exit_price is not None else None,
            "pnl_amount": float(trade.pnl_amount) if trade.pnl_amount is not None else None,
            "pnl_r_multiple": float(trade.pnl_r_multiple) if trade.pnl_r_multiple is not None else None,
        }