import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.market.market_data_service import MarketDataService


def run():
    print("Starting Market Refresh Worker")

    while True:
        db: Session = SessionLocal()

        try:
            for symbol in settings.watchlist:
                result = MarketDataService.refresh_candles_for_symbol(
                    db=db,
                    symbol=symbol,
                    interval="1m",
                    outputsize=100,
                )
                print("market refresh:", result)

        except Exception as e:
            print("market refresh error:", e)

        finally:
            db.close()

        time.sleep(120)


if __name__ == "__main__":
    run()