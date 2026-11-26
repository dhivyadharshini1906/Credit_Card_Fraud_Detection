from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db, Transaction
from app.schemas import TransactionInput

ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = ROOT / "ml" / "fraud_model.joblib"
app = FastAPI(title="Transaction Risk Intelligence API")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")
model = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    global model
    init_db()
    if MODEL_FILE.exists():
        model = joblib.load(MODEL_FILE)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/api/predict")
def predict(item: TransactionInput, db: Session = Depends(get_db)):
    if model is None:
        raise HTTPException(503, "Train the model first: python ml/train_model.py")
    X = pd.DataFrame([item.model_dump()])
    score = float(model.predict_proba(X)[0][1]) * 100
    level = "High" if score >= 70 else "Medium" if score >= 30 else "Low"
    prediction = "Potentially suspicious" if score >= 50 else "Likely legitimate"
    record = Transaction(amount=item.amount, risk_score=round(score, 2), risk_level=level, prediction=prediction)
    db.add(record); db.commit(); db.refresh(record)
    return {"id": record.id, "risk_score": record.risk_score, "risk_level": level, "prediction": prediction}

@app.get("/api/transactions")
def transactions(db: Session = Depends(get_db)):
    rows = db.query(Transaction).order_by(Transaction.id.desc()).limit(20).all()
    return [{"id": r.id, "amount": r.amount, "risk_score": r.risk_score,
             "risk_level": r.risk_level, "prediction": r.prediction} for r in rows]

@app.get("/api/summary")
def summary(db: Session = Depends(get_db)):
    rows = db.query(Transaction).all()
    return {"total": len(rows), "high_risk": sum(r.risk_level == "High" for r in rows),
            "medium_risk": sum(r.risk_level == "Medium" for r in rows),
            "low_risk": sum(r.risk_level == "Low" for r in rows)}
