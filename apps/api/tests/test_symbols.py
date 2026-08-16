def test_create_symbol(client, symbol_payload):
    resp = client.post("/symbols", json=symbol_payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "EURUSD"


def test_create_symbol_duplicate_name_rejected(client, symbol_payload):
    assert client.post("/symbols", json=symbol_payload).status_code == 201
    resp = client.post("/symbols", json=symbol_payload)
    # نام نماد unique است؛ باید با خطای قابل‌فهم رد شود، نه ۵۰۰
    assert resp.status_code in (400, 409, 422)


def test_get_symbol_not_found(client):
    resp = client.get("/symbols/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_symbol(client, symbol_id):
    resp = client.patch(f"/symbols/{symbol_id}", json={"display_name": "یورو دلار به‌روزشده"})
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "یورو دلار به‌روزشده"


def test_delete_symbol(client, symbol_id):
    resp = client.delete(f"/symbols/{symbol_id}")
    assert resp.status_code == 204
