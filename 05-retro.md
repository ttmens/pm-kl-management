# 阶段回顾（Retro）：pm-kl-management（全链路）

## 项目信息

| 项目 | 值 |
|------|-----|
| 产品 slug | kl-management |
| 产品名称 | 产品知识平台（KL Management） |
| 日期 | 2026-06-07 |
| 模型 | qwen3.6-plus |
| 管线版本 | 3.0.0 |
| GitHub | https://github.com/ttmens/pm-kl-management |
| Pages | https://ttmens.github.io/pm-kl-management/ |

## 各阶段时间与产出

| 阶段 | 产出文件 | 耗时估计 | 状态 |
|------|---------|---------|------|
| Stage 0: Brief | 00-brief.md | ~5 min | PASS |
| Stage 1: Research | 01-research.md（7 竞品 × 3 维度，29 来源） | ~10 min | PASS |
| Stage 2: Analysis | 02-analysis.md, decisions.md (5 ADR), CONTEXT.md | ~10 min | PASS |
| Stage 2b: Prototype | 02b-prototype/index.html, DESIGN.md | ~5 min | PASS |
| Stage 3: Spec | 03-prd.md, openspec/* (proposal + design + 4 specs + tasks) | ~10 min | PASS |
| Stage 4: MVP | 04-mvp/ (18 文件 + 9 模板 + 8 测试 + 辅助脚本) | ~15 min | PASS |
| Stage 5: Retro (MVP) | 05-retro.md (初版，仅覆盖 MVP) | ~3 min | PASS |
| Stage 6: Retro (全链路) | 05-retro.md (终版，本文件) | ~5 min | PASS |

**全链路总耗时：~60-70 分钟**（含 OpenCode 生成 + 测试修复 + gate 验证）

## 技能命中与失误

### 命中的技能

| 技能 | 使用阶段 | 效果 |
|------|---------|------|
| `plan` | Stage 3 → 4 | 生成了可执行的 tasks.md 计划 |
| `ui-ux-pro-max` | Stage 3 | 生成了 DESIGN.md 设计令牌 |
| `opencode` | Stage 4 | 一次性生成全部 18+ 文件，覆盖 15 个任务 |
| `test-driven-development` | Stage 4 | 测试文件随代码一起生成 |
| `dogfood` | Stage 4 | 冒烟测试 18 端点全部 200 |
| `pm-git-publish` | Stage 4 | GitHub 推送 + Pages 生成成功 |
| `openspec` | Stage 3 | 4 个 spec 文件 + proposal + tasks.md |

### 技能失误 / 改进空间

| 技能 | 问题 | 改进建议 |
|------|------|---------|
| `test-driven-development` | 实际是「生成→测试→修复」而非严格 TDD（测试先行） | 对 OpenCode 黑盒生成场景，「生成→测试→修复」循环更实际，但应在 plan 中明确 |
| `opencode` | 生成的代码存在 6 个边界 Bug（函数名互换、参数误用、校验不严、重复参数） | 在 prompt 中增加函数命名规范和参数校验的约束 |
| `requesting-code-review` | 未显式调用，而是手动 patch 修复 | 可考虑在 OpenCode 生成后自动触发自 review |

## 假设验证

### 来自 00-brief.md 的开放假设

| # | 假设 | Confidence | 验证结果 | 说明 |
|---|------|-----------|---------|------|
| 1 | 供应链 IT 团队愿意配合试点 | high | **未验证** | MVP 阶段为技术验证，未涉及真实用户参与 |
| 2 | 现有代码仓库可被安全访问 | medium | **未验证** | sys_kl 采用手工标注，未实际读取代码仓库 |
| 3 | Agent 消费端已有基础上下文注入能力 | medium | **未验证** | 知识包导出 API 已就绪，但未对接真实 Agent |
| 4 | DDD 分层映射可由现有架构师提供 | high | **部分验证** | sys_kl 设计了 DDD layer 字段，但未实际标注 |
| 5 | 首期试点控制在单个 BC | high | **已验证** | MVP 确实限定在单个 bounded context |

### 关键发现

- **Assumption #1/#2/#3 均为外部依赖**，MVP 阶段无法验证，需要在试点阶段跟进
- **Assumption #5 被验证**，MVP 范围控制得当，未出现 scope creep

## 经验教训

### 1. OpenCode 生成质量：整体优秀但需防御性约束

OpenCode 一次性生成了完整的 FastAPI 应用 + 8 个测试文件 + 9 个 HTML 模板 + 辅助脚本，覆盖全部 15 个任务。但存在 6 个边界 Bug：

- **链接查询函数名互换**：`api_biz_detail` 调用了 `get_links_for_sys`（应调用 `get_links_for_biz`）
- **测试辅助函数签名错误**：`create_published_biz(db, name=...)` 的 `db` 参数从未使用
- **import 校验不严**：没有 `类型:` 行的纯文本也能被解析
- **conftest.py 重复参数**：`autouse=True` 出现了两次

**教训**：OpenCode prompt 需要增加防御性约束，特别是函数命名规范和参数校验。

### 2. 手动修复 > 二次调用

对于已知失败的测试，直接阅读代码定位 root cause 后 patch 修复（~5 分钟）比重新调用 OpenCode 修复更快。OpenCode 需要上下文重建且有超时风险。

### 3. Windows 路径 + Python 环境问题

Hermes venv 的 Python 没有 pytest/httpx 等依赖，需要用系统 Python 运行测试。在 OpenCode 的 bash 环境中路径解析也有问题。

**教训**：应在 pipeline 配置中统一 Python 环境路径，或确保 venv 包含测试依赖。

### 4. 管线质量 Gate 有效

stage-complete 的 eval-stage 检查 README 是否引用了 MVP 流程/任务，这是一个有效的质量门。

### 5. 全链路 6 阶段流水线运行顺畅

从 brief → research → analysis → spec → prototype → MVP → retro 的 6 阶段管线在 pm-kl-management 上完整跑通，产出了可运行的 MVP 和完整的文档链。这是管线 v3.0.0 的一次成功验证。

## skill_patch_proposals（用于流水线进化）

### Proposal 1: opencode prompt 增加防御性约束

**目标技能**: `opencode`

**变更**：在 prompt template 中加入以下约束：
- 函数命名遵循 `get_{returned_entity}_for_{query_key}` 模式
- 禁止未使用的函数参数
- 所有数据解析必须有格式校验（fail-fast）
- pytest fixture 禁止重复参数

### Proposal 2: test-driven-development 适配黑盒生成

**目标技能**: `test-driven-development`

**变更**：增加「OpenCode 生成模式」分支：
- 当使用 OpenCode 时，流程变为「生成 → 跑测试 → 定位失败 → patch 修复 → 再跑」
- 严格 TDD（测试先行）仅适用于手动编码场景

### Proposal 3: pipeline 统一 Python 环境

**目标技能**: `pm-idea-to-mvp`（管线配置）

**变更**：
- 在 pipeline 配置中声明 Python 路径和必要依赖
- 或在 venv 初始化时自动安装 pytest/httpx/uvicorn

### Proposal 4: 添加 assumption-tracking 阶段

**目标技能**: `pm-idea-to-mvp`

**变更**：在 retro 阶段增加假设验证跟踪：
- 从 brief.md 提取 open assumptions
- 在 retro 中标记每个假设的验证状态（已验证/未验证/部分验证/被推翻）
- 生成假设跟踪矩阵

## feedback.jsonl 中的待处理项

本次运行无 feedback.jsonl 文件。以下为本次 retro 识别的待处理项：

1. **OpenCode prompt 防御性约束** → 提案 1
2. **TDD 流程适配** → 提案 2
3. **Python 环境统一** → 提案 3
4. **假设跟踪机制** → 提案 4
5. **自 review 自动化** → 考虑在 OpenCode 生成后自动触发 requesting-code-review

## 进化章节

### 管线 v3.0.0 成功验证

pm-kl-management 是管线 v3.0.0 在真实产品场景（产品知识平台）上的首次完整运行。6 个阶段全部通过，产出了：

- 1 份简报（00-brief.md）
- 1 份调研报告（01-research.md，29 来源，7 竞品 × 3 维度）
- 1 份分析文档 + 5 个 ADR + 术语表（CONTEXT.md）
- 1 个原型（02b-prototype/）
- 1 份 PRD + 4 个 spec + 15 个任务
- 1 个可运行的 MVP（39 测试通过，18 冒烟端点 200）
- 1 份全链路回顾

### 下一步建议

1. **试点验证**：在供应链 IT 团队中选取 1 个 BC 进行实际知识录入和 Agent 消费验证
2. **自动化增强**：将 Proposal 1-4 合入管线配置
3. **多 BC 扩展**：验证多 bounded context 场景下的知识包组装和跨 BC 引用
