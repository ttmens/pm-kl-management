import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
headers = {"X-User-Id": "user-1"}

@pytest.fixture(autouse=True)
def setup_user():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-1', 'Dev', 'developer')")
    db.commit()
    db.close()
    yield

def test_create_sys():
    r = client.post("/api/sys", json={"name": "Svc", "description": "Desc", "layer": "domain", "file_path": "app/svc.py"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "draft"

def test_create_sys_all_layers():
    for layer in ["domain", "application", "infrastructure"]:
        r = client.post("/api/sys", json={"name": f"Layer {layer}", "layer": layer}, headers=headers)
        assert r.status_code == 200

def test_get_sys_list():
    client.post("/api/sys", json={"name": "Item1", "layer": "domain"}, headers=headers)
    client.post("/api/sys", json={"name": "Item2", "layer": "application"}, headers=headers)
    r = client.get("/api/sys")
    assert r.status_code == 200
    assert len(r.json()) == 2

def test_get_sys_list_by_layer():
    client.post("/api/sys", json={"name": "Domain Svc", "layer": "domain"}, headers=headers)
    client.post("/api/sys", json={"name": "Infra Svc", "layer": "infrastructure"}, headers=headers)
    r = client.get("/api/sys?layer=domain")
    assert all(item["layer"] == "domain" for item in r.json())

def test_get_sys_detail():
    r_create = client.post("/api/sys", json={"name": "Detail Svc", "layer": "domain", "file_path": "app/path.py"}, headers=headers)
    sid = r_create.json()["id"]
    r = client.get(f"/api/sys/{sid}")
    assert r.status_code == 200
    assert r.json()["file_path"] == "app/path.py"

def test_update_sys():
    r_create = client.post("/api/sys", json={"name": "Update Svc", "layer": "domain"}, headers=headers)
    sid = r_create.json()["id"]
    r = client.put(f"/api/sys/{sid}", json={"name": "Updated Svc", "layer": "application"}, headers=headers)
    assert r.status_code == 200
    detail = client.get(f"/api/sys/{sid}").json()
    assert detail["name"] == "Updated Svc"
    assert detail["layer"] == "application"
