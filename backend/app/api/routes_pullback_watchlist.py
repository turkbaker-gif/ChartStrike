from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.hk_patterns.hk_continuation_signal_service import HKContinuationSignalService
from app.services.market.itick_client import ITickClient

router = APIRouter()

@router.get("/pullback-watchlist")
def get_pullback_watchlist(db: Session = Depends(get_db)):
    # Get all HK + CN symbols
    query = text("""
        SELECT DISTINCT symbol FROM stock_prices
        WHERE symbol LIKE '%.HK' OR symbol LIKE '%.SH' OR symbol LIKE '%.SZ'
        ORDER BY symbol
    """)
    result = db.execute(query)
    symbols = [row[0] for row in result.fetchall()]

    pullback_stocks = []

    for symbol in symbols:
        # Get quote to check gain
        quote = ITickClient.get_quote(symbol)
        if not quote:
            continue

        prev_close = quote.get("previous_close", 0)
        last_price = quote.get("price", 0)
        if prev_close <= 0:
            continue

        percent_change = ((last_price - prev_close) / prev_close) * 100
        if percent_change < 3.0:
            continue

        # Get intraday candles for pullback detection
        candles = ITickClient.get_kline(symbol, interval="5m", limit=50)
        if not candles:
            continue

        formatted = [{"high": c["high"], "low": c["low"], "close": c["close"], "volume": c["volume"]} for c in candles]
        signal = HKContinuationSignalService.build_signal(symbol, formatted)

        # Include if in pullback_detected or rebound_started stage
        if signal.get("stage") in ("pullback_detected", "rebound_started"):
            pullback_stocks.append({
                "symbol": symbol,
                "percent_change": round(percent_change, 2),
                "stage": signal.get("stage"),
                "pullback_percent": signal.get("pullback_percent"),
                "trigger_price": signal.get("trigger_price"),
                "reason": signal.get("reason"),
            })

    return {"count": len(pullback_stocks), "watchlist": pullback_stocks}