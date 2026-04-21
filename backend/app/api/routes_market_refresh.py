from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.market.market_data_service import MarketDataService

router = APIRouter()


@router.post("/market/refresh")
def refresh_market_data(db: Session = Depends(get_db)):
    results = []

    for symbol in settings.watchlist:
        result = MarketDataService.refresh_candles_for_symbol(
            db=db,
            symbol=symbol,
            interval="1m",
            outputsize=100,
        )
        results.append(result)

    return {"results": results}