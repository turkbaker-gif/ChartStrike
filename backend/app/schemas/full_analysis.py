from pydantic import BaseModel

from app.schemas.signal import SignalOut
from app.schemas.explanation import SignalExplanationOut
from app.schemas.ai_review import AIReviewOut
from app.schemas.signal_status import SignalStatusOut


class SignalWithStatusOut(SignalOut):
    live_status: SignalStatusOut | None = None


class FullAnalysisOut(BaseModel):
    signal: SignalWithStatusOut
    explanation: SignalExplanationOut
    ai_review: AIReviewOut | None = None