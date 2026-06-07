# 设计文档：产品知识平台 MVP

## C4 架构（权威来源）

本设计文档引用 C4 模型产物，不以 ASCII 图为唯一架构表达：

- [系统上下文](../architecture/c4-context.md)
- [容器图](../architecture/c4-container.md)
- [组件图](../architecture/c4-component.md)

## 架构概览（逻辑摘要）

```
┌──────────────────────────────────────────┐
│           静态前端 (HTML + HTMX)           │
│  知识列表 · 条目详情 · 知识包导出 · 审计日志  │
└────────────────┬─────────────────────────┘
                 │ HTTP (JSON)
┌────────────────▼─────────────────────────┐
│          FastAPI 后端 (单机进程)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ biz_kl   │ │ sys_kl   │ │ package  │  │
│  │ 路由层    │ │ 路由层    │ │ 路由层    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │             │             │        │
│  ┌────▼─────────────▼─────────────▼────┐  │
│  │         业务逻辑 / 服务层            │  │
│  │  条目 CRUD · 审核流程 · 互链管理      │  │
│  │  知识包组装 · 审计日志 · 权限校验     │  │
│  └────────────────┬───────────────────┘  │
│                   │                       │
│  ┌────────────────▼───────────────────┐  │
│  │         SQLite 数据存储              │  │
│  │  biz_kl_items · sys_kl_items       │  │
│  │  kl_links · audit_logs · users     │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## 数据模型

### biz_kl_items


| 字段          | 类型              | 说明                                       |
| ----------- | --------------- | ---------------------------------------- |
| id          | TEXT (UUID)     | 主键                                       |
| name        | TEXT            | 条目名称                                     |
| description | TEXT (Markdown) | 条目描述                                     |
| type        | TEXT            | 概念/流程/规则                                 |
| tags        | TEXT (JSON)     | 标签数组                                     |
| status      | TEXT            | draft / reviewing / published / archived |
| version     | INTEGER         | 版本号（每次修改 +1）                             |
| created_by  | TEXT            | 创建者用户 ID                                 |
| created_at  | DATETIME        | 创建时间                                     |
| updated_at  | DATETIME        | 最后更新时间                                   |


### sys_kl_items


| 字段          | 类型              | 说明                                    |
| ----------- | --------------- | ------------------------------------- |
| id          | TEXT (UUID)     | 主键                                    |
| name        | TEXT            | 条目名称                                  |
| description | TEXT (Markdown) | 模块职责描述                                |
| layer       | TEXT            | domain / application / infrastructure |
| file_path   | TEXT            | 代码路径                                  |
| **bounded_context** | **TEXT**  | **所属 Bounded Context（ADR-008）**       |
| status      | TEXT            | draft / published / archived          |
| created_by  | TEXT            | 创建者用户 ID                              |
| created_at  | DATETIME        | 创建时间                                  |
| updated_at  | DATETIME        | 最后更新时间                                |


### kl_links（互链关系）


| 字段         | 类型          | 说明              |
| ---------- | ----------- | --------------- |
| id         | TEXT (UUID) | 主键              |
| biz_id     | TEXT        | 关联 biz_kl 条目 ID |
| sys_id     | TEXT        | 关联 sys_kl 条目 ID |
| **link_type** | **TEXT**  | **关系类型（ADR-008）：implements / dependsOn / governs / acl / published_language / open_host_service** |
| created_at | DATETIME    | 创建时间            |


### audit_logs


| 字段         | 类型          | 说明                                 |
| ---------- | ----------- | ---------------------------------- |
| id         | TEXT (UUID) | 主键                                 |
| item_type  | TEXT        | biz_kl / sys_kl                    |
| item_id    | TEXT        | 条目 ID                              |
| action     | TEXT        | create / update / publish / reject |
| actor_id   | TEXT        | 操作人用户 ID                           |
| details    | TEXT (JSON) | 操作详情（变更前后）                         |
| created_at | DATETIME    | 操作时间                               |


### users（MVP 阶段简化）


| 字段         | 类型          | 说明                         |
| ---------- | ----------- | -------------------------- |
| id         | TEXT (UUID) | 主键                         |
| name       | TEXT        | 用户名                        |
| role       | TEXT        | expert / developer / admin |
| created_at | DATETIME    | 创建时间                       |


### biz_kl_versions（ADR-009）

| 字段        | 类型            | 说明                              |
| ----------- | --------------- | --------------------------------- |
| id          | TEXT (UUID)     | 主键                              |
| item_id     | TEXT            | 外键 → biz_kl_items.id            |
| version     | INTEGER         | 版本号（与 biz_kl_items.version 一致） |
| snapshot    | TEXT (JSON)     | 条目完整内容快照                     |
| actor_id    | TEXT            | 操作人用户 ID                      |
| created_at  | DATETIME        | 快照创建时间                        |


## API 端点

### 业务知识 (biz_kl)


| 方法   | 路径                    | 说明                  |
| ---- | --------------------- | ------------------- |
| GET  | /api/biz              | 列表（支持搜索、状态筛选）       |
| GET  | /api/biz/{id}         | 详情（含关联 sys_kl、版本历史） |
| POST | /api/biz              | 创建条目                |
| PUT  | /api/biz/{id}         | 更新条目                |
| POST | /api/biz/{id}/submit  | 提交审核                |
| POST | /api/biz/{id}/publish | 发布（审核者权限）           |
| POST | /api/biz/{id}/reject  | 驳回（审核者权限，需 rejection_reason） |
| POST | /api/biz/{id}/withdraw | 撤回（作者权限，回滚到最近 published 版本） |
| GET  | /api/biz/{id}/history | 版本历史列表（ADR-009）    |
| GET  | /api/biz/{id}/history/{v1}/{v2} | 版本 diff（ADR-009） |


### 系统知识 (sys_kl)


| 方法     | 路径                           | 说明             |
| ------ | ---------------------------- | -------------- |
| GET    | /api/sys                     | 列表（支持搜索、层级筛选）  |
| GET    | /api/sys/{id}                | 详情（含关联 biz_kl） |
| POST   | /api/sys                     | 创建条目           |
| PUT    | /api/sys/{id}                | 更新条目           |
| POST   | /api/sys/{id}/link           | 添加 biz_kl 关联   |
| DELETE | /api/sys/{id}/link/{link_id} | 删除关联           |


### 知识包


| 方法  | 路径                         | 说明                     |
| --- | -------------------------- | ---------------------- |
| GET | /api/packages?biz_ids=...  | 按 biz_kl 条目生成知识包（JSON） |
| GET | /api/packages/{biz_ids}.md | Markdown 格式导出          |


### 审计日志


| 方法  | 路径         | 说明                |
| --- | ---------- | ----------------- |
| GET | /api/audit | 列表（支持条目/操作人/时间筛选） |


### 审批队列（ADR-006）


| 方法  | 路径         | 说明                |
| --- | ---------- | ----------------- |
| GET | /api/review | 列出所有 reviewing 状态条目（管理员视角） |


## 前端页面（HTMX 服务端渲染）
## 前端页面（HTMX 服务端渲染）

| 路径        | 说明                             | 旅程触点 |
| --------- | ------------------------------ |--------|
| /         | 知识列表首页（biz_kl / sys_kl tab 切换） | TP1 |
| /biz      | 业务知识列表                         | TP1 |
| /biz/{id} | 业务条目详情（含关联 sys_kl、版本历史、撤回按钮） | TP3, TP11 |
| /biz/{id}/history | 版本历史列表（ADR-009）    | TP11 |
| /biz/{id}/history/{v1}/{v2} | 版本 diff 对比（ADR-009） | TP11 |
| /sys      | 系统知识列表（含 BC 筛选）              | TP5 |
| /sys/{id} | 系统条目详情（含 BC 归属、link_type）   | TP7, TP8 |
| /export   | 知识包导出页（仅 published，权限感知）     | TP9, TP10 |
| /review   | 审批者队列（ADR-006，仅管理员可见）      | TP4 |
| /audit    | 审计日志页                          | TP12 |
| /admin/users | 用户管理页（角色分配）               | TP13 |


## 知识包 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "KnowledgePackage",
  "type": "object",
  "required": ["version", "generated_at", "biz_kl", "sys_kl", "links"],
  "properties": {
    "version": { "type": "string" },
    "generated_at": { "type": "string", "format": "date-time" },
    "biz_kl": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type", "status"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string", "enum": ["概念", "流程", "规则"] },
          "description": { "type": "string" },
          "tags": { "type": "array", "items": { "type": "string" } },
          "status": { "type": "string" },
          "version": { "type": "integer" }
        }
      }
    },
    "sys_kl": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "layer"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "layer": { "type": "string", "enum": ["domain", "application", "infrastructure"] },
          "description": { "type": "string" },
          "file_path": { "type": "string" },
          "linked_biz": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "links": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["biz_id", "sys_id"],
        "properties": {
          "biz_id": { "type": "string" },
          "sys_id": { "type": "string" }
        }
      }
    },
    "lineage": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "created_by": { "type": "string" },
          "created_at": { "type": "string" }
        }
      }
    }
  }
}
```

