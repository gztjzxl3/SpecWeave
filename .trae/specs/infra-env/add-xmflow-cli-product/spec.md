---
title: "第二交付产品 xmflow-cli 提案（纯 CLI 客户镜像收编进 offline-delivery）"
status: "approved"
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

- **本提案批准门已通过**（2026-10-09 人类裁定「就地改写为合规产品后再删」）：实现与提案合并为**同一笔 feat**，允许改动 `bin/relpack`（仅 FR-6 一处）、`tests/`（仅参数化改造与 FR-6 连带断言）、以及客户契约文本；`bin/lib/common.sh` 与 `products/xmnn-runtime/**` 仍**不得**改动。
- 不改 `xmnn-runtime` 产品的任何对外可见契约（compose 逐字、`xmnnctl` 命令面、`.env` 键、`release.json` schema v2 字段）。
- 不在 `client` 复活任何 wheel 消费运行时栈（C26）。
- 不引入 GPU/CUDA 交付形态，不引入 `cu130`（CLI 产品无 Jupyter 交互面，GPU 属另一独立提案）。
- 不负责构建 xmnn wheel 本身（wheel 由 `client` 的 native-dev 构建链产出，本产品只消费）。

## Background & Context

### 原件事实（本次迁出前后逐字一致，md5 为证）

三份原件产出时在 `client` 侧未被 git 跟踪，已按字节 server-side 复制进本目录 `assets/` 留档（CR=0，纯 LF）并入库：

下表为 2026-10-09 在远端 `wc -l -c` / `md5sum` **复核实测**值（初稿记录的行数与 md5 系入库前的旧副本，已过期并作废；本表为准）：

| 文件 | 行数 | 字节 | md5 | 原 mtime |
|---|---|---|---|---|
| `assets/Containerfile.release` | 136 | 7363 | `65de7e183798bcfea96ad24cc8beb52d` | 2026-10-09 10:53 |
| `assets/build-release.sh` | 59 | 2339 | `efb214077b7ae4d7adede28bca6019e4` | 2026-10-09 09:57（mode 755） |
| `assets/USAGE.zh-CN.md` | 135 | 6280 | `be8d9f43a43566cdede45c2aee8edfc9` | 2026-10-09 10:05（含 `2daf20131` 排障更正） |

> 三份原件均已入库跟踪；实现完成后按 FR-12 删除本 `assets/` 留档（内容全部落到 `products/xmflow-cli/`），删除动作在 tasks.md 的 Task 12 中有对应任务，且以「三文件内容去向对照表」为删除前置条件。

### 已在真机验证的产物（2026-10-09 实测，`/usr/local/bin/podman images`）

