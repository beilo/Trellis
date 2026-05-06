# CLI 全局 spec 部署（trellis init / trellis update）

## Goal

在 `trellis init` 和 `trellis update` 中自动部署全局规则到 `~/.trellis/spec/`，使同事无需手动配置即可获得跨项目通用的工程纪律规则。

## Requirements

* 全局 spec 模板放入 `packages/cli/src/templates/global-spec/`，随仓库版本管理
* `trellis init` 时部署全局 spec 到 `~/.trellis/spec/`（与项目级模板部署一起完成）
* `trellis update` 时同步更新 `~/.trellis/spec/`（用户未修改的文件更新，已修改的保留）
* 用户手动修改过的文件不被覆盖

## Acceptance Criteria

* [ ] `trellis init --cursor` 后 `~/.trellis/spec/` 存在且内容正确
* [ ] `trellis update` 后 `~/.trellis/spec/` 与模板同步
* [ ] 用户修改过的文件不被 update 覆盖
* [ ] 幂等：重复运行不出错
* [ ] tsc --noEmit 通过，eslint 通过

## Definition of Done

* Lint / typecheck 通过
* 幂等运行不出错

## Decision (ADR-lite)

**Context**: 全局 spec 需要随 Trellis 版本分发给所有用户，部署目标在用户主目录 `~/.trellis/spec/`，不同于项目级模板部署到项目目录
**Decision**: 模板放在 `packages/cli/src/templates/global-spec/`，CLI 的 init/update 流程中新增全局 spec 部署步骤。不修改 install.sh/update.sh，全局 spec 部署走 CLI 路径
**Consequences**: 用户需要跑 `trellis init` 或 `trellis update` 才能获得全局 spec，install.sh/update.sh 只负责 CLI 安装不负责 spec 部署

## Out of Scope

* install.sh / update.sh 修改（不需要）
* 全局 spec 内容本身的更新/维护
* CLI 新增独立命令（如 `trellis deploy-global-spec`）

## Technical Notes

* 当前全局 spec 位于 `~/.trellis/spec/`：backend/ (7), frontend/ (7), guides/ (6)
* 模板需从 `~/.trellis/spec/` 复制到 `packages/cli/src/templates/global-spec/` 作为源
* CLI template 机制：`createTemplateReader(import.meta.url)` 读取模板目录，`getConfig()` 读取文件
* 全局 spec 部署路径 `~/.trellis/spec/` 需要在 CLI 中用 `os.homedir()` 解析
* `trellis init` 入口：`packages/cli/src/commands/init.ts`
* `trellis update` 入口：`packages/cli/src/commands/update.ts`
* 配置器注册：`packages/cli/src/configurators/index.ts`
