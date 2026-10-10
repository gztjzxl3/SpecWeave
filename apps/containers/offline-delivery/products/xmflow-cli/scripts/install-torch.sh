#!/usr/bin/env bash
# xmflow-cli 内置 torch 层（Containerfile.xmflow-cli Layer 3）
#
# 由 TORCH_FLAVOR 驱动（白名单 none|cpu，bin/relpack 侧已先校验）：
#   none  默认 —— **不装 torch**。本产品交付 caffe/onnx 前端，客户不需要 PyTorch
#         时底座体积最小（对照原件 TORCH_VARIANT=0）。
#   cpu   追加 PyTorch CPU 前端：torch / torchvision / onnx2pytorch，即载荷 wheel
#         的 `torch` extra 三件套（xmnn-*.whl METADATA 实测：torch>=2.2、
#         torchvision>=0.17、onnx2pytorch>=0.4）。本产品**没有 CUDA 形态**——
#         客户机不需要 GPU，交付 §4 P0 也禁止 GPU 栈进客户镜像。
#
# 为什么这三件套必须在**底座**装而不是交给载荷：载荷派生用的是
# `pip install --no-index --no-deps`（§9），extra 依赖不会被解析；而 deps.txt
# 只收 wheel 的**无条件** Requires-Dist（§10，带 `extra == "torch"` marker 的
# 条目按规则排除）。所以 torch 前端只能由本产品自己的形态层显式提供，
# `--torch cpu` 与 `--torch none` 的差别就是这一层装不装。
#
# 为什么索引取阿里云 pytorch-wheels 而不是 download.pytorch.org：实测
# （2026-10-09）本宿主直连 download.pytorch.org 超时不可达，而
# https://mirrors.aliyun.com/pytorch-wheels/cpu/ 返回 200 且确有
# torch-2.14.0+cpu / torchvision-0.29.0+cpu 的 cp314 manylinux_x86_64 轮子；
# onnx2pytorch 由 PyPI 镜像（上一层 pip config 已配好）提供。索引可按形态
# 推导（cpu 目录），故不设独立事实源；确需换索引时用 TORCH_INDEX 覆盖。
#
# 为什么装进 venv（/opt/xmflow）而不是 /opt/conda：载荷 wheel 的 console_script
# 与全部依赖都落在同一个隔离 venv 里，/opt/conda 只是裸解释器（无 site-packages）；
# 混装会让「底座依赖面」与「构建器残留」无法区分。
#
# 形态落盘 /opt/xmflow-torch-flavor 供底座守卫断言（守卫读不到 LABEL）。
set -euo pipefail

PY="${PY:-/opt/xmflow/bin/python}"
MARKER=/opt/xmflow-torch-flavor
TORCH_VERSION="${TORCH_VERSION:-2.14.0}"
TORCHVISION_VERSION="${TORCHVISION_VERSION:-0.29.0}"
FLAVOR="${TORCH_FLAVOR:-none}"

case "${FLAVOR}" in
  none)
    echo "[xmflow-cli] torch: skipped (TORCH_FLAVOR=none —— 镜像不含 torch)"
    ;;
  cpu)
    TORCH_INDEX="${TORCH_INDEX:-https://mirrors.aliyun.com/pytorch-wheels/${FLAVOR}/}"
    echo "[xmflow-cli] torch: 从 ${TORCH_INDEX} 安装 torch==${TORCH_VERSION}+cpu / torchvision==${TORCHVISION_VERSION}+cpu / onnx2pytorch>=0.4"
    "${PY}" -m pip install --no-cache-dir \
      --find-links "${TORCH_INDEX}" \
      "torch==${TORCH_VERSION}+cpu" \
      "torchvision==${TORCHVISION_VERSION}+cpu" \
      "onnx2pytorch>=0.4"
    rm -rf /root/.cache/pip
    "${PY}" - <<'PYCHK'
import torch, torchvision
print("[xmflow-cli] torch", torch.__version__, "cuda=", torch.version.cuda)
print("[xmflow-cli] torchvision", torchvision.__version__)
PYCHK
    ;;
  *)
    echo "[xmflow-cli] ERROR: TORCH_FLAVOR 必须为 none|cpu，实际为 '${FLAVOR}'" >&2
    exit 1
    ;;
esac

printf '%s' "${FLAVOR}" > "${MARKER}"
echo "[xmflow-cli] torch flavor marker: ${MARKER}='${FLAVOR}'"
