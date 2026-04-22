# backend/scripts/import_stock_master.py
import csv
from app.db.session import SessionLocal
from app.db.models import Stock

def import_csv_to_db(csv_file_path: str, region: str, exchange: str, currency: str):
    """Imports stock data from a CSV file into the stocks table."""
    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                # Adjust these field names to match the headers in your CSV files!
                # Common headers might be 'Symbol', 'Name', 'Type', etc.
                symbol = row.get('symbol')
                name = row.get('name')
                asset_type = row.get('type')

                if not symbol or not name:
                    print(f"Skipping row with missing symbol or name: {row}")
                    continue

                # Remove any trailing/leading whitespace
                symbol = symbol.strip()
                name = name.strip()
                asset_type = asset_type.strip().lower()

                # Check if stock already exists
                existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
                if existing_stock:
                    print(f"Updating existing stock: {symbol}")
                    existing_stock.name = name
                    existing_stock.type = asset_type
                    existing_stock.region = region
                    existing_stock.exchange = exchange
                    existing_stock.currency = currency
                else:
                    print(f"Adding new stock: {symbol}")
                    new_stock = Stock(
                        symbol=symbol,
                        name=name,
                        type=asset_type,
                        region=region,
                        exchange=exchange,
                        currency=currency,
                        is_active=True
                    )
                    db.add(new_stock)
                count += 1
                if count % 100 == 0:
                    db.commit()  # Commit in batches
                    print(f"Committed {count} records...")
            db.commit()
            print(f"Finished importing {count} records from {csv_file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Importing Hong Kong stocks...")
    import_csv_to_db('data/stock-hk.csv', region='HK', exchange='HKEX', currency='HKD')
    
    print("\nImporting China stocks...")
    import_csv_to_db('data/stock-cn.csv', region='CN', exchange='SSE', currency='CNY')
    # Note: For China stocks, the region should be 'SH' or 'SZ' depending on the exchange.
    # You might need to inspect the CSV file to determine the correct region.