from app.services.tracking.signal_status_service import SignalStatusService
from app.services.tracking.trade_plan_service import TradePlanService
from app.services.portfolio.portfolio_risk_service import PortfolioRiskService
from app.services.research.catalyst_service import CatalystService


class TradeChecklistService:
    @staticmethod
    def build(
        signal,
        ai_review,
        db,
        account_size,
        risk_percent,
        max_portfolio_risk_percent,
    ):
        checklist = []

        # 1. Entry Zone
        status = SignalStatusService.build_status(db, signal)
        if status["status"] == "in_entry_zone":
            checklist.append({
                "name": "Entry Zone",
                "status": "pass",
                "message": "Price currently inside entry zone",
            })
        else:
            checklist.append({
                "name": "Entry Zone",
                "status": "warn",
                "message": f"Price status: {status['status']}",
            })

        # 2. Risk Reward (now >= 1.5 passes)
        plan = TradePlanService.build_trade_plan(
            signal=signal,
            account_size=account_size,
            risk_percent=risk_percent,
        )
        rr_target_1 = plan.get("rr_target_1")
        if rr_target_1 is not None and rr_target_1 >= 1.5:
            checklist.append({
                "name": "Risk Reward",
                "status": "pass",
                "message": f"R:R = {rr_target_1}",
            })
        else:
            checklist.append({
                "name": "Risk Reward",
                "status": "warn",
                "message": f"Low R:R = {rr_target_1}",
            })

        # 3. Portfolio Heat
        risk = PortfolioRiskService.build_portfolio_risk(
            db=db,
            account_size=account_size,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
        )
        if risk["within_limit"]:
            checklist.append({
                "name": "Portfolio Heat",
                "status": "pass",
                "message": f"Current risk {risk['current_open_risk_percent']}%",
            })
        else:
            checklist.append({
                "name": "Portfolio Heat",
                "status": "fail",
                "message": "Portfolio risk exceeded",
            })

        # 4. AI Verdict
        if ai_review and ai_review.verdict == "actionable":
            checklist.append({
                "name": "AI Verdict",
                "status": "pass",
                "message": "AI considers setup actionable",
            })
        else:
            checklist.append({
                "name": "AI Verdict",
                "status": "warn",
                "message": "AI verdict not strongly positive",
            })

        # 5. Setup Quality
        if ai_review and ai_review.setup_quality in ["clean", "acceptable"]:
            checklist.append({
                "name": "Setup Quality",
                "status": "pass",
                "message": f"Setup quality is {ai_review.setup_quality}",
            })
        else:
            checklist.append({
                "name": "Setup Quality",
                "status": "warn",
                "message": "Setup quality is not ideal",
            })

        # 6. Catalyst Confidence (now medium also passes)
        catalyst = CatalystService.build(signal.symbol)
        if catalyst["confidence"] in ("high", "medium"):
            checklist.append({
                "name": "Catalyst Confidence",
                "status": "pass",
                "message": f"{catalyst['catalyst_type']} with {catalyst['confidence']} confidence",
            })
        else:
            checklist.append({
                "name": "Catalyst Confidence",
                "status": "warn",
                "message": "Catalyst confidence is low or unclear",
            })

        # 7. Timing / Extension
        live_status = status.get("status", "unknown")
        if live_status in {"above_entry", "target_1_hit", "target_2_hit"}:
            checklist.append({
                "name": "Timing",
                "status": "warn" if live_status == "above_entry" else "fail",
                "message": "The setup may already be extended relative to the planned entry zone.",
            })
        elif live_status == "in_entry_zone":
            checklist.append({
                "name": "Timing",
                "status": "pass",
                "message": "Timing is aligned with the intended entry area.",
            })
        else:
            checklist.append({
                "name": "Timing",
                "status": "warn",
                "message": "Timing is not ideal yet. This may need patience.",
            })

        # Final verdict
        fail_count = sum(1 for c in checklist if c["status"] == "fail")
        warn_count = sum(1 for c in checklist if c["status"] == "warn")

        if fail_count > 0:
            verdict = "avoid"
        elif warn_count > 2:
            verdict = "wait"
        else:
            verdict = "ready"

        return {
            "symbol": signal.symbol,
            "verdict": verdict,
            "checklist": checklist,
        }