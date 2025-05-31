from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from database import get_db, engine
from models import PredictionLog, Base
from datetime import datetime

# ✅ Automatically create tables at startup
Base.metadata.create_all(bind=engine)

# ✅ Enable CORS so your frontend can access the API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your frontend URL instead of "*" for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Define input data schema
class WaterQualityInput(BaseModel):
    pH: float
    WaterTemp: float
    Turbidity: float
    TDS: float

# ✅ Load trained XGBoost model
model = joblib.load("xgboost_water_quality_model.joblib")

# ✅ Prediction endpoint
@app.post("/predict")
def predict(data: WaterQualityInput, db: Session = Depends(get_db)):
    try:
        input_df = pd.DataFrame([{
            "pH": data.pH,
            "WaterTemp": data.WaterTemp,
            "Turbidity": data.Turbidity,
            "TDS": data.TDS
        }])

        prediction = model.predict(input_df)[0]

        if prediction == 1:
            status = "Safe"
            recommendation = "✅ Safe – Water is within recommended quality standards."
        else:
            status = "Unsafe"
            recommendation = "❌ Unsafe – Recommendation: Boil water or use purification before drinking."

        # ✅ Log prediction to DB
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

# ✅ Logs endpoint - returns a clean list
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(PredictionLog).order_by(PredictionLog.timestamp.desc()).all()

    # Convert ORM models to dicts
    return [
        {
            "id": log.id,
            "pH": log.pH,
            "WaterTemp": log.WaterTemp,
            "Turbidity": log.Turbidity,
            "TDS": log.TDS,
            "prediction": log.prediction,
            "recommendation": log.recommendation,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]
