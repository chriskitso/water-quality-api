from fastapi import FastAPI, Depends
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

from sqlalchemy.orm import Session
from database import get_db
from models import PredictionLog

# Define input data schema
class WaterQualityInput(BaseModel):
    pH: float
    WaterTemp: float
    Turbidity: float
    TDS: float

# Create FastAPI app instance
app = FastAPI()

# Load trained XGBoost model
model = joblib.load("xgboost_water_quality_model.joblib")

# Prediction endpoint
@app.post("/predict")
def predict(data: WaterQualityInput, db: Session = Depends(get_db)):
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([{
            "pH": data.pH,
            "WaterTemp": data.WaterTemp,
            "Turbidity": data.Turbidity,
            "TDS": data.TDS
        }])

        # Make prediction
        prediction = model.predict(input_df)
        prediction = int(prediction[0])  # Convert array to integer

        # Decide on recommendation
        if prediction == 1:
            status = "Safe"
            recommendation = "✅ Safe – Water is within recommended quality standards."
        else:
            status = "Unsafe"
            recommendation = "❌ Unsafe – Recommendation: Boil water or use purification before drinking."

        # Log into the database
        log = PredictionLog(
            pH=data.pH,
            WaterTemp=data.WaterTemp,
            Turbidity=data.Turbidity,
            TDS=data.TDS,
            prediction=status,
            recommendation=recommendation
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        return {
            "prediction": status,
            "recommendation": recommendation
        }

    except Exception as e:
        return {"error": str(e)}

# New route: Get prediction logs
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(PredictionLog).all()
    return logs
