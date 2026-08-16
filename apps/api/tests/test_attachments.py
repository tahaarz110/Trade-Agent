import io

from PIL import Image


def _make_png_bytes() -> bytes:
    img = Image.new("RGB", (800, 600), color=(70, 130, 180))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _create_trade(client, account_id, symbol_id) -> str:
    resp = client.post(
        "/trades",
        json={
            "account_id": account_id,
            "symbol_id": symbol_id,
            "direction": "buy",
            "entry_time": "2026-08-01T08:00:00Z",
            "entry_price": "1.1000",
            "volume": "1.0",
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_upload_attachment_creates_thumbnail(client, account_id, symbol_id):
    trade_id = _create_trade(client, account_id, symbol_id)
    png_bytes = _make_png_bytes()

    resp = client.post(
        f"/trades/{trade_id}/attachments",
        files={"file": ("chart.png", png_bytes, "image/png")},
        data={"caption": "اسکرین‌شات ورود"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["file_name"] == "chart.png"
    assert body["caption"] == "اسکرین‌شات ورود"
    assert body["thumbnail_path"] is not None


def test_upload_attachment_trade_not_found(client):
    png_bytes = _make_png_bytes()
    resp = client.post(
        "/trades/00000000-0000-0000-0000-000000000000/attachments",
        files={"file": ("chart.png", png_bytes, "image/png")},
    )
    assert resp.status_code == 404


def test_list_attachments(client, account_id, symbol_id):
    trade_id = _create_trade(client, account_id, symbol_id)
    png_bytes = _make_png_bytes()
    client.post(
        f"/trades/{trade_id}/attachments",
        files={"file": ("chart1.png", png_bytes, "image/png")},
    )
    client.post(
        f"/trades/{trade_id}/attachments",
        files={"file": ("chart2.png", png_bytes, "image/png")},
    )
    resp = client.get(f"/trades/{trade_id}/attachments")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_delete_attachment(client, account_id, symbol_id):
    trade_id = _create_trade(client, account_id, symbol_id)
    png_bytes = _make_png_bytes()
    upload = client.post(
        f"/trades/{trade_id}/attachments",
        files={"file": ("chart.png", png_bytes, "image/png")},
    )
    attachment_id = upload.json()["id"]

    resp = client.delete(f"/attachments/{attachment_id}")
    assert resp.status_code == 204

    resp2 = client.get(f"/trades/{trade_id}/attachments")
    assert resp2.json() == []
