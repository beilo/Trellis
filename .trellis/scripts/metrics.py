#!/usr/bin/env python3
"""Metrics 采集与报告脚本。

支持手动记录事件和汇总月度报告。

Usage:
    # 手动记录事件（补记）
    python3 .trellis/scripts/metrics.py log <event-type> [--key value ...]
    python3 .trellis/scripts/metrics.py log check --pass --issues 0
    python3 .trellis/scripts/metrics.py log session-end --files-changed 3 --lines-added 50 --lines-removed 10
    python3 .trellis/scripts/metrics.py log pr-create --pr 42
    python3 .trellis/scripts/metrics.py log pr-merge --pr 42 --review-comments 2

    # 汇总月度报告
    python3 .trellis/scripts/metrics.py report [--month YYYY-MM] [--dev name]
    python3 .trellis/scripts/metrics.py report
    python3 .trellis/scripts/metrics.py report --month 2026-04
    python3 .trellis/scripts/metrics.py report --dev beilo
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── 公共模块引入 ──────────────────────────────────────────────────────────
# 将 scripts/ 目录加入 sys.path，使 common 包可被 import
# 同时将 common/ 也加入，以便 from paths import ... 等直接导入
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
sys.path.insert(0, _SCRIPTS_DIR)
sys.path.insert(0, str(Path(_SCRIPTS_DIR) / "common"))

from paths import get_repo_root, get_developer, get_workspace_dir  # noqa: E402
from log import Colors, colored  # noqa: E402


# ─── JSONL 读写 ──────────────────────────────────────────────────────────────


def _metrics_jsonl_path(repo_root: Path, developer: str, month: str) -> Path:
    """返回指定月份的 metrics JSONL 文件路径。"""
    workspace = get_workspace_dir(repo_root)
    if workspace:
        base = workspace
    else:
        # fallback: 手动构造路径
        base = repo_root / ".trellis" / "workspace" / developer
    return base / f"metrics-{month}.jsonl"


def _read_jsonl(path: Path) -> list[dict]:
    """读取 JSONL 文件，逐行解析，跳过格式错误行。"""
    if not path.is_file():
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print(
                    colored(f"[WARN] 跳过格式错误行 {line_no}: {line[:60]}", Colors.YELLOW),
                    file=sys.stderr,
                )
    return records


def _append_jsonl(path: Path, record: dict) -> None:
    """追加一行 JSONL，目录不存在则创建。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ─── log 子命令 ──────────────────────────────────────────────────────────────


def _parse_key_value_args(raw_args: list[str]) -> dict:
    """解析命令行中任意 --key value 对为 dict。

    支持:
    - --key value → {"key": value}，值尝试转为 int/float，否则保留字符串
    - --key (无 value) → {"key": true}，作为布尔标志

    Args:
        raw_args: parse_known_args 返回的未知参数列表

    Returns:
        解析后的键值对字典
    """
    result: dict = {}
    skip_next = False
    for i, arg in enumerate(raw_args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("--"):
            key = arg[2:].replace("-", "_")  # --files-changed → files_changed
            # 检查下一个参数是否是值（不以 -- 开头）
            if i + 1 < len(raw_args) and not raw_args[i + 1].startswith("--"):
                val = raw_args[i + 1]
                skip_next = True
                # 尝试转为数字，保持类型自然
                try:
                    result[key] = int(val)
                except ValueError:
                    try:
                        result[key] = float(val)
                    except ValueError:
                        result[key] = val
            else:
                # 无值则作为布尔 true
                result[key] = True
    return result


def cmd_log(args: argparse.Namespace, extra: list[str]) -> int:
    """记录自定义事件到 JSONL。

    接受任意 --key value 对，自动加 ts 和 developer。额外参数通过 parse_known_args 的 extra 传入。
    """
    event_type = args.event_type
    if not event_type:
        print(colored("Error: event type required", Colors.RED), file=sys.stderr)
        return 1

    repo_root = get_repo_root()
    developer = args.dev or get_developer(repo_root)
    if not developer:
        print(colored("Error: No developer set. Run init_developer.py first", Colors.RED), file=sys.stderr)
        return 1

    # 构造记录：自动加 ts + event，其余由 --key value 传入
    record: dict = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
    }

    # --pass / --fail 快捷处理：--fail 同时设置 pass=false
    if "--fail" in extra:
        record["pass"] = False
    elif "--pass" in extra:
        record["pass"] = True
    # 从 extra 中移除 --pass/--fail，避免 _parse_key_value_args 重复处理
    filtered_extra = [a for a in extra if a not in ("--pass", "--fail")]

    record.update(_parse_key_value_args(filtered_extra))

    month = datetime.now().strftime("%Y-%m")
    jsonl_path = _metrics_jsonl_path(repo_root, developer, month)
    _append_jsonl(jsonl_path, record)
    print(colored(f"[OK] Logged {event_type} → {jsonl_path.name}", Colors.GREEN))
    return 0


