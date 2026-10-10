---
title: "第二交付产品 xmflow-cli 提案 - Implementation Plan"
status: "approved"
---

# 第二交付产品 xmflow-cli 提案 - Implementation Plan

> 方法链路：I（问题与证据）→ F（约束与方案）→ R（任务拆解）→ T（实施）→ V（验证）→ C（收编登记），场景 3「重构优化」；质量门 G1-G4 由 `TRAE-spec-mode` 批准门与 `review.md` 承担。
>
> 前置约束：本队列**全部任务属后续 feat**，须先通过 spec 批准门；Task 5 是本提案唯一允许的对外契约改动，任何额外 CLI 改动须回到 `delivery-pipeline.md` §7 尾注自查。
>
> 官方落地路径参照：`apps/containers/offline-delivery/docs/01-quickstart.md` §5「新增第二个交付产品」5 步。

## Task 1: 澄清阻塞性开放问题并定稿接入方案
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 就 `spec.md` 的 OQ-1（wheel 源目录与 §7 禁引用 `client/` 的矛盾）、OQ-2（`xmflow-cli` 形态集命名与 tag 影响）、OQ-3（Stage 0 可否移出交付链）取得人类裁定，并把结论回写进 `spec.md`（含必要的 Constraints 调整）。
  - 产出一页方案定稿：底座/载荷切分边界、deps.txt 生成口径、骨架命令面（沿用 `xmnnctl` 或改 `xmflowctl`）。
- **裁定结论（已回写 spec.md）**：
  - OQ-1 → 新建 `apps/containers/workspace/dist` 为唯一合法 wheel 源（D4）；`client/workspace/dist` 不被引用。
  - OQ-2 → `FLAVORS="none|cpu"`、`TORCH_DEFAULT=none`；归档名 `xmflow-cli-base-<形态>.tar.gz`。
  - OQ-3 → 保留构建器镜像为 §7 第三外部输入（文档契约，FR-9），但删除 Stage 0 的 `pip download` wheelhouse（FR-3b）。
  - OQ-4 → 旧 tag 未对外承诺，直接收敛命名。
  - OQ-5 → 守卫不含 `SIM_VTA2.0` 编译冒烟、不随镜像提供示例模型；编译冒烟降级为 README 可粘贴命令。
  - OQ-6 → `assets/` 按 FR-12 删除，以对照表为前置。
  - 附带修正的规范内部矛盾：NFR-3/AC-3 的「离线」口径收窄到客户侧；FR-5 锁死控制脚本名 `xmnnctl` 与 `.env` 键 `XMNN_VERSION`；FR-6 列出 tests/docs 连带面；FR-10/AC-6 改为「通用不变量层 + per-product registry」两层。
- **Acceptance Criteria Addressed**: AC-4、AC-8
- **Test Requirements**:
  - `rule` TR-1.1: `spec.md` 的 Open Questions 三条均为「已裁定」状态且有裁定依据（人类批复记录或条款引用）；Evidence = spec.md diff 与批复原文 —— **已满足**：六条 OQ 全部标注裁定依据（D3/D4 批复原文或条款号）
  - `rule` TR-1.2: 定稿明确写出「底座不含 wheel、载荷只在 `payload/Dockerfile`」与 §9 条款号对应；Evidence = 方案文档片段 —— **已满足**：FR-3 ①② 与 FR-3b
- **Notes**: 未完成本任务不得进入 Task 3 之后任何写代码动作。**本任务已完成，门禁解除。**

## Task 2: 建 `products/xmflow-cli/` 与 `product.env`
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建目录，`product.env` 覆盖 `load_product_env` 必需 9 键（`PRODUCT IMAGE_NAME CONTAINERFILE WHEEL_GLOB WHEEL_PREFIX WHEEL_DIST BASE_IMAGE_DEFAULT TORCH_DEFAULT RELEASE_DIR`），`PRODUCT` 等于目录名，`BASE_IMAGE_DEFAULT` 取 `docker.io/library/ubuntu:26.04`。
  - 按 OQ-2 裁定取值：`FLAVORS="none|cpu"`、`TORCH_DEFAULT=none`；`WHEEL_DIST=../workspace/dist`（D4，与 xmnn-runtime 同构）；归档名相应为 `xmflow-cli-base-none.tar.gz` / `xmflow-cli-base-cpu.tar.gz`。
  - `FLAVORS` 作为可选键先写入 `product.env`。实测机理：`load_product_env` 以 `. product.env` 直接 source，且发生在 `bin/relpack` L240 的 `check_enum` **之前**，故该键一经写入即已生效（`FLAVORS="none|cpu"` 覆盖 L27 全局常量）——这是依赖赋值顺序的**隐式行为**。Task 5 的目标不是让它生效，而是把这一隐式覆盖**固化为显式的「产品可选键优先、缺省回退全局常量」**语义。
- **实测更正（2026-10-09）**：`product.env` 内的 `FLAVORS` 值**必须保留双引号**。`load_product_env` 以 `. product.env` 直接 source，`FLAVORS=none|cpu` 不加引号会被解析为管道（左端 `none` 命令不存在），在 `set -euo pipefail` 下立即终止。连带结论供 Task 9 使用：`tests/conftest.py::product_env` 的朴素解析会**连引号一起返回**，测试断言须显式去引号后再比对白名单。
- **Acceptance Criteria Addressed**: AC-3、AC-4
- **Test Requirements**:
  - `rule` TR-2.1: `bin/relpack -p xmflow-cli version`（或等价的上下文打印）成功打印「产品/形态/镜像/版本」四元组且无缺键报错；Evidence = 命令输出 —— **已满足**：`bin/relpack -p xmflow-cli stage` rc=0，上下文行打印 `[info] 产品=xmflow-cli | 形态=none | 镜像=localhost/xmflow-cli:base-none | 版本=1.2.1.dev0`，无缺键报错
  - `rule` TR-2.2: `PRODUCT` 与目录名一致、9 键齐全（静态断言用例）；Evidence = `tests/` 用例名与通过结果 —— **归 Task 9**（`load_product_env` 的必需键校验已在 TR-2.1 实跑中生效）

## Task 3: 底座 Containerfile 阶段化改造
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 以 `assets/Containerfile.release` 为素材重写 `Containerfile.xmflow-cli`：只保留可重定位最小 CPython 制备与 venv 创建 + 依赖面安装，**删除构建期安装 xmnn 的 Layer**；构建上下文为产品目录且不含 wheel。
  - 依 OQ-3 裁定（FR-3b）：**同时删除 Stage 0 的 `pip download` wheelhouse**，Stage 0 仅保留「制备可重定位最小 CPython」；构建器镜像以产品 Containerfile 内 `ARG BUILDER_IMAGE=localhost/native-dev:nuitka-4.2.2-hotfix` 表达（产品级常量，与 `ARG TORCH_VERSION=2.14.0` 同构），**不进** `product.env` 必需键、**不进** `bin/relpack`。
  - 新增 `.dockerignore`；不在 Containerfile 内内嵌 `xmnn` 版本常量（§7）。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 底座文件内不出现 `xmnn`/`xmflow` 安装语句与 wheel 文件名（`grep` 断言为空）；Evidence = grep 命令与输出
  - `rule` TR-3.2: 底座构建上下文内无 `*.whl`；Evidence = `podman build` 上下文上传日志或 `.dockerignore` 断言
  - `rubric` TR-3.3: 与 `Containerfile.xmnn-runtime` 的 Layer 结构一致性（注释口径、LABEL 键集、`org.specweave.*` 命名）；scale 1-5;anchors 1=结构随意、3=主要 Layer 对齐但 LABEL 缺失、5=结构/LABEL/注释三者与本应用惯例同构;threshold >= 4;evidence = 两文件对照
- **实施记录（2026-10-09，交付物：`Containerfile.xmflow-cli`、`.dockerignore`、`scripts/relocate-cpython.sh`、`scripts/install-torch.sh`）**：
  - TR-3.1 **已取证**：对 `Containerfile.xmflow-cli` 精确 `grep -nE 'pip install [^|]*xmnn|xmnn==|xmnn\[|\.whl|COPY .*whl'` → rc=1 零命中；`COPY` 源仅 `deps.txt`/`scripts/`/`smoke/` 与 `--from=cpython`，无 wheel。
  - TR-3.2 **已取证（结构性）**：`.dockerignore` 首条即 `**/*.whl`，另忽略 `wheels/`；构建上下文 = 产品目录，`find . -type f` 实测目录内无任何 `.whl`。`podman build` 上下文上传日志归 Task 10。
  - TR-3.3 说明：Layer/LABEL/头注口径与 `Containerfile.xmnn-runtime` 同构（LABEL 用 `org.specweave.*` 七个规范键，全部 RUN 显式 `/bin/bash -lc`，含引号逻辑固化为脚本、RUN 行不写内层 `python -c`）。**有意偏离两处并已在文件注释写明理由**：① Layer 顺序改为「`deps.txt` 先于 torch」——本产品默认形态为 `none`，xmnn-runtime「复用 torch 层 200MB CUDA 缓存」的收益不成立，改为优先保证 pip 索引配置单点化；② 新增产品私有键 `org.specweave.cpython="cp314-relocated-conda-prefix"`。
  - **实测新增必要项（原 `assets/` 素材缺失，属构建阻断级）**：`docker.io/library/ubuntu:26.04` **无** `/etc/ssl/certs/ca-certificates.crt`，而 conda CPython 的 OpenSSL 编译期内定默认校验路径为 `cafile=/opt/conda/ssl/cert.pem`；原件 Stage 0 的 relocate 未搬 `ssl/`，因其只做 `pip install --no-index`，从不走 TLS 校验。改造后 Layer 2 需联网装 `deps.txt`，**不搬 `ssl/` 即构建必挂**，故 `relocate-cpython.sh` 显式搬迁 `${SRC_PREFIX}/ssl` 并在缺失时 `exit 1`。底座把 `/pybase/` 落到 `/opt/conda/`，前缀与内定路径天然对齐，无需 `SSL_CERT_FILE`。
  - **实测体积更正**：Stage 0 在 builder 内实跑 `du -sh /pybase` = **80M**（原 `assets/Containerfile.release` 注释「约 40 MB」不实，已按实测口径记录）；同次实跑还验证 `relocated python: 3.14.7`、`ssl cafile: /opt/conda/ssl/cert.pem exists: True`，以及以 `/pybase` 建 venv 后联网 `pip install tabulate` 成功（`pip 26.2.1`）。

