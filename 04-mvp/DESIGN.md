# Design System — 产品知识平台（KL Management）

## Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--primary` | `#1a56db` | 主按钮、链接、激活态 |
| `--primary-hover` | `#1e40af` | 主按钮 hover |
| `--surface` | `#f8fafc` | 页面背景 |
| `--card` | `#ffffff` | 卡片背景 |
| `--border` | `#e2e8f0` | 分割线、边框 |
| `--text` | `#0f172a` | 正文 |
| `--text-secondary` | `#64748b` | 辅助文字、标签 |
| `--success` | `#059669` | 已发布状态 |
| `--warning` | `#d97706` | 审核中状态 |
| `--danger` | `#dc2626` | 已废弃 / 错误 |
| `--biz-accent` | `#7c3aed` | biz_kl 视觉标识（紫色） |
| `--sys-accent` | `#0891b2` | sys_kl 视觉标识（青色） |

## Typography

| Token | Value |
|-------|-------|
| `--font-heading` | `system-ui, -apple-system, sans-serif` |
| `--font-body` | `system-ui, -apple-system, sans-serif` |
| `--font-code` | `'SF Mono', 'Cascadia Code', Consolas, monospace` |
| `--text-sm` | `12px` |
| `--text-base` | `14px` |
| `--text-lg` | `15px` |
| `--text-xl` | `16px` |
| `--text-2xl` | `24px` |
| `--leading-body` | `1.5` |
| `--leading-heading` | `1.3` |

## Spacing Scale

基于 4px 单位：`4, 8, 12, 16, 24, 32, 48`

## Component Patterns

### Buttons

- **Primary**: `background: var(--primary); color: #fff; border: 1px solid var(--primary); border-radius: 4px; padding: 8px 16px`
- **Secondary**: `background: var(--card); color: var(--text); border: 1px solid var(--border); border-radius: 4px; padding: 8px 16px`
- **Small**: 同上，`padding: 4px 10px; font-size: 12px`

### Cards

- `background: var(--card); border: 1px solid var(--border); border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 16px`

### Badges

- **Published**: `background: #d1fae5; color: var(--success); border-radius: 100px; padding: 2px 8px; font-size: 11px`
- **Reviewing**: `background: #fef3c7; color: var(--warning)`
- **Draft**: `background: #f1f5f9; color: var(--text-secondary)`
- **biz_kl tag**: `background: #ede9fe; color: var(--biz-accent)`
- **sys_kl tag**: `background: #cffafe; color: var(--sys-accent)`

### Tables

- 斑马纹：`tr:nth-child(even) td { background: var(--surface) }`
- Hover：`tr:hover td { background: #f0f7ff }`
- 表头：`background: var(--surface); font-size: 12px; color: var(--text-secondary)`

### Tags

- `background: var(--surface); border: 1px solid var(--border); border-radius: 4px; padding: 2px 8px; font-size: 12px; color: var(--text-secondary)`

## UX Rules

1. **每屏最多 3 个主操作** — 避免认知过载，次要操作放在「更多」菜单
2. **biz_kl 用紫色标识，sys_kl 用青色标识** — 视觉上严格区分两种知识类型
3. **空状态显示引导文案** — 如"暂无知识条目，点击创建第一条"，避免空白页
4. **知识包导出提供格式切换** — JSON（Agent 消费）和 Markdown（人工审阅）一键切换
5. **对比度符合 WCAG AA** — 正文文字 `#0f172a` on `#ffffff`，对比度 > 15:1
6. **互链关系用视觉连接指示** — 在关联处使用 🔗 图标 + 可点击卡片
