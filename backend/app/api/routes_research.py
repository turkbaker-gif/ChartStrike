from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal
from app.db.session import get_db
from app.schemas.research import ResearchOut
from app.services.research.research_service import ResearchService

router = APIRouter()


@router.get("/signals/{signal_id}/research", response_model=ResearchOut)
def get_signal_research(signal_id: str, db: Session = Depends(get_db)):
    stmt = select(Signal).where(Signal.id == signal_id)
    signal = db.execute(stmt).scalar_one_or_none()

    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    return ResearchService.build_research_from_db(signal, db)