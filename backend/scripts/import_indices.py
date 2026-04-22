# backend/scripts/import_indices.py
import csv
from app.db.session import SessionLocal
from app.db.models import Index  # We'll create this model next

def import_indices(csv_file_path: str):
    """Imports index data from a CSV file into the indices table."""
    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                # Adjust these field names to match the headers in your CSV file!
                symbol = row.get('symbol')
                name = row.get('name')
                description = row.get('description')
                index_type = row.get('type')
                region = row.get('region')
                exchange = row.get('exchange')
                currency = row.get('Currency')

                if not symbol or not name:
                    print(f"Skipping row with missing symbol or name: {row}")
                    continue

                # Remove any trailing/leading whitespace
                symbol = symbol.strip()
                name = name.strip()
                
                index_type = index_type.strip().lower()
                region = region.strip() if region else 'Global'
                exchange = exchange.strip() if exchange else 'N/A'
                currency = currency.strip() if currency else 'N/A'

                # Check if index already exists
                existing_index = db.query(Index).filter(Index.symbol == symbol).first()
                if existing_index:
                    # Update existing record
                    existing_index.name = name
                    existing_index.description = description # <-- Update description
                    existing_index.type = index_type
                    existing_index.region = region
                    existing_index.exchange = exchange
                    existing_index.currency = currency
                else:
                    # Add new record
                    new_index = Index(
                        symbol=symbol,
                        name=name,
                        description=description, # <-- Add description
                        type=index_type,
                        region=region,
                        exchange=exchange,
                        currency=currency,
                        is_active=True
                    )
                    db.add(new_index)
                count += 1
                if count % 50 == 0:
                    db.commit()
                    print(f"Committed {count} records...")
            db.commit()
            print(f"Finished importing {count} records from {csv_file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_indices('data/indices.csv')