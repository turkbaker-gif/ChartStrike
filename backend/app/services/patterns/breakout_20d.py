from app.services.patterns.base import BasePattern


class Breakout20DPattern(BasePattern):

    name = "breakout_20d"

    timeframe = "1m"

    def evaluate(self, symbol, features):

        close = features["current_close"]

        high_20 = features["high_20"]

        rvol = features["relative_volume"]

        ma20 = features["ma20"]

        triggered = close > high_20 and rvol >= 1.8 and close > ma20

        confidence = 0

        if triggered:
            confidence = min(0.95, 0.6 + (rvol * 0.08))

        return {
            "triggered": triggered,
            "pattern_name": self.name,
            "trigger_price": close if triggered else None,
            "confidence": confidence,
            "evidence": features
        }