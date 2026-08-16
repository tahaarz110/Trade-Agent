def _trade_payload(account_id, symbol_id, **overrides):
    payload = {
        "account_id": account_id,
        "symbol_id": symbol_id,
        "direction": "buy",
        "entry_time": "2026-08-01T08:00:00Z",
        "entry_price": "1.1000",
        "volume": "1.0",
    }
    payload.update(overrides)
    return payload


def test_create_trade(client, account_id, symbol_id):
    resp = client.post("/trades", json=_trade_payload(account_id, symbol_id))
    assert resp.status_code == 201
    body = resp.json()
    assert body["account_id"] == account_id
    assert body["direction"] == "buy"
    assert body["status"] == "open"


def test_create_trade_invalid_account_returns_404(client, symbol_id):
    payload = _trade_payload("00000000-0000-0000-0000-000000000000", symbol_id)
    resp = client.post("/trades", json=payload)
    assert resp.status_code == 404


def test_create_trade_invalid_symbol_returns_404(client, account_id):
    payload = _trade_payload(account_id, "00000000-0000-0000-0000-000000000000")
    resp = client.post("/trades", json=payload)
    assert resp.status_code == 404


def test_create_trade_with_dynamic_field(client, account_id, symbol_id, db_session):
    from app.models.field import FieldDefinition, FieldSection
    from app.models.enums import FieldType

    section = FieldSection(key="test_section", title="سکشن تست", sort_order=1)
    db_session.add(section)
    db_session.flush()
    field = FieldDefinition(
        section_id=section.id,
        slug="test_session",
        title="سشن تست",
        field_type=FieldType.SHORT_TEXT,
        analytic_enabled=True,
    )
    db_session.add(field)
    db_session.commit()

    payload = _trade_payload(account_id, symbol_id, custom_fields={"test_session": "لندن"})
    resp = client.post("/trades", json=payload)
    assert resp.status_code == 201
    trade_id = resp.json()["id"]

    detail = client.get(f"/trades/{trade_id}")
    assert detail.status_code == 200
    custom = detail.json()["custom_fields"]
    assert any(f["field_slug"] == "test_session" and f["value"] == "لندن" for f in custom)


def test_create_trade_with_unknown_dynamic_field_returns_422(client, account_id, symbol_id):
    payload = _trade_payload(account_id, symbol_id, custom_fields={"does_not_exist": "x"})
    resp = client.post("/trades", json=payload)
    assert resp.status_code == 422


def test_get_trade_not_found(client):
    resp = client.get("/trades/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_trade(client, account_id, symbol_id):
    resp = client.post("/trades", json=_trade_payload(account_id, symbol_id))
    trade_id = resp.json()["id"]
    upd = client.patch(f"/trades/{trade_id}", json={"status": "closed", "exit_price": "1.1050"})
    assert upd.status_code == 200
    assert upd.json()["status"] == "closed"


def test_delete_trade(client, account_id, symbol_id):
    resp = client.post("/trades", json=_trade_payload(account_id, symbol_id))
    trade_id = resp.json()["id"]
    assert client.delete(f"/trades/{trade_id}").status_code == 204
    assert client.get(f"/trades/{trade_id}").status_code == 404


def test_filter_trades_by_direction_and_account(client, account_id, symbol_id):
    client.post("/trades", json=_trade_payload(account_id, symbol_id, direction="buy"))
    client.post("/trades", json=_trade_payload(account_id, symbol_id, direction="sell"))

    resp = client.get(f"/trades?account_id={account_id}&direction=buy")
    body = resp.json()
    assert resp.status_code == 200
    assert body["total"] == 1
    assert body["items"][0]["direction"] == "buy"


def test_filter_trades_by_date_range(client, account_id, symbol_id):
    client.post(
        "/trades",
        json=_trade_payload(account_id, symbol_id, entry_time="2026-01-01T08:00:00Z"),
    )
    client.post(
        "/trades",
        json=_trade_payload(account_id, symbol_id, entry_time="2026-06-01T08:00:00Z"),
    )

    resp = client.get(
        f"/trades?account_id={account_id}&date_from=2026-05-01&date_to=2026-07-01"
    )
    body = resp.json()
    assert resp.status_code == 200
    assert body["total"] == 1


def test_trades_pagination(client, account_id, symbol_id):
    for _ in range(15):
        client.post("/trades", json=_trade_payload(account_id, symbol_id))

    resp = client.get(f"/trades?account_id={account_id}&page=2&page_size=10")
    body = resp.json()
    assert resp.status_code == 200
    assert body["total"] == 15
    assert len(body["items"]) == 5
    assert body["page"] == 2
