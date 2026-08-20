def _make_template_with_items(client, *, default=False):
    tpl = client.post(
        "/checklist-templates", json={"name": "چک‌لیست تست", "is_default": default}
    ).json()
    i1 = client.post(
        "/checklist-templates/items",
        json={"template_id": tpl["id"], "title": "آیتم الزامی یک", "is_required": True, "sort_order": 1},
    ).json()
    i2 = client.post(
        "/checklist-templates/items",
        json={"template_id": tpl["id"], "title": "آیتم الزامی دو", "is_required": True, "sort_order": 2},
    ).json()
    i3 = client.post(
        "/checklist-templates/items",
        json={"template_id": tpl["id"], "title": "آیتم اختیاری", "is_required": False, "sort_order": 3},
    ).json()
    return tpl, i1, i2, i3


def _make_trade(client, account_id, symbol_id):
    return client.post(
        "/trades",
        json={
            "account_id": account_id,
            "symbol_id": symbol_id,
            "direction": "buy",
            "entry_time": "2026-08-01T08:00:00Z",
            "entry_price": "1.1",
            "volume": "1.0",
        },
    ).json()


# --- اختصاص قالب و پاسخ‌دهی -------------------------------------------------------
def test_get_checklist_before_assignment_is_empty(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    resp = client.get(f"/trades/{trade['id']}/checklist")
    assert resp.status_code == 200
    body = resp.json()
    assert body["checklist_template_id"] is None
    assert body["items"] == []
    assert body["score_percent"] is None


def test_assign_template_and_answer_items(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [{"item_id": i1["id"], "checked": True, "note": "تأیید شد"}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["checklist_template_id"] == tpl["id"]
    assert body["checklist_template_title"] == tpl["name"]
    assert body["total_items"] == 3
    assert body["checked_items"] == 1


def test_score_calculation(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [
                {"item_id": i1["id"], "checked": True},
                {"item_id": i2["id"], "checked": False},
                {"item_id": i3["id"], "checked": True},
            ],
        },
    )
    body = resp.json()
    # ۲ از ۳ آیتم فعال چک شده‌اند => ۶۶٫۶۷٪
    assert body["score_percent"] == round(2 / 3 * 100, 2)


def test_required_missing_calculation(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [{"item_id": i1["id"], "checked": True}],
        },
    )
    body = resp.json()
    assert body["required_items"] == 2
    assert body["required_checked_items"] == 1
    assert body["required_missing_items"] == ["آیتم الزامی دو"]


def test_updating_existing_answer_does_not_duplicate(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl["id"], "answers": [{"item_id": i1["id"], "checked": False}]},
    )
    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [{"item_id": i1["id"], "checked": True, "note": "به‌روزشده"}],
        },
    )
    body = resp.json()
    updated_item = next(i for i in body["items"] if i["id"] == i1["id"])
    assert updated_item["checked"] is True
    assert updated_item["note"] == "به‌روزشده"
    assert body["checked_items"] == 1  # نباید دو ردیف پاسخ ساخته شده باشد


def test_duplicate_item_in_single_request_uses_last_value(client, account_id, symbol_id):
    """جلوگیری از پاسخ تکراری: اگر یک آیتم دوبار در یک درخواست بیاید،
    فقط آخرین مقدار اعمال می‌شود و به‌جای کرش، پاسخ ۲۰۰ برمی‌گردد."""
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [
                {"item_id": i1["id"], "checked": True, "note": "اول"},
                {"item_id": i1["id"], "checked": False, "note": "دوم"},
            ],
        },
    )
    assert resp.status_code == 200
    item = next(i for i in resp.json()["items"] if i["id"] == i1["id"])
    assert item["checked"] is False
    assert item["note"] == "دوم"


def test_changing_template_preserves_old_answers_but_hides_them(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl1, i1, _, _ = _make_template_with_items(client)
    tpl2 = client.post("/checklist-templates", json={"name": "قالب دوم"}).json()
    item_tpl2 = client.post(
        "/checklist-templates/items", json={"template_id": tpl2["id"], "title": "آیتم قالب دوم"}
    ).json()

    client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl1["id"], "answers": [{"item_id": i1["id"], "checked": True}]},
    )

    switch_resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl2["id"],
            "answers": [{"item_id": item_tpl2["id"], "checked": True}],
        },
    )
    assert switch_resp.status_code == 200
    assert switch_resp.json()["checklist_template_id"] == tpl2["id"]
    # آیتم قالب اول دیگر نمایش داده نمی‌شود (چون به قالب دیگری اختصاص یافته)
    assert not any(i["id"] == i1["id"] for i in switch_resp.json()["items"])

    # بازگشت به قالب اول: پاسخ قبلی باید هنوز موجود باشد (هرگز حذف نشده بود)
    back_resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl1["id"], "answers": []},
    )
    restored_item = next(i for i in back_resp.json()["items"] if i["id"] == i1["id"])
    assert restored_item["checked"] is True


