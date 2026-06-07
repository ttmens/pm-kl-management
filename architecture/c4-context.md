# C4 Level 1 — 系统上下文

## 系统

**产品知识平台（pm-kl-management）** — 在企业 AI 编程场景下，管理业务知识（biz_kl）与系统知识（sys_kl），按 Bounded Context 组织，导出供 Agent/IDE 消费的结构化知识包。

## 外部角色

| 角色 | 说明 |
|------|------|
| 领域专家 | 创建/维护 biz_kl 业务知识条目，按 BC 贡献知识 |
| 开发者 | 维护 sys_kl、关联 biz_kl、按 BC 导出知识包 |
| 管理员 | 审核发布、驳回、撤回审批、查看审计日志 |
| Agent/IDE | 消费导出的 JSON/Markdown 知识包（仅 published 条目，按角色过滤） |
| Git 仓库 | sys_kl 引用代码路径 + commit hash，检测代码变更触发知识更新提醒 |

## 上下文图

```mermaid
C4Context
  title 产品知识平台 — 系统上下文（Refine-2）
  Person(expert, "领域专家", "按 BC 编写业务知识")
  Person(dev, "开发者", "维护系统知识并按 BC 关联")
  Person(admin, "管理员", "审核/驳回/撤回/审计")
  System(kl, "产品知识平台", "biz/sys 知识管理 + BC 组织 + 权限感知导出")
  System_Ext(agent, "Agent/IDE", "注入编程上下文（仅 published 知识包）")
  System_Ext(git, "Git 仓库", "代码路径 + commit hash 引用")
  Rel(expert, kl, "创建/提交审核/撤回")
  Rel(dev, kl, "关联/按BC导出")
  Rel(admin, kl, "发布/驳回/审计")
  Rel(kl, agent, "知识包 JSON/MD（权限过滤）")
  Rel(kl, git, "file_path + commit_hash 引用")
  Rel_U(git, kl, "代码变更通知")
```

## Refine-2 变更说明

相比 MVP 基线，本版本上下文图新增：
- Git 仓库的**双向关系**（平台引用代码路径，代码变更可通知平台更新知识）
- Agent/IDE 明确标注**仅消费 published 条目**（ADR-007 状态过滤）
- 领域专家增加**撤回**操作（ADR-006）
