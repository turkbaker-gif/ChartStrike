import json

from app.db.models import Signal
from app.services.ai.ai_client import AIClient
from app.services.explanations.explanation_service import ExplanationService


class AIReviewService:
    @staticmethod
    def build_prompt(signal: Signal, explanation: dict) -> str:
        signal_payload = {
            "signal_id": signal.id,
            "symbol": signal.symbol,
            "pattern_name": signal.pattern_name,
            "timeframe": signal.timeframe,
            "trigger_price": float(signal.trigger_price) if signal.trigger_price is not None else None,
            "entry_low": float(signal.entry_low) if signal.entry_low is not None else None,
            "entry_high": float(signal.entry_high) if signal.entry_high is not None else None,
            "stop_price": float(signal.stop_price) if signal.stop_price is not None else None,
            "target_1": float(signal.target_1) if signal.target_1 is not None else None,
            "target_2": float(signal.target_2) if signal.target_2 is not None else None,
            "confidence": float(signal.confidence) if signal.confidence is not None else None,
            "signal_state": signal.signal_state,
        }

        base_instructions = f"""
You are a cautious trading signal reviewer for a novice trader.

Your job:
- Review the signal facts and the deterministic system explanation
- Be conservative
- Do not invent facts
- Do not provide financial guarantees
- Prefer "watchlist" over "actionable" if the evidence is mixed

Signal facts:
{json.dumps(signal_payload, indent=2)}

Deterministic explanation:
{json.dumps(explanation, indent=2)}
"""

        # Pattern-specific guidance
        if signal.pattern_name == "hk_preopen_momentum_pullback":
            pattern_guidance = """
This is a Hong Kong pre-open momentum pullback setup. Key considerations:
- The stock gained >3% before the market opened.
- The system has detected a controlled pullback from the intraday high.
- The setup aims to enter on a rebound from the pullback low.

When reviewing, pay special attention to:
- Whether the pullback percentage (typically 2-5%) is healthy.
- Whether the rebound is showing any volume confirmation (if known).
- The risk/reward relative to the intraday high and pullback low.
- The likelihood that pre-open momentum will sustain after the open.

Be especially mindful of the risk that pre-open moves can fade quickly.
"""
        else:
            pattern_guidance = ""

        full_prompt = (
            base_instructions
            + pattern_guidance
            + """
Return ONLY valid JSON with this exact shape:
{{
  "verdict": "actionable | watchlist | avoid",
  "setup_quality": "clean | acceptable | stretched | fragile",
  "analysis": "short paragraph",
  "key_risks": ["risk 1", "risk 2"],
  "what_to_wait_for": ["item 1", "item 2"]
}}
"""
        )

        return full_prompt.strip()

    @staticmethod
    def review_signal(signal: Signal) -> dict:
        explanation = ExplanationService.build_signal_explanation(signal)
        prompt = AIReviewService.build_prompt(signal, explanation)

        client = AIClient()
        review = client.review_signal(prompt)

        return {
            "signal_id": signal.id,
            "symbol": signal.symbol,
            "pattern_name": signal.pattern_name,
            "verdict": review.get("verdict", "watchlist"),
            "setup_quality": review.get("setup_quality", "acceptable"),
            "analysis": review.get("analysis", ""),
            "key_risks": review.get("key_risks", []),
            "what_to_wait_for": review.get("what_to_wait_for", []),
        }