from app.services.market.data_service import LocalDataService

class SignalStatusService:
    @staticmethod
    def build_status(db, signal) -> dict:
        """Quote‑driven status using local stock_prices table."""
        latest_price = LocalDataService.get_latest_price(db, signal.symbol)

        if latest_price is None:
            return {
                "status": "watching",
                "summary": "No local price data available yet.",
                "latest_price": None,
                "distance_to_entry_pct": None,
                "distance_to_stop_pct": None,
                "distance_to_target_1_pct": None,
                "distance_to_target_2_pct": None,
            }

        entry_low = float(signal.entry_low) if signal.entry_low is not None else None
        entry_high = float(signal.entry_high) if signal.entry_high is not None else None
        stop_price = float(signal.stop_price) if signal.stop_price is not None else None
        target_1 = float(signal.target_1) if signal.target_1 is not None else None
        target_2 = float(signal.target_2) if signal.target_2 is not None else None

        def pct_distance(current: float, level: float | None):
            if level is None or level == 0:
                return None
            return round(((current - level) / level) * 100, 2)

        status = "watching"
        summary = "Monitoring setup."

        if stop_price is not None and latest_price <= stop_price:
            status = "invalidated"
            summary = "Price is at or below the stop level. Setup is invalidated."
        elif target_2 is not None and latest_price >= target_2:
            status = "target_2_hit"
            summary = "Price has reached target 2."
        elif target_1 is not None and latest_price >= target_1:
            status = "target_1_hit"
            summary = "Price has reached target 1."
        elif entry_low is not None and entry_high is not None and entry_low <= latest_price <= entry_high:
            status = "in_entry_zone"
            summary = "Price is inside the planned entry zone."
        elif entry_low is not None and latest_price < entry_low:
            status = "below_entry"
            summary = "Price is still below the entry zone."
        elif entry_high is not None and latest_price > entry_high:
            status = "above_entry"
            summary = "Price is above the entry zone and may be getting extended."

        return {
            "status": status,
            "summary": summary,
            "latest_price": round(latest_price, 4),
            "distance_to_entry_pct": pct_distance(latest_price, entry_low),
            "distance_to_stop_pct": pct_distance(latest_price, stop_price),
            "distance_to_target_1_pct": pct_distance(latest_price, target_1),
            "distance_to_target_2_pct": pct_distance(latest_price, target_2),
        }