import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Candle(Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    open: Mapped[Float] = mapped_column(Numeric, nullable=False)
    high: Mapped[Float] = mapped_column(Numeric, nullable=False)
    low: Mapped[Float] = mapped_column(Numeric, nullable=False)
    close: Mapped[Float] = mapped_column(Numeric, nullable=False)
    volume: Mapped[Float] = mapped_column(Numeric, nullable=False)


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    pattern_name: Mapped[str] = mapped_column(String, nullable=False)
    timeframe: Mapped[str] = mapped_column(String, nullable=False)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    trigger_price: Mapped[Float] = mapped_column(Numeric, nullable=False)
    entry_low: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    entry_high: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    stop_price: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    target_1: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    target_2: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    confidence: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    signal_state: Mapped[str] = mapped_column(String, nullable=False, default="new")
    context_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class AIReview(Base):
    __tablename__ = "ai_reviews"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    signal_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("signals.id"),
        nullable=False,
        unique=True,
        index=True
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False)
    pattern_name: Mapped[str] = mapped_column(String, nullable=False)

    verdict: Mapped[str] = mapped_column(String, nullable=False)
    setup_quality: Mapped[str] = mapped_column(String, nullable=False)
    analysis: Mapped[str] = mapped_column(Text, nullable=False)
    key_risks: Mapped[str] = mapped_column(Text, nullable=False)
    what_to_wait_for: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class TradeJournal(Base):
    __tablename__ = "trade_journals"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    signal_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("signals.id"),
        nullable=False,
        unique=True,
        index=True
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False)

    decision: Mapped[str | None] = mapped_column(String, nullable=True)   # took_trade / skipped
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)    # open / won / lost / breakeven
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    lesson: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
class SimulatedTrade(Base):
    __tablename__ = "simulated_trades"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    signal_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("signals.id"),
        nullable=False,
        unique=True,
        index=True
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)

    entry_price: Mapped[Float] = mapped_column(Numeric, nullable=False)
    stop_price: Mapped[Float] = mapped_column(Numeric, nullable=False)
    target_1: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    target_2: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    position_size_shares: Mapped[int] = mapped_column(nullable=False)
    risk_amount: Mapped[Float] = mapped_column(Numeric, nullable=False)

    # New columns for partial exits
    partial_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    remaining_shares: Mapped[int] = mapped_column(Integer, nullable=True)

    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    exit_price: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    pnl_amount: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    pnl_r_multiple: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class RealTrade(Base):
    __tablename__ = "real_trades"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    signal_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("signals.id"),
        nullable=False,
        index=True
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")  # open, closed
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)  # won, lost, breakeven

    entry_price: Mapped[Float] = mapped_column(Numeric, nullable=False)
    stop_price: Mapped[Float] = mapped_column(Numeric, nullable=False)
    target_1: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    target_2: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    position_size_shares: Mapped[int] = mapped_column(nullable=False)
    risk_amount: Mapped[Float] = mapped_column(Numeric, nullable=False)

    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exit_price: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    pnl_amount: Mapped[Float | None] = mapped_column(Numeric, nullable=True)
    pnl_r_multiple: Mapped[Float | None] = mapped_column(Numeric, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class ScannerEvent(Base):
    __tablename__ = "scanner_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    symbol = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
class LatestQuote(Base):
    __tablename__ = "latest_quotes"

    symbol = Column(String, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    turnover = Column(Float, nullable=True)
    timestamp = Column(Integer, nullable=True)  # Unix timestamp from API
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)