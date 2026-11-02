from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class AirQuality(Base):
    __tablename__ = "air_quality"

    id = Column(Integer,primary_key=True,index=True)
    date = Column(Date,nullable=False)
    city = Column(String,nullable=False)
    pm25 =Column(Float,nullable=False)
    no2 = Column(Float,nullable=False)
    co2 = Column(Float,nullable=False)
    aqi = Column(Float,nullable=False)
    aqi_level = Column(String,nullable=False)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer,primary_key=True,index=True)
    date = Column(Date,nullable=False)
    city = Column(String,nullable=False)
    aqi = Column(Float,nullable=False)