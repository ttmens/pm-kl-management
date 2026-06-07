import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

DB_PATH = "data/kl.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    import os
    os.makedirs("data", exist_ok=True)
    conn = get_db()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


@dataclass
class BizKlItem:
    id: str
    name: str
    description: str
    type: str
    tags: list = field(default_factory=list)
    status: str = "draft"
    version: int = 1
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class SysKlItem:
    id: str
    name: str
    description: str
    layer: str
    file_path: str = ""
    status: str = "draft"
    created_by: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class KlLink:
    id: str
    biz_id: str
    sys_id: str
    created_at: str = ""


@dataclass
class AuditLog:
    id: str
    item_type: str
    item_id: str
    action: str
    actor_id: str
    details: str = ""
    created_at: str = ""


@dataclass
class User:
    id: str
    name: str
    role: str
    created_at: str = ""


def get_user(db, user_id: str) -> Optional[User]:
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        return User(**dict(row))
    return None


def audit(db, item_type: str, item_id: str, action: str, actor_id: str, details: dict = None):
    log_id = str(uuid.uuid4())
    details_json = json.dumps(details or {})
    db.execute(
        "INSERT INTO audit_logs (id, item_type, item_id, action, actor_id, details) VALUES (?, ?, ?, ?, ?, ?)",
        (log_id, item_type, item_id, action, actor_id, details_json),
    )


## biz_kl CRUD

def create_biz(db, name: str, description: str, type: str, tags: list, created_by: str) -> BizKlItem:
    item_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    tags_json = json.dumps(tags)
    db.execute(
        "INSERT INTO biz_kl_items (id, name, description, type, tags, status, version, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'draft', 1, ?, ?, ?)",
        (item_id, name, description, type, tags_json, created_by, now, now),
    )
    audit(db, "biz_kl", item_id, "create", created_by, {"name": name})
    db.commit()
    return get_biz(db, item_id)


def get_biz(db, item_id: str) -> Optional[BizKlItem]:
    row = db.execute("SELECT * FROM biz_kl_items WHERE id = ?", (item_id,)).fetchone()
    if row:
        d = dict(row)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        return BizKlItem(**d)
    return None


def list_biz(db, status: str = None, q: str = None) -> list[BizKlItem]:
    sql = "SELECT * FROM biz_kl_items WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    sql += " ORDER BY updated_at DESC"
    rows = db.execute(sql, params).fetchall()
    items = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        items.append(BizKlItem(**d))
    return items


def update_biz(db, item_id: str, name: str = None, description: str = None, type: str = None, tags: list = None, actor_id: str = None) -> Optional[BizKlItem]:
    existing = get_biz(db, item_id)
    if not existing:
        return None
    now = datetime.utcnow().isoformat()
    updates = []
    params = []
    changes = {}
    if name is not None:
        updates.append("name = ?")
        params.append(name)
        changes["name"] = {"old": existing.name, "new": name}
    if description is not None:
        updates.append("description = ?")
        params.append(description)
        changes["description"] = {"old": existing.description, "new": description}
    if type is not None:
        updates.append("type = ?")
        params.append(type)
        changes["type"] = {"old": existing.type, "new": type}
    if tags is not None:
        updates.append("tags = ?")
        params.append(json.dumps(tags))
        changes["tags"] = {"old": existing.tags, "new": tags}
    updates.append("version = ?")
    params.append(existing.version + 1)
    updates.append("updated_at = ?")
    params.append(now)
    params.append(item_id)
    db.execute(f"UPDATE biz_kl_items SET {', '.join(updates)} WHERE id = ?", params)
    audit(db, "biz_kl", item_id, "update", actor_id, changes)
    db.commit()
    return get_biz(db, item_id)


