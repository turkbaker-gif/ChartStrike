from fastapi import APIRouter
from app.services.market.itick_client import ITickClient

router = APIRouter()

INDEX_CODES = ["HSI", "HSCEI", "000300", "000001"]

@router.get("/index-quotes")
def get_index_quotes():
    quotes = ITickClient.get_batch_index_quotes(INDEX_CODES)
    return quotes