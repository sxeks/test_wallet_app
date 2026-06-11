import uuid
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from apps.database.database import get_db
from fastapi import APIRouter


api_router = APIRouter(prefix='/api/v1/wallets', tags=['API'])


@api_router.get("/{wallet_uuid}", response_model=schemas.WalletResponse)
def get_balance(wallet_uuid: uuid.UUID, db: Session = Depends(get_db)):
    balance = crud.get_wallet_balance(db, wallet_uuid)
    if balance is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"wallet_id": str(wallet_uuid), "balance": balance}

@api_router.post("/{wallet_uuid}/operation", response_model=schemas.WalletResponse)
def wallet_operation(
    wallet_uuid: uuid.UUID,
    operation: schemas.WalletOperation,
    db: Session = Depends(get_db)
):
    success, message, new_balance = crud.perform_operation(db, wallet_uuid, operation)
    if not success:
        if message == "Wallet not found":
            raise HTTPException(status_code=404, detail=message)
        elif message == "Insufficient funds":
            raise HTTPException(status_code=409, detail=message)
    return {"wallet_id": str(wallet_uuid), "balance": new_balance}