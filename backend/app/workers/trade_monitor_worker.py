from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.market.quote_service import QuoteService
from app.services.realtime.live_event_service import LiveEventService
from app.services.realtime.scanner_event_service import ScannerEventService
from app.services.simulation.simulated_trade_service import SimulatedTradeService


class TradeMonitorWorker:
    @staticmethod
    def run_once():
        db: Session = SessionLocal()
        results = []

        try:
            open_trades = SimulatedTradeService.list_open_trades(db)

            for trade in open_trades:
                quote = QuoteService.get_latest_quote(trade.symbol)

                if not quote or quote.get("price") is None:
                    result = {
                        "symbol": trade.symbol,
                        "status": "no_quote",
                    }
                    results.append(result)
                    continue

                live_price = float(quote["price"])
                stop_price = float(trade.stop_price)
                entry_price = float(trade.entry_price)
                target_1 = float(trade.target_1) if trade.target_1 is not None else None
                target_2 = float(trade.target_2) if trade.target_2 is not None else None

                # Emit quote update for live cockpit
                LiveEventService.emit("quote_update", quote)

                # 1. Stop loss check (full close)
                if live_price <= stop_price:
                    SimulatedTradeService.close_trade(
                        db=db,
                        trade=trade,
                        exit_price=live_price,
                        outcome="lost",
                        status="stopped",
                    )
                    results.append({
                        "symbol": trade.symbol,
                        "status": "stopped",
                        "price": live_price,
                    })
                    ScannerEventService.create(
                        db=db,
                        event_type="trade_update",
                        symbol=trade.symbol,
                        message=f"Trade stopped @ {live_price}",
                    )
                    continue

                # 2. Target 2 hit (full close)
                if target_2 is not None and live_price >= target_2:
                    SimulatedTradeService.close_trade(
                        db=db,
                        trade=trade,
                        exit_price=live_price,
                        outcome="won",
                        status="target_hit",
                    )
                    results.append({
                        "symbol": trade.symbol,
                        "status": "target_2_hit",
                        "price": live_price,
                    })
                    ScannerEventService.create(
                        db=db,
                        event_type="trade_update",
                        symbol=trade.symbol,
                        message=f"Target 2 hit @ {live_price}",
                    )
                    continue

                # 3. Target 1 hit (partial close + breakeven stop)
                if target_1 is not None and live_price >= target_1:
                    # Check if we've already partially closed
                    if not getattr(trade, "partial_closed", False):
                        # Close 50% at Target 1
                        partial_shares = int(trade.position_size_shares * 0.5)
                        if partial_shares > 0:
                            trade.partial_closed = True
                            trade.remaining_shares = trade.position_size_shares - partial_shares
                            trade.stop_price = entry_price  # Move stop to breakeven
                            db.commit()

                            results.append({
                                "symbol": trade.symbol,
                                "status": "partial_target_1",
                                "price": live_price,
                                "shares_closed": partial_shares,
                            })
                            ScannerEventService.create(
                                db=db,
                                event_type="trade_update",
                                symbol=trade.symbol,
                                message=f"Partial close (50%) @ Target 1, stop moved to breakeven",
                            )
                    # If already partially closed, just report open status with breakeven stop
                    else:
                        results.append({
                            "symbol": trade.symbol,
                            "status": "open_breakeven",
                            "price": live_price,
                        })
                    continue

                # 4. No trigger
                results.append({
                    "symbol": trade.symbol,
                    "status": "open",
                    "price": live_price,
                })

            return results
        finally:
            db.close()