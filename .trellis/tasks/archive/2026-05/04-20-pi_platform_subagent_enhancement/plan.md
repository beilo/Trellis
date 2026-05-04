# Pi hooks 收敛实施计划（strict 单仓版）

## 目标

把 Trellis 现有 hooks 语义以 Pi 原生 extension 方式落地，并按最新边界收敛为：

- 不做兜底
- 不做 monorepo
- 单仓 strict 模式
- 继续复用 `trellis-research` / `trellis-implement` / `trellis-check`

## Trellis 语义映射

### 1. 启动时

Trellis 原生：
- `session-start.py`

Pi 映射：
- `session_start`

负责：
- 注入 `current-state`
- 注入 `workflow`
- 注入 `guidelines`
- 注入 `task-status`
- 注入 `ready`

### 2. 每轮用户输入时

Trellis 原生：
- `inject-workflow-state.py`

Pi 映射：
- `before_agent_start`

负责：
- 每轮注入 `<workflow-state>`

### 3. 子代理上下文注入

Trellis 原生：
- `inject-subagent-context.py`

Pi 映射：
- `before_agent_start`

负责：
- `trellis-research` 注入 task summary + `prd.md` + `info.md`
- `trellis-implement` 注入 `implement.jsonl` + `prd.md` + `info.md`
- `trellis-check` 注入 `check.jsonl` + `prd.md` + `info.md`

### 4. 平台级硬约束

Pi 新增：
- `tool_call`

负责：
- 禁止 `git commit / push / merge`
- 禁止 `.trellis/scripts/task.py`
- 禁止写仓库外路径
- 禁止改 `.trellis/scripts/`
- 禁止改 `.trellis/workflow.md`
- 禁止改 `.trellis/.current-task`
- `trellis-research` 只允许写当前 task 的 `research/*.md`

## 实施步骤

### Step 1：收紧 Pi hooks 边界

修改：
- `packages/cli/src/templates/pi/extensions/trellis-hooks.ts`

要求：
- 删除兜底逻辑
- 删除 monorepo 逻辑
- 缺失 `.trellis` / `workflow.md` / task / `prd.md` 时直接暴露真实状态

### Step 2：实现启动时注入

要求：
- 用 `session_start` 承接 Trellis 启动上下文
- 不迁移 monorepo `spec_scope`
- 不迁移 legacy spec warning

### Step 3：实现每轮与子代理注入

要求：
- 用 `before_agent_start` 注入 `<workflow-state>`
- 按 `research / implement / check` 分流注入 task context
- 不引入新的 fallback prompt

### Step 4：固化 tool_call 硬约束

要求：
- 只保留明确禁止项
- 不做额外推断式拦截
- 不做防御性兜底逻辑

### Step 5：验证

执行：
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`

### Step 6：更新文档

更新：
- `.trellis/spec/cli/backend/platform-integration.md`
- `info.md`

## 当前状态

- 当前处于 `implement`
- 当前未提交改动集中在：
  - `packages/cli/src/templates/pi/extensions/trellis-hooks.ts`
  - `packages/cli/test/templates/pi.test.ts`
  - `packages/cli/test/commands/init.integration.test.ts`
  - `.trellis/spec/cli/backend/platform-integration.md`

## 完成标准

- Pi hooks 覆盖 Trellis 的三类核心语义：启动时 / 每轮输入时 / 子代理上下文注入
- `tool_call` 具备最小必要硬约束
- 不引入兜底
- 不引入 monorepo 逻辑
- lint / typecheck / test 全绿
