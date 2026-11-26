
from pathlib import Path
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve
)

from ml.generate_data import generate

root = Path(__file__).resolve().parent.parent
csv = root / "data" / "synthetic_transactions.csv"

if not csv.exists():
    generate()

df = pd.read_csv(csv)

features = [
    "amount", "hour", "international",
    "online", "recent_transactions", "account_age_days"
]

X = df[features]
y = df["is_fraud"]

# Separate test data
X_train_full, Xte, y_train_full, yte = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Create training and validation data
Xtr, Xval, ytr, yval = train_test_split(
    X_train_full, y_train_full,
    test_size=0.25, random_state=42, stratify=y_train_full
)

model = RandomForestClassifier(
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

params = {
    "n_estimators": [100, 150, 200],
    "max_depth": [8, 10, 12, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

search = RandomizedSearchCV(
    model,
    params,
    n_iter=10,
    scoring="recall",
    cv=3,
    random_state=42,
    n_jobs=-1
)

search.fit(Xtr, ytr)
best_model = search.best_estimator_

# Find the best threshold using validation data
val_probs = best_model.predict_proba(Xval)[:, 1]

precision, recall, thresholds = precision_recall_curve(yval, val_probs)

f1_scores = (
    2 * precision[:-1] * recall[:-1]
    / (precision[:-1] + recall[:-1] + 1e-10)
)

best_index = f1_scores.argmax()
best_threshold = thresholds[best_index]

print("Best Threshold:", round(best_threshold, 4))
print("Validation F1-score:", round(f1_scores[best_index], 4))

# Final evaluation using untouched test data
test_probs = best_model.predict_proba(Xte)[:, 1]
test_predictions = (test_probs >= best_threshold).astype(int)

print("\nFinal Classification Report:")
print(classification_report(yte, test_predictions, zero_division=0))

print("ROC-AUC:", round(roc_auc_score(yte, test_probs), 4))

joblib.dump(best_model, root / "ml" / "fraud_model.joblib")

# Save the selected threshold
joblib.dump(best_threshold, root / "ml" / "threshold.joblib")

print("\nModel and threshold saved successfully!")