## Task 4: `deps.txt` 生成与离线化
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 用 `bin/relpack -p xmflow-cli deps --write` 生成产品 `deps.txt`（§10 语义：wheel METADATA 中无分号 marker 的 `Requires-Dist`，torch 除外），底座 Containerfile 改为 `pip install -r deps.txt`。
  - 记录与原 Stage 0 `pip download` 闭包的差异清单（原件产物为对照），并对差异作结论。
- **Acceptance Criteria Addressed**: AC-2、AC-3
- **Test Requirements**:
  - `rule` TR-4.1: `bin/relpack -p xmflow-cli deps` 校验通过（rc=0；若缺 unzip/bsdtar 只 `[WARN]` 则如实记录）；Evidence = 命令输出
  - `rule` TR-4.2: 依 NFR-3 修订口径——「离线」判据落在**客户侧**：客户在已装底座的派生构建中以 `--no-index --no-deps` 装载荷成功；底座自身构建允许访问 `deps.txt` 所需索引（与 `Containerfile.xmnn-runtime` Layer 2 同构）；Evidence = 派生构建日志 + `release.json`
  - `rubric` TR-4.3: 与在线 `pip download` 闭包的差异解释质量；scale 1-5;anchors 1=未比对、3=列出差异未解释、5=差异逐条定位到 marker/extras/平台轮子原因并有处置结论;threshold >= 4;evidence = 差异表
- **实施记录（2026-10-09）**：
  - TR-4.1 **已取证**：`bin/relpack -p xmflow-cli deps --write` → `[ OK ] 依赖集已写入：products/xmflow-cli/deps.txt（20 项无条件依赖；来源 xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl）`；`bin/relpack -p xmflow-cli deps` → `[ OK ] 依赖集一致：products/xmflow-cli/deps.txt（20 项无条件依赖）`，rc=0。宿主工具实测：`unzip` 在位（校验走 `unzip -p` 主路径），`bsdtar` 缺失但**未触发 `[WARN]`**；`diff`、`sha256sum` 在位。`deps.txt` CR=0。
  - TR-4.2 **未在本任务取证**：判据落在客户侧派生构建（`--no-index --no-deps` 装载荷），其日志与 `release.json` 属 Task 7/Task 10 产物。本任务先给出**同向的机器证据**（见下「双向闭合」），不以此冒充派生构建结论。
  - **对照物（原件产物）**：`localhost/xmflow-release:1.2.1`（即 2026-10-09 用 `assets/Containerfile.release` 以 `TORCH_VARIANT=0` 实建的镜像，恰对应本产品 `none` 形态）内 `/opt/xmflow/bin/python -m pip freeze` 共 38 个分布 + `xmnn==1.2.1.dev0`。
  - **双向闭合**：在该原件镜像内执行 `pip install --dry-run --no-index -r deps.txt` → rc=0：`deps.txt` 的 20 项全部 `Requirement already satisfied`，pip 同时枚举出的 18 项传递依赖也全部命中已装分布（`--no-index` 下零联网）⇒ `deps.txt` 解析闭包 ⊆ 原件闭包；反向：原件 38 项 − `deps.txt` 20 项 = 18 项，与 dry-run 枚举的传递集合**逐名相等** ⇒ 原件闭包 ⊆ `deps.txt` 闭包 ∪ {xmnn}。故除载荷 wheel 外，两侧**集合相等**。
  - **差异清单与结论**：

| 类别 | 条目 | 归因 | 处置结论 |
| --- | --- | --- | --- |
| 载荷 wheel | `xmnn==1.2.1.dev0`（原件有、`deps.txt` 无） | 原件 Stage 0 以 `pip download ... /tmp/${WHL}` 连载荷本体一起下载并在构建期装入镜像 | **唯一实质差异，且方向正确**：依 §9 / FR-3 底座-载荷分离 P0，底座不得消费 wheel；`deps.txt` 不含 `xmnn`，Containerfile 零安装语句（TR-3.1 grep rc=1 已取证）；载荷改由 `release/payload/` 随包发出、派生构建时 `--no-index --no-deps` 装入 |
| 传递依赖（18 项） | `annotated-doc`、`contourpy`、`cycler`、`et_xmlfile`、`fonttools`、`iniconfig`、`kiwisolver`、`markdown-it-py`、`mdurl`、`ml_dtypes`、`packaging`、`pluggy`、`Pygments`、`pyparsing`、`python-dateutil`、`shellingham`、`six`、`wcwidth` | §10 口径只取**直接**无条件 `Requires-Dist`、不展开闭包；原件 Stage 0 的 `pip download` 递归拉了全闭包 | **非缺口**：Layer 2 用 `pip install -r deps.txt`，pip 在解析期自动拉取这 18 项；已由「双向闭合」逐名验证集合相等，无需把它们写进 `deps.txt`（写入反而会造成与 METADATA 漂移、破坏 `deps` 守卫的稳定性） |
| extras 依赖 | `build`、`scikit-build-core`、`opencv-python-headless`、`torch`、`torchvision`、`onnx2pytorch` | METADATA 中这些条目带 `; extra == "..."` marker（含分号）被 §10 口径排除；原件 Stage 0 同样未请求任何 extras | **两侧一致，差异为 0**；PyTorch 前端不属底座依赖面，改由 Layer 3 `scripts/install-torch.sh` 在 `--torch cpu` 下显式提供（`none` 形态不装），与 `torch-flavor` LABEL 双键一致 |
| 环境 marker 依赖 | `importlib-metadata`、`exceptiongroup`、`typing-extensions` backport 之类的条件条目 | 带 `;` marker（`python_version` / `platform_system` 等）被排除；cp314 + Linux 下这些 marker 均不成立 | **无需纳入**：原件 `pip freeze` 中除 `typing_extensions`（无条件声明）外无任何 marker-only 分布，与排除口径吻合 |
| 平台轮子与选版 | 具体版本如 `numpy==2.5.3`、`pandas==3.0.6`、`protobuf==7.36.2`、`typer==0.27.3` | `deps.txt` 全为 `>=` 下界约束、不 pin 版本；原件选版来自 aliyun 索引在 cp314/`manylinux_2_28` 平台的解析结果 | **可复现**：同一索引 + 同一 ABI 约束下解析结果一致；`deps` 守卫只比依赖名集合不比版本，故 pin 反而与 §10 语义冲突。构建期需访问索引属 NFR-3 修订后的允许范围（离线判据在客户侧） |

## Task 5: 形态白名单下移（唯一对外契约修订）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 把 `bin/relpack` L27 的 `FLAVORS="cpu|cu130"` 改为「`product.env` 可选键 `FLAVORS` 优先、缺省回退全局常量」；确认 `xmnn-runtime` 行为逐字不变。
  - 同步 `tests/test_relpack_cli.py`、`docs/`（quickstart §5 与 overview 的形态表述）、`.agents/rules/delivery-pipeline.md` 中受影响的条款文字。
  - 依 FR-6「连带面」逐处定位（属 tests/docs 文字，非 CLI 逻辑）：`test_relpack_cli.py` L264/L272 的 `assert 'FLAVORS="cpu|cu130"' in text` 与「`TORCH_DEFAULT` ∈ 内联白名单」推导、L404 的 `assert product_env["TORCH_DEFAULT"] in ("cpu", "cu130")`；`docs/00-overview.md` 形态白名单表述；`delivery-pipeline.md` §4「形态白名单仅 `cpu|cu130`」文字。`bin/lib/common.sh` 与 `bin/relpack` 其余任何行、`products/xmnn-runtime/**` 均不得改动。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-5.1: 未声明 `FLAVORS` 的产品仍以 `cpu|cu130` 校验，非法形态仍 fail-fast 并打印白名单；Evidence = 用例输出
  - `rule` TR-5.2: `xmflow-cli` 用 Task 1 裁定的形态集通过校验，且 `BASE_REF`/`ARCHIVE_BASE` 按形态正确拼装；Evidence = `print_context` 输出
  - `rule` TR-5.3: `bin/` 与 `tests/` 的 diff 仅涉及本项语义（`git show --stat` 可复核）；Evidence = diff 摘要
- **Notes**: 若实施中发现必须第二处改 CLI，立即停止并按 §7 尾注把常量收回 `product.env`，而不是扩大改动。
- **实施记录（2026-10-09）**:
  - **改动面（共 6 文件）**：`bin/relpack` 两处——L27 `FLAVORS="cpu|cu130"` 重命名为 `FLAVORS_DEFAULT="cpu|cu130"`（注释改「全局缺省」口径）、main 内 `load_product_env` 之后固化 `FLAVORS="${FLAVORS:-$FLAVORS_DEFAULT}"`（含 FR-6 注释）。属**同一契约修订**（白名单下移）的两个编辑点；`check_enum` 两处调用点与 fail-fast 打印逐字未动，L13 帮助文本未动，`usage` 行区间 3-19 无漂移（`-h` 首尾行实测一致）。`tests/test_relpack_cli.py` 三处——L12 docstring 形态白名单表述、`test_delivery_version_and_flavor_rules` 改断言 `FLAVORS_DEFAULT` + 固化行存在且白名单产品驱动（新增共享 helper `_flavor_whitelist`：可选键优先、回退从 relpack 文本解析全局缺省、并守卫 `FLAVORS` 值必须带双引号）、`test_product_env_matches_disk_layout` 的 `TORCH_DEFAULT` 断言改白名单成员判定（签名加 `bin_dir`）。docs 三处——`.agents/rules/delivery-pipeline.md` §4（白名单改「可选键 `FLAVORS` 声明、未声明回退全局缺省 `cpu|cu130`」；L52 cpu/cu130 互斥 rationale 属 xmnn-runtime 场景解释，保留）、`docs/00-overview.md` 中间产物形态表述、`docs/01-quickstart.md` `build` 段补白名单驱动与 fail-fast 时机说明。
  - **TR-5.1 取证**（WSL openKylin bash，本地 temp 副本内容同 SMB）：`bash -n bin/relpack` SYNTAX_OK；`-p xmnn-runtime version` → `形态=cpu`、`localhost/xmnn-runtime:base-cpu`、`xmnn-runtime-base-cpu.tar.gz`（回退路径行为逐字不变）；`TORCH_FLAVOR=none` → `[ERR ] 非法形态：none（白名单 cpu|cu130）` fail-fast ✓。
  - **TR-5.2 取证**：`-p xmflow-cli version` → `形态=none`、`base-none`、`xmflow-cli-base-none.tar.gz`；`TORCH_FLAVOR=cpu` → `base-cpu`、`xmflow-cli-base-cpu.tar.gz`；`-p xmflow-cli build --torch cu130` → `非法形态：cu130（白名单 none|cpu）`（先于 `require_podman`，daemon-free 验证成立）✓。
  - **TR-5.3 取证**：`git diff --stat -- bin tests docs .agents` = 5 文件 +30/−11（relpack +4/−1、tests +19/−6、docs/rules 各 +3~5/−1~2）；`git diff --stat -- products bin/lib` 空输出（禁区零改动，AC-4 复核通过）。
  - **pytest**：SMB/UNC 直跑 70/73 过，3 例失败均为 WSL bash 桥接无法读取 `\\10.16.11.3` UNC 路径的环境限制（`bash -n` 与 smoke-step 真实行为用例，报 `//10.16.11.3/...: No such file or directory`，与 FR-6 语义无关）；同内容同步到本地盘副本重跑 **73 passed** 全绿 ✓。relpack 保持 LF（字节级检测无 `0x0D`）。
  - **已知局限登记**：`bin/relpack.ps1` L24 `$Flavors = @('cpu','cu130')` 未参数化——改动它即构成第二处 CLI 契约改动（D3 禁止），故不动；pwsh 桥接对 `xmflow-cli` 的 `-Torch none` 会误拒，Windows 侧需用 `bin/relpack`（WSL bash）作为该产品交付入口。`AGENTS.md` L82 与 `README.md` L63 的白名单表述属治理文档，按既定归属留待 **Task 11** 同步。

