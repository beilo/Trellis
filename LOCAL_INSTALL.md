# Trellis 本地安装指南

本文档介绍如何通过 `install.sh` 和 `update.sh` 两个脚本，从 Git 仓库直接构建并全局安装 Trellis，无需依赖 NPM 远端发布包。

## 适用场景

- **定制分支开发与测试**：你在 `custom/beilo-v0.5-rc` 或其他自定义分支上迭代，需要快速在本地验证 CLI 行为。
- **不想走 NPM 远端**：包尚未发布到 NPM，或者你希望绕过 NPM 注册表，直接从源码构建。
- **离线/内网环境**：已将仓库镜像到内网 Git，只需调整 `REPO_URL` 即可在内网完成安装。
- **多版本并存**：通过 `--dir` 指定不同目录，可以在同一台机器上保留多个 Trellis 版本。

## 前置依赖

两个脚本会自动检测并安装缺少的依赖，但你仍需确保以下工具已就绪：

| 依赖 | 最低版本 | 说明 |
| ---- | -------- | ---- |
| Git | 任意 | 用于 clone 和 pull |
| Node.js | >= 18 | 运行时 |
| npm | 任意（随 Node.js 附带） | 用于全局 link |
| pnpm | 任意（脚本会在缺失时自动安装） | Trellis 使用 pnpm monorepo |

## 快速开始

### 首次安装

```bash
curl -o install.sh https://raw.githubusercontent.com/beilo/Trellis/custom/beilo-v0.5-rc/install.sh && bash install.sh
```

执行后，脚本会自动完成以下步骤：

1. 克隆仓库到 `~/.trellis-local`
2. 安装依赖（`pnpm install --frozen-lockfile`）
3. 构建项目（`pnpm run build`）
4. 通过 `npm link` 将 `trellis` 注册为全局命令

安装完成后，运行 `trellis --version` 验证是否成功。

### 更新已安装版本

```bash
curl -o update.sh https://raw.githubusercontent.com/beilo/Trellis/custom/beilo-v0.5-rc/update.sh && bash update.sh
```

更新脚本会：

1. 拉取远程仓库最新代码
2. 切换到目标分支并执行 `git pull`
3. 重新安装依赖和构建
4. 智能检测全局链接状态：如果 `npm link` 仍然有效则跳过，否则自动重新链接
5. 输出当前版本信息

## 脚本详情

### install.sh

**用途**：首次从零安装 Trellis。

**参数**：

| 参数 | 说明 | 默认值 |
| ---- | ---- | ------ |
| `--branch <分支名>` | 指定要 clone 的分支 | `custom/beilo-v0.5-rc` |
| `--dir <目录>` | 指定 clone 的目标目录 | `~/.trellis-local` |
| `--help` | 显示帮助信息 | - |

**行为要点**：

- 如果目标目录已存在，脚本会**先删除旧目录**，然后重新 clone（浅克隆，`--depth 1`）。
- 使用 `--frozen-lockfile` 安装依赖，确保依赖版本与锁文件一致。
- 安装完成后通过 `npm link` 创建全局符号链接，使 `trellis` 命令在任何目录下可用。

**使用示例**：

```bash
# 默认分支、默认目录
bash install.sh

# 指定自定义分支
bash install.sh --branch feat/my-experiment

# 指定安装目录
bash install.sh --dir /opt/trellis-local
```

**卸载**：

```bash
cd ~/.trellis-local/packages/cli && npm unlink -g
```

然后手动删除 `~/.trellis-local` 目录即可。

### update.sh

**用途**：更新已通过 `install.sh` 安装的 Trellis。

**参数**：

| 参数 | 说明 | 默认值 |
| ---- | ---- | ------ |
| `--branch <分支名>` | 指定要切换/更新的分支 | `custom/beilo-v0.5-rc` |
| `--dir <目录>` | 指定安装目录 | `~/.trellis-local` |
| `--help` | 显示帮助信息 | - |

