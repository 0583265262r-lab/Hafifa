from datetime import date
from fastapi import Query

from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base, get_db
from models import AirQuality, Alert
from csv_service import process_csv
from calculate_aqi import calculate_aqi
from error_handlers import register_exception_handlers
from air_quality_service import (save_air_quality_data,
                                 get_all_air_quality,
                                 get_air_quality_by_date_range,
                                 get_air_quality_by_city,
                                 get_city_aqi_history,
                                 get_city_aqi_average,
                                 get_all_alerts,
                                 get_alerts_by_date,
                                 get_alerts_by_city)
from logging_config import logger


app = FastAPI()

register_exception_handlers(app)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Air Quality API is running"}

@app.post("/air-quality/upload")
async def upload_air_quality(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    logger.info(f"CSV upload started: {file.filename}")

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    content = await file.read()

    valid_rows, invalid_rows = process_csv(content)

    logger.info(
    f"CSV validation completed: "
    f"{len(valid_rows)} valid rows, "
    f"{len(invalid_rows)} invalid rows"
)

    result = save_air_quality_data(db, valid_rows)

    return {
        "message": "File processed successfully",
        "saved_rows": result["saved_rows"],
        "alerts_created": result["alerts_created"],
        "invalid_rows": invalid_rows
    }
@app.get("/all_air_quality")
def get_all_air_qualities(db: Session = Depends(get_db)):

    return get_all_air_quality(db)

@app.get("/air-quality")
def get_air_quality(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date"
        )

    return get_air_quality_by_date_range(
        db,
        start_date,
        end_date
    )

@app.get("/air-quality/city")
def get_city_air_quality(
    city: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return get_air_quality_by_city(db, city)

@app.get("/air-quality/history")
def city_aqi_history(
    city: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return get_city_aqi_history(db, city)

@app.get("/air-quality/average")
def city_aqi_average(
    city: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return get_city_aqi_average(db, city)

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):

    return get_all_alerts(db)

@app.get("/alerts/date")
def alerts_by_date(
    date: date = Query(...),
    db: Session = Depends(get_db)
):
    return get_alerts_by_date(db, date)

@app.get("/alerts/city")
def alerts_by_city(
    city: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    return get_alerts_by_city(db, city)



