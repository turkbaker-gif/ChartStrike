from sqlalchemy import text
from sqlalchemy.orm import Session
import re

class LocalDataService:
    # ------------------------------------------------------------------
    # 1. Ensure the mapping table exists (idempotent)
    # ------------------------------------------------------------------
    @staticmethod
    def _ensure_mapping_table(db: Session) -> None:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS symbol_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_itick TEXT UNIQUE NOT NULL,
                symbol_local TEXT UNIQUE,
                name TEXT,
                exchange TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        db.commit()

    # ------------------------------------------------------------------
    # 2. Normalize any HK or CN symbol to the iTick format
    #    HK: 06166.HK -> 6166.HK (or just 6166 depending on iTick preference)
    #    CN: 600519.SH -> 600519, 000001.SZ -> 000001
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_to_itick(symbol: str) -> str:
        # HK symbols: strip leading zeros, keep .HK suffix if needed by iTick
        # (iTick actually expects just the numeric code, but we'll use 6166.HK for consistency)
        if symbol.endswith(".HK"):
            code = symbol[:-3]  # remove .HK
            code = code.lstrip("0") or "0"  # strip leading zeros, but keep at least one digit
            return f"{code}.HK"
        
        # CN symbols: 600519.SH -> 600519, 000001.SZ -> 000001
        if symbol.endswith(".SH") or symbol.endswith(".SZ"):
            code = symbol[:-3]  # remove .SH or .SZ
            code = code.lstrip("0") or "0"
            return code  # iTick uses plain numeric code for CN stocks
        
        return symbol

    # ------------------------------------------------------------------
    # 3. Register a symbol in the mapping table if not already present
    # ------------------------------------------------------------------
    @staticmethod
    def _register_symbol(db: Session, local_symbol: str) -> None:
        itick_symbol = LocalDataService._normalize_to_itick(local_symbol)
        db.execute(
            text("""
                INSERT OR IGNORE INTO symbol_mapping (symbol_itick, symbol_local)
                VALUES (:itick, :local)
            """),
            {"itick": itick_symbol, "local": local_symbol}
        )
        db.commit()

    # ------------------------------------------------------------------
    # 4. Resolve any symbol (local or already itick) to the itick format
    # ------------------------------------------------------------------
    @staticmethod
    def resolve_symbol(db: Session, symbol: str) -> str:
        LocalDataService._ensure_mapping_table(db)

        # First, try to find the symbol in the mapping table
        result = db.execute(
            text("""
                SELECT symbol_itick FROM symbol_mapping
                WHERE symbol_local = :symbol OR symbol_itick = :symbol
            """),
            {"symbol": symbol}
        )
        row = result.fetchone()
        if row:
            return row[0]

        # Not found → register it now and return the normalized form
        LocalDataService._register_symbol(db, symbol)
        return LocalDataService._normalize_to_itick(symbol)

    # ------------------------------------------------------------------
    # 5. Get recent candles using the RESOLVED symbol
    # ------------------------------------------------------------------
    @staticmethod
    def get_recent_candles(db: Session, symbol: str, limit: int = 50) -> list[dict]:
        resolved = LocalDataService.resolve_symbol(db, symbol)

        query = text("""
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE symbol = :symbol
            ORDER BY date DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"symbol": resolved, "limit": limit})
        rows = result.fetchall()

        candles = [dict(row._mapping) for row in rows]
        return list(reversed(candles))

    # ------------------------------------------------------------------
    # 6. Get latest price using the RESOLVED symbol
    # ------------------------------------------------------------------
    @staticmethod
    def get_latest_price(db: Session, symbol: str) -> float | None:
        resolved = LocalDataService.resolve_symbol(db, symbol)

        query = text("""
            SELECT close FROM stock_prices
            WHERE symbol = :symbol
            ORDER BY date DESC
            LIMIT 1
        """)
        result = db.execute(query, {"symbol": resolved})
        row = result.fetchone()
        return float(row[0]) if row else None