def _create_section(client, key="custom_section", title="سکشن سفارشی"):
    resp = client.post("/field-sections", json={"key": key, "title": title, "sort_order": 1})
    assert resp.status_code == 201
    return resp.json()


def _create_field(client, section_id, slug="custom_field", field_type="short_text", **overrides):
    payload = {
        "section_id": section_id,
        "slug": slug,
        "title": "فیلد سفارشی",
        "field_type": field_type,
        "sort_order": 1,
    }
    payload.update(overrides)
    resp = client.post("/field-definitions", json=payload)
    assert resp.status_code == 201
    return resp.json()


def _create_trade(client, account_id, symbol_id, **overrides):
    payload = {
        "account_id": account_id,
        "symbol_id": symbol_id,
        "direction": "buy",
        "entry_time": "2026-08-01T08:00:00Z",
        "entry_price": "1.1000",
        "volume": "1.0",
    }
    payload.update(overrides)
    resp = client.post("/trades", json=payload)
    assert resp.status_code == 201
    return resp.json()


# --- FieldSection ------------------------------------------------------------
def test_create_field_section(client):
    section = _create_section(client)
    assert section["key"] == "custom_section"
    assert section["is_system"] is False
    assert section["is_active"] is True


def test_create_duplicate_section_key_conflict(client):
    _create_section(client)
    resp = client.post("/field-sections", json={"key": "custom_section", "title": "تکراری"})
    assert resp.status_code == 409


def test_disable_and_enable_section(client):
    section = _create_section(client)
    resp = client.post(f"/field-sections/{section['id']}/disable")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    resp2 = client.post(f"/field-sections/{section['id']}/enable")
    assert resp2.json()["is_active"] is True


def test_reorder_sections(client):
    s1 = _create_section(client, key="s1", title="سکشن ۱")
    s2 = _create_section(client, key="s2", title="سکشن ۲")

    resp = client.post(
        "/field-sections/reorder",
        json={"items": [{"id": s1["id"], "sort_order": 5}, {"id": s2["id"], "sort_order": 1}]},
    )
    assert resp.status_code == 200
    ordered = resp.json()
    assert ordered[0]["id"] == s2["id"]


def test_delete_empty_section(client):
    section = _create_section(client)
    resp = client.delete(f"/field-sections/{section['id']}")
    assert resp.status_code == 204


# --- FieldDefinition -----------------------------------------------------------
def test_create_field_definition(client):
    section = _create_section(client)
    field = _create_field(client, section["id"])
    assert field["slug"] == "custom_field"
    assert field["is_system"] is False


def test_create_field_with_options(client):
    section = _create_section(client)
    field = _create_field(
        client,
        section["id"],
        slug="setup_type",
        field_type="single_select",
        options=["Order Block", "Fair Value Gap"],
    )
    assert len(field["options"]) == 2
    assert {o["value"] for o in field["options"]} == {"Order Block", "Fair Value Gap"}


def test_create_field_invalid_section_404(client):
    resp = client.post(
        "/field-definitions",
        json={
            "section_id": "00000000-0000-0000-0000-000000000000",
            "slug": "x",
            "title": "x",
            "field_type": "short_text",
        },
    )
    assert resp.status_code == 404


def test_disable_field(client):
    section = _create_section(client)
    field = _create_field(client, section["id"])
    resp = client.post(f"/field-definitions/{field['id']}/disable")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_reorder_fields(client):
    section = _create_section(client)
    f1 = _create_field(client, section["id"], slug="f1")
    f2 = _create_field(client, section["id"], slug="f2")
    resp = client.post(
        "/field-definitions/reorder",
        json={"items": [{"id": f1["id"], "sort_order": 9}, {"id": f2["id"], "sort_order": 1}]},
    )
    assert resp.status_code == 200
    assert resp.json()[0]["id"] == f2["id"]


def test_delete_field_without_history(client):
    section = _create_section(client)
    field = _create_field(client, section["id"])
    resp = client.delete(f"/field-definitions/{field['id']}")
    assert resp.status_code == 204


def test_delete_field_with_history_is_blocked(client, account_id, symbol_id):
    section = _create_section(client)
    field = _create_field(client, section["id"], slug="history_field")

    _create_trade(client, account_id, symbol_id, custom_fields={"history_field": "مقدار تست"})

    resp = client.delete(f"/field-definitions/{field['id']}")
    assert resp.status_code == 422


def test_delete_system_field_is_blocked(client, db_session):
    from app.models.field import FieldDefinition, FieldSection
    from app.models.enums import FieldType

    section = FieldSection(key="sys_section", title="سیستمی", is_system=True, sort_order=1)
    db_session.add(section)
    db_session.flush()
    field = FieldDefinition(
        section_id=section.id,
        slug="sys_field",
        title="فیلد سیستمی",
        field_type=FieldType.SHORT_TEXT,
        is_system=True,
    )
    db_session.add(field)
    db_session.commit()

    resp = client.delete(f"/field-definitions/{field.id}")
    assert resp.status_code == 422


