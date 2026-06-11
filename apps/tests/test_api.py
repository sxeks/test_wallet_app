import uuid
import concurrent.futures
from decimal import Decimal
from fastapi.testclient import TestClient

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

def test_withdraw_insufficient_funds(client: TestClient):
    wallet_uuid = uuid.uuid4()
    # Создаю кошелёк с нулевым балансом
    response = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "0.00"}
    )
    assert response.status_code == 200
    response = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "100.00"}
    )
    assert response.status_code == 409

def test_concurrent_deposits(client: TestClient):
    wallet_uuid = uuid.uuid4()
    num_requests = 20
    amount_per_request = Decimal("50.00")

    def make_deposit():
        return client.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "DEPOSIT", "amount": str(amount_per_request)}
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_deposit) for _ in range(num_requests)]
        results = [f.result() for f in futures]

    assert all(r.status_code == 200 for r in results)
    # Проверяю итоговый баланс
    resp = client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert resp.status_code == 200
    balance = Decimal(resp.json()["balance"])
    expected = amount_per_request * num_requests
    assert balance == expected