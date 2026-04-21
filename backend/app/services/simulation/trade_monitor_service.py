from sqlalchemy.orm import Session

from app.db.models import SimulatedTrade
from app.services.market.quote_service import QuoteService


class TradeMonitorService:

    @staticmethod
    def check_open_trades(db: Session):
        open_trades = (
            db.query(SimulatedTrade)
            .filter(SimulatedTrade.status == "open")
            .all()
        )

        results = []

        for trade in open_trades:
            quote = QuoteService.get_latest_quote(trade.symbol)

            if not quote or quote.get("price") is None:
                results.append({
                    "symbol": trade.symbol,
                    "status": "no_quote"
                })
                continue

            price = float(quote["price"])
            stop_price = float(trade.stop_price)          # ✅ correct field
            target_1 = float(trade.target_1) if trade.target_1 is not None else None
            target_2 = float(trade.target_2) if trade.target_2 is not None else None

            status = "open"

            if price <= stop_price:
                trade.status = "stopped"
                trade.exit_price = price
                status = "stop_hit"

            elif target_2 is not None and price >= target_2:
                trade.status = "target_2_hit"
                trade.exit_price = price
                status = "target_2_hit"

            elif target_1 is not None and price >= target_1:
                trade.status = "target_1_hit"
                trade.exit_price = price
                status = "target_1_hit"

            db.commit()

            results.append({
                "symbol": trade.symbol,
                "status": status,
                "price": price
            })

        return results