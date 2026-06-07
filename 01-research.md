# 调研报告：产品知识平台（KL Management）

> 调研日期：2026-06-07
> 调研范围：企业知识管理平台竞品、代码知识库工具、DDD 知识建模、AI 编程上下文注入
> 置信度标注：[HIGH] = 多源交叉验证 / [MEDIUM] = 单源或信息不完整 / [LOW] = 推测或传闻

---

## 一、企业内部知识管理平台竞品

### 竞品对比表


| #   | 产品                    | AI 能力概要                                                               | 定价模型                                                                     | 目标用户                                   | 优势                                            | 劣势                            | 相关度                                      | 来源 URL                                                                                         | 置信度      |
| --- | --------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------- | --------------------------------------------- | ----------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------- | -------- |
| 1   | **Confluence + Rovo** | Rovo AI：草稿生成、跨应用搜索、页面摘要、AI Agent 工作流自动化、文本转可视化                        | Free（≤10人）→ Standard ~$5.75/人/月 → Premium ~$11/人/月 → Enterprise（定制）      | Atlassian 生态内中大型企业                     | 深度集成 Jira/GitHub、Rovo AI 含于所有付费层、开发者工作流友好     | 重/复杂不适合小团队、AI 仅云端、大规模性能瓶颈     | 中：通用 KM+AI，但不面向 Agent 消费                 | [https://www.atlassian.com/software/confluence](https://www.atlassian.com/software/confluence) | [HIGH]   |
| 2   | **Notion AI**         | Notion Agent（自主 AI 任务）、Enterprise Search、Custom Agents + Workers、写作助手 | Free → Plus ($10/人/月) → Business ($20/人/月，AI 需此层) → Enterprise（定制）       | 知识密集型团队、灵活工作流                          | 灵活的数据库/块模型、AI Agent 能力强、零数据留存                 | 大规模性能差、AI 需 Business 层起步、离线受限 | 中：通用 KM+AI，但知识库无结构化分层                    | [https://www.notion.com/pricing](https://www.notion.com/pricing)                               | [HIGH]   |
| 3   | **Glean（Work AI）**    | Glean Assistant/Agents、混合搜索（企业图谱+个人图谱）、MCP Gateway、代码智能               | 仅企业定制定价                                                                  | 500+ 人大型企业                             | 100+ 应用连接器、权限感知索引、93% 采纳率、开发者功能强              | 昂贵、主要是搜索而非知识创建工具              | 高：权限感知+AI Agent 知识交付，但无 biz_kl/sys_kl 分离 | [https://www.glean.com](https://www.glean.com)                                                 | [HIGH]   |
| 4   | **Guru**              | 知识 Agent（引用式回答）、AI 搜索、MCP 交付给外部 AI 工具、自动化知识质量维护                       | 企业定制定价（非 SaaS 按座席）                                                       | 客服/销售/HR 等对准确性要求高的团队                   | 人工审核降低幻觉、MCP 交付任何 AI Agent、SOC2/HIPAA 合规      | 定价不透明、非开发者导向、卡片结构刚性           | 中：治理型知识交付，但不面向代码/系统知识                    | [https://www.getguru.com/pricing](https://www.getguru.com/pricing)                             | [MEDIUM] |
| 5   | **GitBook**           | AI Assistant（可嵌入聊天）、AI Agent（主动改进建议）、内建 MCP Server（LLM 可发现）、AI 内容审查   | Free（公开文档）→ Premium ($65/站+$12/人/月) → Ultimate ($249/站+$12/人/月)          | 开发者团队、API 产品、技术文档                      | 开发者专用、Git/GitHub 同步、MCP Server 使知识对 LLM 原生可发现 | 双重定价模型、仅面向文档（非完整 KM）、索引延迟 ~1h | 高：MCP Server + 开发者知识原生消费，最接近 KL 定位       | [https://www.gitbook.com](https://www.gitbook.com)                                             | [HIGH]   |
| 6   | **Mintlify**          | AI 写作 Agent、AI 助手、MCP Server、LLMs.txt 生成、自更新文档工作流                     | Starter（$0）→ Pro (~$250-300/月+计量 AI) → Enterprise（定制）                    | 开发者优先公司（Anthropic/Coinbase/Cursor 等使用） | AI 原生、自动更新文档、LLM 优化输出                         | 定价跳跃大（免费→$250+）、计量 AI 费用高     | 高：文档即基础设施理念验证了 sys_kl 方向，但无 DDD 映射       | [https://www.mintlify.com/pricing](https://www.mintlify.com/pricing)                           | [HIGH]   |
| 7   | **Slab**              | 无显著 AI 功能（2025/2026 年为竞品空白）                                           | Free（≤10人）→ Startup ($6.67/人/月) → Business ($12.50/人/月) → Enterprise（定制） | 初创/中型团队的简单内部 Wiki                      | 最便宜、UI 简洁、层次结构清晰                              | 无 AI 功能（重大短板）、无精细权限、大规模知识库吃力  | 低：无 AI 能力                                | [https://slab.com/pricing](https://slab.com/pricing)                                           | [MEDIUM] |


---

## 二、代码知识库工具

### 竞品对比表


| #   | 产品                   | 代码上下文处理方式                                                      | AI 能力                                              | IDE 集成                                                 | 持久知识               | DDD 感知   | 来源 URL                                                                                                                                                                                                                                                 | 置信度      |
| --- | -------------------- | -------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------ | ------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 1   | **Sourcegraph Cody** | 跨仓库符号感知搜索（Sourcegraph Search API）；@提及文件/符号/仓库                  | Chat、自动编辑、自定义 Prompt、调试；顶级 LLM                     | VS Code, JetBrains, Visual Studio, Web, CLI            | 无                  | 部分（符号图谱） | [https://sourcegraph.com/docs/cody](https://sourcegraph.com/docs/cody)                                                                                                                                                                                 | [HIGH]   |
| 2   | **Bloop**            | RAG 管线（GPT-4 重写→MiniLM/Qdrant 语义搜索→LLM 排序→溯源回答）；Tree-sitter 导航 | 对话式代码搜索、Code Studio 实验环境                           | 独立桌面应用（Mac/Win/Linux），非 IDE 插件                         | 无                  | 无        | [https://github.com/bloopAI/bloop](https://github.com/bloopAI/bloop)                                                                                                                                                                                   | [HIGH]   |
| 3   | **GitHub Copilot**   | 即时语义索引（秒级）；@workspace/#codebase 修饰符；多仓库搜索                      | 补全、Chat、Agent 模式（VS Code 自主多步）、PR 生成、代码审查          | VS Code（原生）, github.com, JetBrains, Visual Studio, CLI | 无                  | 无        | [https://github.blog/changelog/2025-03-12-instant-semantic-code-search-indexing-now-generally-available-for-github-copilot](https://github.blog/changelog/2025-03-12-instant-semantic-code-search-indexing-now-generally-available-for-github-copilot) | [HIGH]   |
| 4   | **Cursor**           | 工作区语义索引；.cursor/rules/ 持久项目级指令；@codebase 查询；文档索引；MCP 支持        | Tab 补全、Chat、Composer（多文件 Agent）、Bugbot 审查、云端 Agent | 独立 IDE（VS Code fork），兼容 VS Code 扩展                     | 部分（.cursor/rules/） | 无        | [https://cursor.com](https://cursor.com)                                                                                                                                                                                                               | [HIGH]   |
| 5   | **Devin（Cognition）** | 自主读取整个代码库（嵌入式 IDE+Shell+浏览器）；每次任务重新读取                          | 全自主执行、并行 Agent、迁移、重构、PR 审查、测试生成                    | Web IDE (app.devin.ai), CLI, Slack/Teams               | 无                  | 无        | [https://docs.devin.ai/get-started/devin-intro](https://docs.devin.ai/get-started/devin-intro)                                                                                                                                                         | [MEDIUM] |
| 6   | **Sweep.dev**        | 全代码库感知搜索 + 上下文感知补全；发布 Agent 文件读取策略研究                           | Tab 补全（自研模型，毫秒延迟）、AI 代码审查                          | 仅 JetBrains 插件                                         | 无                  | 无        | [https://sweep.dev](https://sweep.dev)                                                                                                                                                                                                                 | [MEDIUM] |
| 7   | **Composio**         | 不管理代码上下文；为 Agent 提供 1000+ 应用/20,000+ 工具集成（MCP 或直接 API）         | 工具执行、安全 OAuth、沙箱环境、并行执行、"学习型工具"                    | 适用于任何 MCP 兼容 IDE/Agent，CLI 管理                          | 不适用（非代码知识工具）       | 无        | [https://composio.dev](https://composio.dev)                                                                                                                                                                                                           | [HIGH]   |
| 8   | **Mintlify**         | 文档即 AI Agent 基础设施；自更新工作流保持文档与代码同步                              | 文档问答助手、自动文档生成/更新、Claude Opus 集成                    | CI/CD、GitHub 仓库、API（非 IDE 工具）                          | 是（自更新文档）           | 无        | [https://www.mintlify.com](https://www.mintlify.com)                                                                                                                                                                                                   | [HIGH]   |


### 关键发现（方向 1 + 2 综合）

1. **无工具拥有持久化 DDD/领域结构代码知识图谱** — 这是 sys_kl 的核心差异化机会。所有工具都是"每次查询时"检索上下文（语义搜索、RAG、符号图谱），没有持久化的领域知识层。
2. **Cursor 的 `.cursor/rules/` 是最接近持久知识编码的方案** — sys_kl 可在此基础上扩展为结构化 DDD 映射。
3. **Sourcegraph 构建符号/引用图谱但无领域语义** — sys_kl 可在其上加一层语义。
4. **Mintlify 的"文档即基础设施"理念验证了 sys_kl 方向** — 知识必须对 AI Agent 准确、结构化、可消费。
5. **Composio 的 MCP 模式展示了 sys_kl 如何向多个 AI Agent 暴露知识** — 无需原生集成，通过 MCP Server 即可。
6. **语义搜索已是标配** — sys_kl 的差异化在于**结构化的、持久的、领域感知的知识**。

---

## 三、DDD 知识建模相关实践

### 3.1 Bounded Context（有界上下文）作为知识边界

- **核心概念**：Bounded Context 是 DDD 中划分大型领域模型的核心战略模式。每个上下文维护内部一致的通用语言（Ubiquitous Language）。边界由团队间的语言/文化差异驱动，而非技术考虑。来源：[https://martinfowler.com/bliki/BoundedContext.html](https://martinfowler.com/bliki/BoundedContext.html) [HIGH]
- **一词多义处理**：相同术语在不同部门含义不同（如 "meter" 对电网运维 vs 计费）。Eric Evans 明确反对强制统一。来源：[https://martinfowler.com/bliki/BoundedContext.html](https://martinfowler.com/bliki/BoundedContext.html) [HIGH]
- **上下文类型**（Context Mapper 分类）：FEATURE（功能）、APPLICATION（逻辑）、SYSTEM（部署）、TEAM（组织）。来源：[https://contextmapper.org/docs/bounded-context](https://contextmapper.org/docs/bounded-context) [MEDIUM]

### 3.2 上下文映射（Context Mapping）模式

- **9 种模式**（ddd-crew）：Partnership、Customer-Supplier、Shared Kernel、Conformist、Open-Host Service、Published Language、Anticorruption Layer (ACL)、Separate Ways、Big Ball of Mud。来源：[https://github.com/ddd-crew/context-mapping](https://github.com/ddd-crew/context-mapping) [HIGH]
- **最佳实践**："从团队边界开始映射；将地图视为活文档；模式与实际组织能力匹配。" — Alberto Brandolini, InfoQ。来源：[https://www.infoq.com/articles/ddd-contextmapping](https://www.infoq.com/articles/ddd-contextmapping) [HIGH]
- **关键引述**："上下文地图提供了 UML 或架构图完全无法呈现的系统全局视图。"来源：[https://www.infoq.com/articles/ddd-contextmapping](https://www.infoq.com/articles/ddd-contextmapping) [HIGH]

### 3.3 通用语言（Ubiquitous Language）文档化

- **定义**：开发者与领域专家之间的共同、严谨语言，基于领域模型。来源：[https://martinfowler.com/bliki/UbiquitousLanguage.html](https://martinfowler.com/bliki/UbiquitousLanguage.html) [HIGH]
- **文档方法**：将 UL 文档视为词汇表/术语管理项目。建议采用文档软件进行词汇管理。来源：[https://softwareengineering.stackexchange.com/questions/304471/how-to-document-a-ubiquitous-language](https://softwareengineering.stackexchange.com/questions/304471/how-to-document-a-ubiquitous-language) [MEDIUM]
- **关键实践**："在代码、文档、讨论中普遍使用该语言。领域专家应对别扭的术语提出反对；开发者应警惕歧义。"来源：[https://martinfowler.com/bliki/UbiquitousLanguage.html](https://martinfowler.com/bliki/UbiquitousLanguage.html) [HIGH]

### 3.4 结构化工具

- **Bounded Context Canvas**（ddd-crew）：结构化画布，用于设计/记录每个 BC：名称、描述、职责、公共接口、依赖。来源：[https://github.com/ddd-crew/bounded-context-canvas](https://github.com/ddd-crew/bounded-context-canvas) [HIGH]
- **Context Mapper DSL (CML)**：代码优先的 DSL，用文本文件描述上下文映射并自动生成图表。来源：[https://contextmapper.org/docs/bounded-context](https://contextmapper.org/docs/bounded-context) [MEDIUM]

---

## 四、AI 编程上下文注入最佳实践

### 4.1 上下文工程（Context Engineering） > 提示工程

- **定义**：上下文工程 = 在 LLM 推理期间对**所有上下文组件**（系统 Prompt、工具、MCP、外部数据、消息历史）进行最优 token 策展。Prompt 工程是其中的子集。来源：[https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]
- **关键引述**："上下文工程就是策展模型看到的内容，从而获得更好的结果。" — Birgitta Bockeler, Thoughtworks。来源：[https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html) [HIGH]

### 4.2 上下文窗口管理

- **上下文衰减**：注意力随 token 数量递减——不是悬崖而是梯度。Stanford/UC Berkeley 研究显示，尽管窗口支持 1M+ token，但正确性在约 32K token 处开始下降。来源：[https://www.faros.ai/blog/context-engineering-for-developers](https://www.faros.ai/blog/context-engineering-for-developers) [HIGH]
- **"迷失在中间"效应**：注意力机制高度加权开头和结尾，中间内容变成噪声。来源：[https://www.faros.ai/blog/context-engineering-for-developers](https://www.faros.ai/blog/context-engineering-for-developers) [HIGH]
- **位置排序（关键）**：
  1. **开头**：关键约束/规则
  2. **早期**：工具定义、API 文档
  3. **中间**：仓库结构、示例
  4. **末尾前**：近期变更
  5. **结尾**：当前任务
  将 AGENTS.md 从中间移到开头，代码风格违规减少 35-40%。来源：https://www.faros.ai/blog/context-engineering-for-developers [HIGH]
- **压缩策略**：接近限制时总结对话，用高保真摘要重启；丢弃冗余工具输出，保留架构决策。来源：[https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]
- **子 Agent 模式**：主 Agent 协调；专业子 Agent 在干净上下文中处理深度任务，返回精简摘要（~1K-2K token）。来源：[https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]

### 4.3 上下文文件生态（AGENTS.md / CLAUDE.md）

- **AGENTS.md**：开放、厂商无关的标准，已被 Claude Code、Codex CLI、Sourcegraph Amp 等采用。来源：[https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6](https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6) [HIGH]
- **分层架构**：根目录 CLAUDE.md 用于全局约定，子目录 CLAUDE.md 用于领域特定（后端、前端、基础设施）。各层继承父上下文。来源：[https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices](https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices) [MEDIUM]
- **保持精简**：聚焦的 ~400 token 文件优于 sprawling 的 4,000 token 文件。仅在出现差距时添加具体内容。来源：[https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices](https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices) [MEDIUM]
- **工具特定文件**：Cursor: `.cursor/rules/`；GitHub Copilot: `.github/copilot-instructions.md`；JetBrains: `.aiassistant/rules/*.md`；Gemini: `GEMINI.md`。来源：[https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6](https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6) [HIGH]
- **HumanLayer 洞察**：如果 Claude 认为 CLAUDE.md 内容与当前任务无关，它会忽略。非通用信息越多，被跳过的概率越大。来源：[https://www.humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) [MEDIUM]

### 4.4 结构化上下文注入

- **DICE 框架**（Domain-Integrated Context Engineering）：使用领域对象作为一等上下文单元，而非原始 JSON 转储。强制执行双向对齐——Agent 输出必须能回验到领域不变量。来源：[https://engineeringagents.substack.com/p/domain-driven-agent-design](https://engineeringagents.substack.com/p/domain-driven-agent-design) [MEDIUM]
- **Few-shot 原则**：用具体的 before/after 代码示例配对规则。示例是高信号"图片"，而非穷尽规则书。来源：[https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]
- **即时检索（JIT Retrieval）**：Agent 维护轻量级标识符，通过工具动态加载数据（glob、grep、定向查询）。混合策略：预加载关键静态上下文 + JIT 探索。来源：[https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) [HIGH]

---

## 五、DDD + AI 融合（直接关联 KL Management）

### 5.1 Bounded Context = AI 知识包

- DDD Bounded Context 解决了单体架构中 LLM 的认知过载。每个上下文作为独立 SDK，对其他领域内部零感知。来源：[https://understandingdata.com/posts/ddd-bounded-contexts-for-llms](https://understandingdata.com/posts/ddd-bounded-contexts-for-llms) [MEDIUM]
- **通用语言作为语义锚**：代码镜像业务术语为 LLM 提供语义锚点。`confirmOrder()` > `processStatus()`。当存在通用语言时，LLM 生成更高质量的代码。来源：[https://understandingdata.com/posts/ddd-bounded-contexts-for-llms](https://understandingdata.com/posts/ddd-bounded-contexts-for-llms) [MEDIUM]

### 5.2 领域驱动 Agent 设计

- **Russ Miles 框架**：先做 Event Storming 和领域映射。**先定义 Bounded Context，再写 Prompt**。使用领域类型塑造 Prompt，而非临时 JSON 转储。Agent 输出必须针对领域不变量验证。来源：[https://engineeringagents.substack.com/p/domain-driven-agent-design](https://engineeringagents.substack.com/p/domain-driven-agent-design) [MEDIUM]
- **关键引述**："一个没有领域的 Agent 就像一个没有地图的游客。"来源：[https://engineeringagents.substack.com/p/domain-driven-agent-design](https://engineeringagents.substack.com/p/domain-driven-agent-design) [MEDIUM]

### 5.3 多 Agent 系统与 DDD

- 每个 AI Agent = Bounded Context 专家。编排模式（顺序、并发、交接、群聊、管理器）镜像 DDD 上下文关系模式。来源：[https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems](https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems) [MEDIUM]
- 通过结构化输出或 MCP 实现明确定义的契约。Agent 之间松耦合。来源：[https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems](https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems) [MEDIUM]

---

## 六、对本产品（KL Management）的差异化分析

### 6.1 核心差异化


| 维度    | 现有竞品现状                                     | KL Management 差异化                              |
| ----- | ------------------------------------------ | ---------------------------------------------- |
| 知识分层  | 所有竞品为单一知识库（文档/代码/搜索混杂）                     | **biz_kl / sys_kl 严格分离**，业务与系统逻辑互不混淆           |
| 知识消费端 | 面向人类阅读为主，AI 消费为附加（GitBook/Mintlify MCP 除外） | **原生面向 Agent/IDE 消费**，输出结构化"知识包"               |
| 领域结构  | 无工具拥有 DDD/领域感知的代码知识图谱                      | **sys_kl 按 DDD 分层**，每个 Bounded Context = 一个知识包 |
| 持久性   | 所有代码工具为"每次查询时"检索                           | **持久化知识图谱**，支持版本、血缘、审核                         |
| 知识构建  | 全自动逆向或纯人工                                  | **半自动+专家标注**，平衡准确度与成本                          |


### 6.2 最接近竞品与差距

- **GitBook + Mintlify**：有 MCP Server 使知识对 LLM 可发现，但仅限于文档层，无代码/系统逻辑映射。KL 的 sys_kl 补齐了这一层。
- **Glean + Guru**：有权限感知 + AI Agent 知识交付，但面向通用企业搜索，无 DDD 领域结构。KL 的 Bounded Context 知识包填补了这一空白。
- **Sourcegraph Cody + Cursor**：有代码级上下文，但无持久化领域知识层。KL 的 sys_kl 在代码图谱上叠加领域语义。

### 6.3 对 KL Management 的知识包导出建议

基于调研，每个 Bounded Context 的"知识包"应包含：

1. **上下文概览**（AGENTS.md 风格，~400 token，聚焦）
2. **通用语言词汇表**（biz_kl + sys_kl 术语对齐）
3. **领域实体/关系**（DDD 分层：领域层、应用层、基础设施层）
4. **集成契约**（上下文映射关系：ACL、Published Language、Open-Host Service）
5. **血缘信息**（条目来源、版本、审计记录）

### 6.4 上下文注入位置建议

- 关键领域约束/规则 → 放在上下文文件**开头**
- 当前任务描述 → 放在上下文文件**结尾**
- 跨 BC 引用 → 使用 **JIT 检索**，不预加载

---

## 七、来源汇总


| 编号  | 来源                                                  | URL                                                                                                                                                                                                                                                    |
| --- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Confluence + Rovo                                   | [https://www.atlassian.com/software/confluence](https://www.atlassian.com/software/confluence)                                                                                                                                                         |
| 2   | Notion AI                                           | [https://www.notion.com/pricing](https://www.notion.com/pricing)                                                                                                                                                                                       |
| 3   | Glean                                               | [https://www.glean.com](https://www.glean.com)                                                                                                                                                                                                         |
| 4   | Guru                                                | [https://www.getguru.com/pricing](https://www.getguru.com/pricing)                                                                                                                                                                                     |
| 5   | GitBook                                             | [https://www.gitbook.com](https://www.gitbook.com)                                                                                                                                                                                                     |
| 6   | Mintlify                                            | [https://www.mintlify.com/pricing](https://www.mintlify.com/pricing)                                                                                                                                                                                   |
| 7   | Slab                                                | [https://slab.com/pricing](https://slab.com/pricing)                                                                                                                                                                                                   |
| 8   | Sourcegraph Cody                                    | [https://sourcegraph.com/docs/cody](https://sourcegraph.com/docs/cody)                                                                                                                                                                                 |
| 9   | Bloop                                               | [https://github.com/bloopAI/bloop](https://github.com/bloopAI/bloop)                                                                                                                                                                                   |
| 10  | GitHub Copilot 语义索引                                 | [https://github.blog/changelog/2025-03-12-instant-semantic-code-search-indexing-now-generally-available-for-github-copilot](https://github.blog/changelog/2025-03-12-instant-semantic-code-search-indexing-now-generally-available-for-github-copilot) |
| 11  | Cursor                                              | [https://cursor.com](https://cursor.com)                                                                                                                                                                                                               |
| 12  | Devin                                               | [https://docs.devin.ai/get-started/devin-intro](https://docs.devin.ai/get-started/devin-intro)                                                                                                                                                         |
| 13  | Sweep.dev                                           | [https://sweep.dev](https://sweep.dev)                                                                                                                                                                                                                 |
| 14  | Composio                                            | [https://composio.dev](https://composio.dev)                                                                                                                                                                                                           |
| 15  | Martin Fowler: Bounded Context                      | [https://martinfowler.com/bliki/BoundedContext.html](https://martinfowler.com/bliki/BoundedContext.html)                                                                                                                                               |
| 16  | Martin Fowler: Ubiquitous Language                  | [https://martinfowler.com/bliki/UbiquitousLanguage.html](https://martinfowler.com/bliki/UbiquitousLanguage.html)                                                                                                                                       |
| 17  | DDD Crew: Context Mapping                           | [https://github.com/ddd-crew/context-mapping](https://github.com/ddd-crew/context-mapping)                                                                                                                                                             |
| 18  | DDD Crew: Bounded Context Canvas                    | [https://github.com/ddd-crew/bounded-context-canvas](https://github.com/ddd-crew/bounded-context-canvas)                                                                                                                                               |
| 19  | Context Mapper                                      | [https://contextmapper.org/docs/bounded-context](https://contextmapper.org/docs/bounded-context)                                                                                                                                                       |
| 20  | InfoQ: DDD Context Mapping                          | [https://www.infoq.com/articles/ddd-contextmapping](https://www.infoq.com/articles/ddd-contextmapping)                                                                                                                                                 |
| 21  | Anthropic: Context Engineering                      | [https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)                                                                                 |
| 22  | Faros AI: Context Engineering for Developers        | [https://www.faros.ai/blog/context-engineering-for-developers](https://www.faros.ai/blog/context-engineering-for-developers)                                                                                                                           |
| 23  | Thoughtworks: Context Engineering for Coding Agents | [https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html)                                                                 |
| 24  | AGENTS.md 标准汇总                                      | [https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6](https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6)                                                                                                             |
| 25  | Packmind: Context Engineering Best Practices        | [https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices](https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices)                                                                         |
| 26  | HumanLayer: Writing a Good Claude.md                | [https://www.humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)                                                                                                                                   |
| 27  | DDD Bounded Contexts for LLMs                       | [https://understandingdata.com/posts/ddd-bounded-contexts-for-llms](https://understandingdata.com/posts/ddd-bounded-contexts-for-llms)                                                                                                                 |
| 28  | Domain-Driven Agent Design                          | [https://engineeringagents.substack.com/p/domain-driven-agent-design](https://engineeringagents.substack.com/p/domain-driven-agent-design)                                                                                                             |
| 29  | DDD + Multi-Agent AI                                | [https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems](https://www.jamescroft.co.uk/applying-domain-driven-design-principles-to-multi-agent-ai-systems)                                                     |


