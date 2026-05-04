# Research: fork 边界与工作区清理结论

## 已确认的产品/实现边界

### 1. 只对接 Trellis 现有三代理

Pi 适配必须建立在 Trellis 现有三代理之上：

- `trellis-research`
- `trellis-implement`
- `trellis-check`

Pi 平台可以在平台层把它们编排成 chain，但不能新增一套 Trellis 核心代理模型，否则 fork 会越来越难跟上游同步。

### 2. fork 侵入性必须最小

由于上游官方已明确不考虑接入 Pi，fork 的长期策略不是“把 Trellis 改造成 Pi 优先”，而是：

- 尽量不改 Trellis workflow 核心语义
- 尽量不改共享的三代理契约
- 优先通过平台适配层扩展：
  - `AI_TOOLS`
  - `configurator`
  - `templates/pi/`
  - `.pi/` 输出物

### 3. 首版只增强 Execute

首版 Pi MVP 只增强 Execute：

- `trellis-research -> trellis-implement -> trellis-check`

Plan / Finish 暂时继续复用现有 Trellis 流程，避免为了“Pi 全链路编排”去改动过多上游基础设施。

## 工作区清理记录（2026-04-21）

### 发现的本地残留

#### stash

- `stash@{0}`
- 描述：`On main: local pi adapter changes`
- 内容：`.agents/skills/check/SKILL.md` 的本地改动（34 行新增，10 行删除）

#### 未跟踪/本地实验文件

已发现并清理：

- `.pi/` 原型目录
- `.opencode/agents/coordinator*.md`
- `.opencode/commands/trellis/parallel-v*.md`
- `.vscode/settings.json`
- `prompt.md`
- 若干本地 ignored 实验/缓存文件

### 已执行的清理

- 删除上述未跟踪和本地实验文件
- 删除 stash：`stash@{0}`
- 保留 Trellis 当前任务状态文件（`.trellis/tasks/...`、`.trellis/.current-task`、`.trellis/.developer` 等 ignored task/runtime 文件）

### 清理后状态

- `git status --short --branch`：干净
- `git stash list`：空
- 仓库现在没有可见的 tracked/untracked 本地改动，后续规划以 **上游源码 + 当前任务文档** 为唯一依据

## 对后续实现的约束

1. 不把 repo 根目录临时 `.pi/` 原型当正式模板源
2. 不依赖 stash 或本地未跟踪文件继续规划
3. 后续真正实现时，所有 Pi 接入内容必须回到正式模板源：`packages/cli/src/templates/pi/`
