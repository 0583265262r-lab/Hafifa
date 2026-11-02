from database import SessionLocal, engine
from models import AirQuality, Alert
from pathlib import Path

db = SessionLocal()

try:
    print("Database:", Path(engine.url.database).resolve())

    air_quality_count = db.query(AirQuality).count()
    alerts_count = db.query(Alert).count()

    print("Air quality records:", air_quality_count)
    print("Alerts records:", alerts_count)

finally:
    db.close()