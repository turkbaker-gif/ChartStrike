class SignalRankingEngine:

    @staticmethod
    def compute_score(signal, trade_plan=None, catalyst=None):

        score = 0

        # pattern quality
        if signal.pattern_name:
            score += 20

        # momentum strength
        if signal.pattern_strength == "strong":
            score += 25
        elif signal.pattern_strength == "moderate":
            score += 15
        else:
            score += 5

        # risk reward
        if trade_plan:
            rr = trade_plan.get("rr_target_1") or 0

            if rr >= 3:
                score += 30
            elif rr >= 2:
                score += 20
            else:
                score += 10

        # catalyst
        if catalyst and catalyst.get("headline_count", 0) > 0:
            score += 25

        return min(score, 100)