## Task 6: 产品自有守卫（底座期 + 交付期）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新写 `products/xmflow-cli/smoke/_base_guards.py`（root 与 `xmnn` 双跑；含「载荷未安装」反断言、可重定位 CPython 关键扩展 import 断言、`deps.txt` 逐条已装、`pip check` 判据收窄）与 `smoke/_runtime_smoke.py`。
  - 依 OQ-5 裁定：`_runtime_smoke.py` **不含** `SIM_VTA2.0` 编译冒烟（派生构建时 `/workspace/models` 不可能挂载，且「镜像不含示例模型」是既有承诺）；改为 `xmflow --help` + 子命令存在性 + 工具/模块可用性检查，真机编译冒烟以 README 可粘贴命令形式给出。
  - 按 §11 末句把守卫项清单同步进骨架 README、`docs/` 与守卫测试。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 底座守卫在两用户下全绿，且反断言在「误装 xmnn」时确实失败（做一次故意污染验证）；Evidence = 两次运行输出对比
  - `rule` TR-6.2: 守卫项数量与文档列表一致（骨架 README / docs / 测试三处同步）；Evidence = 三处列表截图或行号
  - `rubric` TR-6.3: 守卫断言对客户契约风险的覆盖度（相对 `_base_guards.py` 6 项与 `_runtime_smoke.py` 10 项的等价映射）；scale 1-5;anchors 1=仅 --help、3=覆盖主要运行面但缺可重定位性与权限面、5=每项均有既有产品对应物且新增 CLI 特有断言（uid/挂载写权限/`--network host` 降级说明）;threshold >= 4;evidence = 断言对照表
- **Notes**: 结构惯例逐字沿用 `products/xmnn-runtime/smoke/` 模板（禁区只读，未改动）；两守卫文件 docstring 即项清单事实源，Task 7 README 与 Task 9 守卫测试须与其逐字一致。
- **实施记录（2026-10-09）**:
  - **改动面（共 3 文件）**：新建 `products/xmflow-cli/smoke/_base_guards.py`（6 项：①可重定位 CPython+venv ABI+stdlib 扩展合并探测 FR-7 清单 ②deps.txt 逐条已装 ③`pip check` 放行族为空元组（全量阻断，机制保留，注释载明真机若见系统元数据债务须按 §11 补模式并同步三处） ④torch marker ∈ `none|cpu` **必须存在**（install-torch.sh 恒落盘，刻意严于 xmnn-runtime 模板对 `""`/missing 的容忍；none→import 必失败，cpu→主版本 `2.`/`version.cuda` None/`is_available` False/jit.load/张量 sum） ⑤非 root(xmnn) 身份可用（root 轮 `su -s /bin/bash xmnn -c "set -e ; …"` 断言 uid≠0 + venv 解释器 + deps 可读 + /workspace/temp 写探针；xmnn 轮自验 X_OK/R_OK 与写权限） ⑥反断言载荷未安装（venv bin 无 xmnn*/xmflow、conda+venv 两 purelib 无 xmnn 前缀、`-I -P -c import xmnn` rc≠0 且 stderr 含 ModuleNotFoundError））与 `smoke/_runtime_smoke.py`（10 项 + pip check：ABI/imports 来源 site-packages（`_FORBIDDEN_PREFIXES` 排除 /workspace 与 builder 路径）/_libs 含 libtvm.so+libLLVM/ctypes RTLD_GLOBAL 载入/tvm.build('llvm') 向量乘数值冒烟（零模型依赖，非 OQ-5 禁的编译冒烟）/prelude.rly/载荷数据文件合并项（bootstrap .pth + autolibs/tools_cpp/fonts）/deps.txt 闭包模块可导入（Pillow→PIL、protobuf→google.protobuf 映射）/xmflow console script `--help` 含六子命令 compile/accuracy/infer/performance/excelreport/pipeline（OQ-5 替代断言）/torch 双态同 base；pip check 判据**仅阻断 `^xmnn\b` 冲突行**，其余 INFO 放行——注释载明底座守卫第 3 项已全量把关）。修改 `Containerfile.xmflow-cli` Layer 4 注释与守卫 docstring 六项逐字对齐，并加一句项数三处同步口径。
  - **TR-6.1 取证（blocked 如实登记，非实跑）**：容器内 root+xmnn 双跑与「误装 xmnn 故意污染」验证依赖真机 podman，本机 Windows/UNC 环境不可用，**留待有真机环境时补做**；本段替代取证为静态三项——`ast.parse` AST-OK ×2（Windows Python 3.14 直读 UNC，避开 py_compile 防 `__pycache__` 落盘 repo）、字节级 CR=0 ×3（两守卫 + Containerfile，shebang `#!/usr/bin/env python3\n` 正常）、Containerfile Layer 4 root+xmnn 双跑命令与 Layer 2 `cp /tmp/deps.txt /opt/xmflow-smoke/deps.txt` 落盘路径已核实（守卫默认 `XMFLOW_DEPS_FILE` 回退路径成立）。调用面与反断言逻辑经逐行对照模板静态审查，但**不冒充实跑结论**。
  - **TR-6.2 取证**：三处同步中 Containerfile Layer 4 注释已落（与本段守卫 docstring 逐字一致）；骨架 README 清单 → **Task 7**；守卫测试断言项数 → **Task 9**。docstring 为清单事实源；项数刻意保持 6 / 10+pip check 与既有产品口径一致，未改对外文本结构。
  - **TR-6.3 断言对照表（相对 xmnn-runtime 模板）**：base 1↔1（可重定位解释器，扩展合并探测为新增）、base 2↔2、base 3↔3（判据方向相反：本产品底座放行族为空）、base 4↔4（marker 必须存在，严于模板）、base 5↔5（devuser→xmnn；新增 uid≠0 断言与 /workspace/temp 写探针——CLI 特有交付面）、base 6↔6（反断言方向一致：xmnn-runtime 验载荷已装之对偶，本产品验底座期未装）；runtime 1-6 逐一对应模板 1-6（tvm/vta 运行面等价继承）、runtime 7↔模板 7+8 合并（bootstrap.pth 与三目录并为一项）、腾出槽位给 deps 闭包模块导入（新增，FR-7 客户依赖面）、runtime 9=新增 xmflow console script 项（对应模板的应用入口项）、runtime 10↔模板 torch 项（双态 none|cpu）、pip check↔模板末项（判据收窄 `^xmnn`）。覆盖度自评满足 anchors-5：每项有既有产品对应物，且新增 uid/temp 写权限/闭包模块三个 CLI 特有断言。
  - **已知局限登记**：`--network host` 降级说明不适用于本产品（无网络断言项）；OQ-5 真机模型组冒烟以 README 可粘贴命令形式给出，落 **Task 7/8**。

## Task 7: `release/` 交付骨架新建
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 6
- **Description**:
  - 按 §1 不变量新建 `release/`：控制脚本**必须沿用 `xmnnctl` / `xmnnctl.ps1` 名称**（依 FR-5，`bin/relpack` 的 `cmd_smoke` 与 skeleton 测试的 `TRACKED` 清单三处锁死该名称，改名即触发 AC-4 第二处 CLI 改动；脚本**内容**为产品私有，镜像 ref 用 `localhost/xmflow-cli:$ver`），bash + `*.ps1` 同构命令面、`payload/Dockerfile`（`--no-index --no-deps` 装载荷）、`payload/.gitignore` 忽略 `*.whl` 并保留 `.keep`、`.env.example`、`artifacts/.gitignore`、`workspace/.gitkeep`、`README.md`；挂载契约改为 `/workspace/models:ro` + `/workspace/temp`，无 Jupyter 端口/凭证面，`pull_policy: never`。
  - 骨架内零 `../`、零 Python；`.env.example` **必须保留键 `XMNN_VERSION`**（`cmd_smoke` 以 `grep -E '^XMNN_VERSION='` 解析版本），命令面为 `load/up/smoke/down`（可另含 `init/ps/logs/version`），不含 Jupyter 端口与凭证面。
- **Acceptance Criteria Addressed**: AC-1、AC-3、AC-5、AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 骨架不变量用例全绿（清单、无 `../`、无 `.py`、`pull_policy: never`、`.env.example` 无 CR、shebang 全 LF、两端命令同构）；Evidence = pytest 输出
  - `rule` TR-7.2: `./xmnnctl init → load → up → smoke → down` 全部 rc=0（脚本名固定为 `xmnnctl`，无等价改名选项）；Evidence = `smoke` 命令输出
