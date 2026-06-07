import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
admin_headers = {"X-User-Id": "user-admin"}

@pytest.fixture(autouse=True)
def setup_user():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-admin', 'Admin', 'admin')")
    db.commit()
    db.close()
    yield

def create_published_biz(name="Test Biz"):
    rb = client.post("/api/biz", json={"name": name, "type": "概念", "tags": ["test"]}, headers=admin_headers)
    bid = rb.json()["id"]
    client.post(f"/api/biz/{bid}/submit", headers=admin_headers)
    client.post(f"/api/biz/{bid}/publish", headers=admin_headers)
    return bid

def test_package_single():
    bid = create_published_biz("Pkg Biz 1")
    r = client.get(f"/api/packages?biz_ids={bid}")
    assert r.status_code == 200
    data = r.json()
    assert "biz_kl" in data
    assert "sys_kl" in data
    assert "links" in data
    assert "lineage" in data
    assert len(data["biz_kl"]) == 1
    assert data["biz_kl"][0]["name"] == "Pkg Biz 1"

def test_package_multiple():
    bid1 = create_published_biz("Pkg Biz A")
    bid2 = create_published_biz("Pkg Biz B")
    r = client.get(f"/api/packages?biz_ids={bid1},{bid2}")
    assert r.status_code == 200
    data = r.json()
    assert len(data["biz_kl"]) == 2

def test_package_empty():
    r = client.get("/api/packages?biz_ids=nonexistent")
    assert r.status_code == 200
    data = r.json()
    assert len(data["biz_kl"]) == 0

def test_package_excludes_draft():
    rb = client.post("/api/biz", json={"name": "Draft Biz", "type": "流程"}, headers=admin_headers)
    bid = rb.json()["id"]
    r = client.get(f"/api/packages?biz_ids={bid}")
    data = r.json()
    assert len(data["biz_kl"]) == 0

def test_package_has_version_and_generated_at():
    bid = create_published_biz("Version Test")
    r = client.get(f"/api/packages?biz_ids={bid}")
    data = r.json()
    assert "version" in data
    assert "generated_at" in data
