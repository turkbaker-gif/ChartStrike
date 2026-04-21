from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.signal import SignalOut

router = APIRouter()


@router.get("/signals", response_model=list[SignalOut])
def list_signals(db: Session = Depends(get_db)):
    stmt = select(Signal).order_by(Signal.detected_at.desc())
    return list(db.execute(stmt).scalars().all())


@router.get("/signals/{signal_id}", response_model=SignalOut)
def get_signal(signal_id: str, db: Session = Depends(get_db)):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    return signal