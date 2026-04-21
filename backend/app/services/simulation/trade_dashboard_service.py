from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SimulatedTrade
from app.services.simulation.simulated_trade_service import SimulatedTradeService


class TradeDashboardService:
    @staticmethod
    def build_dashboard(db: Session) -> dict:
        stmt = select(SimulatedTrade).order_by(SimulatedTrade.created_at.desc())
        trades = list(db.execute(stmt).scalars().all())

        open_trades = [t for t in trades if t.status == "open"]
        closed_trades = [t for t in trades if t.status != "open"]

        winning_trades = [
            t for t in closed_trades
            if t.outcome == "won"
        ]
        losing_trades = [
            t for t in closed_trades
            if t.outcome == "lost"
        ]

        total_pnl = sum(float(t.pnl_amount or 0) for t in closed_trades)

        r_values = [
            float(t.pnl_r_multiple)
            for t in closed_trades
            if t.pnl_r_multiple is not None
        ]
        average_r = round(sum(r_values) / len(r_values), 2) if r_values else None

        return {
            "summary": {
                "total_trades": len(trades),
                "open_trades": len(open_trades),
                "closed_trades": len(closed_trades),
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "total_pnl": round(total_pnl, 2),
                "average_r": average_r,
            },
            "open_trades": [SimulatedTradeService.to_dict(t) for t in open_trades],
            "closed_trades": [SimulatedTradeService.to_dict(t) for t in closed_trades],
        }