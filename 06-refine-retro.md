# Refine 深化回顾 — pm-kl-management

## 触发

`hermes kanban refine kl-management` — 对 v3 MVP 实现不满意，需业界深研与 C4/旅程/UX 深度优化。

## 子阶段产出

| 子阶段 | 任务 | 产物 | 状态 |
|--------|------|------|------|
| Refine-1 | `t_0feb2316` | 01b-benchmark.md | ✅ done |
| Refine-2 | `t_799ef925` | architecture/c4-*.md + ADR-006~009 | ✅ done |
| Refine-3 | `t_9768e3cd` | 03b-user-journey.md + 刷新原型 | ✅ done |
| Refine-4 | `t_97fccc47` | schema/models/app 更新 + UX-REVIEW.md | ⚠️ 超时（代码已写入） |

## Refine-1 业界深研（6 个案例）

1. **Backstage Catalog** — Spotify 开源开发者门户，BC 建模参考
2. **Confluence 审批流** — 企业级内容审核参考
3. **GitBook MCP Server** — AI 可发现性参考
4. **Mintlify Docs-as-Code** — Git 同步 + 自动更新参考
5. **Context Mapper / BC Canvas** — DDD BC 建模工具
6. **Glean Knowledge Graph** — 知识图谱 + 权限感知

→ 10 条 actionable feedback 写入 feedback.jsonl

## Refine-2 C4 架构

**新增 ADR：**
- ADR-006：审核撤回回滚机制
- ADR-007：知识包状态过滤 + 权限感知
- ADR-008：BC 建模 + link_type 关系类型
- ADR-009：版本快照表

**C4 三层更新：**
- c4-context.md：外部系统关系
- c4-container.md：新增版本服务、审批服务容器
- c4-component.md：细化 biz_kl_versions、kl_links 组件

## Refine-3 用户旅程

- 4 Persona：领域专家、开发者、审批者、管理员
- 5 核心旅程：J1 知识贡献、J2 系统知识、J3 知识包导出、J4 知识发现、J5 审计治理
- 13 Touchpoint，9 屏幕映射
- 原型新增：审批队列页、版本对比页、撤回弹窗、BC 标签、角色切换器

## Refine-4 MVP 优化（代码已持久化）

**Schema 变更：**
- sys_kl_items 新增 `bounded_context` 列
- kl_links 新增 `link_type` 列（implements/dependsOn/governs/acl/published_language/open_host_service）
- 新增 `biz_kl_versions` 快照表
- audit_logs 新增 `withdraw` action

**API 新增端点：**
- `POST /api/biz/{id}/withdraw` — 撤回并回滚到最近 published 版本
- `POST /api/biz/{id}/reject` — 驳回（含原因）
- `GET /api/biz/{id}/history` — 版本历史
- `GET /api/biz/{id}/history/{v1}/{v2}` — 版本 diff
- `GET /api/review` — 审批队列
- `GET /review` — 审批队列页面
- sys 列表新增 `?bc=` 过滤

**UX 验收（UX-REVIEW.md）：**
- P0 = 0 ✅
- P1 = 1（UX-004 sys 侧关联搜索选择器，留待下一迭代）
- P2 = 3（sys 详情操作、导出权限提示、用户管理页）

**测试：**
- pytest: 40 passed
- smoke test: 全部端点 200

## 差距关闭

| 差距 | 状态 |
|------|------|
| 驳回/撤回回滚 | ✅ 已关闭 |
| 权限感知导出 | ✅ 已关闭 |
| 审批者队列 | ✅ 已关闭 |
| 版本历史 | ✅ 已关闭 |
| BC 建模 + link_type | ✅ 已关闭 |
| sys 侧关联搜索选择器 | ⏳ 下一迭代 |
| 用户管理 UI | ⏳ 下一迭代 |

## 进化建议

1. v4 流水线对新 idea 强制 C4 + journey + design-review
2. Refine CLI 已验证可创建 4 子任务 DAG
3. pm-builder 的 Refine-4 任务（含 60 次迭代）对大量代码更新可能不够 — 考虑增加 max-retries 或拆分任务
4. 建议在 Refine-4 中优先修复 P0 → 跑测试 → 写 UX-REVIEW → 再处理 P1/P2
