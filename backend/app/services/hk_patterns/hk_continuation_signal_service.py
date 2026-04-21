from app.services.hk_patterns.hk_pullback_detector import HKPullbackDetector


class HKContinuationSignalService:
    @staticmethod
    def build_signal(symbol: str, candles: list[dict]) -> dict:
        pullback = HKPullbackDetector.evaluate(candles)

        if not pullback.get("is_valid"):
            return {
                "symbol": symbol,
                "pattern_name": "hk_preopen_momentum_pullback",
                "signal_state": "invalid",
                "stage": "invalid",
                "reason": pullback.get("reason", "unknown"),
                "confidence_boost": 0,
                "confidence": None,
            }

        stage = pullback.get("stage", "preopen_only")

        if stage == "preopen_only":
            return {
                "symbol": symbol,
                "pattern_name": "hk_preopen_momentum_pullback",
                "signal_state": "watching",
                "stage": "preopen_only",
                "reason": "waiting_for_pullback",
                "pullback_percent": pullback.get("pullback_percent"),
                "confidence_boost": pullback.get("confidence_boost", 0),
                "confidence": 0.5,
            }

        if stage == "pullback_detected":
            return {
                "symbol": symbol,
                "pattern_name": "hk_preopen_momentum_pullback",
                "signal_state": "watching",
                "stage": "pullback_detected",
                "reason": "controlled_pullback_detected",
                "pullback_percent": pullback.get("pullback_percent"),
                "confidence_boost": pullback.get("confidence_boost", 0),
                "confidence": 0.6,
            }

        if stage == "rebound_started":
            return {
                "symbol": symbol,
                "pattern_name": "hk_preopen_momentum_pullback",
                "signal_state": "watching",
                "stage": "rebound_started",
                "reason": "rebound_started_waiting_for_trigger",
                "pullback_percent": pullback.get("pullback_percent"),
                "trigger_price": pullback.get("continuation_trigger"),
                "confidence_boost": pullback.get("confidence_boost", 0),
                "confidence": 0.7,
            }

        # Continuation signal
        pullback_low = float(pullback["pullback_low"])
        latest_close = float(pullback["latest_close"])
        intraday_high = float(pullback["intraday_high"])

        entry_low = latest_close
        entry_high = latest_close * 1.002
        stop_price = pullback_low * 0.997

        risk_per_share = entry_low - stop_price
        if risk_per_share <= 0:
            return {
                "symbol": symbol,
                "pattern_name": "hk_preopen_momentum_pullback",
                "signal_state": "invalid",
                "stage": "invalid",
                "reason": "bad_risk_structure",
                "confidence_boost": 0,
                "confidence": None,
            }

        target_1 = intraday_high
        target_2 = intraday_high + (intraday_high - pullback_low)
        trigger_price = pullback.get("continuation_trigger") or entry_high

        confidence_value = 0.9 if pullback.get("confidence_boost", 0) >= 15 else 0.7

        return {
            "symbol": symbol,
            "pattern_name": "hk_preopen_momentum_pullback",
            "timeframe": "1m",
            "confidence": confidence_value,
            "signal_state": "watching",
            "stage": "continuation_signal",
            "trigger_price": round(float(trigger_price), 4),
            "entry_low": round(entry_low, 4),
            "entry_high": round(entry_high, 4),
            "stop_price": round(stop_price, 4),
            "target_1": round(target_1, 4),
            "target_2": round(target_2, 4),
            "pullback_percent": pullback["pullback_percent"],
            "confidence_boost": pullback.get("confidence_boost", 0),
            "reason": "controlled_pullback_with_rebound",
        }