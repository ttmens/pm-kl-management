# Spec: 知识包导出

## ADDED

### 知识包生成 API

- `GET /api/packages?biz_ids=id1,id2,...`：按选中的 biz_kl 条目 ID 生成知识包
  - 自动查询这些条目关联的所有 sys_kl 条目
  - 返回符合 JSON Schema 的完整知识包（biz_kl + sys_kl + links + lineage）
  - 响应头 `Content-Type: application/json`
- `GET /api/packages/{biz_ids}.md`：同上，但返回 Markdown 格式
  - 按业务概念分组
  - 每条包含概念描述、关联代码模块、变更历史
  - 响应头 `Content-Type: text/markdown`

### JSON Schema 验证

知识包 JSON 输出 SHALL 符合 `openspec/design.md` 中定义的 `KnowledgePackage` JSON Schema。

### 前端导出页

- `/export`：知识包导出页
  - 展示已发布的 biz_kl 条目列表，支持多选
  - 格式切换：JSON（Agent 消费）/ Markdown（人工审阅）
  - 实时预览生成的内容
  - 「下载知识包」按钮触发文件下载
  - 「复制到剪贴板」按钮

### 知识包内容组装规则

1. 选中的 biz_kl 条目直接包含
2. 通过 `kl_links` 表查询所有关联的 sys_kl 条目
3. 计算 lineage：从 biz_kl 和 sys_kl 的 created_by / created_at 字段组装
4. 仅包含 status 为 `published` 的条目