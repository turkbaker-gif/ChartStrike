from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.trade_plan import TradePlanOut
from app.services.tracking.trade_plan_service import TradePlanService

router = APIRouter()


@router.get("/signals/{signal_id}/trade-plan", response_model=TradePlanOut)
def get_trade_plan(
    signal_id: str,
    account_size: float = Query(..., gt=0),
    risk_percent: float = Query(..., gt=0, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    try:
        return TradePlanService.build_trade_plan(
            signal=signal,
            account_size=account_size,
            risk_percent=risk_percent,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))