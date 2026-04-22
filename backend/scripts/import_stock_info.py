# backend/scripts/import_stock_info.py
import time
import httpx
from sqlalchemy.orm import Session
from datetime import datetime
from ratelimit import limits, sleep_and_retry

from app.db.session import SessionLocal
from app.db.models import Stock, StockInformation
from app.core.config import settings

# Rate limit: 120 calls per 60 seconds
ONE_MINUTE = 60
CALLS_PER_MINUTE = 120

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=ONE_MINUTE)
def fetch_stock_info(code: str, region: str) -> dict | None:
    """Fetches stock information from the iTick API."""
    url = "https://api.itick.org/stock/info"
    params = {
        "type": "stock",
        "region": region.upper(),
        "code": code,
    }
    headers = {
        "accept": "application/json",
        "token": settings.itick_api_token,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                print(f"API Error for {code}.{region}: {data.get('msg')}")
                return None

            return data.get("data")
    except Exception as e:
        print(f"Request failed for {code}.{region}: {e}")
        return None

def import_all_stock_info():
    """Iterates through all active stocks and imports their information."""
    db = SessionLocal()
    try:
        # Get all active stocks with their symbol (code) and region
        stocks = db.query(Stock).filter(Stock.is_active == True).all()
        total_stocks = len(stocks)
        print(f"Found {total_stocks} active stocks to process.")

        for i, stock in enumerate(stocks, 1):
            print(f"Processing {i}/{total_stocks}: {stock.symbol}.{stock.region}")

            api_data = fetch_stock_info(stock.symbol, stock.region)
            if not api_data:
                continue

            # Check if we already have an entry for this full symbol (e.g., "0700.HK")
            full_symbol = f"{stock.symbol}.{stock.region}"
            existing_info = db.query(StockInformation).filter(
                StockInformation.symbol == full_symbol
            ).first()

            info_data = {
                "symbol": full_symbol,
                "name": api_data.get("n"),
                "name_zh": None,
                "type": api_data.get("t"),
                "exchange": api_data.get("e"),
                "sector": api_data.get("s"),
                "industry": api_data.get("i"),
                "locale": api_data.get("l"),
                "currency": api_data.get("r"),
                "business_description": api_data.get("bd"),
                "website_url": api_data.get("wu"),
                "market_cap": api_data.get("mcb"),
                "shares_outstanding": api_data.get("tso"),
                "pe_ratio": api_data.get("pet"),
                "financial_currency": api_data.get("fcc"),
                "high_52w": api_data.get("ph52"),
                "low_52w": api_data.get("pl52"),
            }

            if existing_info:
                for key, value in info_data.items():
                    if key != "symbol":
                        setattr(existing_info, key, value)
                existing_info.updated_at = datetime.utcnow()
                print(f"Updated information for {full_symbol}")
            else:
                new_info = StockInformation(**info_data)
                db.add(new_info)
                print(f"Added information for {full_symbol}")

            # Commit every 10 stocks
            if i % 10 == 0:
                db.commit()
                print(f"Committed batch of 10 records.")

        db.commit()
        print("Stock information import completed successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting stock information import...")
    import_all_stock_info()