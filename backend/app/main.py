from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_index_quote import router as index_quote_router
from app.api.routes_market_news import router as market_news_router
from app.api.routes_signals_by_symbol import router as signals_by_symbol_router
from app.api.routes_pullback_watchlist import router as pullback_watchlist_router

from app.api.routes_health import router as health_router
from app.api.routes_scan import router as scan_router
from app.api.routes_signals import router as signals_router
from app.api.routes_explanations import router as explanations_router
from app.api.routes_ai_review import router as ai_review_router
from app.api.routes_full_analysis import router as full_analysis_router
from app.api.routes_research import router as research_router
from app.api.routes_candles import router as candles_router
from app.api.routes_tracking import router as tracking_router
from app.api.routes_trade_plan import router as trade_plan_router
from app.api.routes_trade_journal import router as trade_journal_router
from app.api.routes_simulated_trades import router as simulated_trades_router
from app.api.routes_trade_dashboard import router as trade_dashboard_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_portfolio_risk import router as portfolio_risk_router
from app.api.routes_trade_checklist import router as trade_checklist_router
from app.api.routes_news import router as news_router
from app.api.routes_ranked_signals import router as ranked_signals_router
from app.api.routes_quote import router as quote_router
from app.api.routes_market_refresh import router as market_refresh_router
from app.api.routes_intelligence import router as intelligence_router
from app.api.routes_ws import router as ws_router
from app.api.routes_scanner_feed import router as scanner_feed_router
from app.api.routes_hk_patterns import router as hk_patterns_router
from app.api.routes_hk_watchlist import router as hk_watchlist_router

from app.db.base import Base
from app.db.session import engine

import app.db.models  # noqa: F401

app = FastAPI(title="ChartStrike")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(index_quote_router)
app.include_router(market_news_router)
app.include_router(signals_by_symbol_router)
app.include_router(pullback_watchlist_router)

app.include_router(health_router)
app.include_router(scan_router)
app.include_router(signals_router)
app.include_router(explanations_router)
app.include_router(ai_review_router)
app.include_router(full_analysis_router)
app.include_router(research_router)
app.include_router(candles_router)
app.include_router(tracking_router)
app.include_router(trade_plan_router)
app.include_router(trade_journal_router)
app.include_router(simulated_trades_router)
app.include_router(trade_dashboard_router)
app.include_router(analytics_router)
app.include_router(portfolio_risk_router)
app.include_router(trade_checklist_router)
app.include_router(news_router)
app.include_router(ranked_signals_router)
app.include_router(quote_router)
app.include_router(market_refresh_router)
app.include_router(intelligence_router)
app.include_router(ws_router)
app.include_router(scanner_feed_router)
app.include_router(hk_patterns_router)
app.include_router(hk_watchlist_router)

@app.get("/")
def root():
    return {
        "app": "ChartStrike",
        "status": "running",
    }