from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.services.research.catalyst_service import CatalystService
from app.services.intelligence.signal_intelligence import SignalIntelligence
from app.services.tracking.trade_plan_service import TradePlanService

router = APIRouter()


@router.get("/signals/{signal_id}/intelligence")
def get_signal_intelligence(signal_id: str, db: Session = Depends(get_db)):
    signal = db.execute(
        select(Signal).where(Signal.id == signal_id)
    ).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    trade_plan = TradePlanService.build_trade_plan(
        signal=signal,
        account_size=10000,
        risk_percent=1,
    )

    catalyst = CatalystService.build(signal.symbol)

    intelligence = SignalIntelligence.build(
        signal=signal,
        trade_plan=trade_plan,
        catalyst=catalyst,
    )

    return intelligence