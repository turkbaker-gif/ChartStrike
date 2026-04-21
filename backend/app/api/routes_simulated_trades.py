from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.simulated_trade import SimulatedTradeOut, CreateSimulatedTradeIn
from app.services.simulation.simulated_trade_service import SimulatedTradeService

router = APIRouter()


@router.get("/simulated-trades", response_model=list[SimulatedTradeOut])
def list_simulated_trades(db: Session = Depends(get_db)):
    trades = SimulatedTradeService.list_all(db)
    return [SimulatedTradeService.to_dict(t) for t in trades]


@router.get("/simulated-trades/{trade_id}", response_model=SimulatedTradeOut)
def get_simulated_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = SimulatedTradeService.get_by_id(db, trade_id)

    if not trade:
        raise HTTPException(status_code=404, detail="Simulated trade not found")

    return SimulatedTradeService.to_dict(trade)


@router.get("/signals/{signal_id}/simulated-trade", response_model=SimulatedTradeOut | None)
def get_simulated_trade_for_signal(signal_id: str, db: Session = Depends(get_db)):
    trade = SimulatedTradeService.get_by_signal_id(db, signal_id)

    if not trade:
        return None

    return SimulatedTradeService.to_dict(trade)


@router.post("/signals/{signal_id}/simulate", response_model=SimulatedTradeOut)
def create_simulated_trade(
    signal_id: str,
    payload: CreateSimulatedTradeIn,
    db: Session = Depends(get_db),
):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    try:
        trade = SimulatedTradeService.create_from_signal(
            db=db,
            signal=signal,
            account_size=payload.account_size,
            risk_percent=payload.risk_percent,
            max_portfolio_risk_percent=payload.max_portfolio_risk_percent,
        )
        return SimulatedTradeService.to_dict(trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))