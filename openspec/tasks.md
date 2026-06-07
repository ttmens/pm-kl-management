# Tasks: 产品知识平台 MVP

> 参考 `03-prd.md` 用户故事，垂直切片组织。每个任务包含文件路径、验证步骤、完成标准。

---

## T1: 项目骨架 + SQLite 数据库初始化

- **对应故事**: 基础设施
- **文件**: `04-mvp/app.py`, `04-mvp/models.py`, `04-mvp/schema.sql`, `04-mvp/requirements.txt`
- **步骤**:
  1. 创建 FastAPI 项目结构（app.py 入口 + models.py 数据模型 + schema.sql）
  2. 编写 schema.sql 定义 5 张表（biz_kl_items, sys_kl_items, kl_links, audit_logs, users）
  3. 在 app.py 中初始化 SQLite 连接，启动时自动执行 schema.sql
  4. 创建 requirements.txt（fastapi, uvicorn）
- **验证**: `python 04-mvp/app.py` 启动成功，SQLite 文件已创建且包含 5 张表
- **完成标准**: 服务启动返回 200，数据库表结构符合 `openspec/design.md`

---

## T2: biz_kl 条目 CRUD API

- **对应故事**: US-1
- **文件**: `04-mvp/app.py`（路由 + handler）, `04-mvp/test_biz_api.py`
- **步骤**:
  1. 实现 `POST /api/biz` 创建条目（draft 状态）
  2. 实现 `GET /api/biz` 列表查询（支持 `?status=` 和 `?q=` 搜索）
  3. 实现 `GET /api/biz/{id}` 详情查询
  4. 实现 `PUT /api/biz/{id}` 更新（version +1）
  5. 每次操作写入 audit_logs
  6. 编写 6+ 测试用例
- **验证**: `pytest 04-mvp/test_biz_api.py` 全部通过
- **完成标准**: 创建→查询→更新→列表搜索 全链路可用，audit_logs 有记录

---

## T3: biz_kl 审核流程 API

- **对应故事**: US-1
- **文件**: `04-mvp/app.py`, `04-mvp/test_biz_review.py`
- **步骤**:
  1. 实现 `POST /api/biz/{id}/submit`（draft → reviewing）
  2. 实现 `POST /api/biz/{id}/publish`（reviewing → published，仅 admin）
  3. 权限校验：publish 检查 `X-User-Id` 对应角色为 admin
  4. 编写测试：正常流程 + 权限拒绝场景
- **验证**: `pytest 04-mvp/test_biz_review.py` 全部通过
- **完成标准**: 草稿→提交审核→发布 全链路可用，非 admin 调用 publish 返回 403

---

## T4: sys_kl 条目 CRUD API

- **对应故事**: US-2
- **文件**: `04-mvp/app.py`, `04-mvp/test_sys_api.py`
- **步骤**:
  1. 实现 `POST /api/sys` 创建条目（draft 状态，含 DDD layer）
  2. 实现 `GET /api/sys` 列表（支持 `?layer=` 筛选）
  3. 实现 `GET /api/sys/{id}` 详情
  4. 实现 `PUT /api/sys/{id}` 更新
  5. 编写 6+ 测试用例
- **验证**: `pytest 04-mvp/test_sys_api.py` 全部通过
- **完成标准**: 创建→查询→更新→按层级筛选 全链路可用

---

## T5: biz_kl ↔ sys_kl 互链管理 API

- **对应故事**: US-2
- **文件**: `04-mvp/app.py`, `04-mvp/test_links.py`
- **步骤**:
  1. 实现 `POST /api/sys/{id}/link` 添加关联（验证 biz_id 存在）
  2. 实现 `DELETE /api/sys/{id}/link/{link_id}` 删除关联
  3. `GET /api/biz/{id}` 响应包含关联 sys_kl 列表
  4. `GET /api/sys/{id}` 响应包含关联 biz_kl 列表
  5. 编写测试：正常关联 + 不存在的 biz_id 返回 404 + 双向查询
- **验证**: `pytest 04-mvp/test_links.py` 全部通过
- **完成标准**: 关联创建后双向查询均可返回对方条目

---

## T6: 知识包生成 API（JSON）

- **对应故事**: US-3
- **文件**: `04-mvp/app.py`, `04-mvp/test_package.py`
- **步骤**:
  1. 实现 `GET /api/packages?biz_ids=id1,id2` 生成 JSON 知识包
  2. 自动查询关联 sys_kl + 组装 links + lineage
  3. 仅包含 published 状态的条目
  4. 输出符合 `openspec/design.md` JSON Schema
  5. 编写测试：单条目 + 多条目 + 空结果
- **验证**: `pytest 04-mvp/test_package.py` 全部通过，JSON 通过 Schema 校验
- **完成标准**: 响应 JSON 包含 biz_kl / sys_kl / links / lineage 四部分

---

## T7: 知识包导出 API（Markdown）

- **对应故事**: US-3
- **文件**: `04-mvp/app.py`, `04-mvp/test_package_md.py`
- **步骤**:
  1. 实现 `GET /api/packages/{biz_ids}.md` 生成 Markdown 格式
  2. 按业务概念分组，含关联代码模块表格
  3. 编写测试：验证 Markdown 内容包含预期标题和表格
- **验证**: `pytest 04-mvp/test_package_md.py` 通过，手动检查 Markdown 可读性
- **完成标准**: 响应为 text/markdown，内容人类可读

