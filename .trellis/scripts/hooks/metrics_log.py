#!/usr/bin/env python3
"""Metrics 采集 hook — task 生命周期事件自动追加 JSONL。

在 task.py 的 after_create/after_start/after_finish/after_archive hook 中调用，
自动记录任务生命周期事件到月度 JSONL 文件。

Usage (called automatically by task.py hooks):
    python3 .trellis/scripts/hooks/metrics_log.py create
    python3 .trellis/scripts/hooks/metrics_log.py start
    python3 .trellis/scripts/hooks/metrics_log.py finish
    python3 .trellis/scripts/hooks/metrics_log.py archive

Environment:
    TASK_JSON_PATH  - Absolute path to task.json (set by task.py)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── 公共模块引入 ──────────────────────────────────────────────────────────
# 将 scripts/ 目录加入 sys.path，使 common 包可被 import
# 同时将 common/ 也加入，以便 from paths import ... 等直接导入
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, _SCRIPTS_DIR)
sys.path.insert(0, str(Path(_SCRIPTS_DIR) / "common"))

from paths import get_repo_root, get_developer, get_workspace_dir  # noqa: E402

# 使用 import 而非 from import 避免与 Python 标准库 io 冲突
import common.io as io_utils  # noqa: E402


# ─── 事件映射 ────────────────────────────────────────────────────────────────
# action → event 名称
ACTION_EVENTS = {
    "create": "task.create",
    "start": "task.start",
    "finish": "task.finish",
    "archive": "task.archive",
}


# ─── 辅助函数 ────────────────────────────────────────────────────────────────


def _read_task() -> dict | None:
    """读取 TASK_JSON_PATH 指向的 task.json，失败返回 None。"""
    path = os.environ.get("TASK_JSON_PATH", "")
    if not path:
        print("[metrics_log] TASK_JSON_PATH not set, skipping", file=sys.stderr)
        return None
    return io_utils.read_json(Path(path))


def _metrics_jsonl_path(repo_root: Path, developer: str) -> Path:
    """返回当月的 metrics JSONL 文件路径。

    格式: .trellis/workspace/{dev}/metrics-{YYYY-MM}.jsonl
    """
    workspace = get_workspace_dir(repo_root)
    if workspace:
        base = workspace
    else:
        # fallback: 手动构造路径
        base = repo_root / ".trellis" / "workspace" / developer
    month = datetime.now().strftime("%Y-%m")
    return base / f"metrics-{month}.jsonl"


def _append_jsonl(path: Path, record: dict) -> None:
    """追加一行 JSONL，目录不存在则创建。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─── 各 action 处理 ──────────────────────────────────────────────────────────


def cmd_create() -> None:
    """记录 task.create 事件。"""
    task = _read_task()
    repo_root = get_repo_root()
    developer = get_developer(repo_root)
    if not developer:
        print("[metrics_log] No developer set, skipping", file=sys.stderr)
        return
    task_name = task.get("name", "") if task else ""
    task_title = task.get("title", "") if task else ""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": ACTION_EVENTS["create"],
        "task": task_name,
        "title": task_title,
    }
    jsonl_path = _metrics_jsonl_path(repo_root, developer)
    _append_jsonl(jsonl_path, record)
    print(f"[metrics_log] Logged task.create for {task_name}")


def cmd_start() -> None:
    """记录 task.start 事件。"""
    task = _read_task()
    repo_root = get_repo_root()
    developer = get_developer(repo_root)
    if not developer:
        print("[metrics_log] No developer set, skipping", file=sys.stderr)
        return
    task_name = task.get("name", "") if task else ""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": ACTION_EVENTS["start"],
        "task": task_name,
    }
    jsonl_path = _metrics_jsonl_path(repo_root, developer)
    _append_jsonl(jsonl_path, record)
    print(f"[metrics_log] Logged task.start for {task_name}")


def cmd_finish() -> None:
    """记录 task.finish 事件。"""
    task = _read_task()
    repo_root = get_repo_root()
    developer = get_developer(repo_root)
    if not developer:
        print("[metrics_log] No developer set, skipping", file=sys.stderr)
        return
    task_name = task.get("name", "") if task else ""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": ACTION_EVENTS["finish"],
        "task": task_name,
    }
    jsonl_path = _metrics_jsonl_path(repo_root, developer)
    _append_jsonl(jsonl_path, record)
    print(f"[metrics_log] Logged task.finish for {task_name}")


def cmd_archive() -> None:
    """记录 task.archive 事件。"""
    task = _read_task()
    repo_root = get_repo_root()
    developer = get_developer(repo_root)
    if not developer:
        print("[metrics_log] No developer set, skipping", file=sys.stderr)
        return
    task_name = task.get("name", "") if task else ""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": ACTION_EVENTS["archive"],
        "task": task_name,
    }
    jsonl_path = _metrics_jsonl_path(repo_root, developer)
    _append_jsonl(jsonl_path, record)
    print(f"[metrics_log] Logged task.archive for {task_name}")


# ─── 主入口 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    actions = {
        "create": cmd_create,
        "start": cmd_start,
        "finish": cmd_finish,
        "archive": cmd_archive,
    }
    fn = actions.get(action)
    if fn:
        fn()
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        print(f"Valid actions: {', '.join(actions)}", file=sys.stderr)
        sys.exit(1)
