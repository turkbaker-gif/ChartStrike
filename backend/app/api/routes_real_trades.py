from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Signal
from app.services.trading.real_trade_service import RealTradeService

router = APIRouter()

@router.post("/signals/{signal_id}/real-trade")
def start_real_trade(signal_id: str, account_size: float = 10000, risk_percent: float = 1, db: Session = Depends(get_db)):
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    trade = RealTradeService.create_from_signal(db, signal, account_size, risk_percent)
    return {"id": trade.id, "symbol": trade.symbol, "status": trade.status}

@router.get("/real-trades")
def list_real_trades(db: Session = Depends(get_db)):
    return RealTradeService.list_all(db)