# Research: Pi 平台接入前的 Trellis 当前架构

## 结论

当前 Trellis 还没有正式的 Pi 平台接入。仓库里的 `.pi/` 更像手工原型，不在 CLI 平台注册和模板跟踪体系内。现有平台抽象已经支持“是否能拉起子代理”和“是否有 hooks”，但还没有“是否支持平台原生编排链 / 多 worker 并行 / 子代理模板扩展位”这些更细能力位。结合用户补充约束，Pi 接入必须建立在 Trellis 既有三代理契约之上，避免 fork 偏离上游。

因此，Pi 首版最合理的切入点不是直接抽象出跨平台 chain DSL，而是：

1. 先把 Pi 纳入正式平台体系
2. 再在 Pi configurator 中额外生成基于现有三代理的子代理模板与编排辅助文件
3. 让 Execute 阶段优先吃到 Pi 的差异化收益

## 代码证据

### 1. 平台注册入口是 AI_TOOLS

文件：`packages/cli/src/types/ai-tools.ts`

* `AITool`、`TemplateDir`、`CliFlag` 都是显式联合类型。
* 每加一个新平台，都要同步补：
  * 类型联合
  * `AI_TOOLS` 注册项
  * `templateDirs` / `configDir` / `cliFlag`
  * `templateContext`
* 当前 `TemplateContext` 只有：
  * `cmdRefPrefix`
  * `executorAI`
  * `userActionLabel`
  * `agentCapable`
  * `hasHooks`

这说明 Pi 如果只做“第 14/15 个平台”，可以直接沿现有模型接入；但如果想表达“原生链式编排能力”，现有 context 字段不够。

### 2. 平台行为分发在 PLATFORM_FUNCTIONS

文件：`packages/cli/src/configurators/index.ts`

* `PLATFORM_FUNCTIONS` 是平台 configure / collectTemplates 的单一分发表。
* `configurePlatform()` 和 `collectPlatformTemplates()` 都从这里走。
* `getConfiguredPlatforms()` 只看 `configDir` 是否存在。

这意味着 Pi 正式接入至少要补：

* `configurePi()`
* `collectPiTemplates()`
* `.pi` 作为 `configDir`
* CLI 入口 `--pi`

### 3. 现有多平台代理本质仍围绕三类 Trellis 角色

文件：

* `packages/cli/src/templates/shared-hooks/inject-subagent-context.py`
* `packages/cli/src/configurators/shared.ts`

关键现状：

* 共享 hook 只认 `trellis-implement` / `trellis-check` / `trellis-research`
* hook 注入的上下文来源仍是：
  * `implement.jsonl`
  * `check.jsonl`
  * `prd.md`
  * `info.md`
* `shared.ts` 还有 pull-based prelude，用来兼容 hook 不足的平台

这说明 Trellis 当前的“多代理”更像“任务角色分工 + 上下文注入”，不是平台无关的任意链路编排系统。

### 4. 共享模板分两层：common 与 platform-specific

文件：`packages/cli/src/configurators/shared.ts`

* `common/commands`
* `common/skills`
* platform-specific 的 `agents/`、`hooks/`、`settings/config`

这对 Pi 很关键：

* 通用 Trellis 技能和命令，不需要为 Pi 全盘重写
* Pi 真正新增的价值应该放在：
  * `.pi/agents/`
  * 可能新增的 `.pi/chains/` / `.pi/commands/`
  * Pi 平台自己的 `settings.json`

### 5. 仓库根目录 `.pi/` 目前是原型，不是 CLI 正式模板

文件：

* `.pi/settings.json`
* `.pi/agents/check.md`
* `.pi/agents/implement.md`
* `.pi/agents/research.md`

现状：

* `.pi/settings.json` 引入了外部 packages：
  * `beilo/pi-subagents`
  * `nicobailon/pi-prompt-template-model`
* agent 定义里直接写了 `skill: trellis-check` / `skill: implement` 等

但仓库 `packages/cli/src/` 中没有任何 `.pi` 平台模板目录或 configurator 引用，说明这套文件现在不会被 `trellis init` / `trellis update` 正式管理。

## 对计划的影响

### 推荐分层

#### 第一层：平台接入 MVP

目标：让 Pi 成为受支持平台

需要动的地方：

* `packages/cli/src/types/ai-tools.ts`
* `packages/cli/src/configurators/index.ts`
* `packages/cli/src/configurators/pi.ts`
* `packages/cli/src/templates/pi/`
* `packages/cli/src/cli/index.ts`
* `packages/cli/src/commands/init.ts`
* 相关测试

#### 第二层：Pi 专属编排增强

目标：不改动所有平台心智模型的前提下，让 Pi 的执行阶段更强

建议优先做：

* 用 Pi chain 编排现有 `trellis-research -> trellis-implement -> trellis-check`，严格复用现有上下文契约
* 如需更贴近 Pi 心智模型，只在链模板层做别名/封装，不修改 Trellis 核心三角色定义
* planner/scout 在 Plan 阶段做增强，但不把 PRD 生成方式推翻重来
* Finish 阶段仍以 reviewer + 最终总结为主

#### 第三层：未来可抽象能力

如果 Pi 跑通且证明长期有价值，再考虑抽象：

* `supportsSubagents`
* `supportsNativeChains`
* `supportsParallelWorkers`

但这层不应先于 Pi MVP 落地。

## 风险点

1. **抽象过早**：先做平台无关 chain DSL，会把大量精力耗在其他平台的“劣化翻译”上，也会放大 fork 偏离上游的风险。
2. **上下文注入假设不成立**：如果 Pi 不能像理想中那样在 spawn 前改 prompt，就必须退回 pull-based prelude。
3. **角色定义漂移**：如果 Pi 新增 `scout/planner/worker/reviewer`，要避免和现有 `trellis-implement/check/research` 语义冲突。
4. **update 体系漏接**：只做 init 不做 collectTemplates，会像过去某些平台一样在 `trellis update` 时漏更新。

## 建议的首版边界

* 正式支持 Pi 平台
* 生成 Pi 所需 settings + agent 模板
* Execute 阶段新增 Pi 专属链式编排
* Plan / Finish 阶段只做轻增强
* 暂不引入跨平台 chain DSL
