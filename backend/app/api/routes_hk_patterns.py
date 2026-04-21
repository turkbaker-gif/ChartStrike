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


@router.get("/hk/preopen-watchlist")
def get_hk_preopen_watchlist(db: Session = Depends(get_db)):
    watchlist = HKDynamicWatchlistService.build_preopen_watchlist(
        db,
        min_percent_gain=5.0,
    )

    enriched = []
    for item in watchlist:
        symbol = item["symbol"]
        candles = LocalDataService.get_recent_candles(db, symbol, limit=30)

        hk_signal = HKContinuationSignalService.build_signal(symbol, candles)

        enriched.append({
            **item,
            "stage": hk_signal.get("stage", "preopen_only"),
            "reason": hk_signal.get("reason"),
            "trigger_price": hk_signal.get("trigger_price"),
            "pullback_percent": hk_signal.get("pullback_percent"),
            "confidence_boost": hk_signal.get("confidence_boost", 0),
        })

    return {
        "count": len(enriched),
        "watchlist": enriched,
    }