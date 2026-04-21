from fastapi import APIRouter, HTTPException

from app.services.market.quote_service import QuoteService

router = APIRouter()


@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    quote = QuoteService.get_latest_quote(symbol)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    return quote