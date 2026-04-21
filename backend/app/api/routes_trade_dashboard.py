from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trade_dashboard import TradeDashboardOut
from app.services.simulation.trade_dashboard_service import TradeDashboardService

router = APIRouter()


@router.get("/trade-dashboard", response_model=TradeDashboardOut)
def get_trade_dashboard(db: Session = Depends(get_db)):
    return TradeDashboardService.build_dashboard(db)