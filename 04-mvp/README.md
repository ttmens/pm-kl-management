# 产品知识平台 MVP（KL Management）

管理业务知识（biz_kl）和系统知识（sys_kl）的结构化平台，支持知识包导出和 AI Agent 消费。

## 技术栈

- 后端：Python FastAPI
- 存储：SQLite
- 前端：HTML + HTMX + Jinja2
- 测试：pytest + httpx

## 快速启动

```bash
bash run.sh
```

或手动启动：

```bash
pip install -r requirements.txt
python seed_data.py
uvicorn app:app --port 8000
```

## API 文档

启动后访问 `http://localhost:8000/docs` 查看 OpenAPI 文档。

## 核心流程

1. **业务知识管理 (US-1)**: 创建 → 编辑 → 提交审核 → 发布（支持 Markdown 批量导入）
2. **系统知识管理 (US-2)**: 按 DDD 分层创建 → 关联 biz_kl → 双向查询
3. **知识包导出 (US-3)**: 选择 biz_kl → 生成 JSON/Markdown → 下载供 Agent 消费
4. **知识检索浏览 (US-4)**: 全局搜索 → tab 切换 → 详情页互链跳转
5. **审计日志 (US-5)**: 按条目/操作人/时间筛选操作记录

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/biz` | 业务知识列表/创建 |
| GET/PUT | `/api/biz/{id}` | 详情/更新 |
| POST | `/api/biz/{id}/submit` | 提交审核 |
| POST | `/api/biz/{id}/publish` | 发布（admin） |
| GET/POST | `/api/sys` | 系统知识列表/创建 |
| GET/PUT | `/api/sys/{id}` | 详情/更新 |
| POST/DELETE | `/api/sys/{id}/link[/{link_id}]` | 关联管理 |
| GET | `/api/packages?biz_ids=` | 知识包 JSON |
| GET | `/api/packages/{biz_ids}.md` | 知识包 Markdown |
| GET | `/api/audit` | 审计日志 |
| POST | `/api/import/biz` | Markdown 批量导入 |

## 页面

| 路径 | 说明 |
|------|------|
| `/` | 知识列表首页 |
| `/biz` | 业务知识列表 |
| `/sys` | 系统知识列表 |
| `/export` | 知识包导出 |
| `/audit` | 审计日志 |
| `/import` | 批量导入 |

## 测试

```bash
pytest . -v
python smoke_test.py
```
