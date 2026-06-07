import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
expert_headers = {"X-User-Id": "user-expert"}
dev_headers = {"X-User-Id": "user-dev"}

@pytest.fixture(autouse=True)
def setup_users():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-expert', 'Expert', 'expert')")
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-dev', 'Dev', 'developer')")
    db.commit()
    db.close()
    yield

def test_create_link():
    rb = client.post("/api/biz", json={"name": "Biz", "type": "概念"}, headers=expert_headers)
    bid = rb.json()["id"]
    rs = client.post("/api/sys", json={"name": "Sys", "layer": "domain"}, headers=dev_headers)
    sid = rs.json()["id"]
    r = client.post(f"/api/sys/{sid}/link", json={"biz_id": bid}, headers=dev_headers)
    assert r.status_code == 200
    assert "id" in r.json()

def test_link_nonexistent_biz():
    rs = client.post("/api/sys", json={"name": "Sys", "layer": "domain"}, headers=dev_headers)
    sid = rs.json()["id"]
    r = client.post(f"/api/sys/{sid}/link", json={"biz_id": "nonexistent"}, headers=dev_headers)
    assert r.status_code == 404

def test_delete_link():
    rb = client.post("/api/biz", json={"name": "Biz2", "type": "流程"}, headers=expert_headers)
    bid = rb.json()["id"]
    rs = client.post("/api/sys", json={"name": "Sys2", "layer": "application"}, headers=dev_headers)
    sid = rs.json()["id"]
    r_link = client.post(f"/api/sys/{sid}/link", json={"biz_id": bid}, headers=dev_headers)
    link_id = r_link.json()["id"]
    r = client.delete(f"/api/sys/{sid}/link/{link_id}", headers=dev_headers)
    assert r.status_code == 200
    assert r.json()["deleted"] == True

def test_delete_nonexistent_link():
    rs = client.post("/api/sys", json={"name": "Sys3", "layer": "domain"}, headers=dev_headers)
    r = client.delete(f"/api/sys/{rs.json()['id']}/link/nonexistent", headers=dev_headers)
    assert r.status_code == 404

def test_biz_detail_has_linked_sys():
    rb = client.post("/api/biz", json={"name": "Biz", "type": "概念"}, headers=expert_headers)
    bid = rb.json()["id"]
    rs = client.post("/api/sys", json={"name": "Sys", "layer": "domain"}, headers=dev_headers)
    sid = rs.json()["id"]
    client.post(f"/api/sys/{sid}/link", json={"biz_id": bid}, headers=dev_headers)
    r = client.get(f"/api/biz/{bid}")
    linked = r.json()["linked_sys"]
    assert len(linked) == 1
    assert linked[0]["id"] == sid

def test_sys_detail_has_linked_biz():
    rb = client.post("/api/biz", json={"name": "Biz", "type": "规则"}, headers=expert_headers)
    bid = rb.json()["id"]
    rs = client.post("/api/sys", json={"name": "Sys", "layer": "infrastructure"}, headers=dev_headers)
    sid = rs.json()["id"]
    client.post(f"/api/sys/{sid}/link", json={"biz_id": bid}, headers=dev_headers)
    r = client.get(f"/api/sys/{sid}")
    linked = r.json()["linked_biz"]
    assert len(linked) == 1
    assert linked[0]["id"] == bid