- `localhost/xmflow-release:1.2.1` — **1.18 GB**，构建成功（当日 10:5x 前后，43 分钟前）。
- `localhost/native-dev:nuitka-4.2.2-hotfix` — 10.7 GB（Stage 0 wheelhouse 构建器）。
- `docker.io/library/ubuntu:26.04` — 112 MB（Stage 1 runtime 基镜像）。
- 对照：现有产品 `localhost/xmnn-runtime:1.2.1.dev0` 3.18 GB、其基镜像 `localhost/jupyter-podman-rootless:latest` 1.19 GB。
- wheel 实测**只**存在于 `apps/containers/client/workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（177 MB，2026-10-08 21:18）；`apps/containers/workspace/dist/` 下当前**无** whl。**OQ-1 已裁定**：按 §7 新建 `apps/containers/workspace/dist/` 作为唯一合法 wheel 源目录，载荷 wheel 由该处 server-side 复制落位（该路径被 `apps/containers/.gitignore` 的 `workspace/` 规则忽略，不入库）；`client/workspace/dist` 不作为交付输入被引用。

### 该镜像与 `xmnn-runtime` 产品的本质差异

| 维度 | `xmnn-runtime`（现有产品） | `xmflow-cli`（本提案产品） |
|---|---|---|
| 客户交互面 | Jupyter / Notebook 交互 | 纯 CLI（`xmflow compile/accuracy/infer/performance/excelreport/pipeline`） |
| Python 底座 | `/opt/conda`（cp314 GIL base env） | 可重定位最小 CPython 3.14.7（保持 `/opt/conda` 前缀）→ 隔离 venv `/opt/xmflow` |
| torch | 底座必带（形态 `cpu`/`cu130`） | **variant 0 完全不装 torch**；variant 1 装 CPU 版 `torch==2.14.0+cpu` 作为 pytorch 前端 |
| 载荷安装期 | 客户侧 `payload/Dockerfile`（§9） | 原件在**构建期** Stage 1 装入镜像（违反 §9，须改造） |
| 依赖闭包来源 | 产品目录 `deps.txt`（§10） | 构建期 `pip download` 走 aliyun 在线解析（须改为 `deps.txt`，FR-3b/FR-4） |
| 交付形态 | `release/` 骨架 + `xmnnctl` | `docker run -v models -v temp`，无骨架、无控制脚本（须按 FR-5 新建骨架，控制脚本沿用 `xmnnctl` 名称） |
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

此外有一处**输入白名单缺口**：§7 只允许两项外部输入（`../workspace/dist/<WHEEL_GLOB>` 与 `BASE_IMAGE_DEFAULT`），而原件的 Stage 0 必需第三个输入——构建器镜像 `localhost/native-dev:nuitka-4.2.2-hotfix`（它同时提供依赖解析能力与可重定位 CPython 原料）。若按「载荷阶段化」改造后仍需该构建器，则 §7 必须显式登记第三项外部输入（文档契约，非 CLI 契约）。**（OQ-3 已裁定：保留该输入并按 FR-9 登记为第三项；同时删除 Stage 0 的 `pip download` wheelhouse，使 Stage 0 职责收敛为「制备可重定位最小 CPython」一项。）**

### 决策记录（人类裁定，覆盖先前口径）

| 编号 | 决策门 | 裁定 | 影响 |
|---|---|---|---|
| D1 | 分两步走 | 先只提交提案 spec（`9c72cb2e4` 已入库） | 已被 D3 取代其「本轮不触碰契约代码」部分 |
| D2 | 原件目录处置 | 迁移后删除 `client/overlays/native-dev/release/` | 仍有效，落为 FR-12 / Task 12 |
| D3 | 搬迁受阻后的处置 | **就地改写为合规产品后再删**——授权同时改动 `bin/relpack`、`tests/` 与客户契约文本 | 本 spec 的 Non-Goals、FR-5/6/7/10、AC-4/6、Process 全部按此重写 |
| D4 | OQ-1 wheel 源目录 | **新建 `apps/containers/workspace/dist`** 为唯一合法 wheel 源 | FR-2 的 `WHEEL_DIST`、Constraints Dependencies |
| D5 | 交付纪律 | **只提交，不推送**；中文 Conventional Commit | 全队列 |

> 逐字节搬迁「不可行」的取证结论：原件的 `Containerfile.release` 同时违反 §9（构建期装载荷）、§10（在线 `pip download` 闭包）、§7（Stage 0 引入第三外部输入）、§1（无 `release/` 骨架），且 `build-release.sh` 的 dist 路径三级上溯指向 `client/workspace/dist`（违反 §7 禁引用 `client/`）。因此「搬迁 = 复制加改路径」不成立，只能按 D3 就地改写。

## Functional Requirements

- **FR-1**: 新增 `apps/containers/offline-delivery/products/xmflow-cli/`，目录名与 `product.env` 的 `PRODUCT` 一致（`load_product_env` 强校验），内含 `product.env`、`Containerfile.xmflow-cli`、`.dockerignore`、`deps.txt`、`scripts/`、`smoke/`、`release/`（含 `payload/`）。
- **FR-2**: `product.env` 覆盖 `load_product_env` 必需 9 键；`IMAGE_NAME=localhost/xmflow-cli`（命名与本应用产品一致，避免与历史 `xmflow-release` 双标签漂移）；`CONTAINERFILE=Containerfile.xmflow-cli`；`WHEEL_GLOB`/`WHEEL_PREFIX` 指向 `xmnn-*.whl`；`WHEEL_DIST=../workspace/dist`（D4 裁定，实体目录本轮新建）；`BASE_IMAGE_DEFAULT=docker.io/library/ubuntu:26.04`；`RELEASE_DIR=release`；并按 FR-6 声明可选键 `FLAVORS="none|cpu"`、`TORCH_DEFAULT=none`（OQ-2 裁定：`none` = 底座不装 torch，`cpu` = 追加 PyTorch CPU 前端；不复用 `cpu|cu130`，因为 CLI 产品无 CUDA 形态）。
- **FR-3**: 镜像定义改造为**两段两物**：① 底座 `Containerfile.xmflow-cli` 产出 `<IMAGE_NAME>:base-<形态>`，只含可重定位最小 CPython + venv + 依赖面（`COPY deps.txt` 后 `pip install --no-cache-dir -r /tmp/deps.txt`，与 `Containerfile.xmnn-runtime` 同构，并保留 `PIP_MIRROR` 分支），构建上下文为产品目录且**不含 wheel**，绝不安装 `xmnn`，并以反断言兜底（venv 内 `import xmnn` 必失败、site-packages 无 `xmnn*`）；② 载荷由 `release/payload/Dockerfile` 在客户侧以 `--no-index --no-deps` 装入 `<IMAGE_NAME>:<交付版本>`。
- **FR-3b（OQ-3 裁定）**: **彻底删除原件 Stage 0 的 `pip download` wheelhouse**，依赖闭包改由 `deps.txt` 承担；Stage 0 只保留「制备可重定位最小 CPython」这一件事，其镜像 ref 以产品 Containerfile 内 `ARG BUILDER_IMAGE=localhost/native-dev:nuitka-4.2.2-hotfix` 表达——即作为**产品级常量**写在 `products/xmflow-cli/Containerfile.xmflow-cli` 里（与 `Containerfile.xmnn-runtime` 在文件内写 `ARG TORCH_VERSION=2.14.0` 同构），不进入 `product.env` 必需键、不进入 `bin/relpack`。
- **FR-4**: 依赖闭包从「构建期在线 `pip download`」改为 §10 语义的 `deps.txt`（由 `bin/relpack -p xmflow-cli deps --write` 生成、`deps` 校验），底座构建全程可离线；`torch` extras 的选择改由形态参数表达，不得在 Containerfile 内内嵌 `xmnn` 版本常量（§7）。
- **FR-5**: `release/` 交付骨架按 `xmflow` 命令面新建，但**控制脚本名必须仍为 `xmnnctl` 与 `xmnnctl.ps1`**——取证：`bin/relpack` 的 `cmd_smoke`/`smoke_final_down` 硬编码 `./xmnnctl load/up/smoke/down` 四步，`tests/test_release_skeleton.py` 的 `TRACKED` 清单与 `test_ctl_*` 系列、`tests/test_relpack_cli.py::test_smoke_step_calls_pass_command_only` 的 `re.fullmatch` 全部锁死该名称；改脚本名将构成 AC-4 禁止的**第二处** CLI 改动。脚本**内容**是产品私有的（本产品内 `img_ref="localhost/xmflow-cli:$ver"`），故不构成 CLI 改动。同理 `.env` / `.env.example` **必须保留键 `XMNN_VERSION`**（`cmd_smoke` 以 `grep -E '^XMNN_VERSION='` 解析交付版本）。骨架命令面为 `load`/`up`/`smoke`/`down`（`init`/`ps`/`logs`/`version` 按 §1 保留），另含 `payload/`、`.env.example`、`artifacts/.gitignore`、`workspace/.gitkeep`，遵守 §1 全部骨架不变量：零 `../`、零 Python、`pull_policy: never`、shebang 全 LF、挂载点为 `/workspace/models:ro` 与 `/workspace/temp`，**无 Jupyter 端口与凭证面**。
- **FR-6**: **对外契约修订（本提案唯一一处 CLI 改动）**：把形态白名单从 `bin/relpack` 的全局常量 `FLAVORS="cpu|cu130"` 下移为 `product.env` 的可选键 `FLAVORS`（未声明时回退全局常量，`check_enum` 的两处调用点与 fail-fast 打印不变），使 `xmflow-cli` 声明 `none|cpu`。`load_product_env` 允许额外键，故 `FLAVORS` 不进入必需 9 键。
  - **连带面（已由 D3 授权，属 tests/docs 文字而非 CLI 逻辑）**：`tests/test_relpack_cli.py` 中三处形态字面量必须改为产品驱动——L264/L272 的 `assert 'FLAVORS="cpu|cu130"' in text` 与「`TORCH_DEFAULT` ∈ 内联白名单」推导、L404 的 `assert product_env["TORCH_DEFAULT"] in ("cpu", "cu130")`；以及 `docs/00-overview.md` 形态白名单表述、`.agents/rules/delivery-pipeline.md` §4「形态白名单仅 `cpu|cu130`」文字。
  - `bin/lib/common.sh` 与 `bin/relpack` 的其余任何行、`products/xmnn-runtime/**` 的任何文件均不得改动。
- **FR-7**: 产品自有守卫：`smoke/_base_guards.py`（底座期，root 与 `xmnn` 双跑，含「载荷未安装」反断言、`deps.txt` 逐条已装、venv 可导入 `ssl/ctypes/sqlite3/lzma/bz2/zlib/decimal/pyexpat/venv` 的可重定位性断言，守卫项数量对齐 §11 的 6 项骨架）与 `smoke/_runtime_smoke.py`（交付期，对齐 §11 的 10 项 + `pip check`，判据收窄到 `^xmnn` 冲突行）。
  - **OQ-5 裁定：交付期守卫内不得包含 `SIM_VTA2.0` 编译冒烟**——载荷守卫运行于 `podman run --entrypoint /opt/xmflow/bin/python ... _runtime_smoke.py`，此时客户挂载的 `/workspace/models` 在派生构建阶段不可能预挂；且「镜像不含示例模型」是 `USAGE` §6 的既有承诺。改为 `xmflow --help`/子命令存在性 + 关键工具与模块可用性检查；真机编译冒烟以 `release/README.md` 文档形式给出可直接粘贴的 `xmflow compile -n demo.caffe.resnet50` 命令，由客户自备模型组后执行。
  - 按 §11 末句把守卫项清单同步进骨架 README、`docs/` 与守卫测试三处。
- **FR-8**: 客户契约文本完整迁移：`USAGE.zh-CN.md` 7 节（标签表、快速开始、模型组目录契约、常用命令、真机网络、镜像内容边界、FAQ）逐节落入 `release/README.md` 或 `docs/`，命令示例改用最终镜像名与新形态标签；`--network host`、`chmod 0777 temp` / `--user` 规避 uid、`0x7F7F` 毒值判读三条排障口径必须保留。
- **FR-9**: 按 §7 把「构建器镜像」登记为**第三项外部输入**（OQ-3 裁定保留，因可重定位最小 CPython 的制备依赖 conda cp314 原料，本轮不引入 `python-build-standalone` 等新第三方二进制源）。落点为**文档契约、非 CLI 契约**：`.agents/rules/delivery-pipeline.md` §7 的外部输入清单由「仅此两项」改为三项，并写明该输入的产出方（`client` 的 native-dev 构建链）与边界（厂商侧构建期输入，不作为构建依赖进入交付链、不出现在 `product.env` 必需键与 `bin/relpack`）；`docs/00-overview.md` 的「输入」条目同步改为三项。
- **FR-10**: 测试具备多产品能力，并采用**两层拆分**口径（这是「假产品零改测试」能够成立的唯一前提）：
  - **通用不变量层**：`tests/conftest.py` 的产品名由 `PRODUCT_NAME = "xmnn-runtime"` 常量改为按 `products/*/` 自动发现并参数化；只断言与产品无关的 §1 骨架不变量（`TRACKED` 文件清单结构、零 `../`、零 Python、`pull_policy: never`、CR=0 与 shebang 全 LF、`xmnnctl`/`xmnnctl.ps1` 命令面集合、`.env.example` 含 `XMNN_VERSION`、归档内不含 `payload/*.whl`）。该层**自动覆盖任何产品目录，含最小假产品**。
  - **产品私有契约层**：与产品形态强耦合的字面量（`xmnn-runtime` 的服务名 `xmnnrt`、`2225/8893` 端口映射、environment 四键、`/var/lib/jpman/ssh-host-keys` 与 named volume `xmnn-ssh-host-keys`、`.env.example` 8 键精确集合、`--entrypoint /opt/conda/bin/python`、`COPY xmnn-*.whl`、`su -s /bin/bash devuser`；`xmflow-cli` 的 `--entrypoint /opt/xmflow/bin/python`、`/workspace/models:ro` + `/workspace/temp` 挂载对、无端口发布）集中放入 `tests/` 内的 **per-product 契约 registry**，按产品名查表；新产品接入时**只增 registry 条目，不改测试函数**。
  - 既有 `xmnn-runtime` 用例必须**全绿且断言语义不变**（字面量原样搬入 registry，不得放宽）。
- **FR-11**: 文档登记四件套 + 变更日志：`docs/README.md`、`docs/00-overview.md`、`docs/01-quickstart.md`（§5 示例引用新产品）、`.agents/CHANGELOG.md` 追加条目（沿用 `日期 | type | 摘要` + 「关联七概念场景」「背景与动机（I）」「本任务落地」格式）。
- **FR-12**: 清理（OQ-6 裁定）：先删除未跟踪的 `apps/containers/client/overlays/native-dev/release/` 整目录（其内容与 `assets/` 逐字节相同，已由 md5 取证坐实为纯副本，删除不损失任何信息）；再在实现全部落地后删除本 `assets/` 留档。可追溯性由**三道凭据**保证，不需保留重复副本：① `assets/` 三文件的入库与删除各自留有 commit 记录（`9c72cb2e4`、`2daf20131` 与本次 feat）；② Task 12 的「三文件内容去向对照表」逐节写明每处内容落到哪个文件哪个章节；③ 本 spec 正文保留实测 md5 与行数。对照表未产出前不得执行删除。

## Non-Functional Requirements

- **NFR-1**: 零回归：`xmnn-runtime` 产品的 `relpack` 命令面、交付骨架文件清单、`release.json` schema v2 字段、守卫项语义均保持等价。
- **NFR-2**: 底座体积目标不劣于原件：`<IMAGE_NAME>:base-<形态>`（不含载荷）应显著小于原件的 1.18 GB 整体镜像，且派生增量与 §9 的约 0.18 GB / 1-3 分钟量级可比（须实测记录，不得臆断）。
- **NFR-3（口径修订）**: **「离线」限定于客户侧**。厂商侧底座构建与 `Containerfile.xmnn-runtime` 现状一致，允许经 `PIP_MIRROR`（官方 / tuna / aliyun）在线安装 `deps.txt` 与 torch 索引——既有产品 Layer 2 实为在线 `pip install -r deps.txt ipykernel`，原 NFR-3「底座构建不访问任何 pip 索引」与既有事实冲突，故作废。真正的离线不变量只有两条且必须守住：① 客户侧派生只用 `--no-index --no-deps`，载荷 wheel 随归档交付；② 交付归档内不含任何需联网才能完成的步骤。
- **NFR-4**: 所有新增脚本零 Python 依赖（bash 4+ / pwsh 7.4+），失败路径给出中文、可执行、指向下一步的指引。
- **NFR-5**: 行尾纪律：新增 POSIX 脚本与文本一律 LF；无 `.sh` 后缀的 CLI 文件须按 `.gitattributes` 既有惯例追加显式 `**/<name> text eol=lf` 规则（该文件注释已说明原因：shebang 由内核解析，脚本内无法自救）。因 FR-5 裁定控制脚本仍名 `xmnnctl`，根 `.gitattributes` 的既有规则已覆盖该名称，**本提案预计无需新增行尾规则**；若实盘 `git check-attr` 显示未覆盖，唯一修法为 `git add --renormalize .`。
- **NFR-6**: 治理文档同步：`offline-delivery/AGENTS.md`（若含产品清单）、`.agents/rules/delivery-pipeline.md`（形态白名单与外部输入条款）、`apps/containers/AGENTS.md` 相关表述。

## Constraints

- **Technical**: 不得引用 `apps/containers/client/` 与 `shared/` 任何路径或代码（§7）；不得固定 uid（base 镜像已占 uid 1000）；镜像仅支持 x86_64；wheel 的 `Requires-Python >=3.14.6` 决定必须使用可重定位 CPython 3.14.7 而非 `ubuntu:26.04` 的 apt python 3.14.4。
- **Business**: `release/` 骨架与 `USAGE` 契约文本是客户可见承诺，改版须走提案。**OQ-4 裁定**：`xmflow-release:1.2.1` / `:1.2.1-torch` 从未对外承诺过（原件未提交、镜像未出归档、无交付记录），故无需迁移策略——直接收敛为 §3/§4 语义：底座 `<IMAGE_NAME>:base-<形态>`，交付 tag 由客户侧 `payload/Dockerfile` 派生下发；`USAGE` §1 的标签表按新命名重写，历史 tag 至多在文档中以一行说明留痕。
- **Dependencies**: 验证依赖真机 podman 5.6.2 与其上的 `ubuntu:26.04`、`native-dev:nuitka-4.2.2-hotfix`；载荷 wheel 依赖 D4 裁定后新建的 `apps/containers/workspace/dist/`（当前不存在，须由 `client/workspace/dist` 内同名 wheel server-side 复制落位，该目录被 `.gitignore` 忽略、不入库）；pytest 7.1.2（python 3.8.10）可跑静态守卫测试。**注意**：宿主直连 `download.pytorch.org` 不可达，`scripts/install-torch.sh` 须支持 `TORCH_INDEX` 覆盖，实盘用 aliyun pytorch-wheels 镜像。
- **Process**: spec 批准门已由 D3 通过，本队列的 spec/tasks 与实现合并为**同一笔 `feat(offline-delivery)` 中文 Conventional Commit**，**只提交、不推送**；Task 5 是唯一允许的 CLI 改动，发现需第二处改动立即停止并按 §7 尾注自查。

## Assumptions

- xmnn wheel 的 CLI 命令面（`xmnn.cli.xmflow:app`，见 `client/overlays/native-dev/builder/pyproject.toml` L34-36）在交付版本区间内保持稳定，`ENTRYPOINT` 可直接依赖 console script 而不需源码树。
- 依赖解析结果（原件 Stage 0 的 `pip download` 闭包）与 §10 的 `deps.txt` 集合在去掉 torch 后基本等价；差异须由 `deps` 校验实测暴露，不在提案中假设无差异。
- 可重定位最小 CPython 的制备可以在「不依赖 conda 镜像」的前提下由另一可控输入替代（例如官方 `python-build-standalone`），但本提案**不**引入新的第三方二进制源——OQ-3 据此裁定保留构建器镜像，并按 FR-9 登记为第三项外部输入。
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
- **Then**: 五步全部零退出；`pack` 产出归档经 `gzip -t` 校验且 `release.json` 的 `payload.sha256` 与 `archive.sha256` 均可按 §12 块定向读出；**客户侧派生（`payload/Dockerfile`）全程只用 `--no-index --no-deps`**，构建日志内无任何索引 URL（口径依 NFR-3 修订，厂商侧底座构建允许 `PIP_MIRROR`）
- **Pass Condition**: `smoke` 走交付骨架 `./xmnnctl load/up/smoke/down` 四步全绿（脚本名依 FR-5 裁定保持 `xmnnctl`）
- **Evidence**: 命令输出、`release.json` 内容、归档 size/sha256

### AC-4: 对外契约修订面收敛
- **Type**: `rule`
- **Given**: 实现提交
- **When**: `git show --stat` 与 `git diff` 检视 `bin/`、`tests/`
- **Then**: `bin/relpack` 的改动**仅**为形态白名单下移一处（FR-6），`bin/lib/common.sh` **零改动**；`products/xmnn-runtime/**` 无任何改动；`xmnn-runtime` 既有测试断言语义不变（`tests/` 内允许改动的面严格限定为 FR-6 列出的三处形态字面量与 FR-10 的参数化改造，不得夹带其他放宽）
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
- **Given**: `tests/` 按 FR-10 完成**两层拆分**改造后
- **When**: 新增一个最小假产品目录（仅 `product.env` + 骨架文件清单，**不**在 per-product registry 中登记）并在本地跑 `pytest`
- **Then**: **通用不变量层**自动覆盖该假产品且无需修改测试代码；**产品私有契约层**因 registry 无该条目而显式 skip（不得静默通过，也不得因此失败）；删除假产品后 `xmnn-runtime` 与 `xmflow-cli` 用例结果不变
- **Pass Condition**: 通用不变量层的用例收集数随产品目录数线性变化（可观察）；出现「必须改测试函数才能接入假产品」即判不通过
- **Evidence**: `pytest --collect-only -q` 前后对比、registry skip 输出

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

## Open Questions（全部已裁定，2026-10-09）

- **OQ-1（已裁定）** ~~wheel 源目录矛盾~~：人类裁定 **新建 `apps/containers/workspace/dist`** 为唯一合法 wheel 源目录（D4）。§7 的 `WHEEL_DIST=../workspace/dist` 保持不变，载荷 wheel 由 `client/workspace/dist` server-side 复制落位；不把 `client/workspace/dist` 登记为合法上游输入（§7 禁引用 `client/` 的红线不破）。`extract-offline-delivery-app` 记录的双目录历史成因由此收敛。落点见 FR-2 与 Constraints Dependencies。
- **OQ-2（已裁定）** 形态集命名为 **`FLAVORS="none|cpu"`、`TORCH_DEFAULT=none`**。判据：与 `USAGE` §1 的两档客户实物一一对应（`none` = 不装 torch，`cpu` = 追加 PyTorch CPU 前端），不引入 `cu130`（CLI 产品无 CUDA 面，属另一提案）。因此底座归档名为 `xmflow-cli-base-none.tar.gz` / `xmflow-cli-base-cpu.tar.gz`（§3/§4 语义），缺省形态出 `base-none`。否决 `base|torch` 命名的理由：`base` 与 §4 的「形态」维度语义冲突（底座本身就叫 base）。连带改动面见 FR-6。
- **OQ-3（已裁定）** **不移出交付链，但删除 wheelhouse**。Stage 0 的 `pip download` 在线解析闭包**彻底删除**（改由 `deps.txt` 承担，FR-3b/FR-4）；Stage 0 只保留「制备可重定位最小 CPython」，其镜像 ref 作为产品 Containerfile 内的 `ARG BUILDER_IMAGE` 常量。构建器镜像按 **FR-9** 登记为 §7 的第三项外部输入（文档契约），产出方为 `client` 的 native-dev 构建链，边界为「厂商侧构建期输入，不作为构建依赖进入交付链」。不引入 `python-build-standalone` 等新第三方二进制源（见 Assumptions）。
- **OQ-4（已裁定）** 旧 tag **未对外承诺**，无需迁移策略，直接按 §3/§4 收敛命名（见 Constraints Business）。
- **OQ-5（已裁定）** **守卫内不含编译冒烟，不随镜像提供示例模型**。「镜像不含示例模型」是 `USAGE` §6 的既有承诺，且载荷守卫运行于派生构建阶段、`/workspace/models` 不可能预挂。交付期守卫改为 `xmflow --help` / 子命令存在性 / 关键工具与模块可用性检查；真机编译冒烟以 README 文档形式给出可粘贴命令（见 FR-7）。
- **OQ-6（已裁定）** `assets/` **按 FR-12 删除**，不留重复副本。可追溯性由 commit 记录（`9c72cb2e4`、`2daf20131`、本次 feat）+ Task 12 的「三文件内容去向对照表」+ 本 spec 正文的实测 md5/行数三道凭据保证。`extract-offline-delivery-app` 的 spec 目录保留大量附加文件，是因为那些附加文件本身即被迁移对象的唯一副本；本例的原件已入库，副本无必要。
