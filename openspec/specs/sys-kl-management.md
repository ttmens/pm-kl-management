# Spec: sys_kl 知识库管理

## ADDED

### 系统条目数据模型

系统 SHALL 存储 sys_kl 条目，包含以下字段：

- `id`：UUID 文本主键
- `name`：条目名称（必填）
- `description`：Markdown 格式模块职责描述
- `layer`：枚举 — domain / application / infrastructure（DDD 分层）
- `file_path`：代码路径字符串
- `status`：枚举 — draft / published / archived
- `created_by` / `created_at` / `updated_at`：审计字段

### 条目 CRUD API

- `POST /api/sys`：创建条目，初始状态为 `draft`
- `GET /api/sys`：列表查询，支持 `?layer=` 筛选、`?q=` 关键词搜索
- `GET /api/sys/{id}`：返回条目详情、关联 biz_kl 列表
- `PUT /api/sys/{id}`：更新条目，记录审计日志

### 互链管理

- `POST /api/sys/{id}/link`：添加 biz_kl 关联，请求体 `{"biz_id": "..."}`，在 `kl_links` 表中创建记录
- `DELETE /api/sys/{id}/link/{link_id}`：删除关联
- 添加关联时 SHALL 验证 biz_id 对应的条目存在
- `GET /api/sys/{id}` 响应 SHALL 包含关联 biz_kl 条目列表

### 前端页面

- `/sys`：系统知识列表页，支持 DDD 层级筛选和搜索
- `/sys/{id}`：条目详情页，展示完整信息和关联 biz_kl
- 列表页支持「创建系统知识条目」按钮
- 详情页支持「添加关联」操作，提供 biz_kl 搜索选择器
