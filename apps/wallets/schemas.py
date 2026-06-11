from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, condecimal

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class WalletOperation(BaseModel):
    operation_type: OperationType
    amount: condecimal(gt=0, max_digits=15, decimal_places=2)

class WalletResponse(BaseModel):
    wallet_id: str
    balance: Decimal

    class Config:
        from_attributes = True