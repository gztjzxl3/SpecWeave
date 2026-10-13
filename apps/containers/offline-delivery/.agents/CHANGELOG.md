# offline-delivery 变更日志（原子提交汇总）

> 本文件只记录 `apps/containers/offline-delivery` 特有改动；SpecWeave 工作区根级、
> apps/containers 组级、其它成员（jupyter-podman-rootless / client / shared）的改动不在范围内。
> 格式：`日期 | type | 摘要`（type 遵循 Conventional Commits）；每条须可追溯（关联规格或 commit）、
> 关联七概念场景、说明验收点。

## [Unreleased]

### 2026-09-21 | refactor | 底座/载荷分离：xmnn wheel 安装从镜像构建期拆到交付阶段

**关联七概念场景**：场景3「重构优化」——把频繁变动的载荷与极慢变动的底座解耦，消除「换一个 whl 就要重打整镜像」的重复成本。

**背景与动机（I）**：载荷 wheel（约 177 MB）随每个交付版本变化，而底座依赖面（torch + 20 条运行时依赖）变化极慢；
原设计把 wheel 装入镜像构建期，导致每次换 whl 都要重跑 torch 与依赖安装（首轮联网约 3 分钟、数 GB 网络往返），
且交付包必须整包重发。此外，若把 wheel 安装改到交付期却**不做依赖闭包与守卫分段**，缺失依赖只会在客户运行期以
`ImportError` 暴露（`--no-deps` 会静默掩盖），故本次重构必须同时补齐依赖清单与两段守卫。

**本任务落地**：

- **底座镜像**：`localhost/xmnn-runtime:base-<形态>`（cpu|cu130，**无 `:latest`、不含 xmnn**）＝ cp314 GIL base env +
  torch + 依赖面（`products/xmnn-runtime/deps.txt`，20 条无条件依赖）+ ipykernel + 内核注册脚本 + 守卫脚本；
  构建上下文收敛为产品目录（`Containerfile.xmnn-runtime` + `deps.txt` + `scripts/` + `smoke/`），**`wheels/` 目录删除**。
- **底座守卫**：新增 `smoke/_base_guards.py`（Layer 4，root/devuser 双跑，6 项）：双 ABI / `deps.txt` 逐条核验 /
  `pip check`（放行基镜像既有的 conda×ruamel-yaml 单条冲突）/ torch 形态（marker vs `version.cuda`）/ 内核双可见 /
  **反断言 `import xmnn` 必须失败**。
- **交付侧派生构建**：交付包新增 `release/payload/{Dockerfile,.gitignore,.keep}` 与 `payload/xmnn-*.whl`
  （177 MB，不入 git）；客户 `xmnnctl load` 语义改为「幂等导入底座（按 `release.json.image.id` 比对，已在则跳过）→
  校验载荷 sha256 → 以 `payload/` 为上下文派生构建 `localhost/xmnn-runtime:<交付版本>`
  （`pip install --no-index --no-deps`，载荷守卫与 `pip check` 在 `RUN` 内执行，失败即无 tag）→ 校验 `.env` 版本与清单一致」；
  `smoke`/`version` 改用派生镜像与清单；**`compose.yaml` 逐字未变（对外契约稳定）**。
- **制品与清单**：`bin/relpack` 的 `stage` 目标改为 `release/payload/`；新增 `deps [--write]`（解析 whl
  `Requires-Dist` 无条件项并与 `deps.txt` 比对，**deps 变化必须重发底座**）；`build` 产 `:base-<形态>`；
  `pack` 产 `artifacts/<镜像名末段>-base-<形态>.tar.gz` + **schema v2 `release.json`**
  （`payload{file,version,size_bytes,sha256}` / `image{ref,id,torch_version,torch_flavor,abi}` /
  `archive{file,size_bytes,sha256}`）；`smoke` 改为走交付骨架 `load → up → smoke → down`。
- **文档与治理同步（本切片）**：`AGENTS.md`（项目概述 / 路由树 / P0 约束速览 8→12 条）、`README.md`（命令表 + 快速开始 + 收益口径）、
  `docs/00-overview.md`（双制品流）、`docs/01-quickstart.md`（`deps` 命令 + 失败处置 + 新增「更新交付（只换 whl）」）、
  `rules/delivery-pipeline.md`（§1 契约修订至契约冻结 + 新增 §9-§12）。

**影响（交付骨架契约变化点）**：`release/` 新增 `payload/`（载荷 wheel + 派生 `Dockerfile`）并纳入契约；
`xmnnctl load` 语义从「导入镜像」变为「导入底座 + 派生构建」；`release.json` 升 schema v2（顶层 `version` 为载荷版本，
新增 `payload` 块与双 `sha256`）；底座 tag 不再有 `:latest`；**`compose.yaml` / `xmnnctl` 命令面 / `.env` 键未变**。

