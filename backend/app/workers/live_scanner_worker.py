import time
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import SessionLocal
from app.services.hk_patterns.hk_continuation_signal_service import HKContinuationSignalService
from app.services.hk_patterns.hk_signal_store import HKSignalStore
from app.services.market.itick_client import ITickClient
from app.services.realtime.live_event_service import LiveEventService
from app.services.realtime.scanner_event_service import ScannerEventService
from app.services.signals.signal_ranking_service import SignalRankingService


class LiveScannerWorker:
    BATCH_SIZE = 10
    BATCH_DELAY = 1.5
    MIN_GAIN_PERCENT = 3.0

    @staticmethod
    def _get_all_symbols(db: Session) -> list[str]:
        query = text("""
            SELECT DISTINCT symbol FROM stock_prices
            WHERE symbol LIKE '%.HK' OR symbol LIKE '%.SH' OR symbol LIKE '%.SZ'
            ORDER BY symbol
        """)
        result = db.execute(query)
        return [row[0] for row in result.fetchall()]

    @staticmethod
    def _chunk_list(lst: list, chunk_size: int):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    @staticmethod
    def run_once():
        db: Session = SessionLocal()
        results = {
            "scanned": 0,
            "top_gainers": 0,
            "pullbacks": 0,
            "signals": 0,
            "api_calls": 0,
        }

        try:
            before_ranked = SignalRankingService.rank_all(db)
            before_ids = {item["id"] for item in before_ranked}

            all_symbols = LiveScannerWorker._get_all_symbols(db)
            results["scanned"] = len(all_symbols)

            # Group by region for batch requests
            hk_symbols = [s for s in all_symbols if s.endswith('.HK')]
            cn_symbols = [s for s in all_symbols if s.endswith('.SH') or s.endswith('.SZ')]

            all_gainers = []
            pullback_stocks = []
            signals_created = []

            for region_symbols in [hk_symbols, cn_symbols]:
                if not region_symbols:
                    continue

                for batch in LiveScannerWorker._chunk_list(region_symbols, LiveScannerWorker.BATCH_SIZE):
                    # 1. Batch quote
                    quotes = ITickClient.get_batch_quotes(batch)
                    results["api_calls"] += 1
                    time.sleep(LiveScannerWorker.BATCH_DELAY)

                    if not quotes:
                        continue

                    gainers_in_batch = []
                    for symbol, quote in quotes.items():
                        prev_close = quote.get("previous_close", 0)
                        last_price = quote.get("price", 0)
                        if prev_close <= 0:
                            continue

                        percent_change = ((last_price - prev_close) / prev_close) * 100
                        if percent_change < LiveScannerWorker.MIN_GAIN_PERCENT:
                            continue

                        gainers_in_batch.append(symbol)
                        all_gainers.append({
                            "symbol": symbol,
                            "percent_change": round(percent_change, 2),
                            "price": last_price,
                            "prev_close": prev_close,
                        })

                    # 2. Batch klines for gainers in this batch
                    if gainers_in_batch:
                        klines = ITickClient.get_batch_klines(gainers_in_batch, interval="5m", limit=50)
                        results["api_calls"] += 1
                        time.sleep(LiveScannerWorker.BATCH_DELAY)

                        if klines:
                            for symbol, candles in klines.items():
                                if not candles:
                                    continue

                                formatted = [
                                    {"high": c["high"], "low": c["low"], "close": c["close"], "volume": c["volume"]}
                                    for c in candles
                                ]

                                hk_signal = HKContinuationSignalService.build_signal(symbol, formatted)
                                stage = hk_signal.get("stage")

                                if stage in ("pullback_detected", "rebound_started"):
                                    pullback_stocks.append({
                                        "symbol": symbol,
                                        "percent_change": next(
                                            (g["percent_change"] for g in all_gainers if g["symbol"] == symbol), 0
                                        ),
                                        "stage": stage,
                                        "pullback_percent": hk_signal.get("pullback_percent"),
                                        "trigger_price": hk_signal.get("trigger_price"),
                                    })

                                if stage == "continuation_signal":
                                    stored_signal = HKSignalStore.upsert_signal(db, hk_signal)
                                    signals_created.append(stored_signal.symbol)

                                    ScannerEventService.create(
                                        db=db,
                                        event_type="hk_continuation_signal",
                                        symbol=symbol,
                                        message=f"HK/CN continuation signal: {symbol}",
                                    )
                                    LiveEventService.emit("hk_continuation_signal", {
                                        "id": stored_signal.id,
                                        "symbol": stored_signal.symbol,
                                        "entry_low": float(stored_signal.entry_low) if stored_signal.entry_low else None,
                                        "stop_price": float(stored_signal.stop_price) if stored_signal.stop_price else None,
                                    })

            # Emit events for frontend panels
            LiveEventService.emit("top_gainers", all_gainers)
            LiveEventService.emit("pullback_watchlist", pullback_stocks)

            results["top_gainers"] = len(all_gainers)
            results["pullbacks"] = len(pullback_stocks)
            results["signals"] = len(signals_created)

            after_ranked = SignalRankingService.rank_all(db)
            results["ranked_signals"] = after_ranked
            LiveEventService.emit("ranked_signals", after_ranked)

            ScannerEventService.create(
                db=db,
                event_type="ranked_signals",
                message=f"Ranked signals refreshed ({len(after_ranked)})",
            )

            for item in after_ranked:
                if item["id"] not in before_ids:
                    LiveEventService.emit("new_signal", item)

            return results

        except Exception as e:
            print("ERROR in LiveScannerWorker:")
            traceback.print_exc()
            raise
        finally:
            db.close()


def run_forever(interval_seconds: int = 600):  # 10 minutes
    while True:
        try:
            output = LiveScannerWorker.run_once()
            print(f"[{time.strftime('%H:%M:%S')}] "
                  f"Scanned: {output['scanned']}, "
                  f"Top Gainers: {output['top_gainers']}, "
                  f"Pullbacks: {output['pullbacks']}, "
                  f"Signals: {output['signals']}, "
                  f"API Calls: {output['api_calls']}",
                  flush=True)
        except Exception as e:
            print(f"Live scanner error: {e}", flush=True)
        time.sleep(interval_seconds)