**行为要点**：

- 要求目标目录已存在且为 Git 仓库，否则报错并提示先运行 `install.sh`。
- 每次都会先 `git fetch`，再 `git checkout` + `git pull`，确保代码与远程同步。
- 全局链接状态检测：若 `npm link` 已断裂（例如你手动执行过 `npm unlink`），脚本会自动重新链接。这比盲目重新 link 更安全。
- 更新完成后打印当前分支、安装目录和版本号，方便确认。

**使用示例**：

```bash
# 更新到默认分支的最新代码
bash update.sh

# 切换到另一个分支并更新
bash update.sh --branch feat/new-feature

# 指定不同的安装目录
bash update.sh --dir /opt/trellis-local
```

## 高级用法

### 内网/离线环境

如果你的环境无法访问 GitHub，可以将仓库镜像到内网 Git 服务，然后修改脚本中的 `REPO_URL` 变量：

```bash
# 下载脚本后编辑
sed -i 's|https://github.com/beilo/Trellis.git|https://git.internal.example.com/trellis.git|' install.sh
bash install.sh
```

### 多版本并存

通过不同的 `--dir` 可以同时保留多个版本：

```bash
# 安装稳定版
bash install.sh --branch main --dir ~/.trellis-stable

# 安装开发版
bash install.sh --branch custom/beilo-v0.5-rc --dir ~/.trellis-dev
```

注意：`npm link` 全局只能指向一个版本。切换时需要在对应目录执行 `npm link` 来覆盖全局命令。

### 作为 CI 流水线的一步

两个脚本都遵循 "出错即停" 原则（`set -euo pipefail`），适合在 CI 中使用：

```bash
bash install.sh --branch "${CI_COMMIT_BRANCH}" --dir /tmp/trellis-ci
trellis --version
trellis some-command --flag
```

## 注意事项

1. **install.sh 会删除已有目录**：如果 `--dir` 指定的目录已存在，脚本会先执行 `rm -rf` 删除。请确保目录中没有需要保留的未提交修改。
2. **update.sh 不会删除目录**：更新脚本只做 `git fetch/pull`，不会清空工作区。如果你有本地修改，`git pull` 可能因冲突失败。
3. **全局命令覆盖**：`npm link` 会在全局 `node_modules` 中创建符号链接。如果你之前通过 `npm install -g trellis` 安装过，本地安装版本会覆盖它。
4. **shell 环境**：脚本使用 `#!/usr/bin/env bash`，需要 Bash 环境。macOS 和 Linux 默认支持。Windows 用户请在 WSL 或 Git Bash 中运行。
5. **Node.js 版本检查**：脚本会检查 Node.js 主版本号是否低于 18，不满足则直接退出。

## FAQ

### Q: 与 `npm install -g trellis` 有什么区别？

A: NPM 全局安装的是已发布的稳定版本。本地安装脚本直接从 Git 仓库的指定分支构建，适合测试未发布的改动或定制分支。

### Q: 更新后版本号没变？

A: 检查你当前所在分支是否与远程同步。可以进入安装目录手动 `git log -1` 查看最新提交。

### Q: 提示 pnpm 未找到但脚本没有自动安装？

A: 脚本使用 `npm install -g pnpm` 安装 pnpm。如果你的 npm 没有全局安装权限（如 EACCES 错误），请先配置 npm 全局路径或使用 nvm。

### Q: 如何彻底卸载？

A:

```bash
# 1. 取消全局链接
cd ~/.trellis-local/packages/cli && npm unlink -g

# 2. 删除安装目录
rm -rf ~/.trellis-local
```

### Q: 可以在同一台机器上为多个用户安装吗？

A: 可以，但 `npm link` 是全局的。建议每个用户在自己的 home 目录下安装（使用默认 `--dir`），或者使用不同的 `--dir` 并在需要时手动切换 `npm link`。
