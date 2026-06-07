import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
expert_headers = {"X-User-Id": "user-expert"}
admin_headers = {"X-User-Id": "user-admin"}
dev_headers = {"X-User-Id": "user-dev"}

@pytest.fixture(autouse=True)
def setup_users():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-expert', 'Expert', 'expert')")
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-admin', 'Admin', 'admin')")
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-dev', 'Dev', 'developer')")
    db.commit()
    db.close()
    yield

def test_submit_biz():
    r = client.post("/api/biz", json={"name": "Submit Test", "type": "概念"}, headers=expert_headers)
    bid = r.json()["id"]
    r2 = client.post(f"/api/biz/{bid}/submit", headers=expert_headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "reviewing"

def test_publish_biz_by_admin():
    r = client.post("/api/biz", json={"name": "Publish Test", "type": "流程"}, headers=expert_headers)
    bid = r.json()["id"]
    client.post(f"/api/biz/{bid}/submit", headers=expert_headers)
    r2 = client.post(f"/api/biz/{bid}/publish", headers=admin_headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "published"

def test_publish_biz_denied_non_admin():
    r = client.post("/api/biz", json={"name": "Deny Test", "type": "规则"}, headers=expert_headers)
    bid = r.json()["id"]
    client.post(f"/api/biz/{bid}/submit", headers=expert_headers)
    r2 = client.post(f"/api/biz/{bid}/publish", headers=expert_headers)
    assert r2.status_code == 403

def test_publish_not_reviewing():
    r = client.post("/api/biz", json={"name": "Not Reviewing", "type": "概念"}, headers=expert_headers)
    bid = r.json()["id"]
    r2 = client.post(f"/api/biz/{bid}/publish", headers=admin_headers)
    assert r2.status_code == 400

def test_reject_biz_by_admin():
    r = client.post("/api/biz", json={"name": "Reject Test", "type": "规则"}, headers=expert_headers)
    bid = r.json()["id"]
    client.post(f"/api/biz/{bid}/submit", headers=expert_headers)
    r2 = client.post(f"/api/biz/{bid}/reject", json={"reason": "内容不完整"}, headers=admin_headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "draft"
