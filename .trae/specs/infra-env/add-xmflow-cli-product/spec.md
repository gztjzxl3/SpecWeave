---
title: "第二交付产品 xmflow-cli 提案（纯 CLI 客户镜像收编进 offline-delivery）"
status: "draft"
---

# 第二交付产品 xmflow-cli 提案 - Product Requirements Document

## Overview

- **Summary**: 把 2026-10-09 在 `client` 侧临时产出的「xmflow 客户发布镜像」三份资产（`Containerfile.release`、`build-release.sh`、`USAGE.zh-CN.md`）收编为 `apps/containers/offline-delivery/` 的**第二个交付产品** `xmflow-cli`：按 `docs/01-quickstart.md` §5 的官方流程新增 `products/xmflow-cli/`（产品参数、Containerfile、deps、构建脚本、产品自有守卫、独立交付骨架）并在文档登记。本 spec 只做**方案定义与验收标准**，不含实现代码。
- **Purpose**: 这三份资产描述的是一个与现有 `xmnn-runtime` 产品**形态正交**的客户交付物——纯 CLI、零 conda、零 Jupyter、可重定位最小 CPython、`xmflow` console script 作为 ENTRYPOINT。它当前落在 `client/overlays/native-dev/release/`，直接违反 client 侧 C26 红线（wheel 消费运行时栈已整体迁出，本应用不再持有其镜像定义）与 offline-delivery §7（新产品只允许在 `products/<名>/` 落地）。留在 client 会产生两份客户镜像定义漂移；整体丢弃则损失已在真机验证过的镜像与完整的客户侧中文契约文本。
- **Target Users**: 厂商侧交付工程师（用 `bin/relpack -p xmflow-cli` 出包）、CLI 型客户（只需编译/推理，不需要 Notebook 交互面）、后续第三/第四个交付产品的维护者（本提案顺带验证「多产品」这一当初抽应用的核心假设是否真的成立）。

## Goals

- **G1**: 客户镜像定义与使用说明从 `client` 迁至 `offline-delivery/products/xmflow-cli/`，`client` 下不再存在任何客户镜像定义（C26 归位）。
- **G2**: 复用既有交付模型：载荷（xmnn wheel）一律在**客户侧**经 `release/payload/Dockerfile` 以 `--no-index --no-deps` 派生装入交付 tag，构建期不装载荷（§9 红线：底座内绝不安装 xmnn）。
- **G3**: 出包能力全部经 `bin/relpack -p xmflow-cli stage|deps|build|pack|smoke` 驱动，`bin/relpack` 与 `bin/lib/common.sh` 的产品无关性保持不变。
- **G4**: 产品差异（镜像名、Containerfile、基镜像、形态语义、守卫脚本、交付骨架）全部封装在 `products/xmflow-cli/` 内，对外契约修订面收敛到**一处**（见 FR-6 与 AC-4）。
- **G5**: 客户侧契约文本（`USAGE.zh-CN.md` 的 7 节信息）在 `products/xmflow-cli/release/README.md` 与 `docs/` 中完整保留，不丢信息、不改口径。
- **G6**: 交付骨架测试具备多产品能力，使第三个产品接入时不再需要改测试代码。

## Non-Goals

- **本 spec 不写实现代码**，不改 `bin/relpack`、`bin/lib/common.sh`、`tests/`、`products/xmnn-runtime/**`（用户决策：实现另起一笔 feat）。
- 不改 `xmnn-runtime` 产品的任何对外可见契约（compose 逐字、`xmnnctl` 命令面、`.env` 键、`release.json` schema v2 字段）。
- 不在 `client` 复活任何 wheel 消费运行时栈（C26）。
- 不引入 GPU/CUDA 交付形态，不引入 `cu130`（CLI 产品无 Jupyter 交互面，GPU 属另一独立提案）。
- 不负责构建 xmnn wheel 本身（wheel 由 `client` 的 native-dev 构建链产出，本产品只消费）。

## Background & Context

### 原件事实（本次迁出前后逐字一致，md5 为证）

三份原件未被 git 跟踪，已按字节 server-side 复制进本目录 `assets/` 留档（CR=0，纯 LF）：

