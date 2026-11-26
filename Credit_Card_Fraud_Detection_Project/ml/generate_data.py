from pathlib import Path
import numpy as np
import pandas as pd

def generate(rows=12000, seed=42):
    rng = np.random.default_rng(seed)

    amount = np.round(rng.lognormal(5, 1.1, rows), 2)
    hour = rng.integers(0, 24, rows)
    international = rng.binomial(1, 0.15, rows)
    online = rng.binomial(1, 0.65, rows)
    recent_transactions = rng.poisson(2, rows)
    account_age_days = rng.integers(1, 5000, rows)

    risk = (
        -3.5
        + 0.0011 * np.minimum(amount, 5000)
        + 1.3 * international
        + 0.3 * online
        + 0.25 * recent_transactions
        + 0.9 * ((hour <= 4) | (hour >= 23))
        - 0.0002 * np.minimum(account_age_days, 4000)
    )

    probability = 1 / (1 + np.exp(-risk))
    fraud = rng.binomial(1, probability)

    df = pd.DataFrame({
        "amount": amount,
        "hour": hour,
        "international": international,
        "online": online,
        "recent_transactions": recent_transactions,
        "account_age_days": account_age_days,
        "is_fraud": fraud
    })

    output = Path(__file__).resolve().parent.parent / "data" / "synthetic_transactions.csv"
    output.parent.mkdir(exist_ok=True)
    df.to_csv(output, index=False)

    return output

if __name__ == "__main__":
    print("Generated:", generate())