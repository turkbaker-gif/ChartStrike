import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AIReview


class AIReviewStore:
    @staticmethod
    def get_by_signal_id(db: Session, signal_id: str) -> AIReview | None:
        stmt = select(AIReview).where(AIReview.signal_id == signal_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, review_payload: dict) -> AIReview:
        review = AIReview(
            signal_id=review_payload["signal_id"],
            symbol=review_payload["symbol"],
            pattern_name=review_payload["pattern_name"],
            verdict=review_payload["verdict"],
            setup_quality=review_payload["setup_quality"],
            analysis=review_payload["analysis"],
            key_risks=json.dumps(review_payload.get("key_risks", [])),
            what_to_wait_for=json.dumps(review_payload.get("what_to_wait_for", [])),
        )

        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def to_dict(review: AIReview) -> dict:
        return {
            "signal_id": review.signal_id,
            "symbol": review.symbol,
            "pattern_name": review.pattern_name,
            "verdict": review.verdict,
            "setup_quality": review.setup_quality,
            "analysis": review.analysis,
            "key_risks": json.loads(review.key_risks or "[]"),
            "what_to_wait_for": json.loads(review.what_to_wait_for or "[]"),
        }