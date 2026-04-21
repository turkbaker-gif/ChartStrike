from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal, AIReview
from app.db.session import get_db
from app.services.checklist.trade_checklist_service import TradeChecklistService
from app.schemas.trade_checklist import TradeChecklistOut

router = APIRouter()


@router.get("/signals/{signal_id}/checklist", response_model=TradeChecklistOut)
def get_trade_checklist(signal_id: str, db: Session = Depends(get_db)):
    signal = db.execute(
        select(Signal).where(Signal.id == signal_id)
    ).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    ai_review = db.execute(
        select(AIReview).where(AIReview.signal_id == signal_id)
    ).scalar_one_or_none()

    return TradeChecklistService.build(
        signal=signal,
        ai_review=ai_review,
        db=db,
        account_size=10000,
        risk_percent=1,
        max_portfolio_risk_percent=6,
    )