def test_delete_section_with_field_history_is_blocked(client, account_id, symbol_id):
    section = _create_section(client)
    _create_field(client, section["id"], slug="blocking_field")
    _create_trade(client, account_id, symbol_id, custom_fields={"blocking_field": "x"})

    resp = client.delete(f"/field-sections/{section['id']}")
    assert resp.status_code == 422


# --- FieldOption ---------------------------------------------------------------
def test_add_option_to_field(client):
    section = _create_section(client)
    field = _create_field(client, section["id"], slug="opt_field", field_type="single_select")
    resp = client.post(
        "/field-options", json={"field_id": field["id"], "value": "A", "label": "گزینه آ"}
    )
    assert resp.status_code == 201
    assert resp.json()["value"] == "A"


def test_list_options(client):
    section = _create_section(client)
    field = _create_field(
        client, section["id"], slug="opt_field2", field_type="single_select", options=["A", "B"]
    )
    resp = client.get(f"/field-definitions/{field['id']}/options")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_delete_unused_option(client):
    section = _create_section(client)
    field = _create_field(
        client, section["id"], slug="opt_field3", field_type="single_select", options=["A", "B"]
    )
    options = client.get(f"/field-definitions/{field['id']}/options").json()
    resp = client.delete(f"/field-options/{options[0]['id']}")
    assert resp.status_code == 204


def test_delete_used_option_is_blocked(client, account_id, symbol_id):
    section = _create_section(client)
    field = _create_field(
        client, section["id"], slug="opt_field4", field_type="single_select", options=["A", "B"]
    )
    options = client.get(f"/field-definitions/{field['id']}/options").json()
    option_a = next(o for o in options if o["value"] == "A")

    _create_trade(client, account_id, symbol_id, custom_fields={"opt_field4": "A"})

    resp = client.delete(f"/field-options/{option_a['id']}")
    assert resp.status_code == 422


def test_delete_used_multi_select_option_is_blocked(client, account_id, symbol_id):
    """رفع باگ مقیاس‌پذیری پیش از فاز ۶: is_option_value_used باید مسیر
    value_json (چندانتخابی) را هم با کوئری SQL (نه لود به پایتون)
    درست تشخیص دهد."""
    section = _create_section(client)
    field = _create_field(
        client, section["id"], slug="opt_field_multi", field_type="multi_select", options=["X", "Y", "Z"]
    )
    options = client.get(f"/field-definitions/{field['id']}/options").json()
    option_x = next(o for o in options if o["value"] == "X")
    option_z = next(o for o in options if o["value"] == "Z")

    _create_trade(client, account_id, symbol_id, custom_fields={"opt_field_multi": ["X", "Y"]})

    # X در معامله استفاده شده => حذف مسدود
    resp_x = client.delete(f"/field-options/{option_x['id']}")
    assert resp_x.status_code == 422

    # Z اصلاً استفاده نشده => حذف باید موفق باشد
    resp_z = client.delete(f"/field-options/{option_z['id']}")
    assert resp_z.status_code == 204


# --- اعتبارسنجی مقدار در ثبت معامله --------------------------------------------
def test_trade_rejects_invalid_select_option(client, account_id, symbol_id):
    section = _create_section(client)
    _create_field(
        client, section["id"], slug="strict_select", field_type="single_select", options=["A", "B"]
    )
    resp = client.post(
        "/trades",
        json={
            "account_id": account_id,
            "symbol_id": symbol_id,
            "direction": "buy",
            "entry_time": "2026-08-01T08:00:00Z",
            "entry_price": "1.1000",
            "volume": "1.0",
            "custom_fields": {"strict_select": "C"},
        },
    )
    assert resp.status_code == 422


def test_trade_rejects_invalid_number(client, account_id, symbol_id):
    section = _create_section(client)
    _create_field(client, section["id"], slug="num_field", field_type="number")
    resp = client.post(
        "/trades",
        json={
            "account_id": account_id,
            "symbol_id": symbol_id,
            "direction": "buy",
            "entry_time": "2026-08-01T08:00:00Z",
            "entry_price": "1.1000",
            "volume": "1.0",
            "custom_fields": {"num_field": "not-a-number"},
        },
    )
    assert resp.status_code == 422


def test_trade_rejects_value_for_disabled_field(client, account_id, symbol_id):
    section = _create_section(client)
    field = _create_field(client, section["id"], slug="disabled_field")
    client.post(f"/field-definitions/{field['id']}/disable")

    resp = client.post(
        "/trades",
        json={
            "account_id": account_id,
            "symbol_id": symbol_id,
            "direction": "buy",
            "entry_time": "2026-08-01T08:00:00Z",
            "entry_price": "1.1000",
            "volume": "1.0",
            "custom_fields": {"disabled_field": "x"},
        },
    )
    assert resp.status_code == 422


# --- فیلتر داینامیک بر اساس field_id/value --------------------------------------
def test_filter_trades_by_dynamic_field(client, account_id, symbol_id):
    section = _create_section(client)
    field = _create_field(client, section["id"], slug="filter_field")

    t1 = _create_trade(client, account_id, symbol_id, custom_fields={"filter_field": "لندن"})
    _create_trade(client, account_id, symbol_id, custom_fields={"filter_field": "نیویورک"})

    resp = client.get(f"/trades?field_id={field['id']}&field_value=لندن")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == t1["id"]