def submit_biz(db, item_id: str, actor_id: str) -> Optional[BizKlItem]:
    existing = get_biz(db, item_id)
    if not existing or existing.status != "draft":
        return None
    now = datetime.utcnow().isoformat()
    db.execute("UPDATE biz_kl_items SET status = 'reviewing', updated_at = ? WHERE id = ?", (now, item_id))
    audit(db, "biz_kl", item_id, "submit", actor_id)
    db.commit()
    return get_biz(db, item_id)


def publish_biz(db, item_id: str, actor_id: str) -> Optional[BizKlItem]:
    user = get_user(db, actor_id)
    if not user or user.role != "admin":
        return None
    existing = get_biz(db, item_id)
    if not existing or existing.status != "reviewing":
        return None
    now = datetime.utcnow().isoformat()
    db.execute("UPDATE biz_kl_items SET status = 'published', updated_at = ? WHERE id = ?", (now, item_id))
    audit(db, "biz_kl", item_id, "publish", actor_id)
    db.commit()
    return get_biz(db, item_id)


def reject_biz(db, item_id: str, actor_id: str, reason: str = "") -> Optional[BizKlItem]:
    user = get_user(db, actor_id)
    if not user or user.role != "admin":
        return None
    existing = get_biz(db, item_id)
    if not existing or existing.status != "reviewing":
        return None
    now = datetime.utcnow().isoformat()
    db.execute("UPDATE biz_kl_items SET status = 'draft', updated_at = ? WHERE id = ?", (now, item_id))
    audit(db, "biz_kl", item_id, "reject", actor_id, {"reason": reason or "rejected"})
    db.commit()
    return get_biz(db, item_id)


## sys_kl CRUD

def create_sys(db, name: str, description: str, layer: str, file_path: str, created_by: str) -> SysKlItem:
    item_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    db.execute(
        "INSERT INTO sys_kl_items (id, name, description, layer, file_path, status, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'draft', ?, ?, ?)",
        (item_id, name, description, layer, file_path, created_by, now, now),
    )
    audit(db, "sys_kl", item_id, "create", created_by, {"name": name})
    db.commit()
    return get_sys(db, item_id)


def get_sys(db, item_id: str) -> Optional[SysKlItem]:
    row = db.execute("SELECT * FROM sys_kl_items WHERE id = ?", (item_id,)).fetchone()
    if row:
        return SysKlItem(**dict(row))
    return None


def list_sys(db, layer: str = None, q: str = None) -> list[SysKlItem]:
    sql = "SELECT * FROM sys_kl_items WHERE 1=1"
    params = []
    if layer:
        sql += " AND layer = ?"
        params.append(layer)
    if q:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    sql += " ORDER BY updated_at DESC"
    rows = db.execute(sql, params).fetchall()
    return [SysKlItem(**dict(r)) for r in rows]


def update_sys(db, item_id: str, name: str = None, description: str = None, layer: str = None, file_path: str = None, actor_id: str = None) -> Optional[SysKlItem]:
    existing = get_sys(db, item_id)
    if not existing:
        return None
    now = datetime.utcnow().isoformat()
    updates = []
    params = []
    changes = {}
    if name is not None:
        updates.append("name = ?")
        params.append(name)
        changes["name"] = {"old": existing.name, "new": name}
    if description is not None:
        updates.append("description = ?")
        params.append(description)
        changes["description"] = {"old": existing.description, "new": description}
    if layer is not None:
        updates.append("layer = ?")
        params.append(layer)
        changes["layer"] = {"old": existing.layer, "new": layer}
    if file_path is not None:
        updates.append("file_path = ?")
        params.append(file_path)
        changes["file_path"] = {"old": existing.file_path, "new": file_path}
    updates.append("updated_at = ?")
    params.append(now)
    params.append(item_id)
    db.execute(f"UPDATE sys_kl_items SET {', '.join(updates)} WHERE id = ?", params)
    audit(db, "sys_kl", item_id, "update", actor_id, changes)
    db.commit()
    return get_sys(db, item_id)


## Links

