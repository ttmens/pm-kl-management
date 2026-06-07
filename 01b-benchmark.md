# 业界实现深研 — KL Management

> 调研日期：2026-06-07（Refine-1 Benchmark）
> 对照基线：`04-mvp/`（FastAPI + SQLite + HTMX）、`openspec/design.md`、`01-research.md`
> 目标：≥3 个实现级案例研究 + 差距分析 + 可执行反馈

---

## 当前实现基线

| 维度 | 现状 | 置信度 |
|------|------|--------|
| 技术栈 | FastAPI + SQLite + HTMX + Jinja2 | [HIGH] |
| 数据模型 | biz_kl_items / sys_kl_items / kl_links / audit_logs / users | [HIGH] |
| 审核流 | submit → publish（已实现 reject_biz 函数但无 API 路由/UI） | [HIGH] |
| 版本管理 | version 整数自增，无历史快照表 | [HIGH] |
| 权限模型 | Header `X-User-Id` 传用户 ID，服务层校验 role | [HIGH] |
| 审计日志 | 记录 create/update/publish/reject/link，全员可读 /audit | [HIGH] |
| 知识包导出 | JSON + Markdown，含 biz_kl + linked sys_kl + lineage | [HIGH] |
| 详情页操作 | 只读展示，无内联编辑/提交/审核操作区 | [HIGH] |
| 关联 UI | API 层支持 link/unlink，前端无选择器 | [HIGH] |
| Bounded Context | 无 BC 概念，sys_kl.layer 仅分 domain/application/infrastructure | [HIGH] |

---

## 案例 1：Backstage Software Catalog — 实体模型 + 关系图 + 所有权

- 来源 URL：https://backstage.io/docs/features/software-catalog/descriptor-format
- 来源 URL：https://backstage.io/docs/features/software-catalog/well-known-relations
- 来源 URL：https://roadie.io/blog/understanding-the-backstage-system-model

### 实现要点

**实体描述格式（catalog-info.yaml）**：
- 四层信封结构：`apiVersion` + `kind` + `metadata` + `spec`
- 实体种类（Kind）：Component / API / Group / System / Resource / Template
- 关系系统（Relations）：`ownedBy`、`dependsOn`、`providesApis`、`consumesApis`、`subcomponentOf`
- 元数据标签：`labels`（分类/过滤）、`annotations`（外部系统引用）、`tags`
- 生命周期字段：`spec.lifecycle`（experimental / production / deprecated）
- 分布式所有权：每个团队维护自己拥有的实体信息

**关系处理**：
- `relations` 数组为只读自动生字段，由 catalog processor 推导
- 支持双向关系：`spec.owner` 为展示用途，`relations.ownedBy` 为程序查询权威源
- 实体引用格式：`<namespace>/<name>`，避免使用不稳定 UID

**生命周期状态**：
- 实体从注册 → processor 处理 → API 可见 → 状态报告（`status.items`：info/warning/error）
- 移除实体触发"eager deletion"，连带清理数据库中所有辅助数据

### 可借鉴

1. **四层信封结构**可映射到知识包 JSON：`apiVersion`→package_version，`kind`→biz/sys，`metadata`→lineage/tags，`spec`→知识内容
2. **关系系统**：我们的 `kl_links` 表可增强为类型化关系（`implements`、`dependsOn`、`governs`），而非单纯 biz↔sys 关联
3. **生命周期枚举**：`lifecycle` 字段可作为 biz_kl 状态的补充维度（如 `deprecated` 态）

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 无实体种类体系 | 中 | 仅有 biz_kl / sys_kl 两类，缺少 API / System / Group 等扩展种类 |
| 关系无类型化 | 高 | `kl_links` 只记录关联对，无语义（实现/依赖/治理） |
| 无生命周期维度 | 中 | version 自增但无 lifecycle 标记（experimental/production/deprecated） |
| 无 namespace 隔离 | 低 | MVP 阶段可接受，但多团队场景需隔离 |
| 无实体状态报告 | 低 | 无 `status.items` 类字段记录处理错误/警告 |

