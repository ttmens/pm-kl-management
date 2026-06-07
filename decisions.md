# 决策日志（Architecture Decision Records）

## ADR-001: biz_kl 与 sys_kl 严格分离，禁止混库

**状态**: Accepted  
**决策日期**: 2026-06-07  
**决策者**: pm-aligner（基于简报约束推导）

### 背景

平台需要同时管理业务知识（biz_kl）和系统逻辑知识（sys_kl），两者来源、生命周期、消费场景均不同。简报明确要求"知识模型需区分 biz_kl / sys_kl，禁止混库"。

### 决策

biz_kl 与 sys_kl 采用独立存储与独立数据模型，仅通过互链关系（业务概念 ↔ 代码模块）建立关联。

### 理由

- 业务知识变更频率低、依赖专家审核；系统知识变更频率高、随代码迭代
- 两者的检索模式不同：biz_kl 偏语义检索，sys_kl 偏结构化查询
- 分离便于权限控制（专家管 biz_kl，开发管 sys_kl）
- 降低 MVP 阶段的模型复杂度

### 后果

- ✅ 模型清晰，便于分角色治理
- ⚠️ 需要维护跨库的互链关系，增加一致性校验成本
- ⚠️ 跨库联合查询需要额外设计（如知识包组装时的拼接逻辑）

---

## ADR-002: MVP 阶段 sys_kl 采用半自动挂载，不追求全自动逆向

**状态**: Accepted  
**决策日期**: 2026-06-07  
**决策者**: pm-aligner（基于简报约束推导）

### 背景

供应链 IT 系统为百万行级存量代码，全自动静态分析引擎建设成本高、周期长。简报明确"首期不做全仓自动静态分析引擎"，但允许"人工+模板+半自动"。

### 决策

MVP 阶段 sys_kl 条目通过以下方式生成：

1. 专家手工标注核心模块
2. 半自动工具辅助提取模块结构（如 AST 解析、调用链提取）
3. 模板化批量导入辅助数据

### 理由

- 百万行代码全自动逆向工程投入产出比低
- 核心模块（高频变更、高业务价值）优先覆盖即可验证价值
- 半自动方式可快速迭代，积累标注数据后反哺自动化引擎

### 后果

- ✅ 大幅降低 MVP 开发成本，缩短验证周期
- ⚠️ 需要领域专家投入时间进行手工标注
- ⚠️ 覆盖率有限，初期可能遗漏边缘模块

---

## ADR-003: MVP 阶段知识消费仅提供只读 API/导出，不建设 IDE 插件

**状态**: Accepted  
**决策日期**: 2026-06-07  
**决策者**: pm-aligner（基于简报约束推导）

### 背景

简报明确"不做完整 IDE 插件市场（先 API/导出）"，MVP 范围中知识应用定位为"给 Agent 用的知识包导出或 API（先只读）"。

### 决策

MVP 阶段知识消费接口：

1. RESTful API：Agent 可拉取知识包（JSON 格式）
2. 文件导出：支持 JSON/Markdown 格式离线使用
3. 仅支持只读操作，不开放写入或交互式编辑

### 理由

- IDE 插件开发涉及多编辑器兼容、UI/UX 设计，投入大
- Agent 消费是核心验证场景，API 接口更直接
- 只读设计降低安全与权限复杂度

### 后果

- ✅ 聚焦核心价值验证，避免 IDE 兼容性泥潭
- ⚠️ 开发者体验不如原生 IDE 插件流畅
- ⚠️ 需要 Agent 侧具备 API 消费能力（见 Assumption #3）

---

## ADR-004: MVP 技术栈选择——轻量 Web 应用（FastAPI + SQLite + 静态前端）

**状态**: Proposed  
**决策日期**: 2026-06-07  
**决策者**: pm-analyst

### 背景

MVP 需要快速验证 biz_kl/sys_kl 双库 + 知识包导出的核心价值，技术栈需满足：开发速度快、部署简单、后续可迁移。

### 决策

