import uuid
import concurrent.futures
from decimal import Decimal
from fastapi.testclient import TestClient
from apps.wallets import crud, schemas, models
from apps.tests.conftest import TestingSessionLocal

def test_get_balance_of_nonexistent_wallet(client: TestClient):
    response = client.get(f"/api/v1/wallets/{uuid.uuid4()}")
    assert response.status_code == 404

def test_deposit(client: TestClient):
    wallet_uuid = uuid.uuid4()
    # кошелёк создаётся автоматически при первом обращении? По условию задания явное создание не требуется, поэтому
    # реализую логику "создать при операции, если не существует".
    response = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "1000.00"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == str(wallet_uuid)
    assert Decimal(data["balance"]) == Decimal("1000.00")

def test_withdraw_insufficient_funds(client):
    wallet_uuid = uuid.uuid4()
    # Пополню на 100
    resp = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.00"}
    )
    assert resp.status_code == 200

    # Пытаюсь снять 200
    resp = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "200.00"}
    )
    assert resp.status_code == 409

def test_concurrent_deposits():
    wallet_id = uuid.uuid4()

    # Создаю кошелёк с начальным депозитом
    init_db = TestingSessionLocal()
    try:
        op = schemas.WalletOperation(
            operation_type=schemas.OperationType.DEPOSIT,
            amount=Decimal("0.01")   # >0
        )
        crud.perform_operation(init_db, wallet_id, op)
        init_db.commit()
    finally:
        init_db.close()

    num_workers = 20
    amount_per_worker = Decimal("50.00")

    def worker():
        db = TestingSessionLocal()
        try:
            op = schemas.WalletOperation(
                operation_type=schemas.OperationType.DEPOSIT,
                amount=amount_per_worker
            )
            success, _, _ = crud.perform_operation(db, wallet_id, op)
            return success
        finally:
            db.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(num_workers)]
        results = [f.result() for f in futures]

    assert all(results)

    # Проверяю финальный баланс
    check_db = TestingSessionLocal()
    try:
        wallet = check_db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
        expected = Decimal("0.01") + amount_per_worker * num_workers
        assert wallet.balance == expected
    finally:
        check_db.close()