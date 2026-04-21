from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.realtime.scanner_event_service import ScannerEventService

router = APIRouter()


@router.get("/scanner-feed")
def get_scanner_feed(limit: int = 50, db: Session = Depends(get_db)):
    events = ScannerEventService.list_recent(db=db, limit=limit)

    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "symbol": event.symbol,
            "message": event.message,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]