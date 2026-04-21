from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.trade_journal import TradeJournalOut, TradeJournalUpdateIn
from app.services.tracking.trade_journal_service import TradeJournalService

router = APIRouter()


@router.get("/signals/{signal_id}/journal", response_model=TradeJournalOut | None)
def get_trade_journal(signal_id: str, db: Session = Depends(get_db)):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    journal = TradeJournalService.get_by_signal_id(db, signal_id)
    data = TradeJournalService.to_dict(journal)
    return data


@router.post("/signals/{signal_id}/journal", response_model=TradeJournalOut)
def save_trade_journal(
    signal_id: str,
    payload: TradeJournalUpdateIn,
    db: Session = Depends(get_db),
):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    journal = TradeJournalService.upsert(
        db=db,
        signal=signal,
        payload=payload.model_dump(),
    )

    return TradeJournalService.to_dict(journal)