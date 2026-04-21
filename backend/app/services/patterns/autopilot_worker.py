import time
from sqlalchemy import select

from app.core.config import settings
from app.db.models import Signal
from app.db.session import SessionLocal
from app.services.ai.ai_review_service import AIReviewService
from app.services.ai.ai_review_store import AIReviewStore
from app.services.patterns.runner import PatternRunner


class AutopilotWorker:
    def __init__(self) -> None:
        self.runner = PatternRunner()

    def run_scan_cycle(self) -> dict:
        db = SessionLocal()
        try:
            results = []
            new_reviews = []

            for symbol in settings.watchlist:
                result = self.runner.run_for_symbol(db, symbol)
                results.append(result)

                if result.get("status") == "triggered":
                    signal_id = result["signal_id"]

                    stmt = select(Signal).where(Signal.id == signal_id)
                    signal = db.execute(stmt).scalar_one_or_none()

                    if signal:
                        existing_review = AIReviewStore.get_by_signal_id(db, signal.id)
                        if not existing_review:
                            review = AIReviewService.review_signal(signal)
                            AIReviewStore.create(db, review)
                            new_reviews.append({
                                "signal_id": signal.id,
                                "symbol": signal.symbol,
                                "verdict": review["verdict"],
                            })

            return {
                "scan_results": results,
                "new_ai_reviews": new_reviews,
            }

        finally:
            db.close()

    def run_forever(self) -> None:
        while True:
            output = self.run_scan_cycle()
            print(output, flush=True)
            time.sleep(settings.autopilot_scan_seconds)