---

## 案例 2：Confluence 审批工作流 — 完整审核生命周期

- 来源 URL：https://developer.atlassian.com/server/confluence/approval-workflow
- 来源 URL：https://docs.appfox.io/confluence-workflows/content-review-and-approval-processes-in-confluenc

### 实现要点

**状态机设计**：

| 状态 | 触发条件 | 可用操作 → 下一状态 |
|------|----------|---------------------|
| `editing in progress` | 作者编辑页面 | 提交审核 → `waiting for approval` |
| `waiting for approval` | 作者提交审核 | 审批者通过 → `accepted`<br>审批者驳回 → `rejected` |
| `accepted` | 审批通过 或 作者撤回 | 编辑 → 回到 `editing in progress`（默认长期态） |
| `rejected` | 审批者驳回 | 作者编辑 → `editing in progress`<br>作者撤回 → `accepted`（回滚到最近已审批版本） |

**角色与权限**：
- `author` 组：可编辑页面，不能审批自己的修改
- `approver` 组：可审批/驳回
- 用户可同时属于两组，但不能自我审批

**UI 特性**：
- 提交按钮仅在 `editing in progress` 态可见
- 审批者专属队列页：自动列出所有 `waiting for approval` 状态的页面
- 作者仪表盘：仅看自己被驳回/待审批的页面（隔离可见）
- 撤回操作：在 `rejected` 或 `waiting for approval` 态可撤回，自动回滚到最近已审批版本

**版本历史**：
- 页面保留每次编辑的完整历史与 diff
- 空间级权限控制谁可查看/编辑历史

### 可借鉴

1. **撤回 + 回滚机制**：`rejected` 态允许作者撤回变更并回滚到最近 approved 版本 — 我们的 reject 仅回到 draft，无回滚语义
2. **审批者队列页**：独立页面列出所有待审批条目 — 我们无此类视图
3. **作者隔离仪表盘**：每个作者只能看到自己的待审批/被驳回条目 — 我们的 /biz 列表无权限过滤
4. **编辑中内容展示**：审核中页面需展示已审批版本 + 审核中标记 — 我们详情页无此区分

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 审核中无内容展示策略 | 高 | 用户访问 `reviewing` 态条目时看到的是草稿还是已发布版本？无定义 |
| 无撤回/回滚机制 | 高 | reject 后仅状态变 draft，不记录驳回理由到条目级别 |
| 无审批者队列视图 | 中 | 管理员需手动筛选 `reviewing` 状态 |
| 无作者隔离仪表盘 | 中 | 所有用户看到相同列表 |
| 无版本 diff 展示 | 中 | version 整数但无可查看的变更历史 |

---

## 案例 3：GitBook MCP Server — 知识对 AI Agent 原生可消费

- 来源 URL：https://gitbook.com/docs/ai-and-search/mcp-servers-for-published-docs
- 来源 URL：https://www.gitbook.com/blog/what-is-mcp-server-documentation

### 实现要点

**MCP Server 架构**：
- 每个已发布站点自动在 `/<site>/~gitbook/mcp` 提供 MCP 端点
- 仅 HTTP transport（不支持 stdio/SSE）
- 只读访问文档内容，不暴露账户数据/分析数据/内部元数据
- 仅暴露最新已发布版本，草稿和未发布变更保持私密

**认证集成**：
- 支持 OAuth + DCR（Dynamic Client Registration）
- MCP 客户端自动发现 OAuth 服务器 → 动态注册 → 重定向到上游认证提供商 → 交换 access token
- 支持 Auth0 / Azure AD / Okta / AWS Cognito / OIDC

**内容组织**：
- 站点 → 集合（Collection） → 空间（Space） → 页面
- 隐藏页面仍可通过 MCP 访问（仅从 TOC 中隐藏）
- 页面操作（Page actions）必须启用，否则 MCP 端点返回 404

