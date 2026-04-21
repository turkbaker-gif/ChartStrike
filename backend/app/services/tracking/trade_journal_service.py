from datetime import datetime
from sqlalchemy import select

from app.db.models import TradeJournal, Signal


class TradeJournalService:
    @staticmethod
    def get_by_signal_id(db, signal_id: str) -> TradeJournal | None:
        stmt = select(TradeJournal).where(TradeJournal.signal_id == signal_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def to_dict(journal: TradeJournal | None) -> dict | None:
        if not journal:
            return None

        return {
            "signal_id": journal.signal_id,
            "symbol": journal.symbol,
            "decision": journal.decision,
            "outcome": journal.outcome,
            "notes": journal.notes,
            "lesson": journal.lesson,
            "updated_at": journal.updated_at,
        }

    @staticmethod
    def upsert(db, signal: Signal, payload: dict) -> TradeJournal:
        journal = TradeJournalService.get_by_signal_id(db, signal.id)

        if journal is None:
            journal = TradeJournal(
                signal_id=signal.id,
                symbol=signal.symbol,
                decision=payload.get("decision"),
                outcome=payload.get("outcome"),
                notes=payload.get("notes"),
                lesson=payload.get("lesson"),
            )
            db.add(journal)
        else:
            journal.decision = payload.get("decision")
            journal.outcome = payload.get("outcome")
            journal.notes = payload.get("notes")
            journal.lesson = payload.get("lesson")
            journal.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(journal)
        return journal