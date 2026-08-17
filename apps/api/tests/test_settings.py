def test_get_default_theme(client):
    resp = client.get("/theme-settings")
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"] == "default"
    assert body["theme_name"] == "light"


def test_update_theme(client):
    resp = client.patch("/theme-settings", json={"theme_name": "dark", "primary_color": "#111827"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["theme_name"] == "dark"
    assert body["primary_color"] == "#111827"


def test_theme_persists_across_requests(client):
    client.patch("/theme-settings", json={"font_size": "large"})
    resp = client.get("/theme-settings")
    assert resp.json()["font_size"] == "large"


def test_create_checklist_template(client):
    resp = client.post("/checklist-templates", json={"name": "چک‌لیست من"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "چک‌لیست من"
    assert body["is_active"] is True


def test_create_checklist_item_and_list(client):
    tpl = client.post("/checklist-templates", json={"name": "قالب"}).json()
    client.post(
        "/checklist-templates/items",
        json={"template_id": tpl["id"], "title": "آیتم اول", "sort_order": 1},
    )
    client.post(
        "/checklist-templates/items",
        json={"template_id": tpl["id"], "title": "آیتم دوم", "sort_order": 2},
    )
    resp = client.get(f"/checklist-templates/{tpl['id']}/items")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_checklist_item_unknown_template_404(client):
    resp = client.post(
        "/checklist-templates/items",
        json={"template_id": "00000000-0000-0000-0000-000000000000", "title": "x"},
    )
    assert resp.status_code == 404


def test_reorder_checklist_items(client):
    tpl = client.post("/checklist-templates", json={"name": "قالب ترتیب"}).json()
    i1 = client.post(
        "/checklist-templates/items", json={"template_id": tpl["id"], "title": "اول"}
    ).json()
    i2 = client.post(
        "/checklist-templates/items", json={"template_id": tpl["id"], "title": "دوم"}
    ).json()

    resp = client.post(
        f"/checklist-templates/{tpl['id']}/items/reorder",
        json={"items": [{"id": i1["id"], "sort_order": 9}, {"id": i2["id"], "sort_order": 1}]},
    )
    assert resp.status_code == 200
    order_map = {item["id"]: item["sort_order"] for item in resp.json()}
    assert order_map[i1["id"]] == 9
    assert order_map[i2["id"]] == 1


def test_disable_checklist_template(client):
    tpl = client.post("/checklist-templates", json={"name": "قالب غیرفعال"}).json()
    resp = client.post(f"/checklist-templates/{tpl['id']}/disable")
    assert resp.json()["is_active"] is False


def test_delete_checklist_item_without_history_succeeds(client):
    tpl = client.post("/checklist-templates", json={"name": "قالب حذف"}).json()
    item = client.post(
        "/checklist-templates/items", json={"template_id": tpl["id"], "title": "حذف‌شدنی"}
    ).json()
    resp = client.delete(f"/checklist-templates/items/{item['id']}")
    assert resp.status_code == 204


def test_create_ui_tab(client):
    resp = client.post("/ui-tabs", json={"key": "custom_tab_1", "title": "تب سفارشی"})
    assert resp.status_code == 201
    assert resp.json()["is_visible"] is True


def test_create_ui_tab_duplicate_key_rejected(client):
    client.post("/ui-tabs", json={"key": "dup_tab", "title": "تب"})
    resp = client.post("/ui-tabs", json={"key": "dup_tab", "title": "تکراری"})
    assert resp.status_code == 409


def test_hide_and_show_ui_tab(client):
    tab = client.post("/ui-tabs", json={"key": "toggle_tab", "title": "تب"}).json()
    hidden = client.post(f"/ui-tabs/{tab['id']}/hide")
    assert hidden.json()["is_visible"] is False
    shown = client.post(f"/ui-tabs/{tab['id']}/show")
    assert shown.json()["is_visible"] is True


def test_reorder_ui_tabs(client):
    t1 = client.post("/ui-tabs", json={"key": "reorder_a", "title": "الف"}).json()
    t2 = client.post("/ui-tabs", json={"key": "reorder_b", "title": "ب"}).json()
    resp = client.post(
        "/ui-tabs/reorder",
        json={"items": [{"id": t1["id"], "sort_order": 3}, {"id": t2["id"], "sort_order": 1}]},
    )
    assert resp.status_code == 200


def test_delete_ui_tab(client):
    tab = client.post("/ui-tabs", json={"key": "deletable_tab", "title": "تب"}).json()
    resp = client.delete(f"/ui-tabs/{tab['id']}")
    assert resp.status_code == 204
