class RiskModel:

    @staticmethod
    def build_trade_levels(trigger_price, breakout_level, avg_range):

        entry_low = trigger_price

        entry_high = trigger_price + (avg_range * 0.25)

        stop_price = breakout_level

        risk = entry_low - stop_price

        target_1 = entry_low + (risk * 1.5)

        target_2 = entry_low + (risk * 2.5)

        return {
            "entry_low": entry_low,
            "entry_high": entry_high,
            "stop_price": stop_price,
            "target_1": target_1,
            "target_2": target_2
        }