- **Notes**: 与本应用 `xmnn-runtime/release/` 并存的两份骨架属预期（客户面不同），不构成 G4 双写；但公共控制逻辑若出现第三次复制，须先抽公共再取第三产品。
- **实施记录（2026-10-09）**:
  - **改动面（共 12 个新建文件，全部在 `products/xmflow-cli/release/` 下）**：`xmnnctl`（bash，504 行）、`xmnnctl.ps1`（pwsh 7+，与 bash 逐函数同构）、`compose.yaml`、`compose.podman.yaml`（三必需 override 逐字沿用模板）、`.env.example`（仅 `XMNN_VERSION=0.0.0` + `XMNN_CONTAINER_NAME=xmflow-cli` 两键）、`README.md`（11 节）、`release/.gitignore`（`workspace/`）、`artifacts/.gitignore`、`workspace/.gitkeep`、`payload/Dockerfile`、`payload/.gitignore`（`*.whl` 忽略 + `!.gitignore`）、`payload/.keep`。TRACKED 清单与 FR-5 契约一致。
  - **关键口径落实**：①控制脚本名沿用 `xmnnctl`/`xmnnctl.ps1`（relpack `cmd_smoke` 硬编码路径零改动即兼容），版本解析沿用 `grep -E '^XMNN_VERSION='` 口径；命令面 8 个 `init/load/up/down/ps/logs/smoke/version`，bash 版 `usage() { sed -n '3,18p' "$0"; }` 头注 3-18 行。②镜像 ref `localhost/xmflow-cli:$ver` 在 bash 与 ps1 中各**恰好 2 处**（load/smoke），compose 用 `localhost/xmflow-cli:${XMNN_VERSION}`。③常驻语义：底座 ENTRYPOINT 为一次性 CLI，保活放在 compose 层 `command: ["/bin/bash", "-lc", "exec tail -f /dev/null"]`；`payload/Dockerfile` **无 ENTRYPOINT/CMD 指令行**；就绪检查 30×2s 轮询（bash `wait_started` / ps1 `Test-Started`）。④凭证/端口面全部裁剪：两版 `init` 为纯复制模板（无随机凭证、无 chmod 600），删除模板的全部端口预检函数；`.env.example` 无四键凭证面。⑤`payload/Dockerfile`：`ARG BASE_IMAGE=localhost/xmflow-cli:base-none`、pip `--no-index --no-deps`、`_runtime_smoke.py` 恰好 2 处（root + `su -s /bin/bash xmnn` 双跑）、pip check 全量打印仅 `^xmnn[[:space:]]` 冲突行判失败、收尾注释 `# XMFLOW-CLI PAYLOAD INSTALLED`。⑥挂载契约 `/workspace/models`（只读）+ `/workspace/temp`，零 ports/零 environment/零命名卷，`pull_policy: never`。⑦README 11 节融合 xmnn-runtime 骨架九节惯例与 `assets/USAGE.zh-CN.md` 七节（Task 8 覆盖度判据的骨架侧已就位）：形态标签表（base-none ≈1.2GB / base-cpu ≈2.1GB，参考值）、模型组目录契约（`-n a.b.c`↔`models/a/b/c/`、`[compile] target` 六值、`quantized_dtype`、`tune`、`[inference] device_ip/device_mount_dir`、产物落 `temp/<模型名>/compile/`）、真机 `--network host` 与 Docker Desktop/NFS 边界、temp 权限 uid 三口径、`0x7F7F`=target 与板卡不匹配（非镜像问题）、§8 守卫清单与两守卫 docstring **逐字一致**（base 6 项 + runtime 10 项+pip check，TR-6.2 的 README 侧闭环）、OQ-5 口径明示「守卫不含真实模型编译冒烟，以 §4.3 `compile -n demo.caffe.resnet50` 可粘贴命令执行」。
  - **TR-7.1 静态取证（Windows Python 3.14 直读 UNC，全部 PASS）**：12 文件齐全；文本文件（12 个）字节级 CR=0、release/ 内零 `.py` 文件、零 `../`；`xmnnctl` 首行 shebang `#!/usr/bin/env bash`；bash/ps1 镜像 ref 计数各==2；两版 8 命令面齐备；`compose.yaml` 含 `pull_policy: never` 与保活 command 行；Dockerfile `_runtime_smoke.py`==2、无 ENTRYPOINT/CMD 指令行、`^xmnn[[:space:]]` 与 `--no-index --no-deps` 在位；`.env.example` 恰两键。**pytest 实跑归 Task 9**（骨架不变量用例参数化后补）。
  - **TR-7.2 取证（blocked 如实登记，非实跑，口径同 Task 6）**：`./xmnnctl init→load→up→smoke→down` 全 rc=0 依赖真机 podman/buildah 环境，本机 Windows/UNC 不可执行，**留待真机补做**；不冒充实跑结论。
  - **已知局限登记**：取证扫描时 `payload/` 下存在 relpack stage 的本地 wheel（`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`，二进制、含 CR 字节与压缩流内 `../` 序列），由 `payload/.gitignore` `*.whl` 规则忽略不入库——Task 9 的骨架不变量用例须按 TRACKED/文本口径排除 `*.whl` 与 `workspace/`，避免误红。