# ─── report 子命令 ───────────────────────────────────────────────────────────


def _parse_ts(ts_str: str) -> datetime | None:
    """解析 ISO 时间戳，失败返回 None。"""
    try:
        # 兼容带 Z 和不带 Z 的格式
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None


def _seconds_to_days(seconds: float) -> str:
    """将秒数转为易读的天数（保留 1 位小数）。"""
    days = seconds / 86400
    if days < 1:
        return f"{days:.1f}天"
    return f"{days:.1f}天"


def _first_ts(records: list[dict]) -> datetime | None:
    """取事件列表中最早的时间戳。"""
    for r in sorted(records, key=lambda x: x.get("ts", "")):
        ts = _parse_ts(r.get("ts", ""))
        if ts:
            return ts
    return None


def cmd_report(args: argparse.Namespace) -> int:
    """汇总月度 metrics 报告。"""
    repo_root = get_repo_root()
    developer = args.dev or get_developer(repo_root)
    if not developer:
        print(colored("Error: No developer set. Run init_developer.py first", Colors.RED), file=sys.stderr)
        return 1

    month = args.month or datetime.now().strftime("%Y-%m")
    jsonl_path = _metrics_jsonl_path(repo_root, developer, month)
    records = _read_jsonl(jsonl_path)

    if not records:
        print(colored(f"无 {month} 的 metrics 数据 ({jsonl_path.name})", Colors.YELLOW))
        return 0

    # ── 按 task 分组 ─────────────────────────────────────────────────────────
    tasks: dict[str, dict[str, list[dict]]] = {}  # task_name → {event_type: [records]}
    for r in records:
        task_name = r.get("task", "")
        event = r.get("event", "")
        if not task_name:
            continue
        if task_name not in tasks:
            tasks[task_name] = {}
        if event not in tasks[task_name]:
            tasks[task_name][event] = []
        tasks[task_name][event].append(r)

    # ── 输出报告 ────────────────────────────────────────────────────────────
    print(colored(f"\n=== Metrics 月度报告: {month} ({developer}) ===\n", Colors.BLUE))

    # 1. 任务阶段耗时
    print(colored("── 任务耗时 ──", Colors.CYAN))
    for task_name, events in sorted(tasks.items()):
        create_ts = _first_ts(events.get("task.create", []))
        start_ts = _first_ts(events.get("task.start", []))
        check_events = events.get("check", [])
        finish_ts = _first_ts(events.get("task.finish", []))
        archive_ts = _first_ts(events.get("task.archive", []))
        pr_create_events = events.get("pr-create", [])

        # 取 task.create 的 title（若有）
        title = ""
        create_records = events.get("task.create", [])
        if create_records:
            title = create_records[0].get("title", "")

        label = f"{task_name}"
        if title:
            label += f" ({title})"

        parts = []
        # 规划 = task.start.ts - task.create.ts
        if create_ts and start_ts:
            plan_sec = (start_ts - create_ts).total_seconds()
            parts.append(f"规划: {_seconds_to_days(plan_sec)}")

        # 实现 = 首个 check.ts - task.start.ts
        first_check_ts = _first_ts(check_events)
        if start_ts and first_check_ts:
            impl_sec = (first_check_ts - start_ts).total_seconds()
            parts.append(f"实现: {_seconds_to_days(impl_sec)}")

        # Review = archive.ts - 首个 pr-create.ts（若无 pr，用 finish.ts）
        if archive_ts:
            review_base = _first_ts(pr_create_events) or finish_ts
            if review_base:
                review_sec = (archive_ts - review_base).total_seconds()
                parts.append(f"Review: {_seconds_to_days(review_sec)}")

        if parts:
            print(f"  {label}")
            print(f"    {', '.join(parts)}")
        else:
            print(f"  {label} (无耗时数据)")

    # 2. PR 统计
    print(colored("\n── PR 统计 ──", Colors.CYAN))
    all_pr_creates = [r for r in records if r.get("event") == "pr-create"]
    all_pr_merges = [r for r in records if r.get("event") == "pr-merge"]
    if all_pr_creates or all_pr_merges:
        pr_count = len(all_pr_creates)
        # 一次通过率：merge 时 review_comments == 0 的比例
        merge_with_comments = [
            r for r in all_pr_merges
            if r.get("review_comments", 0) == 0
        ]
        one_pass_rate = len(merge_with_comments) / len(all_pr_merges) * 100 if all_pr_merges else 0
        avg_comments = sum(r.get("review_comments", 0) for r in all_pr_merges) / len(all_pr_merges) if all_pr_merges else 0
        print(f"  PR 数: {pr_count}")
        if all_pr_merges:
            print(f"  一次通过率: {one_pass_rate:.0f}% ({len(merge_with_comments)}/{len(all_pr_merges)})")
            print(f"  平均 review 评论: {avg_comments:.1f}")
    else:
        print("  (无 PR 数据)")

    # 3. Session 统计
    print(colored("\n── Session 统计 ──", Colors.CYAN))
    session_ends = [r for r in records if r.get("event") == "session-end"]
    if session_ends:
        total_lines = sum(r.get("lines_added", 0) + r.get("lines_removed", 0) for r in session_ends)
        total_files = sum(r.get("files_changed", 0) for r in session_ends)
        session_count = len(session_ends)
        # 估算 token：假设每 session 约 1 万 token
        est_tokens = session_count * 10000
        per_10k_output = total_lines / (est_tokens / 10000) if est_tokens > 0 else 0
        print(f"  Session 数: {session_count}")
        print(f"  总代码行 (增+删): {total_lines}")
        print(f"  总文件变更: {total_files}")
        print(f"  估算 token: {est_tokens:,}")
        print(f"  每万 token 产出: {per_10k_output:.1f} 行")
    else:
        print("  (无 session-end 数据)")

    # 4. Check 统计
    print(colored("\n── Check 统计 ──", Colors.CYAN))
    checks = [r for r in records if r.get("event") == "check"]
    if checks:
        pass_count = sum(1 for c in checks if c.get("pass") is True)
        fail_count = sum(1 for c in checks if c.get("pass") is False)
        total_issues = sum(c.get("issues", 0) for c in checks)
        print(f"  通过: {pass_count}, 失败: {fail_count}")
        print(f"  总问题数: {total_issues}")
    else:
        print("  (无 check 数据)")

    print()
    return 0


