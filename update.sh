#!/usr/bin/env bash
# 一键更新 Trellis（本地安装版本）
# 用法: bash update.sh
# 可选参数: --branch <分支名>  指定要切换/更新的分支（默认 custom/beilo-v0.5-rc）
#          --dir <目录>       指定安装目录（默认 ~/.trellis-local）
#          --help             显示帮助信息
set -euo pipefail

REPO_URL="https://github.com/beilo/Trellis.git"
DEFAULT_BRANCH="custom/beilo-v0.5-rc"
DEFAULT_DIR="$HOME/.trellis-local"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { printf "${GREEN}[INFO]${NC} %s\n" "$*"; }
log_warn()  { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }
log_error() { printf "${RED}[ERROR]${NC} %s\n" "$*"; }
log_step()  { printf "${CYAN}==>${NC} %s\n" "$*"; }

usage() {
  cat <<EOF
用法: bash update.sh [选项]

一键拉取最新代码、重新构建并验证 Trellis（本地版本）。

选项:
  --branch <分支>   指定要更新到的分支（默认: ${DEFAULT_BRANCH}）
  --dir <目录>      指定安装目录（默认: ${DEFAULT_DIR}）
  --help            显示此帮助信息

示例:
  bash update.sh
  bash update.sh --branch custom/my-branch
  bash update.sh --dir /opt/trellis-local
EOF
  exit 0
}

# 解析参数
BRANCH="${DEFAULT_BRANCH}"
INSTALL_DIR="${DEFAULT_DIR}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch) BRANCH="$2"; shift 2 ;;
    --dir)    INSTALL_DIR="$2"; shift 2 ;;
    --help)   usage ;;
    *)        log_error "未知参数: $1"; echo; usage ;;
  esac
done

echo
echo "========================================"
echo "  Trellis 更新脚本"
echo "========================================"
echo
echo "  安装目录: ${INSTALL_DIR}"
echo "  目标分支: ${BRANCH}"
echo

# 1. 检查安装目录是否存在
if [[ ! -d "${INSTALL_DIR}" ]]; then
  log_error "安装目录 ${INSTALL_DIR} 不存在。"
  echo
  echo "  请先运行 install.sh 进行安装："
  echo "    bash install.sh"
  exit 1
fi

# 检查是否是 git 仓库
if [[ ! -d "${INSTALL_DIR}/.git" ]]; then
  log_error "${INSTALL_DIR} 不是一个 git 仓库，无法更新。"
  echo "  请先运行 install.sh 重新安装。"
  exit 1
fi

cd "${INSTALL_DIR}"

# 检查依赖
for cmd in git node npm; do
  if ! command -v "$cmd" &>/dev/null; then
    log_error "缺少依赖: ${cmd}，请先安装。"
    exit 1
  fi
done

# 检查 pnpm
if ! command -v pnpm &>/dev/null; then
  log_warn "未检测到 pnpm，正在通过 npm 安装..."
  npm install -g pnpm
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [[ "${NODE_VERSION}" -lt 18 ]]; then
  log_error "Node.js 版本过低 (当前: $(node -v))，需要 >= 18"
  exit 1
fi

echo

# 2. 拉取最新代码
log_step "拉取远程仓库..."
git fetch origin

# 3. 切换到目标分支并拉取
log_step "切换到分支 ${BRANCH}..."
git checkout "${BRANCH}"
log_step "拉取分支 ${BRANCH} 最新代码..."
git pull origin "${BRANCH}"

cd "${INSTALL_DIR}/packages/cli"

# 4. 安装/更新依赖
log_step "安装依赖 (pnpm install)..."
pnpm install --frozen-lockfile

# 5. 重新构建
log_step "构建项目..."
pnpm run build

# 6. 检查 npm link 是否还存在，断了则重新链接
log_step "检查全局链接状态..."
# npm ls -g 返回非零时可能表示包不存在或链接断裂
if npm ls -g --depth=0 trellis &>/dev/null; then
  log_info "全局链接正常，无需重新链接。"
else
  log_warn "全局链接已失效，正在重新建立..."
  npm link
fi

# 7. 验证
echo
log_step "验证安装..."
TRELLIS_VERSION=$(trellis --version 2>/dev/null || echo "未知")
log_info "Trellis 版本: ${TRELLIS_VERSION}"

echo
log_info "更新完成!"
echo
echo "  当前分支: ${BRANCH}"
echo "  安装目录: ${INSTALL_DIR}"
echo "  版本信息: ${TRELLIS_VERSION}"
echo