**AI 工作流集成**：
- 48 个 MCP 工具：创建/读取/更新/删除跨组织/集合/空间/内容
- 6 个 AI 驱动 prompt 用于文档工作流
- SKILL.md 文件指导 AI 何时及如何使用这些工具

### 可借鉴

1. **发布/私有分离**：MCP 仅暴露已发布版本 — 我们的知识包导出应仅包含 `published` 状态条目
2. **端点自动发现**：固定 URL 模式 — 知识包可通过固定端点 `/<project>/~kl/mcp` 暴露
3. **版本隔离**：草稿对 AI Agent 不可见 — 我们在知识包生成中应过滤 `draft`/`reviewing` 条目
4. **SKILL.md 模式**：为每个知识包附带一份 SKILL.md 风格指南，说明何时及如何使用该知识包

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 导出无状态过滤 | 高 | 当前知识包可能包含 draft/reviewing 条目，应仅导出 published |
| 无 MCP 暴露端点 | 中 | 知识包需手动下载，无自动发现端点 |
| 无 SKILL.md 指南 | 中 | 导出的知识包缺少"如何使用"的元指令 |
| 无变更增量推送 | 低 | 每次导出全量，无 diff/增量机制 |

---

## 案例 4：Mintlify Docs-as-Code — 自更新文档工作流

- 来源 URL：https://www.mintlify.com/blog/autopilot
- 来源 URL：https://www.mintlify.com/library/docs-as-code-solutions-for-api-teams
- 来源 URL：https://github.com/mintlify/docs/blob/main/skill.md

### 实现要点

**自更新流程（Autopilot）**：
1. **检测代码变更**：监听 Git 仓库变更，识别需要文档更新的代码修改
2. **高亮变更**：向技术写作者展示需要更新的文档区域
3. **生成草稿**：AI 自动生成文档更新草稿，人工审核后再发布

**Docs-as-Code 核心原则**：
- 文档与代码共用版本控制、审核、部署流程
- API 参考文档与 API spec 保持同步
- 非技术贡献者（PM/技术写作者）无需直接操作 Git 即可贡献
- 为 AI 系统生成结构化输出（MCP server、llms.txt）

**结构化 AI 输出**：
- 自动生成 MCP server 从文档
- 自动生成 llms.txt 供 LLM 发现
- 公共 MCP 端点供 admin actions 查询

**SKILL.md 实践**（GitHub 仓库）：
- 仓库根目录放置 `skill.md`，指导 AI 如何操作文档系统
- 内容包括：何时使用、配置指南、组件选择策略、站点结构说明

### 可借鉴

1. **变更检测 → 草稿生成 → 人工审核** 三段式流水线可映射到 KL 的 sys_kl 更新流程
2. **SKILL.md 随知识包分发**：为每个知识包生成 SKILL.md，说明知识包结构与使用方式
3. **结构化输出**：知识包导出应包含 `llms.txt` 风格的索引文件，供 AI Agent 快速发现

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 无变更检测机制 | 高 | sys_kl 与代码仓库无联动，不知道代码变了知识该更新 |
| 无草稿生成工作流 | 中 | 知识更新完全手动，无 AI 辅助生成草稿 |
| 无 llms.txt 输出 | 中 | 知识包导出缺少 AI 发现层索引文件 |
| 无 SKILL.md 附带 | 中 | 导出无"如何使用"的元指令 |

---

## 案例 5：Context Mapper + Bounded Context Canvas — DDD 知识结构化

- 来源 URL：https://contextmapper.org/docs/bounded-context
- 来源 URL：https://github.com/ddd-crew/bounded-context-canvas
- 来源 URL：https://ozimmer.ch/modeling/2022/11/23/ContextMapperInsights.html

### 实现要点

**Context Mapper DSL (CML)**：
- 文本 DSL 描述 Bounded Context、上下文映射关系、聚合、实体
- Bounded Context 类型：FEATURE（功能）、APPLICATION（应用）、SYSTEM（部署）、TEAM（组织）
- 上下文映射模式：Partnership / Customer-Supplier / Shared Kernel / Conformist / Open-Host Service / Published Language / ACL / Separate Ways / Big Ball of Mud
- 团队映射：指定哪个团队实现哪个 Bounded Context

