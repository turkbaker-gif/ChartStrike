from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal, AIReview
from app.db.session import get_db
from app.services.tracking.signal_status_service import SignalStatusService

router = APIRouter()


@router.get("/signals/{signal_id}/full-analysis")
def get_full_analysis(signal_id: str, db: Session = Depends(get_db)):
    signal = db.execute(
        select(Signal).where(Signal.id == signal_id)
    ).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    ai_review = db.execute(
        select(AIReview).where(AIReview.signal_id == signal_id)
    ).scalar_one_or_none()

    live_status = SignalStatusService.build_status(db, signal)

    signal_payload = {
        "id": signal.id,
        "symbol": signal.symbol,
        "pattern_name": signal.pattern_name,
        "timeframe": signal.timeframe,
        "confidence": signal.confidence,
        "signal_state": signal.signal_state,
        "trigger_price": float(signal.trigger_price)
        if signal.trigger_price is not None
        else None,
        "entry_low": float(signal.entry_low) if signal.entry_low is not None else None,
        "entry_high": float(signal.entry_high) if signal.entry_high is not None else None,
        "stop_price": float(signal.stop_price)
        if signal.stop_price is not None
        else None,
        "target_1": float(signal.target_1) if signal.target_1 is not None else None,
        "target_2": float(signal.target_2) if signal.target_2 is not None else None,
        "live_status": live_status,
    }

    ai_review_payload = None
    if ai_review:
        ai_review_payload = {
            "verdict": ai_review.verdict,
            "setup_quality": ai_review.setup_quality,
            "analysis": ai_review.analysis,
            "key_risks": ai_review.key_risks or [],
            "what_to_wait_for": ai_review.what_to_wait_for or [],
        }

    return {
        "signal": signal_payload,
        "explanation": "Signal explanation placeholder",
        "ai_review": ai_review_payload,
        "research": None,
    }