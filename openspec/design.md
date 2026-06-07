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


## 前端页面（HTMX 服务端渲染）


| 路径        | 说明                             |
| --------- | ------------------------------ |
| /         | 知识列表首页（biz_kl / sys_kl tab 切换） |
| /biz      | 业务知识列表                         |
| /biz/{id} | 业务条目详情                         |
| /sys      | 系统知识列表                         |
| /sys/{id} | 系统条目详情                         |
| /export   | 知识包导出页                         |
| /audit    | 审计日志页                          |


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


| 决策                   | 理由                     |
| -------------------- | ---------------------- |
| SQLite 而非 PostgreSQL | MVP 阶段 ≤10 用户，单文件数据库足够 |
| UUID 文本主键            | 避免暴露递增 ID，便于后续分布式迁移    |
| 版本号为简单整数             | MVP 不做完整 Git-like 版本树  |
| 互链为独立表               | 支持多对多，便于审计和查询          |
| HTMX 而非 SPA          | 避免前端构建工具链，降低 MVP 复杂度   |


