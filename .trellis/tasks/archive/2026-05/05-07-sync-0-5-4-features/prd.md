# brainstorm: 同步 0.5.4 功能

## Goal

把上游 `v0.5.4` 中对本地分支有价值的功能和修复同步到 `custom/beilo-v0.5-rc`，同时保留本地已经做过的定制能力，例如 Cursor codebase-search、global spec、local install/update 等。

## What I already know

* 当前分支是 `custom/beilo-v0.5-rc`，工作区干净。
* `origin/custom/beilo-v0.5-rc` 与本地 `HEAD` 一致。
* `upstream/main`、`upstream/feat/v0.5`、`v0.5.4` 都指向 `8afc24e`。
* 当前分支相对 `v0.5.4` 是 `15 commits ahead / 64 commits behind`。
* 上游 `v0.5.4` 的核心功能点包括：
  * `c64d158`：修复 `compareVersions` 对带连字符 prerelease 的比较错误，并新增测试。
  * `2c70346`：修复 `trellis-implement` / `trellis-check` 子代理递归 dispatch 自己的问题，并补齐多平台模板和回归测试。
  * `59810ee`：把 `0.5.4` manifest changelog 改成更清晰的用户可读文案。
  * `8afc24e`：发布版本号 bump 到 `0.5.4`。
* 上游 `0.5.4` 之前还包含一批 `0.5.0-rc.3` 到 `0.5.3` 的修复和发布提交，当前分支也尚未完整包含。
* 当前分支有本地定制提交，不能用会覆盖本地能力的无脑 merge：
  * Cursor MCP / codebase-search agent / rules 目录。
  * global spec 模板和 `init/update` 部署。
  * metrics、local install/update 脚本和相关文档。

## Assumptions (temporary)

* 需要保留当前分支已有的本地定制，不接受删除本地新增模板或脚本。
* 如果 cherry-pick 上游提交冲突很大，可以改为手工移植最小功能 patch。

## Open Questions

* 已确认：同步范围按“全量 0.5”，把 `0.5.0` GA 到 `0.5.4` 的上游修复都纳入。

## Requirements (evolving)

* 保留本地 `custom/beilo-v0.5-rc` 的定制能力。
* 同步 `0.5.0` GA 到 `0.5.4` 的上游修复和发布 manifest。
* 同步 `0.5.4` 子代理递归防护：
  * `workflow.md` / 模板 workflow 的 `in_progress` breadcrumb 必须区分主会话默认 dispatch 和子代理自我豁免。
  * 各平台 `trellis-implement` / `trellis-check` agent 模板必须包含递归防护说明。
  * Codex 当前项目级 agent 文件也要与模板行为一致。
* 同步 `compareVersions` 连字符 prerelease 修复：
  * 保留第一个连字符后的完整 prerelease 字符串。
  * 增加或同步相关单元测试。
* 同步 `0.5.4` migration manifest，确保用户运行 `trellis update` 能看到准确 changelog。
* 不引入 `upstream/feat/v0.6.0-beta` 的功能。

## Acceptance Criteria (evolving)

* [ ] 本地定制文件没有被上游删除或回退。
* [ ] 当前分支包含 `0.5.0` GA 到 `0.5.4` 的上游修复行为。
* [ ] `compareVersions("1.0.0-alpha-1", "1.0.0-alpha-2")` 返回正确排序。
* [ ] 所有 platform 的 `trellis-implement` / `trellis-check` 模板有递归防护。
* [ ] `packages/cli/src/migrations/manifests/0.5.4.json` 存在且说明清晰。
* [ ] 相关回归测试通过。
* [ ] lint / typecheck 通过。

## Definition of Done (team quality bar)

* Tests added/updated where behavior changes.
* Lint / typecheck green.
* Specs or workflow docs updated if behavior contract changes.
* Commit plan明确区分功能同步和 Trellis 任务归档/日志。

## Out of Scope (explicit)

* 不同步 `upstream/feat/v0.6.0-beta` 的 `trellis mem`、Auto Runner、TDD 模版等未发布功能。
* 不重构 release 流程。
* 不移除当前分支已有本地定制能力。

## Technical Notes

* `git log --oneline HEAD..v0.5.4` 显示当前分支落后上游 64 个提交。
* `git log --oneline v0.5.4..HEAD` 显示当前分支有 15 个本地提交。
* `git diff --name-status HEAD..v0.5.4` 显示上游全量差异会删除当前分支新增的 Cursor codebase-search、Cursor MCP、global spec 等文件，因此不适合直接全量覆盖。
* Relevant specs:
  * `.trellis/spec/cli/backend/index.md`
  * `.trellis/spec/cli/unit-test/index.md`
