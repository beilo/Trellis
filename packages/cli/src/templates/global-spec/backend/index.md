# 机器级后端基线规则

> 适用于本机多个 Trellis 项目的后端通用规则。项目级 `.trellis/spec/backend/**` 仍负责记录具体仓库事实。

---

## 概览

这一层只写跨项目通用的后端工程纪律，例如分层边界、接口契约、错误处理、数据库访问、日志和验证要求。

它不记录具体项目的包名、表结构、接口路径、DTO 字段、错误码或部署命令。那些内容必须留在项目级后端 spec 或任务 PRD / info 中。

---

## 加载方式

项目通过符号链接显式选择启用：

```text
.trellis/spec/global -> /Users/am/.trellis/spec
```

后端任务按需在 `implement.jsonl` / `check.jsonl` 同时引用机器级和项目级规则：

```json
{"file": ".trellis/spec/global/backend/index.md", "reason": "机器级全局后端基线规则"}
{"file": ".trellis/spec/backend/index.md", "reason": "当前项目后端规则"}
```

规则优先级：机器级后端基线 < 项目级后端规则 < 任务 PRD / info < 当前会话用户明确指令。

---

## 指南索引

| 指南 | 描述 | 状态 |
|-------|-------------|--------|
| [质量基线](./quality-baseline.md) | 跨项目后端质量、分层、接口、数据库和日志基线 | 已填写 |
| [目录结构](./directory-structure.md) | 项目级目录规则的占位模板，不作为机器级事实 | 模板 |
| [数据库指南](./database-guidelines.md) | 项目级数据库规则的占位模板，不作为机器级事实 | 模板 |
| [错误处理](./error-handling.md) | 项目级错误处理规则的占位模板，不作为机器级事实 | 模板 |
| [质量指南](./quality-guidelines.md) | 旧模板占位；新增任务优先读质量基线 | 模板 |
| [日志指南](./logging-guidelines.md) | 项目级日志规则的占位模板，不作为机器级事实 | 模板 |

---

## 维护边界

- 新增跨项目后端规则时，优先写入 `quality-baseline.md`。
- 只在单个项目成立的规则，不要写到这里。
- 如果项目级规则与本基线冲突，优先相信项目级规则描述的真实代码事实，并在任务 PRD / info 中记录原因。
