from app.db.models import Signal


class TradePlanService:
    @staticmethod
    def build_trade_plan(
        signal: Signal,
        account_size: float,
        risk_percent: float,
    ) -> dict:
        entry_price = float(signal.entry_low) if signal.entry_low is not None else None
        stop_price = float(signal.stop_price) if signal.stop_price is not None else None
        target_1 = float(signal.target_1) if signal.target_1 is not None else None
        target_2 = float(signal.target_2) if signal.target_2 is not None else None

        if entry_price is None or stop_price is None:
            raise ValueError("Signal is missing entry or stop price")

        risk_amount = account_size * (risk_percent / 100)
        risk_per_share = abs(entry_price - stop_price)

        if risk_per_share <= 0:
            raise ValueError("Risk per share must be greater than zero")

        position_size_shares = int(risk_amount // risk_per_share)
        position_value = position_size_shares * entry_price
        max_loss = position_size_shares * risk_per_share

        reward_target_1 = None
        reward_target_2 = None
        rr_target_1 = None
        rr_target_2 = None

        if target_1 is not None:
            reward_per_share_1 = target_1 - entry_price
            reward_target_1 = position_size_shares * reward_per_share_1
            rr_target_1 = reward_per_share_1 / risk_per_share if risk_per_share > 0 else None

        if target_2 is not None:
            reward_per_share_2 = target_2 - entry_price
            reward_target_2 = position_size_shares * reward_per_share_2
            rr_target_2 = reward_per_share_2 / risk_per_share if risk_per_share > 0 else None

        return {
            "signal_id": signal.id,
            "symbol": signal.symbol,
            "account_size": round(account_size, 2),
            "risk_percent": round(risk_percent, 2),
            "risk_amount": round(risk_amount, 2),
            "entry_price": round(entry_price, 4),
            "stop_price": round(stop_price, 4),
            "target_1": round(target_1, 4) if target_1 is not None else None,
            "target_2": round(target_2, 4) if target_2 is not None else None,
            "risk_per_share": round(risk_per_share, 4),
            "position_size_shares": position_size_shares,
            "position_value": round(position_value, 2),
            "max_loss": round(max_loss, 2),
            "reward_target_1": round(reward_target_1, 2) if reward_target_1 is not None else None,
            "reward_target_2": round(reward_target_2, 2) if reward_target_2 is not None else None,
            "rr_target_1": round(rr_target_1, 2) if rr_target_1 is not None else None,
            "rr_target_2": round(rr_target_2, 2) if rr_target_2 is not None else None,
        }