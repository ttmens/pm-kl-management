# 01 — 调研报告：企业 AI 编程场景下的产品知识平台

**项目：** pm-kl-management  
**阶段：** 调研（第 2 阶段）  
**日期：** 2026-06-07  

---

## 1. 执行摘要

本报告调研 **企业内部知识管理平台**、**代码知识库工具**、**DDD 知识建模实践** 与 **AI 编程上下文注入** 四类方向，为「biz_kl + sys_kl 双层知识平台」定位提供依据。

**关键发现：** 通用 KM 平台（Confluence、Notion、Glean）擅长文档沉淀与检索，但**不区分业务知识与系统逻辑知识**；代码智能工具（Sourcegraph Cody、GitHub Copilot）擅长代码理解，但**缺少业务语义层**。将 biz_kl / sys_kl 分离并通过「知识包」结构化导出给 Agent/IDE，是当前竞品尚未覆盖的差异化空间。

---

## 2. 竞品对比表（企业知识管理 + AI）

| 竞品 | 类别 | 核心能力 | 定价（约） | 优势 | 劣势 | 置信度 |
|---|---|---|---|---|---|---|
| **Confluence + Rovo** | 企业 Wiki + AI | 文档协作、跨应用搜索、AI 起草与摘要 | 标准 ~$5.75/人/月 | Atlassian 生态深、研发友好 | 重、AI 仅云版、非结构化 Agent 消费 | [高] |
| **Notion AI** | 全能工作区 | 数据库+Wiki+AI Agent | Business $20/人/月起 | 灵活、AI Agent 强 | 规模化性能差、AI 门槛高 | [高] |
| **Glean** | 企业搜索 | 100+ 应用索引、权限感知搜索 | 企业定制定价 | 跨应用搜索最强、代码智能 | 贵、偏检索非知识构建 | [高] |
| **Guru** | 验证式 KM | 人工审核知识、MCP 交付给 AI | 企业定制 | 准确性高、MCP 集成 | 定价不透明、偏内部政策 | [中] |
| **GitBook** | 技术文档 | Git 同步、MCP Server、AI 助手 | Premium $65/站+$12/人 | 开发者友好、LLM 可发现 | 双计费、偏对外文档 | [高] |
| **Mintlify** | AI 原生文档 | MCP、LLMs.txt、自更新文档 | Pro ~$250/月起 | AI 原生、Cursor 等在用 | 跳价大、非通用 Wiki | [中] |
| **Slab** | 轻量 Wiki | 嵌套页面、统一搜索 | Startup $6.67/人/月 | 最便宜、UI 简洁 | **无 AI 能力** | [高] |

---

## 3. 代码知识库工具对比

| 工具 | 能力 | 与 sys_kl 关系 | 局限 | 置信度 |
|---|---|---|---|---|
| **Sourcegraph Cody** | 全仓代码索引、跨仓库问答、IDE 集成 | 接近 sys_kl 消费端 | 不管理业务知识、需自建标注层 | [高] |
| **GitHub Copilot Workspace** | 代码库上下文、Issue→PR 工作流 | 代码侧上下文注入 | 无 biz_kl、企业私有部署有限 | [高] |
| **Bloop** | 本地/私有代码语义搜索 | 轻量 sys_kl 检索 | 项目活跃度下降、无协作审核 | [中] |
| **Cursor / Windsurf** | IDE 内 Agent + 代码库索引 | 直接消费知识包的理想终端 | 依赖外部知识源，非 KM 平台 | [高] |

**启示：** sys_kl 应与 IDE Agent 消费协议对齐（JSON 知识包、MCP、RAG 切片），而非重复造代码搜索引擎。

---

## 4. DDD 知识建模实践

| 实践 | 说明 | 来源置信度 |
|---|---|---|
| **Bounded Context 作为知识边界** | MVP 限定单 BC，biz_kl 条目与 sys_kl 模块均挂在 BC 下 | [高] |
| **上下文映射表** | 业务概念 ↔ 代码模块的显式映射，是知识包核心结构 | [高] |
| **分层归档 sys_kl** | 领域层/应用层/基础设施层分别挂载，便于变更影响分析 | [中] |
| **事件风暴产出 biz_kl** | 领域事件、聚合根可作为 biz_kl 条目模板 | [中] |

---

## 5. AI 编程上下文注入最佳实践

1. **结构化优于全文塞入**：知识包应含条目 ID、类型、关联、摘要，而非原始 PDF/全仓代码。
2. **双层上下文**：业务规则（biz_kl）+ 实现锚点（sys_kl 代码路径/调用链）分开注入，Agent 按需组装。
3. **MCP / API 只读拉取**：GitBook、Guru、Glean 均已走向 MCP；本平台 MVP 应对齐此协议。
4. **人工审核门控**：专家发布后才进入 Agent 可消费集合，避免草稿污染编码建议。
5. **版本与血缘**：变更场景需追溯「哪条 biz_kl 驱动了哪次代码修改」。

---

## 6. 用户痛点（与本产品相关）

1. **上下文碎片化**：文档在 Confluence、逻辑在工程师脑中、代码在 Git，Agent 三者皆缺。
2. **业务-系统断层**：PRD 与实现模块无稳定映射，百万行存量系统尤甚。
3. **知识维护成本高**：全自动逆向不现实，半自动+专家标注是可行路径。
4. **工具各管一段**：KM 平台不管代码，代码工具不管业务，缺少统一「知识包」出口。

---

## 7. 差异化分析

| 维度 | 通用 KM | 代码智能 | **本产品（KL Management）** |
|---|---|---|---|
| biz_kl | 部分（非结构化文档） | 无 | **核心，结构化条目+审核** |
| sys_kl | 无 | 索引/问答 | **DDD 分层+专家标注+半自动** |
| 互链 | 弱 | 无 | **biz ↔ sys 显式映射** |
| Agent 消费 | MCP 起步 | IDE 内置 | **知识包 API/导出（只读）** |
| 治理 | 权限+版本 | 无 | **草稿/发布+血缘+审计** |

**定位陈述：** 面向企业 AI 编程的「业务-系统双库知识平台」，以结构化知识包对接 Agent/IDE，而非再造一个 Confluence 或 Sourcegraph。

---

## 8. 对本项目 MVP 的启示

- 竞品验证：GitBook/Mintlify 的 MCP 与 Glean/Guru 的治理模式值得借鉴
- 不做：全仓自动静态分析、完整 IDE 插件市场
- 必做：单 BC 试点、biz_kl/sys_kl 各 ≥20 条、互链、知识包 JSON 导出
- 成功标准对齐简报：给定真实维护场景，Agent 仅凭平台知识产出方案草稿（人工验收 ≥70%）

---

## 参考来源

- https://www.atlassian.com/software/confluence
- https://www.notion.com/pricing
- https://www.glean.com
- https://www.getguru.com/pricing
- https://www.gitbook.com
- https://www.mintlify.com/pricing
- https://slab.com/pricing
- https://sourcegraph.com/cody
- https://github.com/features/copilot
- https://bloop.ai
- https://www.cursor.com/
- https://martinfowler.com/bliki/BoundedContext.html
- https://spec.modelcontextprotocol.io/
