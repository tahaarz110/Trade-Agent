def test_create_account(client, account_payload):
    resp = client.post("/accounts", json=account_payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == account_payload["name"]
    assert body["account_type"] == "demo"
    assert body["is_active"] is True
    assert "id" in body


def test_get_account(client, account_id, account_payload):
    resp = client.get(f"/accounts/{account_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == account_payload["name"]


def test_get_account_not_found(client):
    resp = client.get("/accounts/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_account(client, account_id):
    resp = client.patch(f"/accounts/{account_id}", json={"name": "حساب ویرایش‌شده"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "حساب ویرایش‌شده"


def test_delete_account(client, account_id):
    resp = client.delete(f"/accounts/{account_id}")
    assert resp.status_code == 204
    resp = client.get(f"/accounts/{account_id}")
    assert resp.status_code == 404


def test_list_accounts_pagination(client, account_payload):
    for i in range(25):
        payload = {**account_payload, "name": f"حساب {i}"}
        assert client.post("/accounts", json=payload).status_code == 201

    resp = client.get("/accounts?page=1&page_size=10")
    body = resp.json()
    assert resp.status_code == 200
    assert body["total"] == 25
    assert len(body["items"]) == 10
    assert body["page"] == 1
    assert body["total_pages"] == 3

    resp2 = client.get("/accounts?page=3&page_size=10")
    body2 = resp2.json()
    assert len(body2["items"]) == 5
