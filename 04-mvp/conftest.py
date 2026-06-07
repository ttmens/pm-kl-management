import pytest
import os
import models

TEST_DB = "data/test_kl.db"


@pytest.fixture(autouse=True)
def clean_db():
    os.makedirs("data", exist_ok=True)
    models.DB_PATH = TEST_DB
    models.init_db()
    db = models.get_db()
    for table in ["audit_logs", "biz_kl_versions", "kl_links", "biz_kl_items", "sys_kl_items", "users"]:
        db.execute(f"DELETE FROM {table}")
    db.commit()
    db.close()
    yield
    # Cleanup after test
    pass
