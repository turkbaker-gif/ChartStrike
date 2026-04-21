class HKWatchlistService:
    @staticmethod
    def build_today_watchlist(scan_results: list[dict]) -> list[dict]:
        qualified = [item for item in scan_results if item.get("qualified")]

        qualified.sort(
            key=lambda x: float(x.get("percent_change", 0)),
            reverse=True,
        )

        return qualified