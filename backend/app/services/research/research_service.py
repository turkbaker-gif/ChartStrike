from app.db.models import Signal
from app.services.explanations.explanation_service import ExplanationService
from app.services.ai.ai_review_store import AIReviewStore


class ResearchService:
    @staticmethod
    def build_research(signal: Signal, ai_review: dict | None) -> dict:
        explanation = ExplanationService.build_signal_explanation(signal)

        symbol = signal.symbol
        confidence = float(signal.confidence) if signal.confidence is not None else None

        evidence = []
        key_drivers = []
        next_checks = []

        evidence.append(f"Pattern detected: {signal.pattern_name}")
        evidence.append("Deterministic explanation is available.")

        if confidence is not None:
            evidence.append(f"System confidence: {confidence:.2f}")

        if ai_review:
            evidence.append(f"AI verdict: {ai_review.get('verdict', 'unknown')}")
            evidence.append(
                f"AI setup quality: {ai_review.get('setup_quality', 'unknown')}"
            )

        key_drivers.append("Breakout pattern triggered from the rules engine.")
        key_drivers.append("Trade plan has defined entry, stop, and targets.")

        if confidence is not None and confidence >= 0.80:
            key_drivers.append("Signal confidence is relatively strong.")
        elif confidence is not None:
            key_drivers.append("Signal confidence is moderate, which suggests caution.")

        if ai_review:
            verdict = ai_review.get("verdict", "")
            if verdict == "actionable":
                catalyst_type = "technical"
                key_drivers.append("AI review sees the setup as actionable.")
            elif verdict == "watchlist":
                catalyst_type = "technical"
                key_drivers.append("AI review suggests the setup needs confirmation.")
            else:
                catalyst_type = "unclear"
                key_drivers.append("AI review suggests the setup may be weak.")
        else:
            catalyst_type = "technical"

        next_checks.append("Watch whether price holds above the breakout area.")
        next_checks.append("Look for follow-through volume on the next candle(s).")
        next_checks.append("Check whether peer stocks or the broader sector are also strong.")
        next_checks.append("Look for fresh company-specific news or announcements.")

        if catalyst_type == "technical":
            research_summary = (
                f"{symbol} currently looks more like a technically-driven move than a confirmed news-driven move. "
                f"The system detected a valid breakout structure, but external catalyst confirmation is still missing."
            )
        else:
            research_summary = (
                f"{symbol} triggered a signal, but the current internal evidence does not clearly confirm the driver. "
                f"More context is needed before treating the move as high conviction."
            )

        return {
            "signal_id": signal.id,
            "symbol": symbol,
            "research_summary": research_summary,
            "catalyst_type": catalyst_type,
            "key_drivers": key_drivers,
            "evidence": evidence,
            "next_checks": next_checks,
        }

    @staticmethod
    def build_research_from_db(signal: Signal, db) -> dict:
        stored_review = AIReviewStore.get_by_signal_id(db, signal.id)
        ai_review = AIReviewStore.to_dict(stored_review) if stored_review else None
        return ResearchService.build_research(signal, ai_review)