## 安全与权限

MVP 阶段权限为简化模型：

- 领域专家：创建/编辑/提交 biz_kl 条目
- 开发者：创建/编辑 sys_kl 条目、导出知识包
- 管理员：审核 biz_kl 条目、管理用户角色、查看审计日志

MVP 实现方式：通过请求头 `X-User-Id` 传递用户标识，不做认证（内部工具）。权限校验在服务层完成。

## 决策
## 决策

| 决策 | 理由 |
|------|------|
| SQLite 而非 PostgreSQL | MVP 阶段 ≤10 用户，单文件数据库足够 |
| UUID 文本主键 | 避免暴露递增 ID，便于后续分布式迁移 |
| 版本号为简单整数 | MVP 不做完整 Git-like 版本树 |
| 互链为独立表 | 支持多对多，便于审计和查询 |
| HTMX 而非 SPA | 避免前端构建工具链，降低 MVP 复杂度 |
| biz_kl_versions 快照表（ADR-009） | 支持回滚、版本对比、完整审计 |
| bounded_context 字段（ADR-008） | sys_kl 按 BC 分组，知识包按 BC 组织 |
| link_type 字段（ADR-008） | 关系语义化（implements/dependsOn/governs 等） |
| 知识包状态过滤（ADR-007） | 仅导出 published 条目，保证 Agent 消费质量 |
| 权限感知导出（ADR-007） | 按请求者角色过滤可见范围 |
| 撤回 + 回滚机制（ADR-006） | 审核流闭环，支持知识生命周期管理 |


