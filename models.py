from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, String
from database import Base

# Pydantic model for request validation
class WaterQualityInput(BaseModel):
    pH: float
    WaterTemp: float
    Turbidity: float
    TDS: float

# SQLAlchemy model for logging to the database
class PredictionLog(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    pH = Column(Float)
    WaterTemp = Column(Float)
    Turbidity = Column(Float)
    TDS = Column(Float)
    prediction = Column(String)
    recommendation = Column(String)
