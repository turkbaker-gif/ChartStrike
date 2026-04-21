from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.hk_patterns.hk_continuation_signal_service import (
    HKContinuationSignalService,
)
from app.services.hk_patterns.hk_dynamic_watchlist_service import (
    HKDynamicWatchlistService,
)
from app.services.market.data_service import LocalDataService

router = APIRouter()


@router.post("/scan")
def run_scan(db: Session = Depends(get_db)):
    # Build the dynamic HK watchlist (stocks with strong daily gain)
    hk_watchlist = HKDynamicWatchlistService.build_preopen_watchlist(
        db=db,
        min_percent_gain=5.0,
    )

    results = []

    for item in hk_watchlist:
        symbol = item["symbol"]

        # Fetch recent candles for pullback/continuation analysis
        candles = LocalDataService.get_recent_candles(db, symbol, limit=30)

        hk_signal = HKContinuationSignalService.build_signal(symbol, candles)

        results.append({
            "symbol": symbol,
            "percent_change": item.get("percent_change"),
            "stage": hk_signal.get("stage"),
            "reason": hk_signal.get("reason"),
            "trigger_price": hk_signal.get("trigger_price"),
            "pullback_percent": hk_signal.get("pullback_percent"),
            "confidence_boost": hk_signal.get("confidence_boost", 0),
        })

    return {
        "watchlist_count": len(hk_watchlist),
        "watchlist": hk_watchlist,
        "results": results,
    }