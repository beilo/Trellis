# Metrics 采集规范

> **目的**: 确保 AI 在关键节点自动记录量化指标，团队可汇总分析 token 节省率、任务效率、review 质量。

---

## 核心原则

每个 AI session 必须在以下关键节点调用 `metrics.py log` 记录事件。这些数据写入月度 JSONL，由 `metrics.py report` 汇总。

---

## 必须记录的事件

### 1. trellis-check 完成后

每次 `trellis-check` 子代理完成检查后，**必须**调用：

```bash
# 检查通过
python3 .trellis/scripts/metrics.py log check --pass --issues 0

# 检查发现问题
python3 .trellis/scripts/metrics.py log check --fail --issues N
```

- `--pass` / `--fail` 二选一
- `--issues N` 为发现的问题数
- 如果 check 发现问题的次数为 0，`--issues 0`

### 2. Session 结束前

执行 `/trellis:finish-work` 或 session 结束前，**必须**调用：

```bash
python3 .trellis/scripts/metrics.py log session-end \
  --files-changed N   \
  --lines-added N     \
  --lines-removed N
```

- `--files-changed N` 本次 session 变更的文件数
- `--lines-added N` 新增行数
- `--lines-removed N` 删除行数
- 数据可从 `git diff --stat` 获取

### 3. PR 创建后

提交 PR 后，**必须**调用：

```bash
python3 .trellis/scripts/metrics.py log pr-create --pr N
```

- `--pr N` PR 编号

### 4. PR merge 后

PR 被合并后，**必须**调用：

```bash
python3 .trellis/scripts/metrics.py log pr-merge --pr N --review-comments N
```

- `--pr N` PR 编号
- `--review-comments N` review 评论数（0 表示一次通过）

**注意**: `--review-comments` 在 JSONL 中会存储为 `review_comments`（连字符自动转下划线），`report` 命令基于 `review_comments` 字段计算一次通过率。

---

## 事件类型摘要

| 事件 | 触发时机 | 必需参数 |
|------|---------|---------|
| `check` | trellis-check 完成后 | `--pass`/`--fail`, `--issues N` |
| `session-end` | session 结束前 | `--files-changed N`, `--lines-added N`, `--lines-removed N` |
| `pr-create` | PR 创建后 | `--pr N` |
| `pr-merge` | PR merge 后 | `--pr N`, `--review-comments N` |

---

## 报告查看

```bash
# 查看当月报告
python3 .trellis/scripts/metrics.py report

# 查看指定月份
python3 .trellis/scripts/metrics.py report --month 2026-04

# 查看指定开发者
python3 .trellis/scripts/metrics.py report --dev beilo
```

---

## 注意事项

1. 所有 `metrics.py log` 调用自动附加时间戳和开发者名
2. Task 生命周期事件（create/start/finish/archive）由 hook 自动记录，无需手动调用
3. JSONL 文件位于 `.trellis/workspace/{dev}/metrics-{YYYY-MM}.jsonl`
4. `report` 输出含中文，便于团队阅读
