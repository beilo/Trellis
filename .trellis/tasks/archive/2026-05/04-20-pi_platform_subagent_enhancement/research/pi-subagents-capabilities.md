# Research: pi-subagents 能力边界（GitHub README 摘要）

## 来源

* GitHub 仓库：`nicobailon/pi-subagents`

## 已确认能力

根据 README，可确认的能力包括：

* 支持 `.chain.md` 链文件，项目级路径是 `.pi/agents/{name}.chain.md`
* 支持链式步骤、并行步骤、异步执行、TUI clarify
* 支持 worktree 隔离并行运行，避免多个 worker 互相覆盖文件
* 支持链变量：`{task}`、`{previous}`、`{chain_dir}`
* 支持 top-level parallel，也支持 chain 内 fan-out / fan-in

## 对 Trellis 规划的意义

### 1. 你的“Pi 不只是再加一个平台”判断是对的

如果只是把 Pi 当成普通平台接入，最多只是多一个 `.pi/agents/` 目录和命令入口，但 Pi 真正独特的是：

* 原生链文件
* 原生并行
* 原生 worktree 隔离
* 原生 clarify / overlay

这些能力明显高于当前 Trellis 在多数平台上的“单个 implement/check/research 子代理 + hook 注入”。

### 2. Execute 阶段最适合先吃到红利

pi-subagents README 里最成熟的例子是：

* `scout -> planner -> worker -> reviewer`
* `scout -> parallel(worker...) -> reviewer`

这和 Trellis 的 Execute / Finish 非常贴合，尤其适合：

* 影响面先侦察
* 多 worker 并行改局部
* reviewer 汇总审查

### 3. Plan 阶段可以增强，但不宜先重写

Pi 的 chain 很适合做 `scout -> planner`，但 Trellis Plan 阶段已经和 `task/`、`prd.md`、`research/`、`implement.jsonl` 严密耦合。

所以首版更合理的做法是：

* 继续保留 Trellis 的 task-first / PRD-first 主流程
* 只让 Pi 在 Plan 阶段补一个“代码侦察 + 选项收敛”能力
* 不要先把整个 Plan 阶段重写成纯 Pi chain

### 4. 不要一开始就抽象跨平台 chain DSL

虽然 pi-subagents 有清晰 chain 语义，但当前 Trellis 其他平台并没有与之等价的原生承载层。

如果一开始就在 Trellis 内部造通用 chain DSL：

* Pi 会是原生执行
* 其他平台只能退化翻译
* 你会先花大量精力处理“如何优雅降级”而不是先把 Pi 做通

因此更合理的是：

* 第一阶段：Pi 平台专属 chain 编排
* 第二阶段：验证稳定后，再抽象公共能力位

## 对实施计划的直接影响

### 建议新增的 phase 验收点

#### Phase 1

* Trellis 能正式生成 `.pi/` 目录
* `trellis update` 能追踪 `.pi` 模板文件

#### Phase 2

* 能生成 `scout/planner/worker/reviewer` 这类 Pi agent 模板
* 至少有 1 条 Execute 链模板能运行

#### Phase 3

* 能验证 `parallel + worktree: true` 的执行链
* reviewer 能消费 parallel 汇总结果

#### Phase 4

* 再决定是否把 chain 能力上升到平台无关抽象
