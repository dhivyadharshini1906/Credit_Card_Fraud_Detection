from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    amount: float = Field(gt=0, le=1000000)
    hour: int = Field(ge=0, le=23)
    international: bool = False
    online: bool = True
    recent_transactions: int = Field(ge=0, le=100)
    account_age_days: int = Field(ge=0, le=30000)
