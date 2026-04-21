from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.signal_status import SignalStatusOut
from app.services.tracking.signal_status_service import SignalStatusService

router = APIRouter()


@router.get("/signals/{signal_id}/status", response_model=SignalStatusOut)
def get_signal_status(signal_id: str, db: Session = Depends(get_db)):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    status_data = SignalStatusService.build_status(db, signal)

    # Add required fields for the response schema
    return {
        "signal_id": signal.id,
        "symbol": signal.symbol,
        **status_data,
    }