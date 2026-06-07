# Tasks: 产品知识平台 MVP（旅程驱动切片）

> 参考 `03-prd.md` 用户故事和 `03b-user-journey.md` 旅程映射，垂直切片组织。每个任务包含文件路径、验证步骤、完成标准。

---

## 切片 1: 知识贡献路径（J1 + J2）— biz_kl + sys_kl CRUD

### T1: 项目骨架 + SQLite 数据库初始化

- **对应旅程**: J1-1, J2-1（基础设施）
- **文件**: `04-mvp/app.py`, `04-mvp/models.py`, `04-mvp/schema.sql`, `04-mvp/requirements.txt`
- **步骤**:
  1. 创建 FastAPI 项目结构（app.py 入口 + models.py 数据模型 + schema.sql）
  2. 编写 schema.sql 定义 6 张表（biz_kl_items, sys_kl_items, kl_links, biz_kl_versions, audit_logs, users）
  3. sys_kl_items 包含 `bounded_context` 字段（ADR-008），kl_links 包含 `link_type` 字段（ADR-008）
  4. 在 app.py 中初始化 SQLite 连接，启动时自动执行 schema.sql
  5. 创建 requirements.txt（fastapi, uvicorn）
- **验证**: `python 04-mvp/app.py` 启动成功，SQLite 文件已创建且包含 6 张表
- **完成标准**: 服务启动返回 200，数据库表结构符合 `openspec/design.md`

---

### T2: biz_kl 条目 CRUD + 审核流 API（含撤回）

- **对应旅程**: J1-2, J1-3, J1-5
- **文件**: `04-mvp/app.py`, `04-mvp/test_biz_api.py`
- **步骤**:
  1. 实现 `POST /api/biz` 创建条目（draft 状态）
  2. 实现 `GET /api/biz` 列表查询（支持 `?status=` 和 `?q=` 搜索）
  3. 实现 `GET /api/biz/{id}` 详情查询（含关联 sys_kl、版本历史）
  4. 实现 `PUT /api/biz/{id}` 更新（version +1，写入 biz_kl_versions 快照）
  5. 实现 `POST /api/biz/{id}/submit`（draft → reviewing）
  6. 实现 `POST /api/biz/{id}/publish`（reviewing → published，仅 admin）
  7. 实现 `POST /api/biz/{id}/withdraw`（回滚到最近 published 版本，ADR-006）
  8. 实现 `POST /api/biz/{id}/reject`（reviewing → rejected，记录 rejection_reason，ADR-006）
  9. 每次操作写入 audit_logs
  10. 编写 8+ 测试用例
- **验证**: `pytest 04-mvp/test_biz_api.py` 全部通过
- **完成标准**: 创建→查询→更新→审核→发布→撤回 全链路可用，audit_logs 有记录

---

### T3: sys_kl 条目 CRUD + 互链管理 API（含 BC 和 link_type）

- **对应旅程**: J2-2, J2-3, J2-4
- **文件**: `04-mvp/app.py`, `04-mvp/test_sys_api.py`
- **步骤**:
  1. 实现 `POST /api/sys` 创建条目（含 bounded_context 和 DDD layer）
  2. 实现 `GET /api/sys` 列表（支持 `?layer=` 和 `?bc=` 筛选）
  3. 实现 `GET /api/sys/{id}` 详情（含关联 biz_kl 列表）
  4. 实现 `PUT /api/sys/{id}` 更新
  5. 实现 `POST /api/sys/{id}/link` 添加关联（含 link_type：implements/dependsOn/governs/acl/published_language/open_host_service）
  6. 实现 `DELETE /api/sys/{id}/link/{link_id}` 删除关联
  7. 双向查询：GET /api/biz/{id} 返回关联 sys_kl，GET /api/sys/{id} 返回关联 biz_kl
  8. 编写 8+ 测试用例
- **验证**: `pytest 04-mvp/test_sys_api.py` 全部通过
- **完成标准**: 创建→查询→更新→关联→双向查询 全链路可用，link_type 正确持久化

---

### T4: 版本历史 API（ADR-009）

- **对应旅程**: J4-3
- **文件**: `04-mvp/app.py`, `04-mvp/test_version.py`
- **步骤**:
  1. 实现 `GET /api/biz/{id}/history` 返回版本列表
  2. 实现 `GET /api/biz/{id}/history/{v1}/{v2}` 返回两个版本的 diff
  3. 每次 update/publish 自动写入 biz_kl_versions 快照表
  4. 编写测试：快照写入 + 版本列表 + diff 对比
