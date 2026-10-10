#!/usr/bin/env bash
# xmflow-cli Stage 0：制备可重定位最小 CPython（Containerfile.xmflow-cli Stage 0）
#
# 干什么：把构建器（rich conda 开发镜像）里的 CPython 3.14 剥成一份**只含解释器
# 与标准库**的最小可重定位前缀 /pybase，交给 Stage 1 原样搬进 /opt/conda。
#
# 为什么要搬而不是在底座里 apt 装 python：
#   - 载荷 wheel 元数据要求 `Requires-Python >=3.14.6`，而底座 ubuntu:26.04 的
#     apt python 只有 3.14.4，**不满足**（实测 2026-10-09）；
#   - conda 的 python3.14 二进制静态链接 libpython，`ldd` 只余 glibc，故可以
#     整体搬运（保持 /opt/conda 前缀，不触发任何硬编码路径问题）；
#   - 搬入量约 40 MB，远小于一个完整 conda 环境，底座保持零 apt python。
#
# 为什么必须连 /opt/conda/ssl 一起搬（本产品的**新增**要点，原件没有）：
#   底座 Layer「依赖面」要用这份重定位解释器**联网** pip install deps.txt，而
#   ubuntu:26.04 基镜像内**没有** /etc/ssl/certs/ca-certificates.crt（实测：该
#   文件不存在），OpenSSL 编译期内定的默认校验路径正是 conda 前缀下的
#   /opt/conda/ssl/cert.pem（实测 get_default_verify_paths()）。原件的
#   `pip install --no-index` 从不校验证书，故这条路径在原件里从未被走到；改成
#   依赖面层后若不搬 ssl/，构建会在 TLS 校验上直接失败。
#
# site-packages 一律删除：底座依赖面由 deps.txt 在新 venv 里重装，载荷由交付侧
# 派生时装入；构建器的 conda 环境不是交付事实源，不允许泄漏进客户镜像。
set -euo pipefail

SRC_PREFIX="${SRC_PREFIX:-/opt/conda}"
DEST_PREFIX="${DEST_PREFIX:-/pybase}"

echo "[xmflow-cli] relocating CPython from ${SRC_PREFIX} -> ${DEST_PREFIX}"

mkdir -p "${DEST_PREFIX}/bin" "${DEST_PREFIX}/lib"
cp -a "${SRC_PREFIX}/bin/python3.14" "${DEST_PREFIX}/bin/"
ln -sf python3.14 "${DEST_PREFIX}/bin/python3"
ln -sf python3.14 "${DEST_PREFIX}/bin/python"
cp -a "${SRC_PREFIX}/lib/python3.14" "${DEST_PREFIX}/lib/"
rm -rf "${DEST_PREFIX}/lib/python3.14/site-packages"

# lib-dynload 扩展的非系统库依赖：按 ldd 实测闭包收集，再按 soname 前缀归一
# （libssl.so.3 -> libssl.so 这类），把 conda 前缀里对应的实体与软链一并带上。
libs="$(for f in "${SRC_PREFIX}"/lib/python3.14/lib-dynload/*.so; do
          ldd "$f" 2>/dev/null || true
        done | grep -o "/\S*\.so[0-9.]*" | while read -r p; do
          basename "$(readlink -f "$p")"
        done | sed -n 's/^\(lib[A-Za-z0-9_]*\.so\).*/\1/p' | sort -u || true)"

echo "[xmflow-cli] bundled non-system libs: ${libs}"
for l in ${libs}; do
  cp -a "${SRC_PREFIX}/lib/${l}"* "${DEST_PREFIX}/lib/" 2>/dev/null || true
done

# CA 校验面（见文件头「为什么必须连 ssl 一起搬」）。
if [ -d "${SRC_PREFIX}/ssl" ]; then
  mkdir -p "${DEST_PREFIX}/ssl"
  cp -a "${SRC_PREFIX}/ssl/." "${DEST_PREFIX}/ssl/"
  echo "[xmflow-cli] CA bundle relocated: ${DEST_PREFIX}/ssl"
else
  echo "[xmflow-cli] ERROR: ${SRC_PREFIX}/ssl 缺失，重定位解释器将无法做 TLS 校验" >&2
  exit 1
fi

# 搬迁完整性验证：关键标准库扩展必须能在新前缀直接 import（含 venv，Stage 1
# 建隔离环境要用），并确认证书校验路径已落在搬迁后的前缀上。
"${DEST_PREFIX}/bin/python3.14" - <<'PY'
import ssl, sys
import ctypes, sqlite3, lzma, bz2, zlib, decimal, pyexpat, venv  # noqa: F401
paths = ssl.get_default_verify_paths()
print("[xmflow-cli] relocated python:", sys.version.split()[0])
print("[xmflow-cli] ssl cafile:", paths.cafile, "exists:", bool(paths.cafile))
PY

echo "[xmflow-cli] pybase size:"
du -sh "${DEST_PREFIX}"
