import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
headers = {"X-User-Id": "user-1"}

@pytest.fixture(autouse=True)
def setup_user():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-1', 'Test User', 'expert')")
    db.commit()
    db.close()
    yield

def test_create_biz():
    r = client.post("/api/biz", json={"name": "Test", "description": "Desc", "type": "概念", "tags": ["t1"]}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "draft"
    assert data["name"] == "Test"

def test_create_biz_minimal():
    r = client.post("/api/biz", json={"name": "Minimal", "type": "流程"}, headers=headers)
    assert r.status_code == 200

def test_get_biz_list():
    client.post("/api/biz", json={"name": "Item1", "type": "概念"}, headers=headers)
    client.post("/api/biz", json={"name": "Item2", "type": "流程"}, headers=headers)
    r = client.get("/api/biz")
    assert r.status_code == 200
    assert len(r.json()) == 2

def test_get_biz_list_with_status():
    client.post("/api/biz", json={"name": "Draft", "type": "概念"}, headers=headers)
    r = client.get("/api/biz?status=draft")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["status"] == "draft"

def test_get_biz_list_with_search():
    client.post("/api/biz", json={"name": "Order Flow", "description": "Order processing", "type": "流程"}, headers=headers)
    r = client.get("/api/biz?q=Order")
    assert len(r.json()) == 1

def test_get_biz_detail():
    r_create = client.post("/api/biz", json={"name": "Detail Test", "type": "概念"}, headers=headers)
    bid = r_create.json()["id"]
    r = client.get(f"/api/biz/{bid}")
    assert r.status_code == 200
    assert r.json()["name"] == "Detail Test"

def test_update_biz():
    r_create = client.post("/api/biz", json={"name": "Update Me", "type": "规则"}, headers=headers)
    bid = r_create.json()["id"]
    r = client.put(f"/api/biz/{bid}", json={"name": "Updated", "tags": ["new"]}, headers=headers)
    assert r.status_code == 200
    detail = client.get(f"/api/biz/{bid}").json()
    assert detail["name"] == "Updated"
    assert detail["version"] == 2

def test_biz_not_found():
    r = client.get("/api/biz/nonexistent-id")
    assert r.status_code == 404
