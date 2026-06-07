import pytest
from fastapi.testclient import TestClient
import models

models.init_db()
client = TestClient(__import__("app").app)
headers = {"X-User-Id": "user-expert"}

@pytest.fixture(autouse=True)
def setup_user():
    db = models.get_db()
    db.execute("INSERT INTO users (id, name, role) VALUES ('user-expert', 'Expert', 'expert')")
    db.commit()
    db.close()
    yield

valid_markdown = """# 订单处理流程

用户下单后，系统依次进行库存校验、支付处理、物流分配。

类型: 流程
标签: 订单, 支付

# 退货规则

用户申请退货需满足: 1. 订单已签收 2. 7天内 3. 商品完好。

类型: 规则
标签: 售后, 退货
"""

def test_import_valid_markdown():
    r = client.post("/api/import/biz", json={"content": valid_markdown}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2

def test_import_creates_draft_items():
    r = client.post("/api/import/biz", json={"content": valid_markdown}, headers=headers)
    ids = r.json()["ids"]
    for bid in ids:
        detail = client.get(f"/api/biz/{bid}").json()
        assert detail["status"] == "draft"

def test_import_with_bad_format():
    bad_content = "This is not valid markdown format for import"
    r = client.post("/api/import/biz", json={"content": bad_content}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
