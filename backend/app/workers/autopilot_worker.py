import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.patterns.runner import PatternRunner


class AutopilotWorker:
    def __init__(self):
        self.runner = PatternRunner()

    def run_scan_cycle(self) -> dict:
        db: Session = SessionLocal()
        results = []
        try:
            for symbol in settings.watchlist:
                result = self.runner.run_for_symbol(db, symbol)
                results.append(result)
            return {"scan_results": results}
        finally:
            db.close()

    def run_forever(self) -> None:
        while True:
            output = self.run_scan_cycle()
            print(output, flush=True)
            time.sleep(settings.autopilot_scan_seconds)