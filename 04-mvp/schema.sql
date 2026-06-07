CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('expert', 'developer', 'admin')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS biz_kl_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL CHECK(type IN ('概念', '流程', '规则')),
    tags TEXT DEFAULT '[]',
    status TEXT NOT NULL CHECK(status IN ('draft', 'reviewing', 'published', 'archived')) DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    created_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sys_kl_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    layer TEXT NOT NULL CHECK(layer IN ('domain', 'application', 'infrastructure')),
    file_path TEXT,
    status TEXT NOT NULL CHECK(status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
    created_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kl_links (
    id TEXT PRIMARY KEY,
    biz_id TEXT NOT NULL REFERENCES biz_kl_items(id),
    sys_id TEXT NOT NULL REFERENCES sys_kl_items(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL CHECK(item_type IN ('biz_kl', 'sys_kl')),
    item_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('create', 'update', 'publish', 'reject', 'submit', 'link', 'unlink')),
    actor_id TEXT NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