- **验证**: `pytest 04-mvp/test_version.py` 通过
- **完成标准**: 版本快照自动记录，diff API 返回正确变更内容

---

## 切片 2: 知识消费路径（J3）— 知识包导出

### T5: 知识包生成 API（JSON + 状态过滤 + 权限感知）

- **对应旅程**: J3-1, J3-3
- **文件**: `04-mvp/app.py`, `04-mvp/test_package.py`
- **步骤**:
  1. 实现 `GET /api/packages?biz_ids=id1,id2` 生成 JSON 知识包
  2. 自动查询关联 sys_kl + 组装 links + lineage
  3. **仅包含 published 状态的条目**（ADR-007）
  4. **按请求者角色过滤可见范围**（ADR-007）：expert 仅看自己创建的，developer 看全部 published
  5. **按 bounded_context 分组**（ADR-008）
  6. 输出符合 JSON Schema
  7. 编写测试：单条目 + 多条目 + 空结果 + 权限过滤 + 状态过滤
- **验证**: `pytest 04-mvp/test_package.py` 全部通过，JSON 通过 Schema 校验
- **完成标准**: 响应 JSON 包含 biz_kl / sys_kl / links / lineage，仅含 published，权限过滤生效

---

### T6: 知识包导出 API（Markdown）

- **对应旅程**: J3-2
- **文件**: `04-mvp/app.py`, `04-mvp/test_package_md.py`
- **步骤**:
  1. 实现 `GET /api/packages/{biz_ids}.md` 生成 Markdown 格式
  2. 按业务概念分组，含 BC 归属和关联代码模块表格
  3. 编写测试：验证 Markdown 内容包含预期标题、表格、BC 标签
- **验证**: `pytest 04-mvp/test_package_md.py` 通过，手动检查 Markdown 可读性
- **完成标准**: 响应为 text/markdown，内容人类可读，含 BC 分组

---

## 切片 3: 知识发现路径（J4）— 搜索与浏览

### T7: 前端 — 知识列表页 + 全局搜索

- **对应旅程**: J1-1, J2-1, J4-1
- **文件**: `04-mvp/templates/index.html`, `04-mvp/templates/biz_list.html`, `04-mvp/templates/sys_list.html`
- **步骤**:
  1. 使用 HTMX 实现 `/` 页面：顶部搜索栏 + biz_kl/sys_kl tab 切换
  2. biz_kl 列表展示：名称、类型、状态 badge、标签、关联数
  3. sys_kl 列表展示：名称、DDD 层级、BC 归属、路径、关联 biz_kl
  4. 搜索框通过 HTMX 触发后端搜索，结果按 biz_kl/sys_kl 分类展示
  5. 样式遵循 DESIGN.md 设计系统
- **验证**: 启动服务后浏览器访问 `/` 可正常展示列表、tab 切换和搜索结果
- **完成标准**: 列表页可展示条目，搜索 <1 秒返回结果

---

### T8: 前端 — 条目详情页 + 版本历史

- **对应旅程**: J1-3, J1-5, J2-3, J4-2, J4-3
- **文件**: `04-mvp/templates/biz_detail.html`, `04-mvp/templates/sys_detail.html`, `04-mvp/templates/version_history.html`
- **步骤**:
  1. biz 详情页：完整信息、关联 sys_kl 卡片（含 link_type 标签）、版本历史列表
  2. sys 详情页：完整信息、关联 biz_kl 卡片、BC 归属显示
  3. 版本历史页：版本列表 + diff 对比视图（ADR-009）
  4. biz 详情页增加「撤回」按钮（ADR-006，仅 reviewing 态可见）
  5. 关联条目可点击跳转到对方详情页
- **验证**: 点击列表项进入详情页，关联条目可互相跳转，版本历史可对比
- **完成标准**: 详情页展示完整信息，双向链接可点击，版本对比可用

---

## 切片 4: 审核与治理路径（J5）— 审批与审计

### T9: 前端 — 审批者队列页（ADR-006）

- **对应旅程**: J1-4
- **文件**: `04-mvp/templates/review.html`
- **步骤**:
  1. 实现 `/review` 页面：列出所有 reviewing 状态条目
  2. 每个条目展示 diff 预览（当前审核中内容 vs 最近 published 版本）
  3. 提供「发布」和「驳回」操作按钮
  4. 驳回时需填写驳回理由（记录到 audit_logs）
  5. 仅 admin 角色可见（HTMX 条件渲染）
