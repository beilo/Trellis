# brainstorm: Pi 平台与子代理编排增强

## Goal

为 Trellis 落地一个最小侵入的 Pi 平台实现，继续复用现有 `trellis-research` / `trellis-implement` / `trellis-check` 三代理语义，但在平台模板层改为 **Pi 直接消费 Pi 原生模板**，不再通过 Cursor 模板做运行时转化。

## What I already know

* 当前任务已从“总体规划”收敛到“修正 Pi 平台实现边界并继续实施”。
* 用户已明确：要在现有 Trellis 基础上对接其既有 3 个代理对象，遵守它们的规则接入 Pi，而不是发明一套新的 Trellis 内核代理模型。
* 用户已明确：由于官方不考虑接入 Pi，fork 需要保持侵入性最小，方便后续持续跟进官方迭代。
* 用户已明确否定 `Cursor -> Pi` 的模板转化 / 兜底思路，要求 Pi 平台直接消费 Pi 模板。
* 当前 Trellis CLI 的平台注册中心在 `packages/cli/src/types/ai-tools.ts`，平台行为分发在 `packages/cli/src/configurators/index.ts`。
* 当前已支持的平台都走 `AI_TOOLS` + `configureXxx()` + `templates/<platform>/` 这一套接入模型。
* 当前 `TemplateContext` 只有 `agentCapable` / `hasHooks` 两类能力位，没有 `supportsSubagents` / `supportsChains` 之类更细粒度编排能力。
* Trellis 已经有“多代理”概念，但它本质上仍是 `trellis-implement` / `trellis-check` / `trellis-research` 三种角色围绕任务上下文做协作，而不是平台无关的声明式链路编排。
* 现有 hook / prelude 机制已经把平台分成两类：
  * hook 可注入子代理上下文的平台
  * hook 不足，只能让子代理自行拉取上下文的平台（pull-based / class-2）
* 仓库根目录此前存在过一个 `.pi/` 原型目录，说明已有 Pi 方向探索，但该原型已清理，不能再作为事实来源或实现依赖。

## Assumptions (temporary)

* 第一阶段目标是“让 Pi 成为 Trellis 的正式平台，并在尽量不改动 Trellis 核心抽象的前提下，在执行阶段体现出明显优于普通单代理平台的体验”，而不是一步做成跨平台通用编排框架。
* 第一版允许 Plan / Finish 仍然部分复用现有 Trellis 任务结构与 spec 注入机制，不强求一开始就引入完整 chain DSL。
* 历史 `.pi/` 原型只能作为背景线索，后续实现必须回到正式模板源，不直接复用 repo 根目录临时文件。
* 现有 Pi 半成品实现里，`packages/cli/src/templates/pi/index.ts` 直接 import Cursor agents 并做 tools 转化；这条路径需要移除。

## Open Questions

* Pi 的子代理启动链路能否在 spawn 前可靠注入 Trellis task context；若不能，需要继续采用和 Codex/Gemini 类似的 pull-based prelude。

## Requirements (evolving)

* 首版范围锁定为：只增强 Execute 阶段的 Pi 原生 chain 编排；Plan / Finish 继续复用现有 Trellis 流程。
* Trellis 能把 Pi 识别为正式支持的平台，接入 `init` / `update` / 模板追踪。
* Pi 平台接入不能只复制 Cursor/Codex 模式，必须明确哪些阶段使用 Pi 原生子代理能力。
* Pi 平台的 agent 模板必须来自 `packages/cli/src/templates/pi/agents/*.md`，不能在运行时从 Cursor 模板做转化。
* `packages/cli/src/templates/pi/index.ts` 不能再依赖 `../cursor/index.js`。
* 方案必须区分：
  * 平台接入层（AI_TOOLS / configurator / templates / CLI flags）
  * 编排能力层（scout/planner/worker/reviewer 等角色与链路）
  * 任务上下文注入层（prd / jsonl / info / research）
* 首版必须给出清晰边界，避免一开始就引入过度抽象的跨平台 chain DSL。
* 首版应严格复用现有 `trellis-implement` / `trellis-check` / `trellis-research` 任务上下文契约，Pi chain 只做平台侧编排包装，不新增 Trellis 核心代理类型。
* 方案必须最小化 fork diff，优先通过新增平台目录、平台 configurator、平台模板解决，而不是修改 workflow 核心语义。

## Acceptance Criteria (evolving)

* [x] 有明确推荐策略，能解释为什么不是 A，也为什么暂时不做完整 C。
* [x] 有分阶段实施计划，至少覆盖平台注册、模板生成、上下文注入、执行编排、验证与迁移。
* [x] 明确列出涉及的代码入口和新增目录，能指导后续真正实现。
* [x] 明确首版风险点与待验证项。
* [x] Pi 模板源改成 `src/templates/pi/agents/*.md`，不再存在 `Cursor -> Pi` 转化逻辑。
* [x] `trellis init --pi` 生成的 `.pi/agents/*.md` 使用 Pi 原生 tools 语法。
* [x] 测试覆盖 Pi 原生模板读取与 init/update 结果。

## Definition of Done (team quality bar)

* 方案边界清楚，可直接转成实施任务
* 关键技术假设有源码依据
* 后续实现时能据此拆分 phase / backlog
* 文档沉淀到任务目录，避免只留在对话里

## Out of Scope (explicit)

* 本轮不承诺所有平台统一支持 Pi 级别的多代理编排
* 本轮不设计完整的跨平台声明式 chain DSL 语法

## Confirmed Decisions

* 适配策略：严格复用 Trellis 现有三代理，不新增 Trellis 核心代理类型。
* fork 策略：以最小侵入为原则，优先新增 Pi 平台适配层，不改上游 workflow 核心语义。
* MVP 范围：首版只增强 Execute，编排 `trellis-research -> trellis-implement -> trellis-check`。
* 工作区策略：当前规划不再依赖 repo 内历史 stash、未跟踪 `.pi/` 原型或其他本地实验文件，只以上游源码和任务文档为准。
* 模板策略：Pi 平台直接消费 Pi 原生 agent 模板，不做 Cursor 模板转化或任何兜底映射。

## Technical Notes

* 平台注册：`packages/cli/src/types/ai-tools.ts`
* 平台行为分发与 update 模板收集：`packages/cli/src/configurators/index.ts`
* 共享模板能力与 pull-based prelude：`packages/cli/src/configurators/shared.ts`
* 现有 hook 注入：`packages/cli/src/templates/shared-hooks/inject-subagent-context.py`
* 示例平台实现：`packages/cli/src/configurators/cursor.ts`、`packages/cli/src/configurators/codex.ts`
* Pi 模板入口：`packages/cli/src/templates/pi/index.ts`
* Pi agent 模板目录：`packages/cli/src/templates/pi/agents/`
* 历史 Pi 原型已清理，不再作为事实来源；相关结论见：`research/workspace-hygiene-and-fork-boundary.md`
* 工作区清理记录：`research/workspace-hygiene-and-fork-boundary.md`
