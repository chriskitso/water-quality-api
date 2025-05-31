from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import joblib

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for strict security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your model
model = joblib.load("xgboost_model.pkl")

# Define schema for incoming sensor data
class SensorData(BaseModel):
    TDS: float
    Turbidity: float
    pH: float
    WaterTemp: float

# Sample logs store
logs = []

@app.post("/predict")
def predict(data: SensorData):
    features = [[data.TDS, data.Turbidity, data.pH, data.WaterTemp]]
    prediction = model.predict(features)[0]

    # Generate recommendation
    recommendation = (
        "✅ Safe – Water is within recommended quality standards."
        if prediction == "Safe"
        else "❌ Unsafe – Recommendation: Boil water or use purification before drinking."
    )

    log = {
        "id": len(logs) + 1,
        "TDS": data.TDS,
        "Turbidity": data.Turbidity,
        "pH": data.pH,
        "WaterTemp": data.WaterTemp,
        "prediction": prediction,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow()
    }

    logs.append(log)
    return log

@app.get("/logs")
def get_logs():
    return logs
