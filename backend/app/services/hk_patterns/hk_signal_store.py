from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal


class HKSignalStore:
    @staticmethod
    def upsert_signal(db: Session, signal_data: dict) -> Signal:
        symbol = signal_data["symbol"]
        pattern_name = signal_data.get("pattern_name", "hk_preopen_momentum_pullback")

        stmt = select(Signal).where(
            Signal.symbol == symbol,
            Signal.pattern_name == pattern_name,
        )
        existing = db.execute(stmt).scalar_one_or_none()

        if existing:
            existing.signal_state = signal_data.get("signal_state", existing.signal_state)
            existing.entry_low = signal_data.get("entry_low")
            existing.entry_high = signal_data.get("entry_high")
            existing.stop_price = signal_data.get("stop_price")
            existing.target_1 = signal_data.get("target_1")
            existing.target_2 = signal_data.get("target_2")
            existing.confidence = signal_data.get("confidence", existing.confidence)
            existing.timeframe = signal_data.get("timeframe", existing.timeframe)
            existing.trigger_price = signal_data.get("trigger_price")
            db.commit()
            db.refresh(existing)
            return existing

        new_signal = Signal(
            symbol=symbol,
            pattern_name=pattern_name,
            timeframe=signal_data.get("timeframe", "1m"),
            confidence=signal_data.get("confidence", "medium"),
            signal_state=signal_data.get("signal_state", "watching"),
            trigger_price=signal_data.get("trigger_price"),
            entry_low=signal_data.get("entry_low"),
            entry_high=signal_data.get("entry_high"),
            stop_price=signal_data.get("stop_price"),
            target_1=signal_data.get("target_1"),
            target_2=signal_data.get("target_2"),
        )

        db.add(new_signal)
        db.commit()
        db.refresh(new_signal)
        return new_signal