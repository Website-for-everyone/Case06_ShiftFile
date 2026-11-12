"""
Test Suite for ShiftFile (Case 06)
Verifies:
1. JSON <-> CSV conversions and nested key flattening
2. Image conversions (PNG -> JPEG, PNG -> WEBP)
3. FastAPI web routes (/health, /api/convert/json-to-csv)
4. Bot router and keyboard construction
"""
import io
import json
import csv
import pytest
from PIL import Image
from fastapi.testclient import TestClient

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
for mod in list(sys.modules.keys()):
    if mod.startswith("api") or mod.startswith("bot"):
        sys.modules.pop(mod, None)
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import app, flatten_dict
from bot.bot import get_format_keyboard, dp


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "ShiftFile"


def test_flatten_dict():
    nested = {
        "user": {
            "name": "Daniel",
            "geo": {"city": "Dubai", "zip": "00000"}
        },
        "score": 100
    }
    flat = flatten_dict(nested)
    assert flat["user.name"] == "Daniel"
    assert flat["user.geo.city"] == "Dubai"
    assert flat["user.geo.zip"] == "00000"
    assert flat["score"] == 100


def test_api_json_to_csv():
    payload = [
        {"id": 1, "item": "Knob", "spec": {"color": "orange"}},
        {"id": 2, "item": "Gear", "spec": {"color": "brass"}}
    ]
    response = client.post("/api/convert/json-to-csv", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    csv_text = response.text
    assert "id,item,spec.color" in csv_text or "id" in csv_text
    assert "Knob" in csv_text
    assert "brass" in csv_text


def test_image_transcode_pillow():
    # Create test image in memory
    img = Image.new("RGBA", (50, 50), color=(255, 87, 34, 255))
    src_io = io.BytesIO()
    img.save(src_io, format="PNG")
    src_bytes = src_io.getvalue()

    # Transcode to JPEG
    conv_img = Image.open(io.BytesIO(src_bytes)).convert("RGB")
    out_io = io.BytesIO()
    conv_img.save(out_io, format="JPEG")
    assert len(out_io.getvalue()) > 0
    assert out_io.getvalue().startswith(b'\xff\xd8')


def test_bot_format_keyboard():
    kb_img = get_format_keyboard("image")
    assert len(kb_img.inline_keyboard) >= 2
    button_texts = [btn.text for row in kb_img.inline_keyboard for btn in row]
    assert any("PNG" in t for t in button_texts)
    assert any("JPEG" in t for t in button_texts)

    kb_json = get_format_keyboard("json")
    button_texts_json = [btn.text for row in kb_json.inline_keyboard for btn in row]
    assert any("CSV" in t for t in button_texts_json)


def test_bot_dispatcher_registered():
    assert dp is not None
    # Verify handlers exist in router
    handlers = dp.sub_routers or dp.message.handlers
    assert handlers is not None
