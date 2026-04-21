from pydantic import BaseModel


class AnalyticsSummaryOut(BaseModel):
    total_signals: int
    journaled_signals: int
    took_trade_count: int
    skipped_count: int
    open_trade_count: int
    won_count: int
    lost_count: int
    breakeven_count: int
    win_rate: float | None = None
    average_r: float | None = None
    total_pnl: float
    average_pnl: float | None = None


class LessonItemOut(BaseModel):
    symbol: str
    lesson: str


class PatternStatOut(BaseModel):
    pattern_name: str
    total: int
    won: int
    lost: int
    win_rate: float | None = None


class AnalyticsOut(BaseModel):
    summary: AnalyticsSummaryOut
    recent_lessons: list[LessonItemOut]
    pattern_stats: list[PatternStatOut]