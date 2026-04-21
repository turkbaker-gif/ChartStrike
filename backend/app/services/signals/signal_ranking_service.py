import traceback
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Signal, AIReview
from app.services.market.data_service import LocalDataService
from app.services.checklist.trade_checklist_service import TradeChecklistService
from app.services.intelligence.signal_intelligence import SignalIntelligence
from app.services.research.catalyst_service import CatalystService
from app.services.tracking.trade_plan_service import TradePlanService


class SignalRankingService:
    @staticmethod
    def _apply_hk_pattern_boost(item: dict) -> tuple[float, float]:
        score = float(item.get("score", 0))
        hk_boost = 0.0

        if item.get("pattern_name") == "hk_preopen_momentum_pullback":
            hk_boost += 20
            confidence = item.get("confidence")
            if confidence == "high":
                hk_boost += 10
            confidence_boost = float(item.get("confidence_boost", 0) or 0)
            hk_boost += confidence_boost

        final_score = min(score + hk_boost, 100)
        return final_score, hk_boost

    @staticmethod
    def rank_all(
        db: Session,
        account_size: float = 10000,
        risk_percent: float = 1,
        max_portfolio_risk_percent: float = 6,
    ) -> list[dict]:
        stmt = select(Signal)
        signals = list(db.execute(stmt).scalars().all())
        ranked = []

        for signal in signals:
            try:
                # Fetch recent candles from local DB
                candles = LocalDataService.get_recent_candles(db, signal.symbol, limit=50)
                if not candles:
                    continue  # Skip if no data

                # Use latest close as current price (not used directly but kept for consistency)
                latest_price = candles[-1]['close'] if candles else None

                # Build trade plan using local data
                trade_plan = TradePlanService.build_trade_plan(
                    signal=signal,
                    account_size=account_size,
                    risk_percent=risk_percent,
                )

                ai_review = db.execute(
                    select(AIReview).where(AIReview.signal_id == signal.id)
                ).scalar_one_or_none()

                try:
                    catalyst = CatalystService.build(signal.symbol)
                except Exception:
                    catalyst = {
                        "headline_count": 0,
                        "catalyst_type": "unknown",
                        "confidence": "low",
                        "summary": "Catalyst unavailable",
                    }

                intelligence = SignalIntelligence.build(
                    signal=signal,
                    trade_plan=trade_plan,
                    catalyst=catalyst,
                )

                checklist = TradeChecklistService.build(
                    db=db,
                    signal=signal,
                    ai_review=ai_review,
                    account_size=account_size,
                    risk_percent=risk_percent,
                    max_portfolio_risk_percent=max_portfolio_risk_percent,
                )

                # Base score
                base_score = 50.0
                rr = float(trade_plan.get("rr_target_1", 0) or 0)
                if rr >= 3:
                    base_score += 20
                elif rr >= 2:
                    base_score += 12
                elif rr >= 1.5:
                    base_score += 6

                if intelligence.get("momentum") == "Strong":
                    base_score += 10
                elif intelligence.get("momentum") == "Moderate":
                    base_score += 5

                if catalyst.get("headline_count", 0) > 0:
                    base_score += 8

                verdict = checklist.get("verdict", "watch")
                if verdict == "ready":
                    base_score += 10
                elif verdict == "wait":
                    base_score += 3
                elif verdict == "avoid":
                    base_score -= 10

                hk_stage = None
                if signal.pattern_name == "hk_preopen_momentum_pullback":
                    hk_stage = "continuation_signal"

                item = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "pattern_name": signal.pattern_name,
                    "score": round(min(base_score, 100), 2),
                    "momentum": intelligence.get("momentum"),
                    "risk_reward": round(rr, 2) if rr else None,
                    "catalyst": intelligence.get("catalyst"),
                    "verdict": verdict,
                    "reason": checklist.get("summary", intelligence.get("verdict", "No summary")),
                    "confidence": getattr(signal, "confidence", None),
                    "confidence_boost": 0,
                    "hk_stage": hk_stage,
                }

                final_score, hk_boost = SignalRankingService._apply_hk_pattern_boost(item)
                item["score"] = round(final_score, 2)
                item["hk_boost"] = round(hk_boost, 2)

                ranked.append(item)

            except Exception as e:
                print(f"ERROR ranking symbol {signal.symbol}: {e}")
                traceback.print_exc()
                continue

        ranked.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
        return ranked