# ─── 主入口 ─────────────────────────────────────────────────────────────────


def _parse_log_args(raw_args: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """解析 log 子命令的参数，返回 (known_args, unknown_args)。

    先解析 event_type 和 --dev，其余 --key value 由 unknown_args 返回。
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("event_type", nargs="?", help="事件类型")
    parser.add_argument("--dev", help="开发者名称 (默认从 .developer 读取)")
    return parser.parse_known_args(raw_args)


def main() -> int:
    # 先用最小 parser 判断子命令
    if len(sys.argv) < 2:
        # 打印完整帮助
        _print_full_help()
        return 1

    subcommand = sys.argv[1]

    if subcommand == "log":
        # log 子命令：使用 parse_known_args 支持任意 --key value
        known, extra = _parse_log_args(sys.argv[2:])
        return cmd_log(known, extra)

    elif subcommand == "report":
        # report 子命令：标准 argparse
        parser = argparse.ArgumentParser(
            description="Metrics 月度报告",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("--month", help="月份 YYYY-MM (默认当月)")
        parser.add_argument("--dev", help="开发者名称 (默认从 .developer 读取)")
        args = parser.parse_args(sys.argv[2:])
        return cmd_report(args)

    elif subcommand in ("-h", "--help"):
        _print_full_help()
        return 0

    else:
        print(colored(f"Error: 未知子命令 '{subcommand}'", Colors.RED), file=sys.stderr)
        _print_full_help()
        return 1


def _print_full_help() -> None:
    """打印完整帮助。"""
    print("""Metrics 采集与报告

Usage:
  python3 .trellis/scripts/metrics.py log <event-type> [--key value ...]
  python3 .trellis/scripts/metrics.py report [--month YYYY-MM] [--dev name]

示例:
  # 记录 check 事件
  python3 .trellis/scripts/metrics.py log check --pass --issues 0
  python3 .trellis/scripts/metrics.py log check --fail --issues 3

  # 记录 session 结束
  python3 .trellis/scripts/metrics.py log session-end --files-changed 5 --lines-added 100 --lines-removed 20

  # 记录 PR 事件
  python3 .trellis/scripts/metrics.py log pr-create --pr 42
  python3 .trellis/scripts/metrics.py log pr-merge --pr 42 --review-comments 2

  # 查看当月报告
  python3 .trellis/scripts/metrics.py report

  # 查看指定月份
  python3 .trellis/scripts/metrics.py report --month 2026-04
  python3 .trellis/scripts/metrics.py report --dev beilo
""")


if __name__ == "__main__":
    sys.exit(main())
