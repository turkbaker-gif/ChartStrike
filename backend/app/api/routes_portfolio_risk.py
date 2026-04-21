from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.portfolio_risk import PortfolioRiskOut
from app.services.portfolio.portfolio_risk_service import PortfolioRiskService

router = APIRouter()


@router.get("/portfolio-risk", response_model=PortfolioRiskOut)
def get_portfolio_risk(
    account_size: float = Query(..., gt=0),
    max_portfolio_risk_percent: float = Query(..., gt=0, le=100),
    db: Session = Depends(get_db),
):
    return PortfolioRiskService.build_portfolio_risk(
        db=db,
        account_size=account_size,
        max_portfolio_risk_percent=max_portfolio_risk_percent,
    )