## Task 8: 客户契约文本迁移
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 把 `assets/USAGE.zh-CN.md` 7 节逐节迁入 `release/README.md`（客户面）与 `docs/`（厂商面），命令示例改用最终镜像名与形态 tag；保留三条 FAQ 口径与真机网络/NFS 边界表述。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rubric` TR-8.1: 客户文档对原件 7 节的信息覆盖度（判据同 AC-5）；scale 1-5;anchors 1=多节缺失、3=细节丢失、5=全覆盖且可执行;threshold >= 4;evidence = 逐节对照表
  - `rule` TR-8.2: 文档内所有命令示例的镜像名/挂载路径与实际骨架一致（无残留 `xmflow-release` 旧名）；Evidence = grep 断言为空
- **实施记录（2026-10-09）**:
  - **原件事实源**：`apps/containers/client/overlays/native-dev/release/USAGE.zh-CN.md`（135 行，md5 `be8d9f43a43566cdede45c2aee8edfc9`，含 `2daf20131` 排障更正；spec 表中 `assets/` 前缀为留档叙述，原件无该子目录）。承接落点为**客户面** `products/xmflow-cli/release/README.md`（Task 7 已产 11 节融合版）；USAGE 通篇为客户契约内容，`docs/` 厂商面（README/00-overview/01-quickstart）经通读**无承接缺口**——新产品在 docs 三处的登记行属 Task 11 范围，本任务不动 docs。
  - **TR-8.1 逐节对照表（原件 7 节 → README 落点）**：
    1. 镜像标签 → §5.1：旧名 `xmflow-release:1.2.1`/`1.2.1-torch` 改写为形态标签 `base-none`（≈1.2 GB）/`base-cpu`（≈2.1 GB）；**`-torch` 选型判据保留**（`.pth/.pt` 编译必须用 cpu 形态、torch 仅主机端 CPU 前端加载不影响板端）；x86_64 限定（§1 系统要求）、容器内非 root `xmnn`（§5.1）、工具链版本改以交付清单为准（`./xmnnctl version`，Python 3.14 ABI）——具体版本号 1.2.1.dev0/Nuitka 4.2.2 属版本敏感值，由 release.json 承载，非口径变更；原件 `zstd -dc | docker/podman load` 转义为新形态 `xmnnctl load`（底座归档 tar.gz + sha256 双重校验，README 明示客户无需手工 `docker load`）。
    2. 快速开始 → §2 五分钟上手 + §4.1：双挂载点表（`/workspace/models` 只读必需 / `/workspace/temp` 可写必需）**逐字保留**；compile 示例改最终镜像名 `localhost/xmflow-cli:<交付版本>`；`--help` 两例在 §4.3 保留。
    3. 模型组目录契约 → §4.2：**近逐字保留**（模型名即目录层级 `-n a.b.c`、`config.toml` 六 target 枚举/`quantized_dtype`/`tune`+autolibs/`device_ip`+`device_mount_dir`、产物清单 network.xmnn/vta_config.bin/vta_data.bin/cpp_deploy_static）。
    4. 常用命令 → §4.3：六子命令（compile/accuracy/infer/performance/excelreport/pipeline）全覆盖，双挂载行齐全，真机 infer 示例含 `--network host`。
    5. 真机网络 → §4.4：**逐字口径保留**（telnet 23、Linux 推荐 `--network host`、Docker Desktop 需放通到板卡网段路由、板端 NFS/CIFS 共享由现场 IT 预挂载、`SIM_*` 零外部依赖）。
    6. 镜像内容边界 → §5.2：包含面（Python 3.14 隔离 venv、编译后 tvm/vta/xmnn、内置 LLVM 与 libtvm、六 target 预编译工具、预置调优库、报告字体、cpu 形态另含 torch/torchvision）与不包含面（零源码、无 CUDA/GPU、无 jupyter/SSH、无示例模型与校准数据）齐全；**本次回补两处细节**：「内置 LLVM（约 186 MB）」数值与「Nuitka 打包器」字样（与原件逐字对齐）。
    7. FAQ → §9 排障表 + §6 引述块：三条口径锚点全部在位——① `--network host`（§4.3/§4.4/§9 三处）；② temp uid 规避**三方式齐备**（`chmod 0777`／查 uid 后 `chown`／`--user "$(id -u):$(id -g)"`，§6 块quote + §9 行内复述）；③ **`0x7F7F` 毒值判读保留且细化**（target 与板卡不匹配、非镜像问题、核对 `[compile] target` 重编译）；`No module named 'torch'`→索取 base-cpu 形态、重跑编译 `PermissionError 0-compile.log`→删 `temp/<模型名>` 旧产物或 `chmod -R a+w`、固定同一身份运行，均保留。
  - **G5 核验**：技术判据零改动；仅镜像名/形态标签/交付载体按 FR-8 强制新形态适配（zstd tar→tar.gz 归档+xmnnctl、`:1.2.1[-torch]`→清单驱动版本+`base-none|base-cpu`）。
  - **TR-8.2 取证（grep 断言）**：① `xmflow-release` 在 `offline-delivery/**`（含 products/xmflow-cli 与 docs）全库检索 **0 命中**；② README 命令示例镜像名 `localhost/xmflow-cli:<交付版本>` 与 `product.env` `IMAGE_NAME=localhost/xmflow-cli`、`FLAVORS="none|cpu"`（§5.1 形态表 base-none/base-cpu）一致；③ 挂载路径 `/workspace/models:ro`+`/workspace/temp` 与 `Containerfile.xmflow-cli` L104（mkdir 两目录）、L187（VOLUME）、L188（WORKDIR /workspace）一致；可粘贴执行性由 §2/§4.3 完整命令形态保证（一次性 run 与 `xmnnctl` 双路径）。

## Task 9: 测试多产品参数化
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 7
- **Description**:
  - `tests/conftest.py` 的 `PRODUCT_NAME` 改为按 `products/*/` 发现并参数化。
  - 依 FR-10 把 `tests/test_release_skeleton.py` 拆为**两层**：① 通用不变量层（`TRACKED` 结构、零 `../`、零 Python、`pull_policy: never`、CR=0 与 shebang 全 LF、`xmnnctl`/`xmnnctl.ps1` 命令面集合、`.env.example` 含 `XMNN_VERSION`、归档内不含 `payload/*.whl`）——按 `products/*` 参数化自动覆盖，含假产品；② 产品私有契约层（tests 内 per-product registry）——xmnn-runtime 的 `xmnnrt`/2225/8893/environment 四键/`/var/lib/jpman/ssh-host-keys`/named volume/`.env.example` 8 键精确集合/`--entrypoint /opt/conda/bin/python`/`COPY xmnn-*.whl`/`su -s /bin/bash devuser`，xmflow-cli 的 `--entrypoint /opt/xmflow/bin/python`/`/workspace/models:ro`+`/workspace/temp`/无端口发布。
  - registry 中无对应条目时该用例**显式 skip**（不得静默通过），以此保证「新增产品不必改测试」与「私有契约仍被锁死」同时成立。
  - `xmnn-runtime` 既有断言语义**不得**改动（仅允许从「直接字面量」等价迁移为「registry 取值」）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-9.1: `pytest` 全绿，且通用不变量层 `--collect-only -q` 用例数与产品数成**线性关系**（每产品一份参数化实例），私有契约层按 registry 命中或显式 skip；Evidence = 前后 collect 计数与 skip 清单
  - `rule` TR-9.2: 临时新增假产品（仅 `product.env` + 骨架清单，registry 无条目）即被通用不变量层自动覆盖、私有层显式 skip，删除后结果复原；Evidence = 两次运行输出
- **Notes**: 本任务与 Task 5 均触 `tests/`，实施顺序上 Task 9 应在 Task 5 之后合并，避免同一测试文件两笔交叉改动。
- **实施记录（2026-10-09）**:
  - **改动面（仅 2 个 tests 文件，属 D3 明示允许区）**：`tests/conftest.py`（55→111 行）新增 `load_product_env`/`discover_products`（`products/*/` 含 `product.env` 且 `RELEASE_DIR` 目录存在方计入，sorted）、`PRODUCT_NAMES`（import 时求值）、`Product` NamedTuple（name/dir/release_dir/env）、session 级参数化夹具 `any_product`；**单产品锚点夹具 `PRODUCT_NAME="xmnn-runtime"` 与 `app_root/bin_dir/product_dir/release_dir/product_env` 语义逐字保留**（`test_relpack_cli.py` 兼容硬约束）。`tests/test_release_skeleton.py`（748→944 行）整体重构为两层：①通用不变量层 37 项/产品（TRACKED 11 清单、零 `../`、零 Python、`pull_policy: never`、CR=0 与 shebang 全 LF、命令面集合、`.env.example` 含 `XMNN_VERSION`、归档口径排除 `*.whl` 与 `workspace/` 等，全部由 product.env 派生取值）+ 产品无关单跑 2 项；②产品私有契约层 13 项/产品（`PRODUCT_CONTRACTS` per-product registry：compose 精确结构/podman override 三必需/`.env.example` 精确键集/entrypoint/凭证面写侧/端口预检/payload Dockerfile 派生契约）。registry 未命中 → `_contract()` 显式 `pytest.skip`；`port_preflight=False` → 端口三例显式 skip。xmnn-runtime 断言仅做「字面量→registry 取值」等价迁移，语义零改动；`bin/lib/common.sh` 与 `products/xmnn-runtime/**` 禁区未触。
  - **TR-9.1 取证（pytest 7.x，Windows Python 3.14 直跑）**：collect 计数——两真产品 `skeleton=102 = 2×50 + 2`（每产品 50 参数化实例），加假产品 `152 = 3×50 + 2`，线性 +50/产品成立；`test_relpack_cli.py=23` 不变，全量 `125→175`。实跑（本地盘副本，含假产品）：**159 passed, 16 skipped, 0 failed**；skip 清单 `[13] 产品 fake-prod 无私有契约条目（显式 skip，不静默通过）` + `[3] xmflow-cli 无宿主端口面（port_preflight=False，显式 skip）`，pwsh 用例本机实跑通过。注：SMB/UNC 直跑时 `test_relpack_cli.py` 有 3 例因 WSL 无法翻译 UNC cwd 失败（`wsl: Failed to translate '\\10.16.11.3\ai...'`，Task 5 已登记环境局限），同步本地盘副本后全绿，非回归。**本次全绿同时补齐 Task 7 遗留的 TR-7.1 pytest 实跑证据**（骨架不变量用例含 xmflow-cli 参数化实例在内全绿）。
  - **TR-9.2 取证（假产品自测，两次运行输出对照）**：临时复制 `products/xmflow-cli` → `products/fake-prod`（registry 无条目）：通用层对其 37 项自动覆盖并全部通过（证明「新增产品不必改测试」），私有层 13 项显式 skip（证明「不静默通过」）；删除 fake-prod 文件后 collect 复原 `125`（`discover_products` 因 `product.env` 缺失自然不识别）。**残留登记**：`fake-prod/{release,scripts,smoke}` 与 `tests/__pycache__` 的空目录因 IDE 文件监视器持有 SMB 目录句柄处于删除挂起（多次 rmdir 未落），不含任何文件、git 不可见、不影响测试发现与结果，句柄释放后自动消失。

## Task 10: 端到端真机验证与体积实测
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7, Task 9
- **Description**:
  - 在真机执行 `bin/relpack -p xmflow-cli stage → deps → build → pack → smoke` 全链，采集底座体积、派生增量、耗时，与 NFR-2 目标对照；与 `localhost/xmflow-release:1.2.1`（1.18 GB）作对照记录。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-7
- **Test Requirements**:
  - `rule` TR-10.1: 五步全部 rc=0，`release.json` 的 `payload.sha256` 与 `archive.sha256` 按 §12 块定向读取一致；Evidence = 文件内容与校验输出
  - `rule` TR-10.2: `guard_crlf_shebang` 通过且 `pack` 归档经 `gzip -t`；Evidence = pack 日志
  - `rubric` TR-10.3: 体积/耗时对照 `xmnn-runtime` 的合理性解释；scale 1-5;anchors 1=未采集、3=有数字无解释、5=数字+差异归因+是否达 NFR-2 的结论;threshold >= 4;evidence = 实测表
- **Notes**: 若真机 podman 不可用，如实标记本任务 `blocked` 并写 Unblock Condition，不得以静态检查冒充端到端通过。
- **实施记录（2026-10-10）**：
  - **执行环境**：Windows 侧经 WSL 发行版 `podman-machine-default`（root 修 `/run/user/1000` 权限后 `su - user` 侧 rootless podman，命令通道已验证可用）。镜像库仅 `localhost/jupyter-podman-rootless:latest`（1.16 GB）、node:20-alpine、nginx:1.27-alpine 等——**本任务两个构建输入镜像均不在库**：Stage 0 构建器 `localhost/native-dev:nuitka-4.2.2-hotfix`（native-dev 栈产出，约 10.6 GB，只进构建期不进最终镜像）与 Stage 1 基镜像 `docker.io/library/ubuntu:26.04`。
  - **四步实跑（`bash bin/relpack -p xmflow-cli <step>`，逐条计时）**：

    | 步骤 | rc | 耗时 | 实测输出 |
    |------|----|------|----------|
    | stage | 0 | 0s | `[ OK ] 已是最新：payload/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（幂等跳过拷贝）；暂存 wheel 与源 dist 的 sha256 同值 `a3be2d89…4b45` |
    | deps | 0 | 0s | `[WARN] 未找到 unzip 或 bsdtar…本次跳过 deps 校验（不是通过，也未阻断）`——环境缺解压工具，按 rc=2 语义放行 |
    | build | 1 | 7s | Stage 0 `FROM localhost/native-dev:nuitka-4.2.2-hotfix` 三次重试均 `pinging container registry localhost … dial tcp 127.0.0.1:443: connect: connection refused` |
    | pack | 1 | 0s | `[ERR ] 本地缺少底座镜像 localhost/xmflow-cli:base-none：先执行 bin/relpack build --torch none`；pack 前置顺序中缺底座检查先于 `guard_crlf_shebang` 与归档产出，artifacts 目录为空 |
    | smoke | 1 | — | `./xmnnctl init` 失败：`Podman 已安装但缺少 compose 支持`（podman-compose 未安装；按红线不安装新包） |

  - **外部输入取证**：`podman pull docker.io/library/ubuntu:26.04` 三次重试全败——`registry-1.docker.io` 解析到 69.50.221.20 / 157.240.12.35（DNS 污染），i/o timeout。
  - **守卫证据（函数直跑，非 pack 链，仅辅助）**：按 bin/relpack 的 source 序列（log.sh→common.sh→pipeline.sh + `load_product_env xmflow-cli` 派生 `RELEASE_DIR` 等）装配后直调 `guard_crlf_shebang`：扫描 11 文件（排除 artifacts/ 与 *.ps1/psm1/bat/cmd），其中 shebang 脚本 1 个、无 CRLF，**rc=0**。因 pack 链未跑至守卫，此证据不冒充 TR-10.2 的 pack 链证据。
  - **兄弟产品对照（同码路径类比）**：`xmnn-runtime` 归档 1,199,948,906 字节（1,144.4 MB，与对照基准 `localhost/xmflow-release:1.2.1` 1.18 GB 同量级），实算 sha256 `aa656a30…308a` 与 release.json 记录逐字一致、size_bytes 一致；归档 gzip 完整性校验（tar -tzf 全列 111 成员）rc=0、耗时 124s。但该 manifest 为旧 schema（仅 version/image/archive/created_at 2026-09-17T07:43:41Z，**无 payload 块**），§12 双 sha256 定向读取无法由此补齐。
  - **TR 逐条裁定**：TR-10.1 **未达成**（五步非全 rc=0，release.json 未产出）；TR-10.2 **未达成**（pack 链未触达守卫与 `gzip -t`，函数直跑 rc=0 仅辅助）；TR-10.3 评 3（有数字与部分差异归因——xmflow-cli 为厚底座设计，预期体积大于 xmnn-runtime 薄底座谱系，但缺 xmflow-cli 底座实测值与 NFR-2 结论，未达阈值 4）。
  - **纪律声明**：曾评估换用本地既有镜像（`--build-arg BUILDER_IMAGE` / `--base-image` 指向 jupyter-podman-rootless 等）凑跑 pack——**明确否决**：产物 LABEL 与语义将偏离产品契约，属冒充端到端通过。
- **Unblock Condition**：
  1. Stage 0 构建器镜像 `localhost/native-dev:nuitka-4.2.2-hotfix` 入 podman 库（或改在 NPU 开发真机执行，该镜像由 native-dev 栈就地产出）；
  2. 基镜像 `docker.io/library/ubuntu:26.04` 经 docker.io 可拉取（修复 DNS）或离线预置入库；
  3. smoke 依赖 podman-compose 在执行环境预装（本机不安装新包）。
  - 以上满足后重跑五步全链，补登底座实测体积/耗时、release.json 双 sha256 与 TR-10.3 定级。
- **Unblock 进展登记（2026-10-10，经用户逐项授权推进）**：
  - **条件 1（构建器镜像）— 部分解除**：完整 native-dev 五连败于 conda/apt 镜像站（tuna apt pool 403、aliyun conda `repdata.json` 404、tuna `.zst` 仅回 15 KB 损坏、基底 `/opt/conda/.condarc` 的 `custom_channels` 把 conda-forge 顽固映射回 tuna、`use_zstd: false` 对当前 mamba 不生效），本环境无外网 conda 源无法完整重建 native-dev。经用户授权改用**最小功能等价镜像** `localhost/native-dev:nuitka-4.2.2-hotfix`（1.16 GB，基底 `jupyter-podman-rootless` 已含 Python 3.14.6 + `/opt/conda/ssl/cacert.pem`，即 xmflow-cli Stage 0 `relocate-cpython.sh` 的唯一输入 `/opt/conda`），LABEL 与真实 native-dev 同构并含 `org.specweave.base-image` 溯源。**如实登记**：此为保真 Stage 0 输入的最小等价物，非完整 native-dev（无 LLVM/Nuitka 实体），完整镜像须于 NPU 真机构建。据此底座构建实测 `localhost/xmflow-cli:base-none` = **547 MB**。
  - **条件 2（基镜像 ubuntu:26.04）— 已解除**：docker.io 直连仍 DNS 污染；经 `docker.m.daocloud.io/library/ubuntu:26.04` 拉取（112 MB）后 `podman tag` 归一化为 `docker.io/library/ubuntu:26.04`，满足 Stage 1 契约引用名。另修 buildah `no FROM statement found`（Stage 1 `ARG` 前置于 `FROM` 的写法在本 podman 5.8.2 解析失败；**SMB 原件已按用户指令修复**：硬编码 `FROM docker.io/library/ubuntu:26.04` + `ARG BASE_IMAGE` 后置仅作用 LABEL 溯源，附注释登记实证；修复后原件 LF 无 CR，刷新 Temp 构建副本实跑 `podman build` 全 22 步 rc=0，产出 `localhost/xmflow-cli:base-argfix` 547 MB 与 base-none 同体积，日志无 `no FROM statement`）与守卫 `pip check` 假阳性（`_base_guards.py` L297 成功消息行 `No broken requirements found.` 被误计入 blocking，加过滤）。第三次底座构建全绿 rc=0。
  - **条件 3（podman-compose）— 已解除（本次）**：WSL 发行版为 **Fedora 43**，官方仓库直供 `podman-compose-1.5.0-4.fc43`（携 python3-click/python3-dotenv）。系统 python3.14 无 pip、无 pipx，故 `pip/pipx install` 路线不通；`dnf install -y podman-compose` 成功（bfsu 镜像个别 repo 元数据 403，但包体经有效镜像下载完成，Transaction Complete）。三级实证（RunRoot 前置修复后）：① `podman-compose --version` = 1.5.0，落位 `/usr/sbin/podman-compose`（PATH 内，命中 xmnnctl 探测链第 2 档；`podman compose` 第 1 档经 podman 5.8.2 自动委派亦 rc=0）；② 真实产物 `compose.yaml + compose.podman.yaml` 合并 `config` 解析全字段正确（`image: localhost/xmflow-cli:1.2.1`、`network_mode: bridge`、`pull_policy: never`、override 三必需 `devices/cgroupns/security_opt` 齐备），`--dry-run up` rc=0；③ 最小 compose 实跑 `up -d → ps → down` 全生命周期 rc=0（容器 `pc-min_t_1` Up→清理，用库内既有 ubuntu:26.04，非产品镜像，仅证明工具执行路径可用）。
  - **五步全链正式跑通（2026-10-10，Temp 工作副本实跑，经用户「按建议全走」与修复方案两项授权）**：`version` rc=0 → `stage` rc=0（wheel 177,617,215 B，sha256 `a3be2d89…4b45`）→ `deps` 真通过（首跑 rc=0 实为「缺 unzip 跳过、不是通过」，`dnf install unzip` 后复跑 20 项一致）→ `build` rc=0（22 步全绿，base-none 重建 id `c3fddcc85c33`）→ `pack` rc=0（归档 197,354,286 B，sha256 `4654db7e…21da`）→ `smoke` 三轮收敛后**实质通过**：
    1. 第 1 轮外层 rc=0 但日志 `[ERR] 版本不一致`（`.env` XMNN_VERSION=0.0.0 占位 vs 清单 1.2.1.dev0）——load 的版本契约**正确拦截**，按报错指引修 `.env`；
    2. 第 2 轮派生构建 `[Errno 13] Permission denied: '/opt/xmflow/lib/python3.14/site-packages/_libs'`——根因：`payload/Dockerfile` 无 `USER` 指令、继承底座镜像配置 `User=xmnn`（`podman inspect` 实锤；容器内 site-packages 属主 `root:root drwxr-xr-x`），而该文件的 root+xmnn 双身份守卫与 `/root/.cache` 清理本就按 root 构建身份编写。经用户授权修复：构建层前显式 `USER root`、文件末 `USER xmnn` 恢复运行契约（SMB 原件 CR 字节实测 0，同步 Temp 副本）；
    3. 第 3 轮全链绿：load 派生构建 STEP 1/8–8/8（`USER root`→装 wheel→双身份守卫→`USER xmnn`）COMMIT tag `localhost/xmflow-cli:1.2.1.dev0`（id `f130acd13cdc`）；root 与 xmnn 双身份守卫各 `SUMMARY: 11 passed, 0 failed`（10 项守卫 + payload 域 pip check）；`up` 容器就绪 → 一次性容器 smoke 同 11/11 全绿 → `down` 正常；日志无任何 `[ERR]`。
  - **TR-10.1 裁定：达成**。五步全部 rc=0；修复 payload 后重跑 pack 独立复算，`release.json`（schema v2，块序 payload→image→archive）`payload.sha256`=`a3be2d895d3d…f20a4b45`、`archive.sha256`=`4654db7ec0e0…766521da` 与 `sha256sum` 实测逐字一致，size_bytes 一致。Evidence=release.json 全文 + sha256sum 输出。
  - **TR-10.2 裁定：达成**（补齐此前「函数直跑仅辅助」缺口）。`guard_crlf_shebang` 位于 `cmd_pack` 第①位（`bin/relpack` L121，成功静默 return 0、失败 err+return 1），本次 pack 链 rc=0 且归档产出即为守卫链上通过证据；新改 `payload/Dockerfile` 4,902 B 实测 CR=0。`gzip -t` 归档 rc=0。Evidence=pack 日志 + `GZIP_OK`。
  - **TR-10.3 自评 5/5（数字+归因+NFR-2 结论）**：

    | 对象 | 实测 | 对照 |
    |------|------|------|
    | 底座 `base-none`（不含载荷） | **547 MB** | `xmflow-release:1.2.1` 一体镜像 1.18 GB → NFR-2 前半**达成**（≈53%） |
    | 派生 `xmflow-cli:1.2.1.dev0` | **1.28 GB** | 一体镜像 +≈0.1 GB |
    | 派生增量 | ≈733 MB | §9 的 0.18 GB 量级**不可比**（见归因） |
    | 载荷 wheel | 177.6 MB | COPY 独立层永久留存 |
    | 归档 `xmflow-cli-base-none.tar.gz` | 197.4 MB | `gzip -t` 通过 |
    | 耗时 | 底座 22 步构建为分钟级；smoke 全链（派生构建+双身份守卫+up/down）约 4 分钟；pack 导出（save\|gzip）约 2 分钟 | 派生构建在 payload 头注宣称的「约 1-3 分钟」量级附近 |

    **差异归因**：(1) `payload/Dockerfile` 的 `COPY xmnn-*.whl` 是独立层，RUN 内 `rm -rf /tmp/payload` 不消减其 177 MB；(2) wheel 含 Nuitka 编译的 TVM/VTA 全栈，解包后 `_libs` 内 libLLVM.so.22.1 即 200 MB 级——§9 的 0.18 GB 是 `xmnn-runtime` 载荷体量，不是普适规律。**NFR-2 结论**：前半（底座显著小于 1.18 GB）达成；后半（派生增量与 0.18 GB 可比）未达成、如实登记——增量由载荷体量决定，与底座/载荷分离架构本身无关；一体镜像与新派生镜像同为 1.2 GB 量级，「一底座多派生」场景仍保有底座复用与分发面（归档 197 MB）净收益。改进方向（`COPY --mount=type=bind` 消 COPY 残留层）属交付契约变更，**超出本任务范围，留待用户裁决**。
  - **环境局限沿用登记**：全链在 WSL rootless podman 5.8.2 + podman-compose 1.5.0 实跑；Stage 0 构建器为最小功能等价镜像（见条件 1 登记），完整 native-dev 与 CPU/GPU 形态验证仍须 NPU 真机；Temp 工作副本与验证镜像（`base-none`、`1.2.1.dev0` 及归档）保留待用户处置。
  - **NFR-2 后半改进实施记录（2026-10-10，经用户「好的，执行吧」授权立项）**：`payload/Dockerfile` 的 `COPY xmnn-*.whl /tmp/payload/` 改为 `RUN --mount=type=bind,source=.,target=/tmp/payload,ro`（bind 挂载仅在 RUN 执行期可见、不进任何镜像层），RUN 内相应移除 `rm -rf /tmp/payload`（挂载只读、生命周期止于 RUN）；改动后文件 5,302 B、CR 字节实测 0，Temp 工作副本同步。**验证**（smoke 三轮收敛）：第 4 轮 bind-mount 构建通过（STEP 6/7，层 ID `815f846fd45c`，构建内 root/xmnn 双身份守卫各 11 passed 实证于该层输出），但 up 后 smoke exec 报 `container state improper`（RunRoot 不可写环境问题）；第 5 轮因 RunRoot 修复与 podman 调用分离（`/run/user/1000` 随 WSL 发行版终止清空）load 失败；第 6 轮 RunRoot 修复与 smoke 同命令链内完成，实质全绿——STEP 6 缓存命中同层、一次性容器守卫 `SUMMARY: 11 passed, 0 failed`、up→smoke→down 全链无 `[ERR]`；pack 重跑 rc=0（归档 197,354,286 B 与 sha256 `4654db7ec0e0…` 均不变——归档为底座镜像 save，不受 payload Dockerfile 改动影响）。**体积实测**：派生 `xmflow-cli:1.2.1.dev0` 由 **1.28 GB → 1.1 GB**（id `a2b7d2c104bf`），消减 ≈177 MB 恰为 wheel COPY 残留层；底座 `base-none` 547 MB 不变；派生增量 ≈733 MB → ≈553 MB。**NFR-2 复核**：后半仍未达成（增量 553 MB vs §9 的 0.18 GB 量级），但归因更新——可避免的架构残留已消除，剩余增量即 wheel 解包实体体量（`_libs` 内 libLLVM.so.22.1 200 MB 级），属载荷真实体量而非架构问题。**环境操作口径登记**：WSL 发行版在 wsl 调用间终止时 `/run/user/1000`（tmpfs）随之清空——RunRoot 修复（root 身份 mkdir/chown/chmod）与 podman 命令必须在**同一 wsl 调用内**完成（经 `su - user` 切换），否则 podman 报 `RunRoot is not writable` / `permission denied`；分离调用曾致第 4 轮 smoke 容器 `state improper`、第 5 轮 load 失败。

## Task 11: 治理文档与变更日志登记
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 8, Task 10
- **Description**:
  - 按 §5 第 5 步登记新产品：`docs/README.md`、`docs/00-overview.md`、`docs/01-quickstart.md`；`.agents/CHANGELOG.md` 追加 `日期 | type | 摘要` 条目（含「关联七概念场景」「背景与动机（I）」「本任务落地」块）；应用 `AGENTS.md` 产品清单同步。
  - 依 NFR-5：因控制脚本沿用 `xmnnctl` 名称，预计**无需**在根 `.gitattributes` 新增行尾规则；仅当实施中确实出现新的无 `.sh` 后缀 CLI 时才按 `**/<name> text eol=lf` 追加并沿用该文件注释体例，且须以 `git check-attr -a` 复核。
  - `.trae/specs` 看板经 `docgen` 刷新（不手改生成区）。
- **Acceptance Criteria Addressed**: AC-1、AC-7
- **Test Requirements**:
  - `rule` TR-11.1: 三处 docs 与 CHANGELOG 均出现 `xmflow-cli`，且 CHANGELOG 条目格式与既有条目同构；Evidence = 文件行号
  - `rule` TR-11.2: `git check-attr -a` 对新增 CLI 返回 `text: set / eol: lf`；Evidence = 命令输出
- **实施记录（2026-10-10）**:
  - **登记面（6 处治理文件行号，TR-11.1 Evidence）**：`docs/README.md` 16 处（L11/L15/L41/L44/L45/L47/L51/L55/L58/L62/L69/L72/L88/L117/L120/L131）；`docs/00-overview.md` 4 处（L16/L17/L44/L45）；`docs/01-quickstart.md` 7 处（L19/L24/L77/L181/L184-L186）；`.agents/CHANGELOG.md` 新条目 `### 2026-10-10 | feat | 新增第二个交付产品 xmflow-cli（纯 CLI 客户镜像收编）` 位于 L88-L108，与既有 Task 1 条目（L62-L86）结构同构（`关联七概念场景`/`背景与动机（I）`/`本任务落地`/`影响（交付骨架契约变化点）`/`验收点`/规格链接六块齐全），`xmflow-cli` 出现于 L88/L96/L104/L106/L108；`AGENTS.md` 产品清单同步 13 处（L29/L31/L56/L67/L83/L84/L98 等）；`.agents/rules/delivery-pipeline.md` 4 处（L88/L90/L92）。全仓 count 口径：`xmflow-cli` **173 处 / 24 文件**（Grep count 模式输出 `Found 173 total occurrences across 24 files`）。
  - **TR-11.1 取证**：三处 docs 与 CHANGELOG 均含 `xmflow-cli`（行号如上），CHANGELOG 条目格式与既有条目逐块同构 ✓。
  - **TR-11.2 取证**（PowerShell PATH 无裸 `git`，用全路径 `D:\Program Files\Git\mingw64\bin\git.exe`；cwd=`apps/containers/offline-delivery`）：`git check-attr -a products/xmflow-cli/release/xmnnctl products/xmflow-cli/release/xmnnctl.ps1 bin/relpack bin/relpack.ps1` → 四路径全部 `text: set` / `eol: lf` ✓。依 NFR-5 控制脚本沿用 `xmnnctl` 名称，根 `.gitattributes` **未新增**规则（实施中无新的无 `.sh` 后缀 CLI 出现）。
  - **看板经 docgen 刷新**：环境限制如实登记——本机 Windows 无 Python、WSL 无法访问 SMB 映射盘，经「`robocopy` 同步 `.trae/specs` → 本地 Temp 副本 `C:\Users\XMICUser\AppData\Local\Temp\dashroot`（rc=0）→ WSL 经 `/mnt/c` 运行」变通执行。`docgen.py theme-dashboards --path …` RC=0（共 25 主题 672 Spec，更新 13 主题看板；infra-env 幂等无变化——`add-xmflow-cli-product` 行已在看板且状态口径稳定）；`docgen.py update-spec-readme --path …` RC=0（全局看板压缩至 7 KB / 672 Spec）。副本与 SMB 全量 MD5 比对仅 `.trae/specs/README.md` 1 文件差异（生成日期 2026-09-30→2026-10-10；infra-env 30→31；合计 662→672 spec、完成 439→442、进行中 54→54、待启动 169→176；另含 2026-09-30 以来其他 spec 累积新增：standards-tools +2、okf-wiki-ecosystem +3、classics-knowledge +1、workspace-governance +1 与 cubesandbox/openkylin-wsl-devkit/travel-planner 三新主题行），docgen 产物原样回灌 SMB（生成区未手改）。
  - **docgen 口径差异登记**：docgen 以 frontmatter `status ∈ {completed,done,finished,complete}` 或「`- [x]` 全勾且总数>0」判定完成；本 spec frontmatter 为 `status: "approved"`（SpecWeave 批准门状态，不在集合内）且 Task 用 `- **Status**: `completed`` 文本体例（非 checkbox），故主题看板对本 spec 恒显示「? 待启动」。此为 docgen 既有解析口径与 SpecWeave tasks.md 体例之差异，非本任务引入；修 docgen 或改 tasks.md 体例均超出 Task 11 范围，如实登记不处理。