---

## T8: 审计日志 API

- **对应故事**: US-5
- **文件**: `04-mvp/app.py`, `04-mvp/test_audit.py`
- **步骤**:
  1. 实现 `GET /api/audit` 查询日志（支持 `?item_id=`、`?actor_id=`、`?from=`、`?to=`）
  2. 按 `created_at` 倒序排列
  3. 所有 T2/T3/T4 的 API 操作已自动写入 audit_logs
  4. 编写测试：创建条目后审计日志有记录 + 筛选功能
- **验证**: `pytest 04-mvp/test_audit.py` 通过
- **完成标准**: 执行 CRUD 操作后 `/api/audit` 返回对应记录

---

## T9: 前端 — 知识列表页（biz_kl / sys_kl tab 切换）

- **对应故事**: US-4
- **文件**: `04-mvp/templates/index.html`, `04-mvp/templates/biz_list.html`, `04-mvp/templates/sys_list.html`
- **步骤**:
  1. 使用 HTMX 实现 `/` 页面：顶部搜索栏 + biz_kl/sys_kl tab 切换
  2. biz_kl 列表展示：名称、类型、状态 badge、标签、关联数
  3. sys_kl 列表展示：名称、DDD 层级、路径、关联 biz_kl
  4. 样式遵循 `04-mvp/DESIGN.md` 设计系统
  5. 搜索框通过 HTMX 触发后端搜索
- **验证**: 启动服务后浏览器访问 `/` 可正常展示列表和 tab 切换
- **完成标准**: 列表页可展示已发布的 biz_kl 和 sys_kl 条目，搜索有结果

---

## T10: 前端 — 条目详情页

- **对应故事**: US-4
- **文件**: `04-mvp/templates/biz_detail.html`, `04-mvp/templates/sys_detail.html`
- **步骤**:
  1. biz 详情页：展示完整信息、关联 sys_kl 卡片列表、版本历史
  2. sys 详情页：展示完整信息、关联 biz_kl 卡片列表
  3. 详情页支持「编辑」和「提交审核」操作（HTMX 局部更新）
  4. 关联条目可点击跳转到对方详情页
- **验证**: 点击列表项进入详情页，关联条目可互相跳转
- **完成标准**: 详情页展示完整信息，双向链接可点击

---

## T11: 前端 — 知识包导出页

- **对应故事**: US-3
- **文件**: `04-mvp/templates/export.html`
- **步骤**:
  1. 实现 `/export` 页面：多选 biz_kl 条目（checkbox）
  2. JSON/Markdown 格式切换按钮
  3. 实时预览区展示生成的内容
  4. 「下载知识包」按钮触发文件下载
- **验证**: 选择条目后预览区显示对应 JSON/Markdown，下载按钮可下载文件
- **完成标准**: 导出页可生成并下载知识包

---

## T12: 前端 — 审计日志页

- **对应故事**: US-5
- **文件**: `04-mvp/templates/audit.html`
- **步骤**:
  1. 实现 `/audit` 页面：表格展示操作记录
  2. 支持按条目 ID、操作人、时间范围筛选
  3. 仅 admin 角色可见（通过 HTMX 条件渲染）
- **验证**: admin 用户访问 `/audit` 可看到日志表格和筛选器
- **完成标准**: 审计日志页面功能完整

---

## T13: 种子数据 + 冒烟测试脚本

- **对应故事**: 全部
- **文件**: `04-mvp/seed_data.py`, `04-mvp/smoke_test.py`
- **步骤**:
  1. seed_data.py：插入 5 条 biz_kl + 5 条 sys_kl + 互链 + 模拟用户
  2. smoke_test.py：验证所有 API 端点返回 2xx
  3. 包含知识包导出 + 审计日志查询验证
- **验证**: `python 04-mvp/seed_data.py` 成功后 `python 04-mvp/smoke_test.py` 全部通过
- **完成标准**: 冒烟测试覆盖所有 API 端点，无 4xx/5xx

---

## T14: 批量导入（Markdown 模板）

- **对应故事**: US-1, US-2
- **文件**: `04-mvp/app.py`, `04-mvp/test_import.py`, `04-mvp/templates/import.html`
- **步骤**:
  1. 实现 `POST /api/import/biz` 从 Markdown 文件批量导入 biz_kl 草稿
  2. Markdown 格式：`# 名称\n\n描述\n\n类型: 流程\n标签: tag1, tag2`
  3. 实现前端 `/import` 页面：上传 Markdown 文件，预览导入结果
  4. 编写测试：有效文件 + 格式错误文件
- **验证**: `pytest 04-mvp/test_import.py` 通过
- **完成标准**: 上传符合格式的 Markdown 文件后，批量创建草稿条目

---

## T15: README + 部署说明

- **对应故事**: 基础设施
- **文件**: `04-mvp/README.md`, `04-mvp/run.sh`
- **步骤**:
  1. README.md 包含：产品简介、技术栈、安装步骤、启动命令、API 文档链接
  2. run.sh：一键启动脚本（安装依赖 → 初始化数据库 → 插入种子数据 → 启动服务）
  3. 验证在新环境中 `bash run.sh` 可完整启动
- **验证**: 新目录中 `bash run.sh` 成功启动，浏览器访问 `/` 正常
- **完成标准**: README 清晰，一键启动脚本工作正常
