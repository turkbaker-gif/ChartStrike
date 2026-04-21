from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AnalyticsOut
from app.services.analytics.trade_analytics_service import TradeAnalyticsService

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db)):
    return TradeAnalyticsService.build_analytics(db)