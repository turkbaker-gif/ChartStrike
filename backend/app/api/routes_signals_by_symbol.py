from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db

router = APIRouter()


@router.get("/signals/by-symbol/{symbol}")
def get_signals_by_symbol(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get the most recent signals for a given stock symbol.
    """
    stmt = (
        select(Signal)
        .where(Signal.symbol == symbol)
        .order_by(Signal.detected_at.desc())
        .limit(limit)
    )
    signals = db.execute(stmt).scalars().all()

    if not signals:
        raise HTTPException(status_code=404, detail=f"No signals found for {symbol}")

    return [
        {
            "id": s.id,
            "symbol": s.symbol,
            "pattern_name": s.pattern_name,
            "timeframe": s.timeframe,
            "detected_at": s.detected_at.isoformat(),
            "trigger_price": float(s.trigger_price) if s.trigger_price else None,
            "entry_low": float(s.entry_low) if s.entry_low else None,
            "entry_high": float(s.entry_high) if s.entry_high else None,
            "stop_price": float(s.stop_price) if s.stop_price else None,
            "target_1": float(s.target_1) if s.target_1 else None,
            "target_2": float(s.target_2) if s.target_2 else None,
            "confidence": float(s.confidence) if s.confidence else None,
            "signal_state": s.signal_state,
        }
        for s in signals
    ]