## Task 12: 清理原件与留档
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3, Task 8, Task 10
- **Description**:
  - 确认内容已全部落地后删除 `apps/containers/client/overlays/native-dev/release/`（若本 feat 之前未删）与本 spec 的 `assets/` 留档；核对仓库内客户镜像定义唯一。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-12.1: 删除前完成 `assets/` 三文件与目标文件的内容去向对照表（每处内容落到哪个文件哪个章节）；Evidence = 对照表
  - `rule` TR-12.2: 删除后 `git grep` 命中集合只落在 `offline-delivery/`（历史条目与本 spec 正文除外）；Evidence = grep 输出
- **TR-12.1 三文件内容去向对照表（2026-10-10，删除前置）**:
  - **前置取证**：`assets/` 三文件与 `apps/containers/client/overlays/native-dev/release/` 三文件 MD5 全等（Containerfile.release `65DE7E183798BCFEA96AD24CC8BEB52D`、USAGE.zh-CN.md `BE8D9F43A43566CDEDE45C2AEE8EDFC9`、build-release.sh `EFB214077B7AE4D7ADEDE28BCA6019E4`，与 spec.md L41-43 登记一致），坐实两处互为纯副本，删除任一不损失信息（FR-12 前提）。
  - **文件一 `USAGE.zh-CN.md`（135 行，7 节）→ 客户面 `products/xmflow-cli/release/README.md`（11 节融合版）**：
    - §1 镜像标签（`xmflow-release:1.2.1`/`:1.2.1-torch` 标签表、体积 1.18 GB/2.09 GB、zstd 加载命令、x86_64、非 root `xmnn`）→ README §5.1 底座形态标签（L272-286，按 OQ-4 裁定以 `base-none`/`base-cpu` 新命名重写：OQ-4 认定历史 tag 从未对外承诺，无需迁移策略；体积改注「参考值，压缩归档以实物为准」）；zstd 离线加载的等价物为 README §7 完整性校验的归档校验口径（L320-338）。
    - §2 快速开始（`/workspace` 工作目录、`/workspace/models:ro` + `/workspace/temp` 挂载表、`compile -n demo.caffe.resnet50` 示例、`--help` 查看参数）→ README §2 五分钟上手（L49-117）+ §4.1 挂载点约定（L190-201）+ §4.3 常用任务命令之 compile 示例（L232-235）。
    - §3 模型组目录契约（目录树、模型名即目录层级 `-n a.b.c`↔`models/a/b/c/`、`config.toml` 字段 `target` 六值/`quantized_dtype`/`tune`/`device_ip`/`device_mount_dir`、产物落 `temp/<模型名>/compile/`）→ README §4.2 模型组目录契约（L202-225）。
    - §4 常用命令（`accuracy`/`infer`/`performance`/`excelreport`/`pipeline`）→ README §4.3 常用任务命令（L226-258）。
    - §5 真机推理网络说明（`--network host`、Docker Desktop 需放通到板卡网段路由、NFS/CIFS 由现场 IT 预挂、`SIM_*` 不依赖外部设备）→ README §4.4 真机推理网络说明（L259-269）。
    - §6 镜像内容边界（包含：Python 3.14 运行时/编译后 tvm-vta-xmnn/LLVM 186MB/六个 target 预编译工具/预置调优库/报告字体；不包含：源码/Nuitka/CUDA-GPU/jupyter-SSH/示例模型）→ README §5.2 镜像内容边界（L288-296，逐项对应）。
    - §7 常见问题（`No module named 'torch'`→改用 cpu 形态；temp 权限→`chmod 0777`/`--user "$(id -u):$(id -g)"`/uid 查询后 `chown`；旧产物权限冲突→`rm -rf temp/<模型名>`；`0x7F7F` 毒值→target 与板卡不匹配非镜像问题）→ README §9 排障（L380-399）+ §11.2 高频问题（L427 起）；FR-8 要求的三条排障口径（`--network host`、uid 规避、`0x7F7F` 判读）均逐条保留。
    - 厂商面：`docs/00-overview.md` 与 `docs/01-quickstart.md` 经 Task 8 通读无承接缺口（USAGE 为纯客户契约），新产品登记行于 Task 11 落盘。
  - **文件二 `Containerfile.release`（136 行，两阶段单文件）→ 拆分为「底座 + 载荷」两段两物（FR-3）**：
    - 头注设计 rationale（wheel-only 客户运行时、无源码树/Nuitka/LLVM dev/conda/jupyter/SSH/CUDA-GPU 栈）→ `products/xmflow-cli/Containerfile.xmflow-cli` 头注（L1-51，重写为底座/载荷两段定位、与 xmnn-runtime 薄镜像的本质差异、外部输入三件、`/opt/conda`↔`/opt/xmflow` ABI 契约）。
    - Stage 0 `pip download` wheelhouse（在线解析依赖闭包）→ **按 FR-3b 彻底删除**，依赖面改由 `deps.txt` 承担（`bin/relpack -p xmflow-cli deps --write` 生成、`deps` 校验；底座 Layer 2 经 `PIP_MIRROR` 联网解析，NFR-3 口径修订：离线限定于客户侧）。
    - Stage 0 可重定位最小 CPython 制备（`cp -a python3.14`、`lib-dynload` 的 `ldd` 闭包收集、`import ssl,ctypes,sqlite3,...` 完整性验证）→ `Containerfile.xmflow-cli` Stage 0（L54-60），制备逻辑固化为 `scripts/relocate-cpython.sh`（符合「含引号验证逻辑固化为脚本文件」范式，§1）。
    - `TORCH_VARIANT=0|1` 形态 ARG 与 torch 2.14.0/torchvision 0.29.0 版本钉死 → `product.env` 可选键 `FLAVORS="none|cpu"` + `TORCH_DEFAULT=none`（FR-6 形态白名单下移，Task 5）；`Containerfile.xmflow-cli` ARG `TORCH_VERSION=2.14.0`/`TORCHVISION_VERSION=0.29.0`（L71-72 同值钉死）+ `--torch` 下发；`scripts/install-torch.sh` 默认值同源。
    - Stage 1 runtime（`FROM docker.io/library/ubuntu:26.04`、ENV 面、`python3.14 -m venv /opt/xmflow`、`useradd xmnn`、`/workspace/models`+`/workspace/temp` 创建与 chown）→ `Containerfile.xmflow-cli` Stage 1（L62 起，同构；`BASE_IMAGE=docker.io/library/ubuntu:26.04` 为 `product.env` 必需键，FR-2）。
    - wheelhouse bind mount 装载货（`pip install --no-index --find-links /wheelhouse`）→ `release/payload/Dockerfile`（`pip install --no-index --no-deps` 装入 `/opt/xmflow` venv + root/xmnn 双身份运行时守卫 + `pip check` 判据收窄到 `^xmnn` 冲突行）。
    - `VOLUME`/`USER xmnn`/`ENTRYPOINT ["/opt/xmflow/bin/xmflow"]`/`CMD ["--help"]` → 底座 ENTRYPOINT/CMD 沿用（payload/Dockerfile 硬约束第 2 条：派生不改 ENTRYPOINT/CMD/WORKDIR，常驻保活由 compose.yaml `command` 覆盖）；非 root `xmnn` 用户与挂载点在底座声明。
    - LABEL `org.specweave.*` 版本溯源 → 底座 LABEL（交付版本由 `bin/relpack` 解析暂存 wheel 后下发，文件内不内嵌常量，§7）+ payload LABEL（`org.specweave.payload-version`/`payload-abi`/`base-image`）。
    - 构建命令（`podman build --network host -f … -t localhost/xmflow-release:1.2.1`）→ `bin/relpack -p xmflow-cli build [--torch cpu] [--pip-mirror aliyun]`（Containerfile.xmflow-cli L32）；镜像名收敛为 `localhost/xmflow-cli:base-<形态>`（OQ-4，消除与历史 `xmflow-release` 的双标签漂移，FR-2）。
  - **文件三 `build-release.sh`（59 行）→ `bin/relpack` 命令面 + `release/xmnnctl`**：
    - 前置检查（`podman image exists` 构建器镜像、wheel 文件存在性，缺失中文 FATAL 退出）→ `bin/relpack` stage/build 前置校验（同构失败路径，NFR-4）。
    - `build_one`（`podman build --network host` + `BUILDER_IMAGE`/`WHL`/`TORCH_VARIANT`/`PIP_INDEX`/`TORCH_INDEX` 五 build-arg + `-t` tag）→ `bin/relpack -p xmflow-cli build` 子命令（形态经 `--torch` 下发、pip 镜像经 `--pip-mirror` 下发，参数化为产品维度）；交付侧派生由 `release/xmnnctl load` 下发 payload/Dockerfile（`--build-arg BASE_IMAGE`/`PAYLOAD_VERSION` + `-t`）。
    - `DIST_DIR` 三级上溯指向 `client/workspace/dist`（违反 §7 禁引用 `client/`，D2 取证要点）→ `product.env` `WHEEL_DIST=../workspace/dist`（D4 裁定，实体目录在 offline-delivery 应用内新建，被 `.gitignore` 忽略不入库）。
    - 用法帮助（`grep '^#'` 头注自打印）与 standard/torch/all 形态子命令 → `bin/relpack -h` 既有 usage 口径 + `--torch none|cpu` 形态参数（`check_enum` fail-fast，Task 5 TR-5.2 取证）。
  - **结论**：三文件内容均已落到 `products/xmflow-cli/`（及 `bin/relpack`、`product.env`、docs 登记行），无信息损失（AC-5 覆盖度判据见 Task 8 实施记录），满足 FR-12「对照表未产出前不得执行删除」的前置条件。
