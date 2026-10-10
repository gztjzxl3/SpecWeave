# payload/Dockerfile —— XMNN 载荷（wheel）派生构建入口【客户机执行】
# ------------------------------------------------------------
# 定位：底座镜像 localhost/xmflow-cli:base-<形态> 不含 XMNN 载荷（只有可重定位
# CPython、/opt/xmflow venv 依赖面、torch 前端与守卫脚本）；客户拿到交付包后由
# xmnnctl load 用本文件把随包 wheel（内含 xmflow console_script）装入 venv，
# 产出派生镜像 localhost/xmflow-cli:<交付版本>——该 tag 与 compose.yaml 的
# ${XMNN_VERSION} 逐字一致，故 compose 无需改动。
#
# 构建上下文 = 本目录（payload/）：只送 wheel，
# 绝不把同级 artifacts/ 的底座归档送进 build（避免无谓的上下文拷贝）。
# 由 xmnnctl 下发：--build-arg BASE_IMAGE=<底座 ref> --build-arg PAYLOAD_VERSION=<交付版本>；
# 产物 tag 由 xmnnctl 用 -t 指定，本文件不打 tag。
#
# 三条硬约束：
#   1) 完全离线：--no-index 禁网、--no-deps 跳过依赖解析（依赖已由底座 venv 预装）；
#   2) 不改 ENTRYPOINT/CMD/WORKDIR：派生只是"加一层载荷"，入口契约沿用底座
#      （ENTRYPOINT = /opt/xmflow/bin/xmflow，一次性 CLI；常驻模式的保活命令
#      由 compose.yaml 的 command 覆盖，不写进镜像）；
#   3) 失败即构建失败：载荷守卫（root + xmnn 双身份，10 项）与依赖区间校验
#      （pip check）任一不过即中止——不产出 tag，客户机上不会出现半成品镜像。
#      ⚠️ pip check 的判据必须**限定在载荷相关冲突**上：底座 venv 之外的既有
#      元数据债务与本次交付无关（底座层已由 _base_guards.py 全量把关），若要求
#      pip check 整体 exit 0，派生构建可能在客户机上无辜失败。故此处先完整
#      打印全部冲突供人查阅，只有以 xmnn 开头的冲突行（＝载荷声明的依赖在底座
#      缺失或版本不符）才判定为交付失败。
# ------------------------------------------------------------

ARG BASE_IMAGE=localhost/xmflow-cli:base-none
FROM ${BASE_IMAGE}

# FROM 之前声明的 ARG 不能用于 LABEL/RUN，须在 FROM 之后重新声明
ARG BASE_IMAGE
ARG PAYLOAD_VERSION

LABEL org.specweave.component="xmflow-cli-payload" \
      org.specweave.layer="xmnn-wheel-payload" \
      org.specweave.payload-version="${PAYLOAD_VERSION}" \
      org.specweave.payload-abi="cp314-gil" \
      org.specweave.base-image="${BASE_IMAGE}"

# 底座镜像默认 USER=xmnn（Containerfile 末行 USER xmnn 烙进镜像配置），派生构建
# 若不显式切回 root，本层 RUN 会以 uid=1001(xmnn) 执行：向 root 属主的
# /opt/xmflow/lib/python3.14/site-packages 写 wheel 落 _libs 时报
# [Errno 13] Permission denied（2026-10-10 smoke 实证），且下方 su 双身份守卫
# 与 /root/.cache 清理本就要求 root。构建层显式 root，末行恢复 xmnn 运行契约。
USER root

# 载荷 wheel（只可能有一个：payload/.gitignore 忽略 *.whl，交付流水线每次 stage 一个）
# 不再 COPY：改用下方 RUN 的 bind 挂载只读注入。COPY 会生成独立镜像层，
# RUN 内 rm -rf 无法消减（2026-10-10 实测派生残留 177 MB，致 NFR-2 后半未达成）；
# type=bind 挂载仅在 RUN 执行期可见、不进任何层，派生体积 = 底座 + 解包实体。
# source=. 即构建上下文根（payload/），保持 xmnn-*.whl 通配契约不变。

# 装载荷（venv = /opt/xmflow，载荷与 console_script 均落此处）+ 双身份守卫 + pip check
RUN --mount=type=bind,source=.,target=/tmp/payload,ro /bin/bash -lc 'set -euo pipefail ; \
    WHL="$(ls /tmp/payload/xmnn-*.whl | head -1)" ; \
    echo "[payload] installing wheel: $WHL" ; \
    /opt/xmflow/bin/python -m pip install --no-index --no-deps --no-cache-dir "$WHL" ; \
    /opt/xmflow/bin/python -m pip show xmnn | grep -E "^(Name|Version|Location)" ; \
    rm -rf /root/.cache/pip ; \
    echo "[payload] runtime smoke (root)" ; \
    /opt/xmflow/bin/python /opt/xmflow-smoke/_runtime_smoke.py ; \
    echo "[payload] runtime smoke (xmnn)" ; \
    su -s /bin/bash xmnn -c "cd /opt/xmflow-smoke && /opt/xmflow/bin/python _runtime_smoke.py" ; \
    echo "[payload] dependency interval check (pip check)" ; \
    /opt/xmflow/bin/python -m pip check > /tmp/pipcheck.txt 2>&1 || true ; \
    cat /tmp/pipcheck.txt ; \
    if grep -Eq "^xmnn[[:space:]]" /tmp/pipcheck.txt ; then \
      echo "[payload] FAIL: 载荷声明的依赖未在底座满足（见上方 pip check 输出）" ; \
      exit 1 ; \
    fi ; \
    echo "[payload] no xmnn-related dependency conflict" ; \
    rm -f /tmp/pipcheck.txt ; \
    find /opt/xmflow-smoke -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null ; \
    find /opt/xmflow-smoke -type f -name "*.pyc" -delete 2>/dev/null ; \
    echo "########################################################################" ; \
    echo "# XMFLOW-CLI PAYLOAD INSTALLED" ; \
    echo "# payload : $WHL" ; \
    echo "# version : ${PAYLOAD_VERSION}" ; \
    echo "# base    : ${BASE_IMAGE}" ; \
    echo "########################################################################"'

# 恢复底座运行契约：容器默认身份 xmnn（与 base-<形态> 的 USER 一致）
USER xmnn
