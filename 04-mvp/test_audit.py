import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
headers = {"X-User-Id": "user-1"}

@pytest.fixture(autouse=True)
def setup_user():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-1', 'Test', 'expert')")
    db.commit()
    db.close()
    yield

def test_audit_logs_on_create():
    client.post("/api/biz", json={"name": "Audit Test", "type": "概念"}, headers=headers)
    r = client.get("/api/audit")
    assert len(r.json()) == 1
    assert r.json()[0]["action"] == "create"

def test_audit_filter_by_item():
    rb = client.post("/api/biz", json={"name": "Filter Test", "type": "流程"}, headers=headers)
    bid = rb.json()["id"]
    r = client.get(f"/api/audit?item_id={bid}")
    assert len(r.json()) == 1
    assert r.json()[0]["item_id"] == bid

def test_audit_filter_by_actor():
    client.post("/api/biz", json={"name": "Actor Test", "type": "规则"}, headers=headers)
    r = client.get("/api/audit?actor_id=user-1")
    assert len(r.json()) >= 1
    assert all(log["actor_id"] == "user-1" for log in r.json())

def test_audit_ordered_by_date():
    client.post("/api/biz", json={"name": "First", "type": "概念"}, headers=headers)
    client.post("/api/biz", json={"name": "Second", "type": "概念"}, headers=headers)
    r = client.get("/api/audit")
    logs = r.json()
    assert len(logs) >= 2
    assert logs[0]["created_at"] >= logs[1]["created_at"]