- 后端：Python FastAPI（RESTful API，原生异步，类型安全）
- 存储：SQLite（单文件数据库，MVP 足够，后续可迁移 PostgreSQL）
- 前端：静态 HTML + HTMX（无需构建工具，服务端渲染）
- 部署：单机 Python 进程，无容器依赖

### 理由

- 团队有 Python 经验，FastAPI 学习成本低
- SQLite 零配置，适合单 BC 试点（数据量 ≤1000 条目）
- 静态前端 + HTMX 避免前端工程化开销
- 技术栈轻量，验证失败时沉没成本低

### 后果

- ✅ 2-4 周可完成 MVP 开发
- ✅ 部署极简，一台机器即可运行
- ⚠️ SQLite 不支持高并发，但 MVP 阶段用户 ≤10 人
- ⚠️ 后续扩展需迁移数据库，但数据结构设计时可预留兼容性

---

## ADR-005: 知识包导出格式——JSON Schema + Markdown 双格式

**状态**: Proposed  
**决策日期**: 2026-06-07  
**决策者**: pm-analyst

### 背景

MVP 需要提供「给 Agent 用的知识包」，消费端可能是 API 调用也可能是离线文件。

### 决策

- JSON 格式：结构化数据，包含 biz_kl 条目、sys_kl 条目、互链关系、血缘信息，符合预定义 JSON Schema
- Markdown 格式：人类可读版本，按业务概念分组，每条包含概念描述、关联代码模块、变更历史

### 理由

- JSON 适合 Agent/API 消费，可被程序解析
- Markdown 适合人工审阅和 Git 版本控制
- 双格式覆盖 MVP 两种消费场景（API 拉取 + 文件导出）

### 后果

- ✅ 同时满足机器和人类消费
- ⚠️ 需维护两种格式的一致性（可由同一数据源生成）
- ⚠️ JSON Schema 需要版本管理，向后兼容

---

## ADR-006: 审核流完善——撤回 + 回滚机制

**状态**: Proposed
**决策日期**: 2026-06-07
**决策者**: pm-analyst（Refine-2）

### 背景

Refine-1 benchmark（案例 2：Confluence 审批工作流）发现当前审核流仅支持 submit → publish / reject，缺少撤回（withdraw）和回滚到最近已审批版本的能力。reject 后仅状态变 draft，不记录驳回理由，用户无法区分"被驳回的草稿"与"从未提交的草稿"。

### 决策

- 增加 `POST /api/biz/{id}/withdraw` 端点，允许作者在 `reviewing` 或 `rejected` 态撤回
- 撤回时自动回滚到最近 `published` 版本的内容（如存在）
- `reject_biz` API 路由补全（函数已存在但无路由/UI）
- `audit_logs` 增加 `rejection_reason` 字段记录驳回理由
- 审核中页面展示策略：`reviewing` 态条目同时展示已发布版本 + 审核中标记 + 变更 diff

### 理由

- Confluence 完整状态机（editing → waiting → accepted/rejected + withdraw）是业界成熟模式
- 无回滚能力时，驳回后的知识丢失风险高
- 驳回理由持久化是审计合规的基本要求

### 后果

- ✅ 审核流闭环，支持知识生命周期管理
- ✅ 驳回理由可追溯，便于作者修改
- ⚠️ 需增加版本快照机制（见 ADR-009）支撑回滚
- ⚠️ 审核中内容展示策略增加 UI 复杂度

**影响的 C4 容器**: API Server、Audit Service、Web UI

---

## ADR-007: 知识包导出——状态过滤 + 权限感知

**状态**: Proposed
**决策日期**: 2026-06-07
**决策者**: pm-analyst（Refine-2）

### 背景

Refine-1 benchmark 发现两个 P0 差距：

1. GitBook MCP 仅暴露已发布版本，当前知识包可能包含 draft/reviewing 条目
2. Glean 按权限过滤内容，当前知识包对所有条目一视同仁，无角色感知

### 决策