def create_link(db, sys_id: str, biz_id: str, actor_id: str) -> Optional[KlLink]:
    biz = get_biz(db, biz_id)
    sys = get_sys(db, sys_id)
    if not biz or not sys:
        return None
    link_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    db.execute(
        "INSERT INTO kl_links (id, biz_id, sys_id, created_at) VALUES (?, ?, ?, ?)",
        (link_id, biz_id, sys_id, now),
    )
    audit(db, "biz_kl", biz_id, "link", actor_id, {"sys_id": sys_id})
    db.commit()
    return KlLink(id=link_id, biz_id=biz_id, sys_id=sys_id, created_at=now)


def delete_link(db, sys_id: str, link_id: str, actor_id: str) -> bool:
    link = db.execute("SELECT * FROM kl_links WHERE id = ? AND sys_id = ?", (link_id, sys_id)).fetchone()
    if not link:
        return False
    audit(db, "biz_kl", link["biz_id"], "unlink", actor_id, {"link_id": link_id})
    db.execute("DELETE FROM kl_links WHERE id = ? AND sys_id = ?", (link_id, sys_id))
    db.commit()
    return True


def get_links_for_biz(db, biz_id: str) -> list[SysKlItem]:
    rows = db.execute(
        "SELECT s.* FROM sys_kl_items s JOIN kl_links l ON s.id = l.sys_id WHERE l.biz_id = ?",
        (biz_id,),
    ).fetchall()
    return [SysKlItem(**dict(r)) for r in rows]


def get_links_for_sys(db, sys_id: str) -> list[BizKlItem]:
    rows = db.execute(
        "SELECT b.* FROM biz_kl_items b JOIN kl_links l ON b.id = l.biz_id WHERE l.sys_id = ?",
        (sys_id,),
    ).fetchall()
    items = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        items.append(BizKlItem(**d))
    return items


## Audit

def list_audit(db, item_id: str = None, actor_id: str = None, from_dt: str = None, to_dt: str = None) -> list[AuditLog]:
    sql = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    if item_id:
        sql += " AND item_id = ?"
        params.append(item_id)
    if actor_id:
        sql += " AND actor_id = ?"
        params.append(actor_id)
    if from_dt:
        sql += " AND created_at >= ?"
        params.append(from_dt)
    if to_dt:
        sql += " AND created_at <= ?"
        params.append(to_dt)
    sql += " ORDER BY created_at DESC"
    rows = db.execute(sql, params).fetchall()
    return [AuditLog(**dict(r)) for r in rows]


## Import

def import_biz_from_markdown(db, content: str, created_by: str) -> list[BizKlItem]:
    """Parse markdown format: # 名称\n\n描述\n\n类型: xxx\n标签: tag1, tag2"""
    items = []
    normalized = content.strip()
    if not normalized.startswith("# "):
        normalized = "# " + normalized
    blocks = normalized.split("\n# ")

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            block = block[2:]

        lines = block.split("\n")
        name = lines[0].strip()
        if not name:
            continue

        # Must have 类型: line to be valid
        metadata_start = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip().startswith("类型:") or line.strip().startswith("类型："):
                metadata_start = i
                break

        if metadata_start < 0:
            continue

        description = "\n".join(lines[1:metadata_start]).strip()

        item_type = "概念"
        tags = []
        for line in lines[metadata_start:]:
            line = line.strip()
            if line.startswith("类型:"):
                item_type = line.replace("类型:", "").strip()
            elif line.startswith("类型："):
                item_type = line.replace("类型：", "").strip()
            elif line.startswith("标签:"):
                tags = [t.strip() for t in line.replace("标签:", "").split(",") if t.strip()]
            elif line.startswith("标签："):
                tags = [t.strip() for t in line.replace("标签：", "").split(",") if t.strip()]

        item = create_biz(db, name=name, description=description, type=item_type, tags=tags, created_by=created_by)
        items.append(item)

    return items
