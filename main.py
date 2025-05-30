from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load
import pandas as pd

from database import SessionLocal, create_tables
from models import WaterQualityInput, PredictionLog

# Initialize FastAPI app
app = FastAPI()

# Load trained XGBoost model
model = load("xgboost_water_quality_model.joblib")

# Create database tables if they don't exist
create_tables()

# Prediction endpoint
@app.post("/predict")
def predict(data: WaterQualityInput):
    try:
        # Convert input to DataFrame for the model
        input_df = pd.DataFrame([data.dict()])

        # Make prediction
        prediction = model.predict(input_df)[0]
        status = "Safe" if prediction == 1 else "Unsafe"
        recommendation = (
            "✅ Safe – Water is within recommended quality standards."
            if status == "Safe"
            else "❌ Unsafe – Recommendation: Boil water or use purification before drinking."
        )

        # Log to the database
        db = SessionLocal()
        log = PredictionLog(
            pH=data.pH,
            WaterTemp=data.WaterTemp,
            Turbidity=data.Turbidity,
            TDS=data.TDS,
            prediction=status,
            recommendation=recommendation,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        db.close()

        return {
            "prediction": status,
            "recommendation": recommendation
        }

    except Exception as e:
        return {"error": str(e)}
from fastapi import FastAPI
from pydantic import BaseModel
from joblib import load
import pandas as pd

from database import SessionLocal, create_tables
from models import WaterQualityInput, PredictionLog

# Initialize FastAPI app
app = FastAPI()

# Load trained XGBoost model
model = load("xgboost_water_quality_model.joblib")

# Create database tables if they don't exist
create_tables()

# Prediction endpoint
@app.post("/predict")
def predict(data: WaterQualityInput):
    try:
        # Convert input to DataFrame for the model
        input_df = pd.DataFrame([data.dict()])

        # Make prediction
        prediction = model.predict(input_df)[0]
        status = "Safe" if prediction == 1 else "Unsafe"
        recommendation = (
            "✅ Safe – Water is within recommended quality standards."
            if status == "Safe"
            else "❌ Unsafe – Recommendation: Boil water or use purification before drinking."
        )

        # Log to the database
        db = SessionLocal()
        log = PredictionLog(
            pH=data.pH,
            WaterTemp=data.WaterTemp,
            Turbidity=data.Turbidity,
            TDS=data.TDS,
            prediction=status,
            recommendation=recommendation,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        db.close()

        return {
            "prediction": status,
            "recommendation": recommendation
        }

    except Exception as e:
        return {"error": str(e)}
