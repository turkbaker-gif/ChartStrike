from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.hk_patterns.hk_preopen_scanner import HKPreopenScanner
from app.services.hk_patterns.hk_watchlist_service import HKWatchlistService

router = APIRouter()


@router.get("/hk/watchlist")
def get_hk_watchlist(db: Session = Depends(get_db)):
    # Fetch all HK symbols from the database
    query = text("SELECT DISTINCT symbol FROM stock_prices WHERE symbol LIKE '%.HK' ORDER BY symbol")
    result = db.execute(query)
    symbols = [row[0] for row in result.fetchall()]

    # Scan the symbols
    scan_results = HKPreopenScanner.scan_watchlist(
        db=db,
        symbols=symbols,
        min_percent_gain=3.0,
    )

    watchlist = HKWatchlistService.build_today_watchlist(scan_results)

    return {
        "count": len(watchlist),
        "watchlist": watchlist,
    }