**Bounded Context Canvas（ddd-crew）**：
- 9 宫格结构化画布：
  1. **Name**：上下文名称
  2. **Description**：一句话描述
  3. **Business Capabilities**：业务能力
  4. **Domain Concepts**：领域概念（通用语言）
  5. **Inbound Communication**：入站通信（谁调用我）
  6. **Outbound Communication**：出站通信（我依赖谁）
  7. **Public Interface / API**：公共接口
  8. **Dependencies**：依赖项
  9. **Team**：负责团队

**关键实践**：
- 按顺序填写画布：先明确名称和描述，再填充其他
- 将画布视为活文档，随系统演进更新
- 从团队边界开始映射上下文关系

### 可借鉴

1. **BC Canvas 作为知识条目模板**：每个 Bounded Context 的知识包可内嵌 Canvas 9 宫格信息
2. **上下文映射模式分类**：kl_links 可增强为映射模式（ACL / Published Language / Open-Host Service）
3. **CML DSL**：可设计 KL 专用的知识描述 DSL，用文本文件描述知识条目并自动生成结构化知识包
4. **BC 类型标签**：sys_kl 可标记为 FEATURE / APPLICATION / SYSTEM / TEAM 类型

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 无 BC 概念 | 高 | sys_kl 无 Bounded Context 归属，仅按 DDD 层分类 |
| 无上下文映射模式 | 高 | kl_links 无关系类型（ACL / Published Language 等） |
| 无 Canvas 结构模板 | 中 | 知识条目无结构化画布指导录入 |
| 无团队/责任人映射 | 中 | 无 BC 与负责团队的关联 |

---

## 案例 6：Glean Knowledge Graph — 权限感知 + 知识图谱

- 来源 URL：https://www.glean.com/resources/guides/glean-knowledge-graph
- 来源 URL：https://www.glean.com/blog/knowledge-graph-agentic-engine
- 来源 URL：https://rmax.ai/notes/enterprise-ai-agents-knowledge-layer-beyond-rag

### 实现要点

**知识图谱架构**：
- 100+ 连接器接入企业所有应用，为每个客户构建独特知识图谱
- 三层图谱：企业知识图谱（内容） + 人员图谱（组织关系） + 个人图谱（工作模式）
- 混合搜索：语义向量 + 知识图谱关系 + 权限感知排序
- 自调整搜索排名模型，随使用持续改进

**权限感知**：
- 索引时即嵌入权限信息，搜索结果按用户权限过滤
- 知识图谱节点附带权限元数据，确保 AI 回答不泄露未授权内容
- 个人图谱层捕获用户工作模式，实现个性化搜索

**Agentic Engine**：
- MCP Gateway：允许外部 AI 工具通过 MCP 协议访问企业知识
- 知识图谱为 Agent 提供上下文，支持复杂推理和多步操作
- 93% 采纳率（企业级验证）

### 可借鉴

1. **权限感知索引**：知识包导出应按请求者角色过滤，不同角色看到不同内容
2. **关系图谱**：知识条目间关系不只是 biz↔sys，还包括依赖、引用、层级等
3. **三层结构**：企业知识（biz_kl）+ 系统知识（sys_kl）+ 个人知识（用户级 notes/favorites）

### 对当前实现的差距

| 差距 | 严重程度 | 说明 |
|------|----------|------|
| 导出无权限过滤 | 高 | 当前知识包对所有条目一视同仁，无角色感知 |
| 无知识图谱可视化 | 中 | 有关系数据但无图展示 |
| 无个人知识层 | 低 | 用户无收藏夹/笔记/标注功能 |
| 无搜索排名优化 | 低 | 当前为 LIKE 模糊搜索，无语义/图谱增强 |

---

## 差距汇总表

