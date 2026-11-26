
from pathlib import Path
import joblib

from fastapi import FastAPI
from pydantic import BaseModel, Field

# Project paths
ROOT = Path(__file__).resolve().parent.parent

# Load trained model and threshold
model = joblib.load(ROOT / "ml" / "fraud_model.joblib")
threshold = joblib.load(ROOT / "ml" / "threshold.joblib")

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="API for detecting suspicious transactions",
    version="1.0"
)

# Transaction input
class Transaction(BaseModel):
    amount: float = Field(ge=0)
    hour: int = Field(ge=0, le=23)
    international: int = Field(ge=0, le=1)
    online: int = Field(ge=0, le=1)
    recent_transactions: int = Field(ge=0)
    account_age_days: int = Field(ge=0)

# Home endpoint
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running!"}

# Fraud prediction endpoint
@app.post("/predict")
def predict(transaction: Transaction):

    data = [[
        transaction.amount,
        transaction.hour,
        transaction.international,
        transaction.online,
        transaction.recent_transactions,
        transaction.account_age_days
    ]]

    probability = model.predict_proba(data)[0][1]

    prediction = int(probability >= threshold)

    return {
        "prediction": prediction,
        "result": "Fraudulent" if prediction == 1 else "Legitimate",
        "fraud_probability": round(float(probability), 4),
        "threshold": float(threshold)
    }
