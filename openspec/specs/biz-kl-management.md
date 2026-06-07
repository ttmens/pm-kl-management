# Spec: biz_kl 知识库管理

## ADDED

### 业务条目数据模型

系统 SHALL 存储 biz_kl 条目，包含以下字段：

- `id`：UUID 文本主键
- `name`：条目名称（必填）
- `description`：Markdown 格式描述
- `type`：枚举 — 概念 / 流程 / 规则
- `tags`：JSON 字符串数组
- `status`：枚举 — draft / reviewing / published / archived
- `version`：整数，每次修改 +1
- `created_by` / `created_at` / `updated_at`：审计字段

### 条目 CRUD API

- `POST /api/biz`：创建条目，初始状态为 `draft`，记录审计日志
- `GET /api/biz`：列表查询，支持 `?status=` 筛选、`?q=` 关键词搜索（name + description + tags）
- `GET /api/biz/{id}`：返回条目详情、关联 sys_kl 列表、版本历史
- `PUT /api/biz/{id}`：更新条目，版本号 +1，记录审计日志

### 审核流程

- `POST /api/biz/{id}/submit`：将状态从 `draft` 改为 `reviewing`，记录审计日志
- `POST /api/biz/{id}/publish`：仅 admin 角色可操作，将状态从 `reviewing` 改为 `published`
- 发布后的条目不可直接编辑，需通过创建新版本的方式

### 版本历史

每次 `PUT /api/biz/{id}` 更新操作 SHALL 在 audit_logs 中记录变更详情（旧值与新值对比）。
`GET /api/biz/{id}` 的响应 SHALL 包含该条目的版本历史列表。

### 前端页面

- `/biz`：业务知识列表页，支持状态筛选和搜索
- `/biz/{id}`：条目详情页，展示完整信息、关联 sys_kl、版本历史
- 列表页支持「创建业务知识条目」按钮，打开创建表单
- 详情页支持「编辑」和「提交审核」操作