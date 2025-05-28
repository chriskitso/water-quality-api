from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

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
def predict(data: WaterQualityInput):
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

        return {
            "prediction": status,
            "recommendation": recommendation
        }

    except Exception as e:
        return {"error": str(e)}
