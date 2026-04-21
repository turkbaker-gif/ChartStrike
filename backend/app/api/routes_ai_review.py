from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.ai_review import AIReviewOut
from app.services.ai.ai_review_service import AIReviewService
from app.services.ai.ai_review_store import AIReviewStore

router = APIRouter()


@router.get("/signals/{signal_id}/ai-review", response_model=AIReviewOut)
def get_ai_review(signal_id: str, db: Session = Depends(get_db)):
    stored = AIReviewStore.get_by_signal_id(db, signal_id)
    if stored:
        return AIReviewStore.to_dict(stored)

    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    try:
        review = AIReviewService.review_signal(signal)
        AIReviewStore.create(db, review)
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))