from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.news import CatalystOut
from app.services.research.catalyst_service import CatalystService

router = APIRouter()


@router.get("/signals/{signal_id}/catalyst", response_model=CatalystOut)
def get_signal_catalyst(signal_id: str, db: Session = Depends(get_db)):
    signal = db.execute(
        select(Signal).where(Signal.id == signal_id)
    ).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    pattern_context = {
        "pattern_name": signal.pattern_name,
        # You could enrich with more data if available, e.g., pullback_percent from a service.
    }

    return CatalystService.build(signal.symbol, pattern_context=pattern_context)