# Metrics 量化采集系统：文件驱动的开发者指标日志

## Goal

为团队提供基于文件的、零侵入的指标采集机制，让 Trellis 工作流中每个关键节点自动记录事件到 JSONL，月末一键出报告，支撑「token 节省率 / 任务效率 / review 质量」三个量化维度。

## What I already know

* 团队基于 Cursor 平台，无法通过脚本拉取 API 数据
* 指标数据必须记录在文件中（JSONL 追加写入）
* Trellis 已有 `task.py` 生命周期 + `config.yaml` hooks 机制 + `linear_sync.py` hook 参考实现
* `task.json` 已有 `createdAt` / `completedAt`，缺中间态时间戳
* `.cursor/skills/` 和 `.cursor/commands/` 由 trellis update 管理，不应修改
* `.trellis/spec/guides/` 已被 skill 加载，适合放 AI 行为指令
* workspace 按 `{developer}/` 组织，metrics 文件应放在同层

## Assumptions (temporary)

* Cursor 不暴露精确 token 数，session 级 token 需估算或月末手动填
* PR create / merge 事件无法自动触发，需 AI 在 workflow 中按指令补记
- 开发者每人每月一个 metrics 文件即可，不需要按 session 拆分

## Open Questions

* session 级产出数据（lines added/removed, files changed）由 AI 估算还是月末人工填？

## Requirements

### R1: Metrics JSONL 日志格式

文件位置：`.trellis/workspace/{developer}/metrics-{YYYY-MM}.jsonl`

每行一个 JSON 对象，追加写入，不修改历史行。事件类型：

| event | 触发方式 | 必填字段 | 可选字段 |
|-------|---------|---------|---------|
| `task.create` | hook 自动 | `task`, `title` | - |
| `task.start` | hook 自动 | `task` | - |
| `task.check` | AI 按 spec 指令写 | `task`, `pass` (bool), `issues` (int) | - |
| `task.finish` | hook 自动 | `task` | - |
| `task.archive` | hook 自动 | `task` | - |
| `pr.create` | AI 按 spec 指令写 | `task`, `pr` (int) | - |
| `pr.merge` | AI 按 spec 指令写 | `task`, `pr` (int), `review_comments` (int) | - |
| `session.end` | AI 按 spec 指令写 | - | `files_changed`, `lines_added`, `lines_removed`, `tokens_est` |

所有事件共用 `ts` (ISO 8601) 字段。

### R2: Hook 自动记录（metrics_log.py）

仿照 `linear_sync.py` 的模式，新建 `.trellis/scripts/hooks/metrics_log.py`，注册到 `config.yaml` 的 after_create / after_start / after_finish / after_archive hooks。

行为：读取 TASK_JSON_PATH，追加一行 JSONL 到当前开发者的 metrics 文件。

### R3: 手动/半自动记录（metrics.py log）

新建 `.trellis/scripts/metrics.py`，提供：

- `metrics.py log <event-type> [--key value ...]` — 手动/AI 补记事件
- `metrics.py report [--month YYYY-MM] [--dev name]` — 读取 JSONL 输出月度汇总

### R4: AI 行为规范 spec

新建 `.trellis/spec/guides/metrics.md`，内容：

1. `trellis-check` 完成后，必须调用 `metrics.py log check --pass/fail --issues N`
2. session 结束前（finish-work），必须调用 `metrics.py log session-end` 并附 `--files-changed` `--lines-added` `--lines-removed`
3. 创建 PR 后，调用 `metrics.py log pr-create --pr N`
4. PR merge 后，调用 `metrics.py log pr-merge --pr N --review-comments N`

### R5: 月度汇总报告

`metrics.py report` 从 JSONL 读取数据，输出：

```
=== {YYYY-MM} Metrics Report: {developer} ===

任务效率:
  完成任务数: N
  平均耗时: X.X 天 (规划 X.Xd / 实现 X.Xd / review X.Xd)

Review 质量:
  PR 数: N
  一次通过率: XX% (N/N)
  平均 review 评论: X.X
  check 拦截问题: N

产出效率:
  总代码行: +N / -N
  session 数: N
  估算 token: ~XM
  每万 token 产出: X.X 行
```

