# Credit Card Fraud Detection & Transaction Risk Intelligence Platform

Educational full-stack ML demo: estimates transaction risk using synthetic data.

## Stack
Python, FastAPI, Pandas, NumPy, scikit-learn, HTML, CSS, JavaScript, SQLite (default) / PostgreSQL (optional), Git/GitHub.

## Run on Windows PowerShell
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ml/train_model.py
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

SQLite works by default. For PostgreSQL, set:
```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/fraud_db"
```

The model is trained on generated synthetic data, not real card transactions. This is a learning project, not a production fraud-prevention system. Never enter real card numbers, CVVs, PINs, or personal financial information.
