class HKPullbackDetector:
    @staticmethod
    def evaluate(candles: list[dict]) -> dict:
        if not candles or len(candles) < 10:
            return {"is_valid": False, "reason": "not_enough_candles"}

        # Use last 10 days for context
        highs = [float(c["high"]) for c in candles[-10:]]
        lows = [float(c["low"]) for c in candles[-10:]]
        closes = [float(c["close"]) for c in candles[-10:]]

        intraday_high = max(highs)          # recent swing high
        latest_close = closes[-1]
        pullback_low = min(lows[-5:])       # lowest of last 5 days

        if intraday_high <= 0:
            return {"is_valid": False, "reason": "invalid_intraday_high"}

        pullback_percent = ((intraday_high - pullback_low) / intraday_high) * 100

        # Adjusted for daily: 3–8% pullback is controlled
        is_controlled_pullback = 3.0 <= pullback_percent <= 8.0
        rebound_started = latest_close > pullback_low

        recent_high = max(closes[-3:]) if len(closes) >= 3 else latest_close
        continuation_trigger = recent_high
        continuation_signal = latest_close >= continuation_trigger and is_controlled_pullback

        stage = "preopen_only"
        if continuation_signal:
            stage = "continuation_signal"
        elif rebound_started and is_controlled_pullback:
            stage = "rebound_started"
        elif is_controlled_pullback:
            stage = "pullback_detected"

        return {
            "is_valid": True,
            "intraday_high": round(intraday_high, 4),
            "pullback_low": round(pullback_low, 4),
            "latest_close": round(latest_close, 4),
            "pullback_percent": round(pullback_percent, 2),
            "is_controlled_pullback": is_controlled_pullback,
            "rebound_started": rebound_started,
            "continuation_trigger": round(continuation_trigger, 4),
            "continuation_signal": continuation_signal,
            "stage": stage,
        }