# 阶段回顾（Retro）：pm-kl-management

## 阶段信息

| 项目 | 值 |
|------|-----|
| 产品 slug | kl-management |
| 阶段 | MVP（Stage 5） |
| 日期 | 2026-06-07 |
| 模型 | qwen3.6-plus |

## 阶段耗时

OpenCode 一次性生成全部文件（约 8-10 分钟），修复 6 个测试失败（约 5 分钟），冒烟测试 + stage-complete（约 3 分钟）。总计约 **15-20 分钟**。

## 完成成果

- **39 个 pytest 测试**全部通过（8 个测试文件）
- **18 个冒烟测试端点**全部返回 200
- **15 个 tasks.md 任务**全部完成
- Gate 验证通过，已推送到 GitHub

## 经验教训

### 1. OpenCode 生成的代码质量良好但有边界 Bug

OpenCode 一次性生成了完整的 FastAPI 应用 + 8 个测试文件 + 9 个 HTML 模板 + 辅助脚本，覆盖全部 15 个任务。但存在 6 个边界 Bug：

- **链接查询函数名互换**：`api_biz_detail` 调用了 `get_links_for_sys`（应调用 `get_links_for_biz`），`api_sys_detail` 反之。这是因为函数命名从「为谁查」的角度不够直观。
- **测试辅助函数签名错误**：`create_published_biz(db, name=...)` 的 `db` 参数从未使用，导致调用时 name 参数被当作 db 传入。
- **import 校验不严**：没有 `类型:` 行的纯文本也能被解析为条目。
- **conftest.py 重复参数**：`@pytest.fixture(autouse=True, scope="session", autouse=True)` 有重复的 `autouse`。

### 2. 手动修复比二次调用 OpenCode 更高效

对于 6 个已知失败的测试，直接阅读代码定位 root cause 后 patch 修复（~5 分钟）比重新调用 OpenCode 修复（需要上下文重建 + 可能超时）更快。

### 3. Windows 路径 + Python 环境问题

Hermes venv 的 Python 没有 pytest/httpx 等依赖，需要用系统 Python（`C:\Users\FIREBAT\AppData\Local\Programs\Python\Python312\python.exe`）运行测试。在 OpenCode 的 bash 环境中路径解析也有问题。

### 4. 测试文件模块级 `init_db()` 的设计

每个测试文件在模块加载时调用 `models.init_db()`，通过 conftest.py 的 session fixture 将 DB 路径指向 `data/test_kl.db`。这样设计避免了测试之间的状态干扰，但需要注意 init_db 的时序。

## 进化章节

### 改进 OpenCode Prompt

下次可以在 prompt 中加入以下预防措施：
- 要求函数命名遵循 `get_X_for_Y` 模式时，明确文档化 X 是返回类型、Y 是查询键
- 要求测试辅助函数不要包含未使用的参数
- 要求 import 解析器必须有格式校验

### 测试驱动开发流程优化

本次是 OpenCode 先生成代码后跑测试发现失败再修复，严格来说不是 TDD（测试先行）。但对于 OpenCode 这种黑盒生成工具，「生成→测试→修复」循环是更实际的流程。

### README 质量 Gate

stage-complete 的 eval-stage 检查 README 是否引用了 MVP 流程/任务，这是一个有效的质量门。下次可以在 OpenCode prompt 中明确要求包含核心流程描述。

## 总结

MVP 阶段顺利完成，产品知识平台（KL Management）的核心功能已全部实现并可运行。下一步应进行 retro 阶段合并知识。