- **实施记录（2026-10-10）**:
  - **用户批准**：用户于 2026-10-10 回复「批准」，授权删除两个目录（工作区红线：删除文件须经人类批准）。
  - **删除执行**：`apps/containers/client/overlays/native-dev/release/` 与 `.trae/specs/infra-env/add-xmflow-cli-product/assets/` 各 3 文件。PowerShell `Remove-Item -Recurse -Force` 先清空文件内容；SMB 网络盘上 PowerShell 对空目录壳删除静默失效（`Test-Path` 假阳性），改用 `[System.IO.Directory]::Delete()` 清除两个空目录壳成功。删除后 `native-dev/` 保留 `builder/`、`docs/`、`scripts/`、`smoke/` 等无关内容；spec 目录仅剩 `spec.md`、`tasks.md`。
  - **git status 取证**：`.trae/specs/infra-env/add-xmflow-cli-product/assets/{Containerfile.release,USAGE.zh-CN.md,build-release.sh}` 呈 `D` 状态；client 侧 release 目录三文件从未纳入 git（2026-10-09 临时产物），删除后无 git 记录，符合「临时产出不入库」纪律。
  - **TR-12.2 取证**（git.exe 全路径，cwd=仓库根 `//10.16.11.3/ai/notebook/dev/libs/AI`）：
    - AC-1 When 口径 `git grep -l -E 'xmflow-release|Containerfile\.release|BUILDER_IMAGE=localhost/native-dev' -- 'apps'` → 命中仅 `apps/containers/offline-delivery/.agents/CHANGELOG.md`（1 文件，落在 `offline-delivery/` 内；其中 `Containerfile.release`/`localhost/xmflow-release:1.2.1` 系 Task 11 新条目「背景与动机（I）」块 L92 对 2026-10-09 收编来源的历史性陈述，属「历史条目除外」范畴，非消费端违例残留）✓
    - 全仓库口径（无 pathspec）→ 命中 3 文件：本 spec 正文 `spec.md`、`tasks.md`（本 spec 正文除外）+ `apps/containers/offline-delivery/.agents/CHANGELOG.md`（历史条目）✓
    - 结论：命中集合只落在 `offline-delivery/`（历史条目与本 spec 正文除外），client 侧零命中 ✓

## Task 13: 独立 Review
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1 - Task 12
- **Description**:
  - Implement 队列清空后创建 `review.md`，为每条 AC/TR 建立检查点（`CP-R*` 覆盖 rule、`CP-U*` 覆盖 rubric），记录 R1 结果与发现。
- **Acceptance Criteria Addressed**: AC-1 至 AC-8
- **Test Requirements**:
  - `rule` TR-13.1: `review.md` 中每条 AC 与 TR 均被至少一个检查点覆盖，无 Pending 证据残留；Evidence = 覆盖映射表
  - `rubric` TR-13.2: 审查结论对「第二产品接入是否验证了当初抽应用的多产品假设」给出判断；scale 1-5;anchors 1=未触及、3=承认假设需验证、5=以改动面数据回答并给出第三产品接入建议;threshold >= 4;evidence = 结论段落
- **Notes**: Specify/Plan 阶段**不得**创建 `review.md`（本队列当前状态即遵守此约束，故本目录只有 spec/tasks 两件套）。
