from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.db.models import ScannerEvent


class ScannerEventService:
    @staticmethod
    def create(
        db: Session,
        event_type: str,
        message: str,
        symbol: str | None = None,
    ) -> ScannerEvent:
        event = ScannerEvent(
            event_type=event_type,
            symbol=symbol,
            message=message,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def list_recent(db: Session, limit: int = 50) -> list[ScannerEvent]:
        stmt = (
            select(ScannerEvent)
            .order_by(desc(ScannerEvent.created_at))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())