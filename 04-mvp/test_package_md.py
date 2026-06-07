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

def create_published_biz(name="Test"):
    rb = client.post("/api/biz", json={"name": name, "type": "概念", "description": "Desc", "tags": ["test"]}, headers=admin_headers)
    bid = rb.json()["id"]
    client.post(f"/api/biz/{bid}/submit", headers=admin_headers)
    client.post(f"/api/biz/{bid}/publish", headers=admin_headers)
    return bid

def test_package_md():
    bid = create_published_biz("MD Test")
    r = client.get(f"/api/packages/{bid}.md")
    assert r.status_code == 200
    content = r.text
    assert "MD Test" in content

def test_package_md_has_title():
    bid = create_published_biz("Title Test")
    r = client.get(f"/api/packages/{bid}.md")
    assert "Title Test" in r.text

def test_package_md_has_description():
    bid = create_published_biz("Desc Test")
    rs = client.post("/api/sys", json={"name": "Sys", "layer": "domain", "file_path": "app/svc.py"}, headers=admin_headers)
    sid = rs.json()["id"]
    client.post(f"/api/sys/{sid}/link", json={"biz_id": bid}, headers=admin_headers)
    r = client.get(f"/api/packages/{bid}.md")
    assert "关联代码模块" in r.text
