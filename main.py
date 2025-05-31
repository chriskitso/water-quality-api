from fastapi import FastAPI, Depends
from pydantic import BaseModel
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from database import get_db, engine
from models import PredictionLog, Base
from datetime import datetime

# ✅ Automatically create tables at startup
Base.metadata.create_all(bind=engine)

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
        input_df = pd.DataFrame([{
            "pH": data.pH,
            "WaterTemp": data.WaterTemp,
            "Turbidity": data.Turbidity,
            "TDS": data.TDS
        }])

        prediction = model.predict(input_df)
        prediction = int(prediction[0])

        if prediction == 1:
            status = "Safe"
            recommendation = "✅ Safe – Water is within recommended quality standards."
        else:
            status = "Unsafe"
            recommendation = "❌ Unsafe – Recommendation: Boil water or use purification before drinking."

        # Log prediction
        log = PredictionLog(
            pH=data.pH,
            WaterTemp=data.WaterTemp,
            Turbidity=data.Turbidity,
            TDS=data.TDS,
            prediction=status,
            recommendation=recommendation,
            timestamp=datetime.utcnow()
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

# View all logs
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(PredictionLog).all()
    return logs
