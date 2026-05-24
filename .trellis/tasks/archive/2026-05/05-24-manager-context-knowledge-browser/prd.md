# Manager 下一版 UI：Context 与知识库浏览

## Goal

让 Trellis Manager 在项目中心内只读浏览任务级 context 文件，以及项目级 `.trellis/spec` / `.trellis/workspace` 知识资产，减少用户必须跳回编辑器或 Finder 查文件的次数。

本 worktree 已经包含大部分实现，本任务只补齐当前验收缺口并完成验证、记录和提交。

## Requirements

- 在任务详情中提供 `Context` 子 Tab，列出任务目录内的 `research.jsonl`、`implement.jsonl`、`check.jsonl`、`debug.jsonl` 与 `research/*.md`。
- JSONL 文件按分页读取并渲染为可展开记录，摘要优先展示 `ts` / `event` / `summary` 等字段，展开后可查看原始 JSON。
- Markdown context、spec、journal 文件复用 `MarkdownViewer` 预览。
- 在项目 Tab 增加 `知识库` 子 Tab，使用 master-detail 布局浏览 `.trellis/spec` 和 `.trellis/workspace`。
- 预览区必须显示相对 `.trellis/` 的可见路径，帮助用户确认当前文件位置。
- 项目切换时重置知识库文件树 selection。
- 从看板跳进任务详情时默认进入 `Context` Tab。
- 所有文件读取必须经后端 SafeFileReader 限制在项目 `.trellis/` 内。
- 无 `.trellis` 的项目显示初始化引导，不触发文件读取。

## Acceptance Criteria

- [x] active task 可浏览 `implement.jsonl` 各行。
- [x] 可打开并渲染 `.trellis/spec/guides/index.md`。
- [x] 可浏览 `.trellis/workspace/{dev}/journal-*.md`。
- [x] 路径穿越攻击被后端拒绝。
- [x] 无 `.trellis` 项目显示 init 引导。
- [x] Context 和知识库预览区显示相对 `.trellis/` 的路径 breadcrumb。

## Notes

- 非目标：编辑保存、全文搜索、wiki 式 cross-link 跳转。
- 既有脏文件：`.trellis/scripts/common/__pycache__/*.pyc` 与本 issue 无关，不纳入提交。
- 验证：`python3 apps/trellis-manager-desktop/tests/test_file_reader.py`、`pnpm --dir apps/trellis-manager-desktop/frontend lint`、`pnpm --dir apps/trellis-manager-desktop/frontend build` 均通过。
