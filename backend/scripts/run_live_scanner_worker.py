from app.workers.live_scanner_worker import run_forever
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting Live Scanner Worker (interval: {settings.autopilot_scan_seconds}s)")
    run_forever(interval_seconds=settings.autopilot_scan_seconds)