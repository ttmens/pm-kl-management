# 产品知识平台（pm-kl-management）— 运行说明

## 流水线概览

本流水线按 `pm-idea-to-mvp v3` 执行，共 7 个阶段（Stage 0 → Stage 6）。

## Kanban 任务图

```
T1 (ready)   pm-aligner    → Stage 0+1: 对齐想法 & 产出 CONTEXT.md
  └─ T2 (todo) pm-researcher → Stage 2: 深度调研
       └─ T3 (todo) pm-analyst   → Stage 3: 方案论证
            └─ T4 (todo) pm-planner  → Stage 4: 原型+PRD+OpenSpec
                 └─ T5 (todo) pm-builder  → Stage 5: MVP 实现
                      └─ T6 (todo) pm-builder  → Stage 6: Retro + 自进化
```

## 任务 ID


| 阶段         | 任务 ID        | 状态    | 负责人           |
| ---------- | ------------ | ----- | ------------- |
| 0+1 Align  | `t_cbef8b9e` | ready | pm-aligner    |
| 2 Research | `t_8180aedb` | todo  | pm-researcher |
| 3 Analysis | `t_99248123` | todo  | pm-analyst    |
| 4 Spec     | `t_a523399c` | todo  | pm-planner    |
| 5 MVP      | `t_62c97069` | todo  | pm-builder    |
| 6 Retro    | `t_a79213fd` | todo  | pm-builder    |


## 人工检查点

流水线默认在两处暂停，等待用户确认后继续：

1. **Align 完成后**：等待用户确认 CONTEXT.md 和 brief 的对齐结果
2. **Spec 完成后**：等待用户确认 PRD 和原型范围

用户通过 `hermes kanban unblock <task_id>` 解锁。

## 产物目录

```
D:/workspace/projects/pm-kl-management/
  00-brief.md          ← 已创建
  gates.json           ← 已创建
  CONTEXT.md           ← Align 阶段产出
  decisions.md         ← Align/Analysis 阶段产出
  01-research.md       ← Research 阶段产出
  02-analysis.md       ← Analysis 阶段产出
  02b-prototype/       ← Spec 阶段产出（原型）
  03-prd.md            ← Spec 阶段产出
  openspec/            ← Spec 阶段产出
  04-mvp/              ← MVP 阶段产出
  05-retro.md          ← Retro 阶段产出
```

## 跟踪进度

```bash
hermes kanban show <task_id>
hermes kanban tail <task_id>
```

## GitHub Pages（完成后发布）

- Pages: [https://ttmens.github.io/pm-kl-management/](https://ttmens.github.io/pm-kl-management/)
- GitHub: [https://github.com/ttmens/pm-kl-management](https://github.com/ttmens/pm-kl-management)