**实测事实**：底座镜像 2.47 GB（首轮联网装依赖约 3 分钟）；底座校验 6 项全过、`deps.txt` 20 条逐条 `[OK]`；
载荷守卫 10/10；派生镜像增量约 +0.18 GB、构建 1-3 分钟。收益口径：换 whl 只需重发约 **177 MB 载荷**，
而非约 **1.1 GB 底座归档**（旧口径「4 GB」指 cu130 形态镜像，属误传，不沿用）。

**验收点**：底座守卫 6/6、载荷守卫 10/10、`deps` 一致性校验、`pack` schema v2 清单与归档原子性；
真机端到端结论见统一验证记录（后续统一验证回填实测输出与 `release.json` 核对结论）。

### 2026-09-21 | feat | 应用抽取：客户离线交付链路从 client 迁出为独立应用

**关联七概念场景**：场景3「重构优化」——把寄居在消费端的交付链路还给交付方自持。

**背景与动机（I）**：客户交付物（镜像定义 + 打包器 + `release/` 骨架）原寄居在
`apps/containers/client/overlays/xmnn-runtime/`，打包器 `relpack.py` 位于 `jpman_client`
包内并硬编码 client 根路径，镜像构建依赖 client 的 `overlays/_shared/base-rootless.yaml`
与 invoke 编排内核——「一份客户交付物要拖着整个 client 与 shared 才能构建」。
交付物应独立演进（自有产品参数、版本语义、发布节奏），不应被消费端重构连带影响。

**本任务（Task 1：应用骨架与治理资产）落地**：

- 新建应用根 `apps/containers/offline-delivery/`（目录名**不含 `xmnn`**，为多产品扩展预留）
- `AGENTS.md`：启动协议块（PRIORITY ZERO）+ 项目概述 + 嵌套路由图 + 上下文路由表 + P0 约束速览 8 条
- `README.md`：人类入口（定位、与 client / jupyter-podman-rootless 的关系、快速开始、命令表）
- `.gitignore`：wheel 与镜像归档不入 git（保留 `wheels/.gitignore` 与 `artifacts/.gitignore` 例外）
- `.agents/`：资产容器索引 + 本变更日志 + 唯一规则主题 `rules/delivery-pipeline.md`（8 节）
- `docs/`：`README.md`（索引）+ `00-overview.md`（定位/制品流/边界）+ `01-quickstart.md`（逐命令 + 失败处置 + 新增第二个产品）
- 仓库根 `.gitattributes`：新增 `**/relpack` 与 `**/relpack.ps1` 的 `text eol=lf`，注释由旧便捷壳指向本应用

**验收点**：AC-5（治理资产同步）、AC-9（文档可执行）；规格
[.trae/specs/infra-env/extract-offline-delivery-app/](../../../../.trae/specs/infra-env/extract-offline-delivery-app/spec.md)。

**未跟踪 / 待后续任务完成（本应用当前不可运行）**：

- `bin/relpack` 与 `bin/relpack.ps1`：尚未落盘（并行任务负责），故本次无 `bash -n` / pwsh 解析证据
- `products/xmnn-runtime/`：`product.env`、`Containerfile.xmnn-runtime`、`scripts/`、`smoke/`、
  `wheels/`、`release/` 交付骨架均待迁移（Task 2 / Task 3）
- `tests/`：交付骨架与 CLI 静态守卫测试待新增（Task 5）
- `client/` 侧原实现（`overlays/xmnn-runtime/`、`relpack.py`、`tasks/xmnnrt.py` 等）尚在（Task 6）；
  在此之前 `.gitattributes` 中 `**/xmnnctl` 旧规则仍被 client 侧文件需要，不得删除
- 看板刷新与全量门禁（Task 7 / Task 8）未执行

**待验证**：本文件所列路径在 Task 2/Task 3 落盘前，`docs/01-quickstart.md` 中命令示例不可执行；
Task 8 真机验证通过后须回填 `pack` / `smoke` 实测输出与 `release.json` 核对结论。

### 2026-10-10 | feat | 新增第二个交付产品 xmflow-cli（纯 CLI 客户镜像收编）

**关联七概念场景**：场景3「重构优化」——把寄居在消费端覆盖层的三份客户交付资产收编进交付方自持应用，并借收编实证「多产品」假设（`products/<名>/` 扩展无需 CLI 改动）；场景5「知识沉淀」——原 `USAGE.zh-CN.md` 七节用法知识落入 `release/README.md` 与 `docs/` 文档集。

