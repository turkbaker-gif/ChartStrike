class SignalIntelligence:
    @staticmethod
    def build(signal, trade_plan, catalyst):
        rr = trade_plan.get("rr_target_1") or 0

        if rr >= 3:
            momentum = "Strong"
        elif rr >= 2:
            momentum = "Moderate"
        else:
            momentum = "Weak"

        if catalyst.get("headline_count", 0) > 0:
            catalyst_label = "News catalyst detected"
        else:
            catalyst_label = "No major news"

        if rr >= 3 and catalyst.get("headline_count", 0) > 0:
            verdict = "High probability setup with catalyst"
        elif rr >= 3:
            verdict = "Technically strong setup"
        elif rr >= 2:
            verdict = "Acceptable trade structure"
        else:
            verdict = "Low quality trade"

        return {
            "momentum": momentum,
            "risk_reward": rr,
            "catalyst": catalyst_label,
            "verdict": verdict,
        }