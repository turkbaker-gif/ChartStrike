from collections import defaultdict
from sqlalchemy import select

from app.db.models import Signal, TradeJournal, SimulatedTrade


class TradeAnalyticsService:
    @staticmethod
    def build_analytics(db) -> dict:
        signals = list(db.execute(select(Signal)).scalars().all())
        journals = list(db.execute(select(TradeJournal)).scalars().all())
        trades = list(db.execute(select(SimulatedTrade)).scalars().all())

        signal_map = {s.id: s for s in signals}

        took_trade_count = sum(1 for j in journals if j.decision == "took_trade")
        skipped_count = sum(1 for j in journals if j.decision == "skipped")

        open_trade_count = sum(1 for t in trades if t.outcome == "open")
        won_count = sum(1 for t in trades if t.outcome == "won")
        lost_count = sum(1 for t in trades if t.outcome == "lost")
        breakeven_count = sum(1 for t in trades if t.outcome == "breakeven")

        closed_trades = [t for t in trades if t.outcome in ("won", "lost", "breakeven")]

        win_rate = None
        if won_count + lost_count > 0:
            win_rate = round((won_count / (won_count + lost_count)) * 100, 2)

        r_values = [float(t.pnl_r_multiple) for t in closed_trades if t.pnl_r_multiple is not None]
        average_r = round(sum(r_values) / len(r_values), 2) if r_values else None

        pnl_values = [float(t.pnl_amount) for t in closed_trades if t.pnl_amount is not None]
        total_pnl = round(sum(pnl_values), 2)
        average_pnl = round(sum(pnl_values) / len(pnl_values), 2) if pnl_values else None

        lessons = []
        for j in sorted(journals, key=lambda x: x.updated_at or x.created_at, reverse=True):
            if j.lesson and j.lesson.strip():
                lessons.append({
                    "symbol": j.symbol,
                    "lesson": j.lesson.strip(),
                })
        recent_lessons = lessons[:5]

        pattern_buckets = defaultdict(lambda: {"total": 0, "won": 0, "lost": 0})

        for t in trades:
            signal = signal_map.get(t.signal_id)
            if not signal:
                continue

            pattern_name = signal.pattern_name
            pattern_buckets[pattern_name]["total"] += 1

            if t.outcome == "won":
                pattern_buckets[pattern_name]["won"] += 1
            elif t.outcome == "lost":
                pattern_buckets[pattern_name]["lost"] += 1

        pattern_stats = []
        for pattern_name, stats in pattern_buckets.items():
            denom = stats["won"] + stats["lost"]
            pattern_stats.append({
                "pattern_name": pattern_name,
                "total": stats["total"],
                "won": stats["won"],
                "lost": stats["lost"],
                "win_rate": round((stats["won"] / denom) * 100, 2) if denom > 0 else None,
            })

        pattern_stats.sort(key=lambda x: x["total"], reverse=True)

        return {
            "summary": {
                "total_signals": len(signals),
                "journaled_signals": len(journals),
                "took_trade_count": took_trade_count,
                "skipped_count": skipped_count,
                "open_trade_count": open_trade_count,
                "won_count": won_count,
                "lost_count": lost_count,
                "breakeven_count": breakeven_count,
                "win_rate": win_rate,
                "average_r": average_r,
                "total_pnl": total_pnl,
                "average_pnl": average_pnl,
            },
            "recent_lessons": recent_lessons,
            "pattern_stats": pattern_stats,
        }