| 文件 | 行数 | 字节 | md5 | 原 mtime |
|---|---|---|---|---|
| `assets/Containerfile.release` | 135 | 7245 | `c18bd3544dce2985ae277ded1f0313ee` | 2026-10-09 10:53 |
| `assets/build-release.sh` | 59 | 2339 | `efb214077b7ae4d7adede28bca6019e4` | 2026-10-09 09:57（mode 755） |
| `assets/USAGE.zh-CN.md` | 128 | 5613 | `fc58b539614daff2e4d027cae7fca9ca` | 2026-10-09 10:05 |

> 实现完成后应删除本 `assets/` 留档（内容已全部落到 `products/xmflow-cli/`），删除动作在 tasks.md 中有对应任务。

### 已在真机验证的产物（2026-10-09 实测，`/usr/local/bin/podman images`）

- `localhost/xmflow-release:1.2.1` — **1.18 GB**，构建成功（当日 10:5x 前后，43 分钟前）。
- `localhost/native-dev:nuitka-4.2.2-hotfix` — 10.7 GB（Stage 0 wheelhouse 构建器）。
- `docker.io/library/ubuntu:26.04` — 112 MB（Stage 1 runtime 基镜像）。
- 对照：现有产品 `localhost/xmnn-runtime:1.2.1.dev0` 3.18 GB、其基镜像 `localhost/jupyter-podman-rootless:latest` 1.19 GB。
- wheel 实测**只**存在于 `apps/containers/client/workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（177 MB，2026-10-08 21:18）；`apps/containers/workspace/dist/` 下当前**无** whl。

### 该镜像与 `xmnn-runtime` 产品的本质差异

| 维度 | `xmnn-runtime`（现有产品） | `xmflow-cli`（本提案产品） |
|---|---|---|
| 客户交互面 | Jupyter / Notebook 交互 | 纯 CLI（`xmflow compile/accuracy/infer/performance/excelreport/pipeline`） |
| Python 底座 | `/opt/conda`（cp314 GIL base env） | 可重定位最小 CPython 3.14.7（保持 `/opt/conda` 前缀）→ 隔离 venv `/opt/xmflow` |
| torch | 底座必带（形态 `cpu`/`cu130`） | **variant 0 完全不装 torch**；variant 1 装 CPU 版 `torch==2.14.0+cpu` 作为 pytorch 前端 |
| 载荷安装期 | 客户侧 `payload/Dockerfile`（§9） | 原件在**构建期** Stage 1 装入镜像（违反 §9，须改造） |
| 依赖闭包来源 | 产品目录 `deps.txt`（§10，离线） | 构建期 `pip download` 走 aliyun 在线解析（须改为 deps.txt + 离线） |
| 交付形态 | `release/` 骨架 + `xmnnctl` | `docker run -v models -v temp`，无骨架、无控制脚本 |
| 运行用户 | devuser | 非 root `xmnn`（uid 不固定，需 `chmod 0777 temp` 或 `--user` 规避） |

### 既有规范与先例（本 spec 的约束来源）

- `apps/containers/client/AGENTS.md` L170：wheel 消费运行时栈已于 2026-09-21 整体迁出为独立应用 `apps/containers/offline-delivery`，client 不再持有其镜像定义（compose/Containerfile/wheels）。
- `offline-delivery/.agents/rules/delivery-pipeline.md`：§7 外部输入白名单与「新增第二个交付产品 = **只**新增 `products/<名>/`，CLI 代码零改动」；§9 底座/载荷分离红线（底座内绝不安装 xmnn）；§10 `deps.txt` 为底座依赖面唯一事实源；§11 守卫分段与「守卫项增删属交付契约变更，须同步骨架 README、docs/ 与守卫测试」；§12 `release.json` schema v2 按块解析。
- `offline-delivery/docs/01-quickstart.md` §5：新增第二个交付产品的官方 5 步（建 `product.env` → 落 Containerfile/`.dockerignore`/deps/scripts/smoke → 迁入或新建 `release/` 骨架与 `release/payload/` → 所有命令加 `-p <名>` → 在 `docs/README.md`、`00-overview.md`、quickstart 登记并追加 `.agents/CHANGELOG.md` 条目）。
- 先例 spec：`infra-env/extract-offline-delivery-app`（抽应用的动机即「为后续扩展第二个交付产品预留」），其 Open Questions 已记录「`apps/containers/workspace/dist` 与 `client/workspace/dist` 双目录并存的历史成因需确认」与「GPU 交付属后续提案」——本提案正面对上第一条。
- `bin/relpack`（253 行）实测契约：`--base-image` 可覆盖、`BASE_IMAGE_DEFAULT` 为产品级键 ⇒ **基镜像改为 `ubuntu:26.04` 不构成契约修订**；`load_product_env` 必需 9 键（`PRODUCT IMAGE_NAME CONTAINERFILE WHEEL_GLOB WHEEL_PREFIX WHEEL_DIST BASE_IMAGE_DEFAULT TORCH_DEFAULT RELEASE_DIR`）且 `PRODUCT` 必须等于目录名；`pack` 前置 `guard_crlf_shebang` + `require_staged_wheel` + `deps_consistency`；`smoke` 强依赖骨架内 `./xmnnctl load/up/smoke/down` 四步。

## Problem Statement

原件是「一步到位构建出客户镜像」的形态：`ARG BUILDER_IMAGE=localhost/native-dev:nuitka-4.2.2-hotfix` 起 Stage 0，在线 `pip download` 解析 xmnn 依赖闭包，把 conda 的 python3.14 + `lib/python3.14` 抽成可重定位最小 CPython，再以 `ubuntu:26.04` 为 Stage 1 建 venv 并**在构建期**安装 `xmnn[torch]==1.2.1.dev0`，最终 `ENTRYPOINT ["/opt/xmflow/bin/xmflow"]`。这与 offline-delivery 的交付模型存在四处结构性错位：

1. **依赖闭包语义冲突（§10）**：`deps.txt` 定义的是「底座依赖面 = wheel METADATA 中无分号 marker 的 Requires-Dist（torch 除外）」，用于**离线**装底座；原件的闭包来自构建期在线 `pip download`，且按变体切换 `xmnn` / `xmnn[torch]` extras。二者语义不可直接互换。
2. **形态白名单无法表达「无 torch」**（`bin/relpack` L27 `FLAVORS="cpu|cu130"`，L103/L240 两处 `check_enum` 强制；`build` 恒传 `--build-arg TORCH_FLAVOR=$FLAVOR`；§11 含「torch 形态 vs 实物」守卫项）。CLI 产品的主力形态恰是**不装 torch**。
3. **守卫硬耦合 conda + Jupyter**：`products/xmnn-runtime/smoke/_base_guards.py`（403 行）写死 `_MAIN_PYTHON=/opt/conda/envs/main/bin/python`、`_MAIN_JUPYTER`、`kernel.json` 路径、双 ABI 与 root+devuser 双跑，并含「载荷未安装」反断言。零 conda、零内核的 CLI 底座必须自带一套守卫，而 §11 末句把「守卫项增删」定性为交付契约变更。
4. **测试与客户骨架不可复用**：`tests/conftest.py` 的 `PRODUCT_NAME = "xmnn-runtime"` 为写死常量，`tests/test_release_skeleton.py`（747 行）断言 `img_ref="localhost/xmnn-runtime:$ver"`、`_map(lines)["name"] == "xmnn-runtime"`、`svc["image"] == "localhost/xmnn-runtime:${XMNN_VERSION}"` 等字面量；而 CLI 客户不需要 Jupyter 端口/凭证面，其 `release/` 骨架须按 `xmflow` 命令面重写，规模参照现有骨架约 1500 行（`xmnnctl` 608 + `xmnnctl.ps1` 233 + `lib/pipeline.sh` 349 + `README` 272）。

此外有一处**输入白名单缺口**：§7 只允许两项外部输入（`../workspace/dist/<WHEEL_GLOB>` 与 `BASE_IMAGE_DEFAULT`），而原件的 Stage 0 必需第三个输入——构建器镜像 `localhost/native-dev:nuitka-4.2.2-hotfix`（它同时提供依赖解析能力与可重定位 CPython 原料）。若按「载荷阶段化」改造后仍需该构建器，则 §7 必须显式登记第三项外部输入（文档契约，非 CLI 契约）。

**本轮决策事实**：用户在两次决策门中明确选择「分两步——先提交第二产品提案 spec」与「迁移后删除原目录」，并约束「只提交，不推送」；本轮**不触碰** `relpack`/守卫/测试等对外契约代码，以零回归风险换取方案定稿。

## Functional Requirements

- **FR-1**: 新增 `apps/containers/offline-delivery/products/xmflow-cli/`，目录名与 `product.env` 的 `PRODUCT` 一致（`load_product_env` 强校验），内含 `product.env`、`Containerfile.xmflow-cli`、`.dockerignore`、`deps.txt`、`scripts/`、`smoke/`、`release/`（含 `payload/`）。
- **FR-2**: `product.env` 覆盖 `load_product_env` 必需 9 键；`IMAGE_NAME=localhost/xmflow-cli`（命名与本应用产品一致，避免与历史 `xmflow-release` 双标签漂移）；`CONTAINERFILE=Containerfile.xmflow-cli`；`WHEEL_GLOB`/`WHEEL_PREFIX` 指向 `xmnn-*.whl`；`BASE_IMAGE_DEFAULT=docker.io/library/ubuntu:26.04`；`RELEASE_DIR=release`；`TORCH_DEFAULT` 取值由 FR-6 决定。
- **FR-3**: 镜像定义改造为**两段两物**：① 底座 `Containerfile.xmflow-cli` 产出 `<IMAGE_NAME>:base-<形态>`，只含可重定位最小 CPython + venv + 依赖面（`pip install -r deps.txt`），构建上下文为产品目录且**不含 wheel**，绝不安装 `xmnn`，并以反断言兜底（venv 内 `import xmnn` 必失败、site-packages 无 `xmnn*`）；② 载荷由 `release/payload/Dockerfile` 在客户侧以 `--no-index --no-deps` 装入 `<IMAGE_NAME>:<交付版本>`。
- **FR-4**: 依赖闭包从「构建期在线 `pip download`」改为 §10 语义的 `deps.txt`（由 `bin/relpack -p xmflow-cli deps --write` 生成、`deps` 校验），底座构建全程可离线；`torch` extras 的选择改由形态参数表达，不得在 Containerfile 内内嵌 `xmnn` 版本常量（§7）。
- **FR-5**: `release/` 交付骨架按 `xmflow` 命令面新建（`xmnnctl`/`xmnnctl.ps1` 同名 CLI 契约或等价的 `xmflowctl`，含 `load`/`run`/`smoke`/`down` 语义、`.env.example`、`artifacts/.gitignore`、`workspace/.gitkeep`），遵守 §1 全部骨架不变量：零 `../`、零 Python、`pull_policy: never`、shebang 全 LF、挂载点为 `/workspace/models:ro` 与 `/workspace/temp`。
- **FR-6**: **对外契约修订（本提案唯一一处 CLI 改动）**：把形态白名单从 `bin/relpack` 的全局常量 `FLAVORS="cpu|cu130"` 下移为 `product.env` 的可选键 `FLAVORS`（缺省回退全局值），使 `xmflow-cli` 可声明形如 `none|cpu` 的形态集；同时同步 `tests/test_relpack_cli.py` 与 `docs/` 中形态白名单的表述。除此之外 CLI 代码零改动。
- **FR-7**: 产品自有守卫：`smoke/_base_guards.py`（底座期，root+`xmnn` 双跑，含「载荷未安装」反断言与 venv 可导入 `ssl/ctypes/sqlite3/lzma/bz2/zlib/decimal/pyexpat/venv` 的可重定位性断言）与 `smoke/_runtime_smoke.py`（交付期，含 `xmflow --help` 与一次 `SIM_VTA2.0` 冒烟编译）；按 §11 末句同步骨架 README、`docs/` 与守卫测试。
- **FR-8**: 客户契约文本完整迁移：`USAGE.zh-CN.md` 7 节（标签表、快速开始、模型组目录契约、常用命令、真机网络、镜像内容边界、FAQ）逐节落入 `release/README.md` 或 `docs/`，命令示例改用最终镜像名与新形态标签；`--network host`、`chmod 0777 temp` / `--user` 规避 uid、`0x7F7F` 毒值判读三条排障口径必须保留。
- **FR-9**: 按 §7 登记第三项外部输入（构建器镜像）或论证其可消除（见 Open Questions OQ-3）；若保留，须在 `delivery-pipeline.md` §7 与应用 `docs/00-overview.md` 写明该输入的产出方（`client` 的 native-dev 构建链）与「不作为构建依赖进入交付链」的边界。
- **FR-10**: 测试具备多产品能力：`tests/conftest.py` 的产品名参数化（按 `products/*/` 发现），`test_release_skeleton.py` 的产品字面量改为产品参数驱动；新增 `xmflow-cli` 骨架不变量用例；既有 `xmnn-runtime` 用例必须**全绿且不改动断言语义**。
- **FR-11**: 文档登记四件套 + 变更日志：`docs/README.md`、`docs/00-overview.md`、`docs/01-quickstart.md`（§5 示例引用新产品）、`.agents/CHANGELOG.md` 追加条目（沿用 `日期 | type | 摘要` + 「关联七概念场景」「背景与动机（I）」「本任务落地」格式）。
- **FR-12**: 清理：删除 `apps/containers/client/overlays/native-dev/release/` 整目录（原件留档在本 spec 的 `assets/`），实现完成后删除本 `assets/` 留档，使仓库内客户镜像定义**唯一**存在于 `products/xmflow-cli/`。

## Non-Functional Requirements

- **NFR-1**: 零回归：`xmnn-runtime` 产品的 `relpack` 命令面、交付骨架文件清单、`release.json` schema v2 字段、守卫项语义均保持等价。
- **NFR-2**: 底座体积目标不劣于原件：`<IMAGE_NAME>:base-<形态>`（不含载荷）应显著小于原件的 1.18 GB 整体镜像，且派生增量与 §9 的约 0.18 GB / 1-3 分钟量级可比（须实测记录，不得臆断）。
- **NFR-3**: 交付链全程可离线：底座构建不访问任何 pip 索引；客户侧派生只用 `--no-index --no-deps`。
- **NFR-4**: 所有新增脚本零 Python 依赖（bash 4+ / pwsh 7.4+），失败路径给出中文、可执行、指向下一步的指引。
- **NFR-5**: 行尾纪律：新增 POSIX 脚本与文本一律 LF；无 `.sh` 后缀的 CLI 文件须按 `.gitattributes` 既有惯例追加显式 `**/<name> text eol=lf` 规则（该文件注释已说明原因：shebang 由内核解析，脚本内无法自救）。
- **NFR-6**: 治理文档同步：`offline-delivery/AGENTS.md`（若含产品清单）、`.agents/rules/delivery-pipeline.md`（形态白名单与外部输入条款）、`apps/containers/AGENTS.md` 相关表述。

## Constraints

- **Technical**: 不得引用 `apps/containers/client/` 与 `shared/` 任何路径或代码（§7）；不得固定 uid（base 镜像已占 uid 1000）；镜像仅支持 x86_64；wheel 的 `Requires-Python >=3.14.6` 决定必须使用可重定位 CPython 3.14.7 而非 `ubuntu:26.04` 的 apt python 3.14.4。
- **Business**: `release/` 骨架与 `USAGE` 契约文本是客户可见承诺，改版须走提案；标签命名从 `xmflow-release:1.2.1[-torch]` 收敛到 `<IMAGE_NAME>:<版本>[形态]` 需与客户同步。
- **Dependencies**: 验证依赖真机 podman 5.6.2 与其上的 `ubuntu:26.04`、`native-dev:nuitka-4.2.2-hotfix`、`client/workspace/dist` 内的 wheel；pytest 7.1.2（python 3.8.10）可跑静态守卫测试。
- **Process**: 本轮产物仅为 spec（`spec.md` + `tasks.md`）与原件留档；实现属后续 feat，须先通过 spec 批准门。

## Assumptions

- xmnn wheel 的 CLI 命令面（`xmnn.cli.xmflow:app`，见 `client/overlays/native-dev/builder/pyproject.toml` L34-36）在交付版本区间内保持稳定，`ENTRYPOINT` 可直接依赖 console script 而不需源码树。
- 依赖解析结果（原件 Stage 0 的 `pip download` 闭包）与 §10 的 `deps.txt` 集合在去掉 torch 后基本等价；差异须由 `deps` 校验实测暴露，不在提案中假设无差异。
- 可重定位最小 CPython 的制备可以在「不依赖 conda 镜像」的前提下由另一可控输入替代（例如官方 `python-build-standalone`），但本提案**不**引入新的第三方二进制源。
- CLI 客户不需要 Jupyter 端口与凭证面，因此其骨架与 `xmnn-runtime` 骨架不可能共用同一 `compose.yaml`，两份骨架并存属预期而非双写。

## Acceptance Criteria

### AC-1: 客户镜像定义唯一落点
- **Type**: `rule`
- **Given**: 实现完成的提交（feat）落地后
- **When**: 在 `notebook/dev/libs/AI` 仓库根执行 `git grep -l -E 'xmflow-release|Containerfile\.release|BUILDER_IMAGE=localhost/native-dev' -- 'apps'`
- **Then**: 命中集合**只**允许出现在 `apps/containers/offline-delivery/` 内（历史 CHANGELOG 条目与本 spec 目录除外）
- **Pass Condition**: `apps/containers/client/overlays/native-dev/release/` 不存在，且 `git status --porcelain` 干净
- **Evidence**: 命令输出 + `ls` 结果

### AC-2: 载荷阶段化（§9 红线不破）
- **Type**: `rule`
- **Given**: `products/xmflow-cli/Containerfile.xmflow-cli` 与 `release/payload/Dockerfile`
- **When**: 静态检查底座文件、并实际构建底座
- **Then**: 底座构建上下文中无 `.whl`；底座镜像内 `python -c "import xmnn"` 必失败且 `site-packages` 无 `xmnn*` 目录；载荷安装只出现在 `payload/Dockerfile` 且使用 `--no-index --no-deps`
- **Pass Condition**: 反断言在守卫中以「预期失败」形式固化（非人工目视）
- **Evidence**: 守卫运行输出、`podman run --rm <base> ls /opt/xmflow/lib/python3.14/site-packages`

### AC-3: 离线交付链端到端
- **Type**: `rule`
- **Given**: `bin/relpack -p xmflow-cli`
- **When**: 依次执行 `stage` → `deps` → `build` → `pack` → `smoke`
- **Then**: 五步全部零退出；`build` 期间无任何 pip 索引网络访问；`pack` 产出归档经 `gzip -t` 校验且 `release.json` 的 `payload.sha256` 与 `archive.sha256` 均可按 §12 块定向读出
- **Pass Condition**: `smoke` 走交付骨架 `load/up/smoke/down` 四步全绿
- **Evidence**: 命令输出、`release.json` 内容、归档 size/sha256

### AC-4: 对外契约修订面收敛
- **Type**: `rule`
- **Given**: 实现提交
- **When**: `git show --stat` 与 `git diff` 检视 `bin/`、`tests/`
- **Then**: `bin/relpack` 与 `bin/lib/common.sh` 的改动**仅**为形态白名单下移（FR-6）；`products/xmnn-runtime/**` 无任何改动；`xmnn-runtime` 既有测试断言语义不变
- **Pass Condition**: 出现任何第二处 CLI 契约改动即判不通过，须回到 §7 尾注自查（「说明产品常量泄漏到了代码里」）
- **Evidence**: diff 摘要、`pytest` 全绿输出

### AC-5: 客户契约文本无信息损失
- **Type**: `rubric`
- **Dimension**: 迁移后客户文档对原件 7 节信息（标签/体积、挂载契约、模型组目录与 `config.toml` 字段、六个 target 与 `quantized_dtype`/`tune`、常用命令、真机网络与 NFS 边界、镜像内容边界、三条 FAQ）的覆盖完整度与口径一致性
- **Scale**: 1-5
- **Anchors**: 1 = 多节缺失或命令示例不可执行；3 = 各节均在但若干细节（如 `-torch` 选型判据、`0x7F7F` 判读、uid 规避方式）丢失；5 = 7 节全覆盖、命令可直接粘贴执行、标签与形态口径与最终实现一致
- **Pass Threshold**: >= 4
- **Evidence**: 与 `assets/USAGE.zh-CN.md`（实现删除留档前）逐节对照表

### AC-6: 多产品测试可复用
- **Type**: `rule`
- **Given**: `tests/` 参数化改造后
- **When**: 新增一个最小假产品目录（仅 `product.env` + 骨架文件清单）并在本地跑 `pytest`
- **Then**: 测试自动覆盖该产品且无需修改测试代码；删除假产品后 `xmnn-runtime` 与 `xmflow-cli` 用例结果不变
- **Pass Condition**: 用例收集数随产品目录数变化（可观察）
- **Evidence**: `pytest --collect-only -q` 前后对比

### AC-7: 行尾与 shebang 守卫
- **Type**: `rule`
- **Given**: 全部新增文本与脚本
- **When**: `pack` 前置 `guard_crlf_shebang` 与 `git show :<path> | tr -cd '\r' | wc -c`
- **Then**: 归档内所有文本 CR=0；无 `.sh` 后缀的 CLI 文件在 `.gitattributes` 中有显式 `text eol=lf` 规则
- **Pass Condition**: 任一 CR>0 即 fail-fast
- **Evidence**: 守卫输出、`git check-attr -a` 结果

### AC-8: 提案质量
- **Type**: `rubric`
- **Dimension**: 本 spec 对「第二产品是否值得接入 offline-delivery、以何种最小契约代价接入」的决策支撑力（冲突定位准确性、方案可执行性、风险与开放问题的诚实度）
- **Scale**: 1-5
- **Anchors**: 1 = 仅复述需求；3 = 冲突点定位正确但未量化契约改动面；5 = 每项冲突给出条款级证据、唯一契约修订面有替代方案比较、不可验证项全部列入 Open Questions
- **Pass Threshold**: >= 4
- **Evidence**: 批准门记录

## Open Questions

- **OQ-1（必须实现前澄清）**: wheel 源目录矛盾——§7 规定 `WHEEL_DIST=../workspace/dist`（即 `apps/containers/workspace/dist`），但当前 CLI 产品的 wheel 实测**只**在 `apps/containers/client/workspace/dist/`，而 §7 同时禁止引用 `client/`。是统一搬运 wheel、还是把 `client/workspace/dist` 登记为合法上游产出目录？（`extract-offline-delivery-app` 已把此矛盾记为待确认历史成因。）
- **OQ-2**: 形态白名单下移后，`xmflow-cli` 的形态集应命名为 `none|cpu`、`base|torch`，还是复用 `cpu|cu130` 语义并另立「载荷 extras」维度？命名会影响 `<IMAGE_NAME>:base-<形态>` 归档名与客户可见 tag（§2 契约）。
- **OQ-3**: 载荷阶段化后，Stage 0（依赖在线解析 + 最小 CPython 制备）是否可完全移出交付链、由 `native-dev` 构建链产出一个「运行时基座镜像」交付物？若可以，§7 无需新增外部输入；若不可以，须论证 `nuitka` 构建器不进交付契约的边界。
- **OQ-4**: 客户 tag 从 `xmflow-release:1.2.1` / `:1.2.1-torch` 收敛为 `xmflow-cli:<版本>` / 形态化 tag 的迁移策略——是否已对外承诺旧 tag（本 spec 认定尚未承诺，因为原件未提交、镜像未发布归档）。
- **OQ-5**: `smoke` 编译冒烟需要一个可用模型组目录；`USAGE` §3 的契约目录是否随产品提供一份最小示例（镜像内「不含示例模型」是既有承诺，冲突需定口径）。
- **OQ-6**: 本提案留档的 `assets/` 与「实现完成后删除」是否会与 spec 目录的历史可追溯性冲突（`extract-offline-delivery-app` 的 spec 目录保留了附加文件；431 个附加文件先例说明 spec 目录允许放资产）。