| # | 维度 | 业界做法 | 我们现状 | 建议优化 | 优先级 |
|---|------|----------|----------|----------|--------|
| 1 | 审核流 | 完整状态机（editing→waiting→accepted/rejected）+ 撤回回滚 | 仅 submit/publish/reject，无撤回/回滚，无审核中内容展示策略 | 增加撤回 API + 审核中页面展示已发布版本 + 驳回理由持久化 | P0 |
| 2 | 知识包状态过滤 | 仅暴露已发布版本（GitBook MCP） | 导出可能包含 draft/reviewing 条目 | 知识包生成时仅包含 published 状态条目 | P0 |
| 3 | 权限感知导出 | 按用户权限过滤内容（Glean） | 导出无角色过滤，所有条目全量输出 | 按请求者角色过滤：expert 仅看 biz_kl，developer 看全部 | P0 |
| 4 | 关系类型化 | 类型化关系（ownedBy/dependsOn/providesApis）（Backstage） | kl_links 仅记录关联对，无语义类型 | 增加 `link_type` 字段（implements/dependsOn/governs）+ 上下文映射模式 | P1 |
| 5 | Bounded Context | BC Canvas 9 宫格 + CML DSL + 上下文映射模式 | 无 BC 概念，sys_kl 仅按 DDD 层分类 | sys_kl 增加 `bounded_context` 字段 + Canvas 结构模板 | P1 |
| 6 | 版本历史 | 完整历史 diff + 可视化（Confluence） | version 整数自增，无可查看的变更历史 | 增加 `biz_kl_versions` 快照表 + 版本对比 UI | P1 |
| 7 | 审批者队列 | 独立页面列出所有待审批条目（Confluence） | 无此类视图，需手动筛选 | 增加 /review 页面，按状态过滤展示待审批条目 | P1 |
| 8 | SKILL.md 知识包指南 | 每个知识包附带 SKILL.md 说明使用方式（Mintlify） | 导出无"如何使用"的元指令 | 知识包导出增加 `SKILL.md` 节，说明结构与消费方式 | P2 |
| 9 | llms.txt AI 发现层 | 自动生成 llms.txt 供 LLM 发现（Mintlify） | 无 AI 发现层索引文件 | 知识包导出增加 `llms.txt` 风格索引 | P2 |
| 10 | 变更检测联动 | 检测代码变更触发知识更新草稿（Mintlify Autopilot） | sys_kl 与代码仓库无联动 | sys_kl 可关联 Git commit hash，检测代码变更提醒更新 | P2 |
| 11 | 生命周期维度 | lifecycle 标记（experimental/production/deprecated）（Backstage） | 无生命周期维度 | biz_kl 增加 `lifecycle` 字段补充 status | P2 |
| 12 | 作者隔离仪表盘 | 每个作者仅看到自己的条目（Confluence） | 所有用户看到相同列表 | /biz 列表按 created_by 过滤 + 角色可见控制 | P3 |

---

## 建议反馈

以下条目追加到 `feedback.jsonl`（stage: benchmark）：

