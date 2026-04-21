from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE simulated_trades ADD COLUMN partial_closed BOOLEAN DEFAULT 0"))
    conn.execute(text("ALTER TABLE simulated_trades ADD COLUMN remaining_shares INTEGER"))
    conn.commit()
    print("Columns added successfully.")