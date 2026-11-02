import csv 
import io
import math
from datetime import datetime
from error_handlers import InvalidCSVError

def process_csv(file_content):
    valid_row = []
    invalid_row = []

    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InvalidCSVError("CSV file must be UTF-8 encoded")

    csv_reader = csv.DictReader(io.StringIO(text))

    required_columns = {"date", "city", "PM2.5", "NO2", "CO2"}

    if not required_columns.issubset(csv_reader.fieldnames or []):
        raise InvalidCSVError("CSV file is missing required columns")

    for row_number, row in enumerate(csv_reader, start=2):
        try:
            date = datetime.strptime(
                row["date"], "%Y-%m-%d"
            ).date()

            city = row["city"].strip()

            pm25 = float(row["PM2.5"])
            no2 = float(row["NO2"])
            co2 = float(row["CO2"])

            if not city:
                raise ValueError("city cannot be empty")
            
            if any(
                value < 0 or not math.isfinite(value)
                for value in [pm25,no2,co2]
            ):
                raise ValueError("Invalid pollutant value")
            valid_row.append({
                "date":date,
                "city":city,
                "pm25":pm25,
                "no2":no2,
                "co2":co2
            })

        except (ValueError, TypeError, KeyError, AttributeError) as e:
            invalid_row.append({
                "row": row_number,
                "error": str(e)
            })
    return valid_row, invalid_row
        