- **验证**: admin 用户访问 `/review` 可看到待审条目列表、diff 和审批操作
- **完成标准**: 审批操作完成，audit_logs 记录发布/驳回操作及驳回理由

---

### T10: 前端 — 知识包导出页 + 审计日志页

- **对应旅程**: J3-1, J3-2, J5-1
- **文件**: `04-mvp/templates/export.html`, `04-mvp/templates/audit.html`
- **步骤**:
  1. `/export`：多选 biz_kl 条目（仅 published），JSON/Markdown 格式切换，实时预览，下载按钮
  2. `/audit`：审计日志表格（操作类型、条目、操作人、时间、详情）
  3. 审计日志支持按条目 ID、操作人、时间范围筛选
  4. 导出页展示权限过滤提示（ADR-007）
- **验证**: 导出页可生成并下载知识包，审计日志页面筛选功能正常
- **完成标准**: 两个页面功能完整，导出数据正确

---

### T11: 审计日志 API + 用户管理

- **对应旅程**: J5-1, J5-2
- **文件**: `04-mvp/app.py`, `04-mvp/test_audit.py`
- **步骤**:
  1. 实现 `GET /api/audit` 查询日志（支持 `?item_id=`、`?actor_id=`、`?from=`、`?to=`）
  2. 按 `created_at` 倒序排列
  3. 所有 CRUD/审核/撤回操作已自动写入 audit_logs
  4. 实现简单的用户角色管理（admin 可为用户分配角色）
  5. 角色变更记录在审计日志中
  6. 编写测试：创建条目后审计日志有记录 + 筛选功能
- **验证**: `pytest 04-mvp/test_audit.py` 通过
- **完成标准**: 执行操作后 `/api/audit` 返回对应记录，角色管理可用

---

## 切片 5: 验证与交付

### T12: 审批队列 API

- **对应旅程**: J1-4
- **文件**: `04-mvp/app.py`, `04-mvp/test_review.py`
- **步骤**:
  1. 实现 `GET /api/review` 列出所有 reviewing 状态条目（管理员视角）
  2. 返回条目详情 + diff 信息（当前内容 vs 最近 published 快照）
  3. 编写测试：有 reviewing 条目时返回列表，无时为空
- **验证**: `pytest 04-mvp/test_review.py` 通过
- **完成标准**: `/api/review` 返回正确的待审条目列表

---

### T13: 批量导入（Markdown 模板）

- **对应旅程**: J1-2, J2-2（辅助路径）
- **文件**: `04-mvp/app.py`, `04-mvp/test_import.py`, `04-mvp/templates/import.html`
- **步骤**:
  1. 实现 `POST /api/import/biz` 从 Markdown 文件批量导入 biz_kl 草稿
  2. Markdown 格式：`# 名称\n\n描述\n\n类型: 流程\n标签: tag1, tag2`
  3. 实现前端 `/import` 页面：上传 Markdown 文件，预览导入结果
  4. 编写测试：有效文件 + 格式错误文件
- **验证**: `pytest 04-mvp/test_import.py` 通过
- **完成标准**: 上传符合格式的 Markdown 文件后，批量创建草稿条目

---

### T14: 种子数据 + 冒烟测试脚本

- **对应旅程**: 全部
- **文件**: `04-mvp/seed_data.py`, `04-mvp/smoke_test.py`
- **步骤**:
  1. seed_data.py：插入 5 条 biz_kl（含 reviewing 状态）+ 5 条 sys_kl（含 BC 归属）+ 互链（含 link_type）+ 模拟用户 + 版本快照
  2. smoke_test.py：验证所有 API 端点返回 2xx
  3. 包含知识包导出 + 审计日志查询 + 审批队列验证
- **验证**: `python 04-mvp/seed_data.py` 成功后 `python 04-mvp/smoke_test.py` 全部通过
- **完成标准**: 冒烟测试覆盖所有 API 端点，无 4xx/5xx

---

### T15: README + 部署说明

- **对应旅程**: 基础设施
- **文件**: `04-mvp/README.md`, `04-mvp/run.sh`
- **步骤**:
  1. README.md 包含：产品简介、技术栈、安装步骤、启动命令、API 文档链接
  2. run.sh：一键启动脚本（安装依赖 → 初始化数据库 → 插入种子数据 → 启动服务）
  3. 验证在新环境中 `bash run.sh` 可完整启动
- **验证**: 新目录中 `bash run.sh` 成功启动，浏览器访问 `/` 正常
- **完成标准**: README 清晰，一键启动脚本工作正常