```jsonl
{"stage": "benchmark", "type": "gap", "priority": "P0", "title": "审核流完善：撤回+回滚", "description": "Confluence 状态机包含撤回（withdraw）和回滚到最近已审批版本。当前 reject 仅回 draft，无回滚语义。需增加 POST /api/biz/{id}/withdraw 和版本回滚逻辑。", "source": "https://developer.atlassian.com/server/confluence/approval-workflow"}
{"stage": "benchmark", "type": "gap", "priority": "P0", "title": "知识包状态过滤", "description": "GitBook MCP 仅暴露已发布版本。知识包生成应过滤掉 draft/reviewing 条目，仅包含 published 状态。", "source": "https://gitbook.com/docs/ai-and-search/mcp-servers-for-published-docs"}
{"stage": "benchmark", "type": "gap", "priority": "P0", "title": "权限感知导出", "description": "Glean 索引时嵌入权限信息。知识包导出应按请求者角色过滤内容，不同角色看到不同范围的条目。", "source": "https://www.glean.com/resources/guides/glean-knowledge-graph"}
{"stage": "benchmark", "type": "gap", "priority": "P1", "title": "关系类型化", "description": "Backstage 使用类型化关系（ownedBy/dependsOn/providesApis）。kl_links 应增加 link_type 字段，区分实现/依赖/治理等语义。", "source": "https://backstage.io/docs/features/software-catalog/well-known-relations"}
{"stage": "benchmark", "type": "gap", "priority": "P1", "title": "Bounded Context 支持", "description": "sys_kl 应按 Bounded Context 分组，增加 bounded_context 字段。参考 Context Mapper 的 BC 类型和 ddd-crew 的 Canvas 9 宫格。", "source": "https://contextmapper.org/docs/bounded-context"}
{"stage": "benchmark", "type": "gap", "priority": "P1", "title": "版本历史快照表", "description": "增加 biz_kl_versions 表记录每次变更的完整快照，支持版本对比和回滚。", "source": "https://developer.atlassian.com/server/confluence/approval-workflow"}
{"stage": "benchmark", "type": "gap", "priority": "P1", "title": "审批者队列页面", "description": "增加 /review 页面，列出所有 reviewing 状态条目，供管理员快速审批。", "source": "https://developer.atlassian.com/server/confluence/approval-workflow"}
{"stage": "benchmark", "type": "gap", "priority": "P2", "title": "知识包 SKILL.md 指南", "description": "每个知识包导出附带 SKILL.md 节，说明知识包结构、消费方式和适用场景。", "source": "https://github.com/mintlify/docs/blob/main/skill.md"}
{"stage": "benchmark", "type": "enhancement", "priority": "P2", "title": "llms.txt AI 发现层", "description": "知识包导出增加 llms.txt 风格索引文件，供 LLM 快速发现和导航知识条目。", "source": "https://www.mintlify.com/blog/generate-mcp-servers-for-your-docs"}
{"stage": "benchmark", "type": "enhancement", "priority": "P2", "title": "代码变更检测联动", "description": "sys_kl 关联 Git commit hash，检测代码变更时提醒相关知识条目需更新。", "source": "https://www.mintlify.com/blog/autopilot"}
```

---

## 来源汇总

| # | 来源 | URL |
|---|------|-----|
| 1 | Backstage Catalog Descriptor Format | https://backstage.io/docs/features/software-catalog/descriptor-format |
| 2 | Backstage Well-Known Relations | https://backstage.io/docs/features/software-catalog/well-known-relations |
| 3 | Backstage System Model (Roadie) | https://roadie.io/blog/understanding-the-backstage-system-model |
| 4 | Confluence Approval Workflow | https://developer.atlassian.com/server/confluence/approval-workflow |
| 5 | Confluence Content Review (AppFox) | https://docs.appfox.io/confluence-workflows/content-review-and-approval-processes-in-confluenc |
| 6 | GitBook MCP Servers | https://gitbook.com/docs/ai-and-search/mcp-servers-for-published-docs |
| 7 | GitBook MCP Blog | https://www.gitbook.com/blog/what-is-mcp-server-documentation |
| 8 | Mintlify Autopilot | https://www.mintlify.com/blog/autopilot |
| 9 | Mintlify Docs-as-Code | https://www.mintlify.com/library/docs-as-code-solutions-for-api-teams |
| 10 | Mintlify SKILL.md | https://github.com/mintlify/docs/blob/main/skill.md |
| 11 | Context Mapper Bounded Context | https://contextmapper.org/docs/bounded-context |
| 12 | ddd-crew Bounded Context Canvas | https://github.com/ddd-crew/bounded-context-canvas |
| 13 | Context Mapper Insights | https://ozimmer.ch/modeling/2022/11/23/ContextMapperInsights.html |
| 14 | Glean Knowledge Graph Guide | https://www.glean.com/resources/guides/glean-knowledge-graph |
| 15 | Glean Knowledge Graph + Agentic | https://www.glean.com/blog/knowledge-graph-agentic-engine |
| 16 | Glean Knowledge Layer Beyond RAG | https://rmax.ai/notes/enterprise-ai-agents-knowledge-layer-beyond-rag |
