from sqlalchemy.orm import Session
from app.db.models import Signal, RealTrade
from app.services.tracking.trade_plan_service import TradePlanService

class RealTradeService:
    @staticmethod
    def create_from_signal(db: Session, signal: Signal, account_size: float, risk_percent: float) -> RealTrade:
        # Reuse trade plan logic
        plan = TradePlanService.build_trade_plan(signal, account_size, risk_percent)
        
        trade = RealTrade(
            signal_id=signal.id,
            symbol=signal.symbol,
            entry_price=plan["entry_price"],
            stop_price=plan["stop_price"],
            target_1=plan["target_1"],
            target_2=plan["target_2"],
            position_size_shares=plan["position_size_shares"],
            risk_amount=plan["risk_amount"],
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def list_all(db: Session) -> list[RealTrade]:
        return db.query(RealTrade).order_by(RealTrade.opened_at.desc()).all()