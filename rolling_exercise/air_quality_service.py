from sqlalchemy.orm import Session
from sqlalchemy import func

from models import AirQuality, Alert
from calculate_aqi import calculate_aqi
from logging_config import logger
from datetime import date
from sqlalchemy.orm import Session
from models import AirQuality


def save_air_quality_data(db: Session, valid_rows: list):

    saved_rows = 0
    alerts_created = 0

    for row in valid_rows:

        aqi, level = calculate_aqi(
            row["pm25"],
            row["no2"],
            row["co2"]
        )

        logger.info(
            f"AQI calculated for {row['city']}: {aqi}"
        )

        if aqi > 300:

            alert = Alert(
                date=row["date"],
                city=row["city"],
                aqi=aqi
            )

            db.add(alert)

            alerts_created += 1

            logger.warning(
                f"Alert added for {row['city']}: AQI {aqi}"
            )

        else:

            air_quality = AirQuality(
                date=row["date"],
                city=row["city"],
                pm25=row["pm25"],
                no2=row["no2"],
                co2=row["co2"],
                aqi=aqi,
                aqi_level=level
            )

            db.add(air_quality)

            saved_rows += 1

    db.commit()

    logger.info(
        f"Database commit completed. "
        f"Saved rows: {saved_rows}, "
        f"Alerts: {alerts_created}"
    )

    return {
        "saved_rows": saved_rows,
        "alerts_created": alerts_created
    }
def get_all_air_quality(db: Session):

    air_quality = db.query(AirQuality).all()

    logger.info("All air quality requested")

    return air_quality
def get_air_quality_by_date_range(
    db: Session,
    start_date: date,
    end_date: date
):
    return db.query(AirQuality).filter(
        AirQuality.date >= start_date,
        AirQuality.date <= end_date
    ).all()
def get_air_quality_by_city(db: Session, city: str):

    results = db.query(AirQuality).filter(
        AirQuality.city == city
    ).all()

    logger.info(f"Air quality data requested for city: {city}")

    return results

def get_city_aqi_history(db: Session, city: str):

    results = db.query(
        AirQuality.date,
        AirQuality.aqi,
        AirQuality.aqi_level
    ).filter(
        AirQuality.city == city
    ).order_by(
        AirQuality.date.asc()
    ).all()

    logger.info(f"AQI history requested for city: {city}")

    return [
        {
            "date": row.date,
            "aqi": row.aqi,
            "aqi_level": row.aqi_level
        }
        for row in results
    ]
def get_city_aqi_average(db: Session, city: str):

    average = db.query(
        func.avg(AirQuality.aqi)
    ).filter(
        AirQuality.city == city
    ).scalar()

    logger.info(f"Average AQI requested for city: {city}")

    if average is None:
        return {
            "city": city,
            "average_aqi": None,
            "message": "No data found for this city"
        }

    return {
        "city": city,
        "average_aqi": round(average, 2)
    }
def get_all_alerts(db: Session):

    alerts = db.query(Alert).all()

    logger.info("All alerts requested")

    return alerts

def get_alerts_by_date(db: Session, selected_date: date):

    alerts = db.query(Alert).filter(
        Alert.date == selected_date
    ).all()

    logger.info(f"Alerts requested for date: {selected_date}")

    return alerts

def get_alerts_by_city(db: Session, city: str):

    alerts = db.query(Alert).filter(
        Alert.city == city
    ).all()

    logger.info(f"Alerts requested for city: {city}")

    return alerts