**背景与动机（I）**：2026-10-09 在 client 侧临时产出 xmflow 客户发布镜像，三份资产（`Containerfile.release`、`build-release.sh`、`USAGE.zh-CN.md`）落 `apps/containers/client/overlays/native-dev/release/`，违反 delivery-pipeline §7「禁依赖 client」与 C26 归属纪律（交付物寄居消费端）；且与既有 `xmnn-runtime` 镜像定义形成两份平行镜像定义的漂移风险；客户侧真机验证镜像（`localhost/xmflow-release:1.2.1`，约 1.18 GB）与中文契约文本存在丢失风险。经 D3 裁定就地改写而非另起应用：原资产与交付链存在四处结构性错位——依赖闭包语义（`pip download` wheelhouse 预装 vs `deps.txt` 底座依赖面）、形态白名单无法表达 `none`（全局 `cpu|cu130`）、守卫硬耦合 conda+Jupyter 谱系、测试与交付骨架不可复用（参数硬编码 `xmnn-runtime`）。

**本任务落地**：

- **产品资产**（`products/xmflow-cli/`）：`product.env`（9 必需键 + 可选键 `FLAVORS="none|cpu"`、`TORCH_DEFAULT=none`、`BASE_IMAGE_DEFAULT=docker.io/library/ubuntu:26.04`）；`Containerfile.xmflow-cli` 两段两物——Stage 0 借构建器镜像 `localhost/native-dev:nuitka-4.2.2-hotfix` 制备可重定位最小 CPython（`ARG BUILDER_IMAGE` 产品级常量，不进 `product.env` 必需键与 `bin/relpack`），Stage 1 以 `ubuntu:26.04` 为基座建隔离 venv `/opt/xmflow`、按 `deps.txt`（20 条）装依赖面、torch 前端形态 `none|cpu` 分层、反断言 `import xmnn` 必须失败；`scripts/`（`relocate-cpython.sh` + `install-torch.sh`）；`smoke/` 产品自有双守卫（`_base_guards.py` 6 项 + `_runtime_smoke.py` 10 项 + `pip check`）；`release/` 交付骨架沿用 `xmnnctl` 名与 `XMNN_VERSION` 键（FR-5），无 Jupyter/SSH 端口面与凭证注入，数据面为 `./workspace/models:ro` 与 `./workspace/temp` 两处绑定挂载。
- **载荷阶段化**（§9 同构）：载荷 wheel 只在交付侧由 `xmnnctl load` 以 `--no-index --no-deps` 派生装入，不进底座构建上下文。
- **FR-6 唯一 CLI 改动**：`bin/relpack` 形态白名单下放为 `product.env` 可选键 `FLAVORS`（未声明回退全局缺省 `cpu|cu130`）；`bin/relpack.ps1` 同步。
- **FR-10 测试两层拆分**：`tests/` 拆为通用不变量层（37 项/产品）与私有契约层（13 项/产品 registry），新增产品零测试改动。
- **知识保留**（Task 8）：`USAGE.zh-CN.md` 七节信息逐节对照落入 `release/README.md`，含 `--network host`、uid 规避、`0x7F7F` 三条排障口径。
- **FR-9 外部输入登记**：`.agents/rules/delivery-pipeline.md` §7 外部输入清单由两项改为三项（构建器镜像登记为厂商侧构建期输入，不进入交付链）；`docs/00-overview.md`「输入」同步。
- **Task 11 治理登记**：`docs/` 三篇、`AGENTS.md`（概述/路由树/路由表/P0 约束速览）、`README.md`（关系表/目录结构/命令表）同步为两产品口径。

**影响（交付骨架契约变化点）**：`xmnn-runtime` 对外契约零变化；新产品 `products/xmflow-cli/release/` 为新客户契约（`compose.yaml` 无端口面、`xmnnctl` 命令面与 `.env` 键沿用既有骨架契约）。

**实测事实**：pytest 本地盘副本 159 passed / 16 skipped / 0 failed（SMB/UNC 直跑 3 例属 WSL UNC 翻译环境限制，已登记非回归）；collect 线性（骨架 `skeleton=102=2×50+2`，加假产品 `152=3×50+2`），`test_relpack_cli.py=23` 不变；`guard_crlf_shebang` 函数直跑扫描 11 文件 rc=0；`git check-attr -a` 四路径（`products/xmflow-cli/release/xmnnctl`、`xmnnctl.ps1`、`bin/relpack`、`bin/relpack.ps1`）均 `text: set / eol: lf`（TR-11.2）。Task 10 端到端实跑 blocked：五步 rc 依次 0/0/1/1/1（build Stage 0 构建器镜像 `connection refused` 三次重试败；`podman pull ubuntu:26.04` 三次败于 DNS 污染），根因逐条登记于 tasks.md；底座体积与派生增量实测值待 Unblock Condition 满足后回填。

**验收点**：AC-1（Task 12 删除 client 侧原件后达成）、AC-2/AC-3/AC-7（随 Task 10 真机解禁回填）、AC-4/AC-5/AC-6 已由 Task 5/8/9 取证；规格：[.trae/specs/infra-env/add-xmflow-cli-product/](../../../../.trae/specs/infra-env/add-xmflow-cli-product/spec.md)。