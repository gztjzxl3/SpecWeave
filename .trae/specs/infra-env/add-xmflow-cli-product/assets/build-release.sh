#!/usr/bin/env bash
# ==============================================================================
# build-release.sh — 构建 xmflow 客户发布镜像（标准版 / torch CPU 版）
#
# 前置：
#   1. localhost/native-dev:nuitka-4.2.2-hotfix 已构建（Stage 0 wheelhouse）
#   2. workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl 已存在
#   3. 使用 /usr/local/bin/podman（root wrapper，默认 runtime crun130）
#
# 用法：
#   bash build-release.sh standard   # 仅 caffe/onnx，tag 1.2.1
#   bash build-release.sh torch      # 追加 CPU torch，tag 1.2.1-torch
#   bash build-release.sh all        # 两者都构
#
# 网络：Stage 0 pip download 走 aliyun（宿主 download.pytorch.org 不可达）。
# ==============================================================================
set -euo pipefail

PODMAN=${PODMAN:-/usr/local/bin/podman}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$(cd "${SCRIPT_DIR}/../../../workspace/dist" && pwd)"
WHL="xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl"
BUILDER_IMAGE="localhost/native-dev:nuitka-4.2.2-hotfix"
VERSION="1.2.1"
PIP_INDEX="${PIP_INDEX:-https://mirrors.aliyun.com/pypi/simple/}"
TORCH_INDEX="${TORCH_INDEX:-https://mirrors.aliyun.com/pytorch-wheels/cpu/}"

[ -f "${DIST_DIR}/${WHL}" ] || { echo "[FATAL] wheel 缺失: ${DIST_DIR}/${WHL}" >&2; exit 1; }
$PODMAN image exists "${BUILDER_IMAGE}" || { echo "[FATAL] 构建器镜像缺失: ${BUILDER_IMAGE}" >&2; exit 1; }

build_one() {
    local variant="$1"   # 0|1
    local tag
    if [ "${variant}" = "0" ]; then
        tag="localhost/xmflow-release:${VERSION}"
    else
        tag="localhost/xmflow-release:${VERSION}-torch"
    fi
    echo "==> 构建 ${tag} (TORCH_VARIANT=${variant})"
    $PODMAN build --network host \
        --build-arg BUILDER_IMAGE="${BUILDER_IMAGE}" \
        --build-arg WHL="${WHL}" \
        --build-arg TORCH_VARIANT="${variant}" \
        --build-arg PIP_INDEX="${PIP_INDEX}" \
        --build-arg TORCH_INDEX="${TORCH_INDEX}" \
        -f "${SCRIPT_DIR}/Containerfile.release" \
        -t "${tag}" \
        "${DIST_DIR}"
    echo "[OK] ${tag}"
}

case "${1:-}" in
    standard) build_one 0 ;;
    torch)    build_one 1 ;;
    all)      build_one 0; build_one 1 ;;
    *)
        grep '^#' "$0" | sed 's/^# \{0,1\}//'
        exit 1 ;;
esac
