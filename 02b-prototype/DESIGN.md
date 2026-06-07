# Design Contract — 产品知识平台（KL Management）

## Product feel

B2B 内部工具，面向供应链 IT 团队。风格务实、信息密度高、减少装饰。类似内部 Dashboard 而非营销页面。

## Colors（hex）

| Token | Value | Usage |
|-------|-------|-------|
| primary | `#1a56db` | 主按钮、链接、激活态 |
| primary-hover | `#1e40af` | 主按钮 hover |
| surface | `#f8fafc` | 页面背景 |
| card | `#ffffff` | 卡片背景 |
| border | `#e2e8f0` | 分割线、边框 |
| text | `#0f172a` | 正文 |
| text-secondary | `#64748b` | 辅助文字、标签 |
| success | `#059669` | 已发布状态 |
| warning | `#d97706` | 审核中状态 |
| danger | `#dc2626` | 已废弃/错误 |
| biz-accent | `#7c3aed` | biz_kl 视觉标识 |
| sys-accent | `#0891b2` | sys_kl 视觉标识 |

## Typography

- Heading: system-ui, -apple-system, sans-serif, 16–24px
- Body: system-ui, -apple-system, sans-serif, 14px
- Code: 'SF Mono', 'Cascadia Code', Consolas, monospace, 13px
- Line height: 1.5 body, 1.3 heading

## Spacing scale

4px base unit: 4, 8, 12, 16, 24, 32, 48

## Component notes

- 卡片：白底 + 1px border + 4px border-radius +  subtle shadow
- 标签：小圆角 pill，浅色背景 + 深色文字
- 状态 badge：彩色圆点 + 文字
- 搜索框：顶部固定，带图标
- 表格：斑马纹 + hover 高亮行
- 按钮：主按钮填充色，次按钮描边框

## UX rules

- 每屏最多 3 个主操作（避免认知过载）
- biz_kl 用紫色标识，sys_kl 用青色标识，互链关系用连接图标
- 空状态显示引导文案（"暂无知识条目，点击创建第一条"）
- 知识包导出提供 JSON / Markdown 格式切换

## Out of scope for prototype

- 后端交互（原型为纯静态 HTML）
- 真实搜索（用 placeholder 数据展示）
- 权限/登录界面
- 审计日志详细页
