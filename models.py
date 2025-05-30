from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    pH = Column(Float, nullable=False)
    WaterTemp = Column(Float, nullable=False)
    Turbidity = Column(Float, nullable=False)
    TDS = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)
    recommendation = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