- 知识包导出时仅包含 `status = published` 的条目
- 导出 API 接受请求者身份（`X-User-Id`），按角色过滤可见范围：
  - `expert`：仅包含其创建/审核通过的 biz_kl 条目
  - `developer`：包含全部 published 条目
  - `admin`：包含全部 published 条目 + 审计元数据
- 知识包 JSON 增加 `access_control` 字段，记录导出时的角色过滤规则

### 理由

- Agent 消费的知识包必须保证内容质量，draft/reviewing 条目不应泄露
- 权限感知是企业级知识平台的标配（Glean 93% 采纳率验证）
- 角色过滤在导出时完成，不影响存储层设计

### 后果

- ✅ 知识包内容质量可控
- ✅ 符合企业安全合规要求
- ⚠️ 导出逻辑复杂度增加
- ⚠️ 需确保 `X-User-Id` 在导出请求中可靠传递

**影响的 C4 容器**: Export Service、API Server

---

## ADR-008: Bounded Context 建模——sys_kl 增加 BC 归属

**状态**: Proposed
**决策日期**: 2026-06-07
**决策者**: pm-analyst（Refine-2）

### 背景

Refine-1 benchmark（案例 5：Context Mapper + BC Canvas）发现当前 sys_kl 无 Bounded Context 概念，仅按 DDD 层（domain/application/infrastructure）分类。这导致：

- 知识包无法按 BC 组织
- 无法表达上下文映射模式（ACL / Published Language / Open-Host Service）
- 无法指导专家按 BC 贡献知识

### 决策

- `sys_kl_items` 增加 `bounded_context` 字段（TEXT，可为空以兼容 MVP 数据）
- `kl_links` 增加 `link_type` 字段，枚举：`implements`、`dependsOn`、`governs`、`acl`、`published_language`、`open_host_service`
- 知识包导出按 `bounded_context` 分组，每个 BC 作为一个知识子包
- MVP 阶段仅试点单个 BC（如"订单管理"），`bounded_context` 设默认值

### 理由

- BC 是 DDD 战略模式的核心，知识包天然以 BC 为消费单元
- 类型化关系（Backstage relations 模式）比单纯 biz↔sys 关联更具语义
- 空值兼容确保 MVP 数据无需迁移

### 后果

- ✅ 知识包可按 BC 独立消费，符合 Agent 使用场景
- ✅ 关系语义化，支持更精确的影响分析
- ⚠️ 数据迁移需处理存量数据的 `bounded_context` 默认值
- ⚠️ UI 需增加 BC 选择器

**影响的 C4 容器**: API Server、SQLite DB、Export Service

---

## ADR-009: 版本历史——biz_kl_versions 快照表

**状态**: Proposed
**决策日期**: 2026-06-07
**决策者**: pm-analyst（Refine-2）

### 背景

Refine-1 benchmark（案例 2：Confluence）发现当前仅 `version` 整数自增，无历史快照，无法支持：

- 版本对比（diff 展示）
- 回滚到指定版本（ADR-006 撤回回滚依赖此）
- 变更审计追溯

### 决策

- 新增 `biz_kl_versions` 表，每次 `update` 或 `publish` 时插入快照
- 快照字段：`id`（UUID）、`item_id`（外键）、`version`（整数）、`snapshot`（JSON，条目完整内容）、`actor_id`、`created_at`
- `GET /api/biz/{id}/history` 返回版本列表
- `GET /api/biz/{id}/history/{v1}/{v2}` 返回两个版本的 diff
- MVP 阶段不实现版本对比 UI，仅提供 API

### 理由

- 快照表是版本管理的标准模式，比增量 diff 更易实现和恢复
- JSON 快照保留完整内容，不依赖当前表结构
- MVP 先有 API，UI 可在后续阶段补充

### 后果

- ✅ 支持回滚、版本对比、完整审计
- ✅ JSON 快照解耦版本存储与当前表结构
- ⚠️ 存储成本增加（每次更新复制整条记录）
- ⚠️ 单 BC 试点（≤1000 条目）下存储可控

**影响的 C4 容器**: SQLite DB、API Server