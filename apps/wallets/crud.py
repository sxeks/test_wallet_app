import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from . import models, schemas


def get_wallet_balance(db: Session, wallet_id: uuid.UUID) -> Decimal | None:
    """
    Получаем баланс
    """
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    return wallet.balance if wallet else None

def perform_operation(
    db: Session, wallet_id: uuid.UUID, operation: schemas.WalletOperation
) -> tuple[bool, str, Decimal | None]:
    """
    Выполняет операцию пополнения или снятия.
    Возвращает: (успех, сообщение, новый баланс)
    """
    # Пытаемся найти с блокировкой, если нет – создаём
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).with_for_update().first()
    if not wallet:
        if operation.operation_type == schemas.OperationType.WITHDRAW:
            return False, "Wallet not found", None
        # Создаю новый кошелёк
        wallet = models.Wallet(id=wallet_id, balance=0.0)
        db.add(wallet)
        db.flush()  # чтобы запись появилась, но ещё не зафиксирована
        # повторно получаю с блокировкой
        db.refresh(wallet)
    # Блокирую строку кошелька до конца транзакции
    wallet = (
        db.query(models.Wallet)
        .filter(models.Wallet.id == wallet_id)
        .with_for_update()
        .first()
    )

    if not wallet:
        return False, "Wallet not found", None

    if operation.operation_type == schemas.OperationType.DEPOSIT:
        wallet.balance += operation.amount
    elif operation.operation_type == schemas.OperationType.WITHDRAW:
        if wallet.balance < operation.amount:
            return False, "Insufficient funds", None
        wallet.balance -= operation.amount

    db.commit()
    db.refresh(wallet)
    return True, "Success", wallet.balance