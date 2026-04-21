from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.explanation import SignalExplanationOut
from app.services.explanations.explanation_service import ExplanationService

router = APIRouter()


@router.get("/signals/{signal_id}/explanation", response_model=SignalExplanationOut)
def get_signal_explanation(signal_id: str, db: Session = Depends(get_db)):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    explanation = ExplanationService.build_signal_explanation(signal)
    return explanation