from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.candle import CandleOut

router = APIRouter()


@router.get("/signals/{signal_id}/candles", response_model=list[CandleOut])
def get_signal_candles(
    signal_id: str,
    limit: int = Query(default=50, ge=10, le=500),
    db: Session = Depends(get_db),
):
    # Get the signal
    signal = db.get(Signal, signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    # Query stock_prices table directly (no timeframe column)
    query = text("""
        SELECT date as ts, open, high, low, close, volume
        FROM stock_prices
        WHERE symbol = :symbol
        ORDER BY date DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"symbol": signal.symbol, "limit": limit})
    rows = result.fetchall()

    # Convert to expected format and reverse for chronological order
    candles = []
    for row in reversed(rows):
        candles.append({
            "ts": row[0],  # date column aliased as ts
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": int(row[5]) if row[5] else 0,
        })

    return candles