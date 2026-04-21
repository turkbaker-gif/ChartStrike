from app.db.models import Signal


class ExplanationService:
    @staticmethod
    def build_signal_explanation(signal: Signal) -> dict:
        symbol = signal.symbol
        pattern_name = signal.pattern_name
        trigger_price = float(signal.trigger_price) if signal.trigger_price else None
        entry_low = float(signal.entry_low) if signal.entry_low else None
        entry_high = float(signal.entry_high) if signal.entry_high else None
        stop_price = float(signal.stop_price) if signal.stop_price else None
        target_1 = float(signal.target_1) if signal.target_1 else None
        target_2 = float(signal.target_2) if signal.target_2 else None
        confidence = float(signal.confidence) if signal.confidence else None

        # Initialize all return variables to prevent UnboundLocalError
        summary = ""
        strengths = []
        risks = []
        invalidation = []
        trade_plan = []

        if pattern_name == "breakout_20d":
            summary = (
                f"{symbol} triggered a 20-bar breakout signal. "
                f"Price moved above the recent breakout level and the system marked it as a momentum setup."
            )

            strengths.append("Price broke above the recent 20-bar high.")
            strengths.append("The setup is structured as a continuation breakout.")
            strengths.append("A defined stop and profit targets are available.")

            risks.append("Breakouts can fail quickly if price falls back below the breakout area.")
            risks.append("Chasing too far above the entry zone can damage risk-reward.")
            risks.append("Low follow-through after the breakout candle may weaken the setup.")

            if stop_price is not None:
                invalidation.append(
                    f"A move back toward or below the stop area around {stop_price:.2f} would weaken the bullish thesis."
                )
            else:
                invalidation.append("A failed hold above the breakout area would weaken the setup.")

            if entry_low is not None and entry_high is not None:
                trade_plan.append(
                    f"Preferred entry zone: {entry_low:.2f} to {entry_high:.2f}."
                )

            if stop_price is not None:
                trade_plan.append(
                    f"Risk is defined below the stop area at {stop_price:.2f}."
                )

            targets_text = []
            if target_1 is not None:
                targets_text.append(f"Target 1: {target_1:.2f}")
            if target_2 is not None:
                targets_text.append(f"Target 2: {target_2:.2f}")
            if targets_text:
                trade_plan.append("Profit objectives: " + " | ".join(targets_text))

            if confidence is not None:
                if confidence >= 0.80:
                    strengths.append("System confidence is high for this pattern.")
                elif confidence >= 0.65:
                    strengths.append("System confidence is moderate-to-good.")
                else:
                    risks.append("System confidence is not especially high, so extra caution is sensible.")

        elif pattern_name == "hk_preopen_momentum_pullback":
            summary = (
                f"{symbol} has triggered a Hong Kong pre-open momentum continuation signal. "
                f"The stock showed strong pre-market interest and is now exhibiting a controlled pullback "
                f"followed by a rebound, suggesting a potential continuation of the upward move."
            )
            strengths.append("Strong pre-open momentum (>3%) indicates institutional or aggressive retail interest.")
            strengths.append("Controlled pullback keeps the structure intact and reduces chase risk.")
            strengths.append("Defined stop and targets allow for disciplined risk management.")
            risks.append("Pre-open strength can fade quickly if broader market sentiment shifts.")
            risks.append("If price fails to hold above the pullback low, the bullish thesis weakens.")
            risks.append("Continuation may require sustained volume; watch for volume dry-up.")
            if stop_price:
                invalidation.append(f"A drop below the pullback low near {stop_price:.2f} would invalidate the setup.")
            else:
                invalidation.append("A drop below the recent pullback low would invalidate the setup.")
            if entry_low and entry_high:
                trade_plan.append(f"Entry zone: {entry_low:.2f} to {entry_high:.2f}")
            if stop_price:
                trade_plan.append(f"Stop loss: {stop_price:.2f}")
            if target_1:
                trade_plan.append(f"Target 1 (intraday high): {target_1:.2f}")
            if target_2:
                trade_plan.append(f"Target 2 (extension): {target_2:.2f}")
            if confidence:
                if confidence >= 0.75:
                    strengths.append("Confidence is elevated due to clean pullback structure.")
                else:
                    risks.append("Confidence is moderate; consider waiting for additional confirmation.")
        else:
            # Fallback for any other pattern name
            summary = (
                f"{symbol} triggered a signal for pattern '{pattern_name}'. "
                f"ChartStrike generated a structured trade plan for review."
            )
            strengths.append("A valid signal was generated by the rules engine.")
            risks.append("This pattern does not yet have a custom explanation template.")
            invalidation.append("Loss of the signal structure would weaken the setup.")
            if trigger_price:
                trade_plan.append(f"Trigger price: {trigger_price:.2f}")
            else:
                trade_plan.append("Trigger price unavailable.")

        return {
            "signal_id": signal.id,
            "symbol": symbol,
            "pattern_name": pattern_name,
            "summary": summary,
            "strengths": strengths,
            "risks": risks,
            "invalidation": invalidation,
            "trade_plan": trade_plan,
        }