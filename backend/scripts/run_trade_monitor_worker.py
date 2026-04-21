import time
from app.workers.trade_monitor_worker import TradeMonitorWorker
from app.utils.market_hours import is_any_target_market_open

def run():
    print("Starting Trade Monitor Worker")
    while True:
        if is_any_target_market_open():
            try:
                result = TradeMonitorWorker.run_once()
                print(result, flush=True)
            except Exception as e:
                print(f"trade monitor error: {e}", flush=True)
        else:
            print("Market closed, sleeping...", flush=True)
        time.sleep(30)

if __name__ == "__main__":
    run()