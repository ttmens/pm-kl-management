# Spec: 审计日志与权限管理

## ADDED

### 审计日志数据模型

系统 SHALL 记录所有条目操作的审计日志，包含：

- `id`：UUID 主键
- `item_type`：biz_kl / sys_kl
- `item_id`：关联条目 ID
- `action`：create / update / submit / publish / reject
- `actor_id`：操作人用户 ID
- `details`：JSON 格式操作详情（变更前后值）
- `created_at`：操作时间戳

### 审计日志 API

- `GET /api/audit`：查询审计日志
  - 支持 `?item_id=`、`?actor_id=`、`?from=`、`?to=` 筛选
  - 按 `created_at` 倒序排列

### 审计日志页面

- `/audit`：审计日志页面（仅 admin 角色可见）
  - 表格展示：条目 ID、操作类型、操作人、时间
  - 支持按条目、操作人、时间范围筛选

### 用户管理（MVP 简化）

- `users` 表存储用户基本信息（id, name, role）
- 角色：expert（领域专家）/ developer（开发者）/ admin（管理员）
- MVP 阶段通过请求头 `X-User-Id` 传递用户标识，不做认证
- 管理员可修改用户角色（记录在审计日志中）
- 权限校验在服务层完成：
  - `publish` biz_kl：仅 admin
  - 创建/编辑 biz_kl：expert
  - 创建/编辑 sys_kl：developer
  - 导出知识包：developer / admin
  - 查看审计日志：admin