#!/usr/bin/env bash
# 一键本地安装 Trellis（自定义分支版本）
# 用法: curl -o install.sh https://raw.githubusercontent.com/beilo/Trellis/custom/beilo-v0.5-rc/install.sh && bash install.sh
# 可选参数: --branch <分支名>  指定要安装的分支（默认 custom/beilo-v0.5-rc）
#          --dir <目录>       指定 clone 目标目录（默认 ~/.trellis-local）
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
用法: bash install.sh [选项]

一键从 Git 仓库 clone、构建并全局安装 Trellis（本地版本，不走 NPM 远端）。

选项:
  --branch <分支>   指定要安装的分支（默认: ${DEFAULT_BRANCH}）
  --dir <目录>      指定 clone 目标目录（默认: ${DEFAULT_DIR}）
  --help            显示此帮助信息

示例:
  bash install.sh
  bash install.sh --branch custom/my-branch
  bash install.sh --dir /opt/trellis-local
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
echo "  Trellis 本地安装脚本"
echo "========================================"
echo
echo "  仓库:     ${REPO_URL}"
echo "  分支:     ${BRANCH}"
echo "  安装目录: ${INSTALL_DIR}"
echo

# 检查依赖
for cmd in git node npm; do
  if ! command -v "$cmd" &>/dev/null; then
    log_error "缺少依赖: ${cmd}，请先安装。"
    exit 1
  fi
done

# 检查 pnpm（Trellis 是 pnpm monorepo）
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

# 清理旧目录
if [[ -d "${INSTALL_DIR}" ]]; then
  log_warn "目录 ${INSTALL_DIR} 已存在，正在删除..."
  rm -rf "${INSTALL_DIR}"
fi

# Clone
log_step "克隆仓库..."
git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${INSTALL_DIR}"

cd "${INSTALL_DIR}/packages/cli"

# 安装依赖
log_step "安装依赖 (pnpm install)..."
pnpm install --frozen-lockfile

# 构建
log_step "构建项目..."
pnpm run build

# 全局 link
log_step "全局链接 (npm link)..."
npm link

echo
log_info "安装完成!"
echo
echo "  验证安装: trellis --version"
echo "  卸载方式: cd ${INSTALL_DIR}/packages/cli && npm unlink -g"
echo "  更新方式: 重新运行此脚本即可"
echo