def test_assign_inactive_template_is_rejected(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, _, _, _ = _make_template_with_items(client)
    client.post(f"/checklist-templates/{tpl['id']}/disable")

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl["id"], "answers": []},
    )
    assert resp.status_code == 422


def test_answering_inactive_item_in_new_submission_is_rejected(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, _, _ = _make_template_with_items(client)
    client.put(f"/trades/{trade['id']}/checklist", json={"checklist_template_id": tpl["id"], "answers": []})
    client.post(f"/checklist-templates/items/{i1['id']}/disable")

    resp = client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl["id"], "answers": [{"item_id": i1["id"], "checked": True}]},
    )
    assert resp.status_code == 422


def test_disabled_item_with_history_still_visible_and_excluded_from_score(
    client, account_id, symbol_id
):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)

    client.put(
        f"/trades/{trade['id']}/checklist",
        json={
            "checklist_template_id": tpl["id"],
            "answers": [{"item_id": i1["id"], "checked": True}, {"item_id": i2["id"], "checked": True}],
        },
    )
    client.post(f"/checklist-templates/items/{i2['id']}/disable")

    resp = client.get(f"/trades/{trade['id']}/checklist")
    body = resp.json()
    disabled_item = next(i for i in body["items"] if i["id"] == i2["id"])
    assert disabled_item["is_active"] is False
    assert disabled_item["checked"] is True  # تاریخچه حفظ شده
    # امتیاز فقط بر اساس آیتم‌های فعال محاسبه می‌شود (i1 checked, i3 unchecked => 1/2)
    assert body["score_percent"] == 50.0


def test_assign_default_template(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, _, _, _ = _make_template_with_items(client, default=True)

    resp = client.post(f"/trades/{trade['id']}/checklist/assign-default")
    assert resp.status_code == 200
    assert resp.json()["checklist_template_id"] == tpl["id"]

    # عملیات idempotent: بار دوم نباید خطا بدهد یا تغییری کند
    resp2 = client.post(f"/trades/{trade['id']}/checklist/assign-default")
    assert resp2.status_code == 200
    assert resp2.json()["checklist_template_id"] == tpl["id"]


def test_assign_default_without_any_default_template_404(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    resp = client.post(f"/trades/{trade['id']}/checklist/assign-default")
    assert resp.status_code == 404


def test_trade_detail_includes_checklist_summary(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, i2, i3 = _make_template_with_items(client)
    client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl["id"], "answers": [{"item_id": i1["id"], "checked": True}]},
    )

    detail = client.get(f"/trades/{trade['id']}").json()
    assert detail["has_checklist"] is True
    assert detail["checklist_template_title"] == tpl["name"]
    assert detail["checklist_score_percent"] == round(1 / 3 * 100, 2)
    assert detail["required_missing_count"] == 1


def test_trade_detail_without_checklist(client, account_id, symbol_id):
    trade = _make_trade(client, account_id, symbol_id)
    detail = client.get(f"/trades/{trade['id']}").json()
    assert detail["has_checklist"] is False
    assert detail["checklist_template_title"] is None
    assert detail["checklist_score_percent"] is None
    assert detail["required_missing_count"] == 0


def test_checklist_not_found_for_unknown_trade(client):
    resp = client.get("/trades/00000000-0000-0000-0000-000000000000/checklist")
    assert resp.status_code == 404


def test_deleting_template_with_trade_usage_is_blocked(client, account_id, symbol_id):
    """رفع باگ کشف‌شده فاز ۵.۵: حذف قالبی که به معامله‌ای اختصاص یافته
    نباید آیتم‌ها/پاسخ‌ها را CASCADE پاک کند."""
    trade = _make_trade(client, account_id, symbol_id)
    tpl, i1, _, _ = _make_template_with_items(client)
    client.put(
        f"/trades/{trade['id']}/checklist",
        json={"checklist_template_id": tpl["id"], "answers": [{"item_id": i1["id"], "checked": True}]},
    )

    resp = client.delete(f"/checklist-templates/{tpl['id']}")
    assert resp.status_code == 422

    # تأیید سالم ماندن پاسخ
    check = client.get(f"/trades/{trade['id']}/checklist").json()
    assert check["checklist_template_id"] == tpl["id"]
