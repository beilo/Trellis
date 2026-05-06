# 机器级前端基线规则

> 适用于本机多个 Trellis 项目的前端通用规则。项目级 `.trellis/spec/frontend/**` 仍负责记录具体仓库事实。

---

## 概览

这一层只写跨项目通用的前端工程纪律，例如组件边界、Hook 设计、状态管理、类型安全和验证要求。

它不记录具体项目的目录结构、业务组件、接口字段、UI 细节或历史兼容逻辑。那些内容必须留在项目级前端 spec 或任务 PRD / info 中。

---

## 加载方式

项目通过符号链接显式选择启用：

```text
.trellis/spec/global -> /Users/am/.trellis/spec
```

前端任务按需在 `implement.jsonl` / `check.jsonl` 同时引用机器级和项目级规则：

```json
{"file": ".trellis/spec/global/frontend/index.md", "reason": "机器级全局前端基线规则"}
{"file": ".trellis/spec/frontend/index.md", "reason": "当前项目前端规则"}
```

规则优先级：机器级前端基线 < 项目级前端规则 < 任务 PRD / info < 当前会话用户明确指令。

---

## 指南索引

| 指南 | 描述 | 状态 |
|-------|-------------|--------|
| [质量基线](./quality-baseline.md) | 跨项目前端质量、组件、Hook、状态和类型基线 | 已填写 |
| [目录结构](./directory-structure.md) | 项目级目录规则的占位模板，不作为机器级事实 | 模板 |
| [组件指南](./component-guidelines.md) | 项目级组件规则的占位模板，不作为机器级事实 | 模板 |
| [Hook 指南](./hook-guidelines.md) | 项目级 Hook 规则的占位模板，不作为机器级事实 | 模板 |
| [状态管理](./state-management.md) | 项目级状态管理规则的占位模板，不作为机器级事实 | 模板 |
| [质量指南](./quality-guidelines.md) | 旧模板占位；新增任务优先读质量基线 | 模板 |
| [类型安全](./type-safety.md) | 项目级类型规则的占位模板，不作为机器级事实 | 模板 |

---

## 维护边界

- 新增跨项目前端规则时，优先写入 `quality-baseline.md`。
- 只在单个项目成立的规则，不要写到这里。
- 如果项目级规则与本基线冲突，优先相信项目级规则描述的真实代码事实，并在任务 PRD / info 中记录原因。
