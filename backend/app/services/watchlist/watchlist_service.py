from sqlalchemy.orm import Session
from app.db.models import Watchlist
from app.core.config import settings


class WatchlistService:
    @staticmethod
    def get_active_symbols(db: Session, fallback_to_env: bool = True) -> list[str]:
        """
        Return list of active watchlist symbols from database.
        If no symbols found and fallback_to_env is True, use settings.watchlist_symbols.
        """
        symbols = db.query(Watchlist.symbol).filter(Watchlist.is_active == True).all()
        symbols = [s[0] for s in symbols]

        if not symbols and fallback_to_env:
            # Fallback to environment variable (comma-separated)
            env_symbols = [s.strip() for s in settings.watchlist_symbols.split(",") if s.strip()]
            return env_symbols

        return symbols

    @staticmethod
    def add_symbol(db: Session, symbol: str, notes: str = None) -> Watchlist:
        existing = db.query(Watchlist).filter(Watchlist.symbol == symbol).first()
        if existing:
            existing.is_active = True
            if notes:
                existing.notes = notes
        else:
            new_entry = Watchlist(symbol=symbol, notes=notes)
            db.add(new_entry)
        db.commit()
        return existing or new_entry

    @staticmethod
    def remove_symbol(db: Session, symbol: str) -> bool:
        entry = db.query(Watchlist).filter(Watchlist.symbol == symbol).first()
        if entry:
            entry.is_active = False
            db.commit()
            return True
        return False