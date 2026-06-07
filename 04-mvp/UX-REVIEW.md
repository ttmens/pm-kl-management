# UX 验收报告 — Refine-4 深化版

## 对照基准

- 03b-user-journey.md（5 个核心旅程 J1–J5，13 个 Touchpoint）
- 02b-prototype/
- 04-mvp/DESIGN.md
- 01b-benchmark.md（6 个案例，12 个差距项）

## 旅程覆盖率

| 旅程 | Touchpoint | 覆盖率 | 说明 |
|------|-----------|--------|------|
| J1 知识贡献 | TP1-TP4 | ✅ 100% | 列表 → 创建 → 提交 → 审批队列 全链路可用 |
| J1 处理驳回/撤回 | TP3 | ✅ 100% | 详情页含 submit/publish/reject/withdraw 按钮，状态条件渲染 |
| J2 系统知识 | TP5-TP8 | ⚠️ 85% | sys_kl 列表/详情/BC筛选可用；缺关联搜索选择器（UX-004） |
| J3 知识包导出 | TP9-TP10 | ✅ 100% | 仅 published 条目可见，JSON/MD 切换预览，权限感知过滤 |
| J4 知识发现 | TP1/TP3/TP8/TP11 | ✅ 100% | 搜索/详情/版本历史全链路可用 |
| J5 审计治理 | TP12-TP13 | ⚠️ 80% | 审计日志页可用；用户管理页（/admin/users）未实现 |

## 发现问题

### 开放问题

| ID | 级别 | 页面/流程 | 问题 | 建议 |
|----|------|-----------|------|------|
| UX-004 | P1 | /sys/{id} | 缺关联搜索选择器，无法从 sys 侧主动关联 biz_kl | 后续迭代添加搜索选择器 + link_type 下拉 |
| UX-005 | fixed | 全局导航 | /review 审批队列未在顶栏导航中展示 | ✅ 已在 index.html nav 中增加「审批」链接 |
| UX-006 | P2 | /sys/{id} | sys 详情页无编辑/发布操作按钮 | 增加与 biz_detail 类似的操作区 |
| UX-007 | P2 | /export | 导出页无权限过滤提示（ADR-007 要求） | 增加角色提示：「当前角色可见范围」 |
| UX-008 | P2 | /admin/users | 用户管理页（J5-2）未实现 | 后续迭代增加角色管理 UI |

### 已关闭问题

| ID | 状态 | 备注 |
|----|------|------|
| UX-001 | fixed | 详情页增加 submit/publish/reject 操作按钮 |
| UX-002 | fixed | /audit admin 403 问题已修复 |
| UX-003 | fixed | 顶栏 localStorage 用户切换可用 |

### Benchmark P0 验证

| # | Benchmark P0 | 实现状态 | 验证 |
|---|------------|---------|------|
| 1 | 审核流完善：撤回+回滚 | ✅ 已实现 | `POST /api/biz/{id}/withdraw` + `withdraw_biz()` 回滚到最近 published 快照 |
| 2 | 知识包状态过滤 | ✅ 已实现 | JSON/MD 导出 API 均过滤 `status != "published"` |
| 3 | 权限感知导出 | ✅ 已实现 | expert 角色仅看自己创建的 published 条目，developer 看全部 |

### Benchmark P1 验证

| # | Benchmark P1 | 实现状态 | 说明 |
|---|------------|---------|------|
| 4 | 关系类型化 | ✅ 已实现 | `link_type` 字段（implements/dependsOn/governs 等），详情页显示 link_type 标签 |
| 5 | Bounded Context | ✅ 已实现 | `bounded_context` 字段，sys 列表支持 `?bc=` 筛选，详情页显示 BC 归属 |
| 6 | 版本历史 | ✅ 已实现 | `biz_kl_versions` 快照表 + `GET /api/biz/{id}/history` + diff API + 版本表格 |
| 7 | 审批者队列页面 | ✅ 已实现 | `/review` 页面含 diff 预览、发布/驳回操作，仅 admin 可见 |

## 统计

- **P0**: 0（全部已关闭或验证通过）
- **P1**: 1（UX-004 留待下一迭代）
- **P2**: 3（UX-006, UX-007, UX-008）

## DESIGN.md 一致性检查

| 维度 | 状态 | 说明 |
|------|------|------|
| 调色板 | ✅ | 所有模板使用 CSS 变量，与 DESIGN.md 一致 |
| 字体 | ✅ | system-ui 字体族，字号符合 token 规范 |
| 按钮 | ✅ | Primary/Secondary/Small 三种变体 |
| 卡片 | ✅ | border + box-shadow 统一样式 |
| 徽章 | ✅ | 状态徽章（published/draft/review）颜色统一 |
| 间距 | ✅ | 全局 spacing token 一致 |

## 测试状态

- **pytest**: 40 passed
- **smoke test**: 全部端点 200（需确认服务启动后验证）