耗时计算逻辑：
- 规划耗时 = task.start.ts - task.create.ts
- 实现耗时 = task.check.ts - task.start.ts（取第一个 check 事件）
- Review 耗时 = task.archive.ts - 第一个 pr.create.ts（若无 pr 事件，用 task.finish.ts）

## Acceptance Criteria

- [ ] `metrics_log.py` 在 task 生命周期 hook 中正确追加 JSONL
- [ ] `metrics.py log` 能手动补记任意事件类型
- [ ] `metrics.py report` 输出包含三个维度的汇总
- [ ] `config.yaml` 已注册 hooks（仅取消注释 + 加 4 行）
- [ ] `.trellis/spec/guides/metrics.md` 存在且内容完整
- [ ] 不修改任何 `.cursor/` 下的文件
- [ ] 不修改任何现有 `.trellis/scripts/common/` 下的文件

## Definition of Done

- Lint / typecheck 通过（scripts 目录下无语法错误）
- 手动测试 `metrics_log.py` 的 create/start/finish/archive 四个事件
- 手动测试 `metrics.py log check --pass --issues 0`
- 手动测试 `metrics.py report`
- `metrics.md` spec 被读取验证

## Technical Approach

### 文件改动清单（只改 1 个现有文件，其余新建）

1. **修改** `.trellis/config.yaml` — 取消注释 hooks 段 + 注册 4 个 hook 命令
2. **新建** `.trellis/scripts/hooks/metrics_log.py` — hook 脚本，读取 TASK_JSON_PATH + developer，追加 JSONL
3. **新建** `.trellis/scripts/metrics.py` — log 子命令（补记事件）+ report 子命令（汇总）
4. **新建** `.trellis/spec/guides/metrics.md` — AI 行为规范

### metrics_log.py 核心逻辑

```
1. 读 TASK_JSON_PATH → 解析 task.json 拿 task name/title/createdAt
2. 读 .trellis/.developer → 拿 developer name
3. 构造 JSONL 行：{"ts": ISO, "event": "task.create", "task": "05-04-metrics-log", "title": "..."}
4. 追加到 .trellis/workspace/{dev}/metrics-{YYYY-MM}.jsonl
   文件不存在则创建（含目录）
```

### metrics.py report 核心逻辑

```
1. 读取指定月份的 metrics JSONL
2. 按 task 分组，关联 task.create/start/check/finish/archive 事件
3. 计算各阶段耗时
4. 汇总 pr.create/pr.merge 统计 review 质量
5. 汇总 session.end 统计产出效率
6. 格式化输出
```

## Decision (ADR-lite)

**Context**: 需要量化 Trellis 工作流价值，但只能基于 Cursor 平台、只能用文件记录
**Decision**: JSONL 追加日志 + hook 自动写入 + spec 驱动 AI 半自动写入
**Consequences**: hook 触发的事件 100% 自动，AI 写入的事件依赖 spec 规范的执行力；不依赖外部 API；文件可能被 git track（需考虑 .gitignore 或 .trellis/.gitignore_deny）

## Out of Scope

* 精确 token 计数（需 Anthropic API 接入，Cursor 不支持）
* 可视化 dashboard
* 跨团队聚合（MVP 只做单人月度报告）
* 与飞书/Linear 等外部系统集成
* 自动从 `gh api` 拉 PR review 数据（AI 补记即可）

## Technical Notes

* 参考 `linear_sync.py` 的 hook 注册模式（TASK_JSON_PATH 环境变量）
* 参考 `common/paths.py` 的 `get_developer()` / `get_workspace_dir()`
* 参考 `common/io.py` 的 `read_json()`
* `metrics-{YYYY-MM}.jsonl` 文件命名与 `journal-N.md` 同目录
* `config.yaml` hooks 段已有注释模板，取消注释即可
