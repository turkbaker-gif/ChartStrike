from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.signals.signal_ranking_service import SignalRankingService

router = APIRouter()


@router.get("/ranked-signals")
def get_ranked_signals(db: Session = Depends(get_db)):
    ranked = SignalRankingService.rank_all(
        db=db,
        account_size=10000,
        risk_percent=1,
        max_portfolio_risk_percent=6,
    )

    deduped = {}
    for item in ranked:
        key = f"{item.get('symbol')}::{item.get('pattern_name')}"
        existing = deduped.get(key)

        if existing is None or float(item.get("score", 0)) > float(existing.get("score", 0)):
            deduped[key] = item

    result = sorted(
        deduped.values(),
        key=lambda x: float(x.get("score", 0)),
        reverse=True,
    )

    return result