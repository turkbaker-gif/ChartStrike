from pydantic import BaseModel


class ChecklistItem(BaseModel):
    name: str
    status: str
    message: str


class TradeChecklistOut(BaseModel):
    symbol: str
    verdict: str
    checklist: list[ChecklistItem]