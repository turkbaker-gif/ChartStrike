class FeatureEngine:

    @staticmethod
    def compute_breakout_features(candles):

        ordered = sorted(candles, key=lambda c: c.ts)

        current = ordered[-1]

        history = ordered[-21:-1]

        high_20 = max(float(c.high) for c in history)

        avg_volume_20 = sum(float(c.volume) for c in history) / len(history)

        ma20 = sum(float(c.close) for c in history) / len(history)

        avg_range = sum(
            float(c.high) - float(c.low)
            for c in history
        ) / len(history)

        current_close = float(current.close)

        current_volume = float(current.volume)

        rvol = current_volume / avg_volume_20

        return {
            "current_close": current_close,
            "high_20": high_20,
            "relative_volume": rvol,
            "ma20": ma20,
            "avg_range_20": avg_range
        }