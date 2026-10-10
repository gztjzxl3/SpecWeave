# offline-delivery - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本应用是 SpecWeave apps/containers/ 下的独立交付应用：
>         ../AGENTS.md（组级路由）、../../AGENTS.md（apps 应用区入口）、
>         ../../../AGENTS.md（SpecWeave 根契约）、../../.agents/（组级 AI 资产容器）
> 步骤 3：文档边界 — 对外人类可读文档唯一入本应用 docs/（docs/README.md 为索引入口）；
>         .agents/ 只放 AI 资产；禁止向 .agents/docs/ 写入任何产出物（该路径已废止）
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本应用=公开开源代码；产出物落本应用 docs/ 或应用目录内，
>     禁止向 .agents/docs/ 写入任何产出物）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 改动涉及客户交付骨架（release/）时已加载 .agents/rules/delivery-pipeline.md §1
>   □ 未把本应用规则/文档复制到父级组层（组层反双写纪律 G4）
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **apps/containers/offline-delivery（厂商侧离线交付链路）** 的应用级路由入口，
> 只承载本应用特有事实；未覆盖的规则逐级回退父级（见「上下文路由表」末两行）。

## 项目概述

- **应用性质**：厂商侧**离线交付链路**——把预构建载荷 wheel 与基镜像变成客户可自持的离线交付包；镜像采用**底座/载荷分离**（2026-09-21 起）：底座镜像（cp314 GIL base env + torch + 依赖面，**不含 xmnn**）在厂商侧构建归档，载荷 wheel 随交付包发出、由客户侧 `xmnnctl load` 派生装入
- **能力面**：`stage`（暂存载荷 wheel）→ `deps`（校验/重写载荷依赖集 `deps.txt`）→ `build`（构建底座镜像 `<镜像名>:base-<形态>`）→ `pack`（导出底座归档 + 校验清单）→ `smoke`（以交付骨架为唯一入口做 `load → up → smoke → down` 端到端验证）；日常运行与排障直接使用交付骨架自带的 `xmnnctl` / `xmnnctl.ps1`
- **产物**：① 客户 `release/` 交付骨架（零 Python、零仓库外引用）；② `release/artifacts/<镜像名末段>-base-<形态>.tar.gz` + 同目录 `release.json`（schema v2）；③ `release/payload/` 内载荷 wheel（约 177 MB，随交付包发出、不入 git）
- **外部输入（共三项，权威清单见 `.agents/rules/delivery-pipeline.md` §7）**：预构建载荷 wheel `../workspace/dist/xmnn-*.whl`（不进底座构建上下文）；基镜像 `BASE_IMAGE_DEFAULT`（按产品：`xmnn-runtime` 为 `localhost/jupyter-podman-rootless:latest`、`xmflow-cli` 为 `docker.io/library/ubuntu:26.04`）；构建器镜像 `localhost/native-dev:nuitka-4.2.2-hotfix`（仅 `xmflow-cli` 构建期使用，由 `client` 的 native-dev 构建链产出，厂商侧构建期输入，不进入交付链）
- **工具链**：`bin/relpack`（bash，WSL/Linux/macOS）+ `bin/relpack.ps1`（pwsh7，Windows 原生经 `wsl.exe` 桥接）；**零 Python**，不引入 pip / invoke / podman-py
- **产品分层**：应用工具（`bin/`）+ 多产品（`products/<产品名>/`）；现有两个产品——首个 `products/xmnn-runtime/`（Notebook 交互面）与第二产品 `products/xmflow-cli/`（纯 CLI 客户镜像，形态 `none|cpu`），产品参数单一事实源为 `products/<产品>/product.env`
- **禁止依赖**：`apps/containers/client/` 与 `apps/containers/shared/` 的任何路径或代码
- **父级工作区**：[../AGENTS.md](../AGENTS.md)（组级）→ [../../AGENTS.md](../../AGENTS.md)（apps 区）→ [../../../AGENTS.md](../../../AGENTS.md)（根契约）
- **AI 资产容器**：[.agents/](.agents/README.md)（仅一个规则主题 `rules/delivery-pipeline.md`）
- **人类文档**：[docs/](docs/README.md)（索引 + 概述 + 快速开始）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ apps/containers/AGENTS.md（组级路由入口，仅承载跨成员事实）
            └─ apps/containers/offline-delivery/AGENTS.md（本文件 = 应用级路由入口）
                 ├─ README.md                        ← 人类入口：定位、快速开始、命令表
                 ├─ docs/                            ← 人类可读文档（索引 + 2 篇）
                 │    ├─ README.md                   ← 文档索引
                 │    ├─ 00-overview.md              ← 定位 / 底座与载荷双制品流 / 与组内其它应用边界 / 目录结构
                 │    └─ 01-quickstart.md            ← 前置条件 + 逐命令（stage/deps/build/pack/smoke）+ 失败处置 + 更新交付 + 新增交付产品
                 ├─ .agents/                         ← 本应用 AI 资产容器
                 │    ├─ README.md                   ← 资产索引 + 父级回退链
                 │    ├─ CHANGELOG.md                ← 应用变更日志（原子提交汇总）
                 │    └─ rules/delivery-pipeline.md  ← 唯一规则主题：离线交付流水线硬约束（12 节）
                 ├─ bin/                             ← relpack（bash）+ relpack.ps1（pwsh7）工具链入口
                 ├─ products/<产品名>/               ← 单产品全部资产；product.env 为参数单一事实源
                 │    ├─ xmnn-runtime/               ← 首个产品：product.env + deps.txt + Containerfile + scripts/ + smoke/ + release/（含 payload/ 载荷目录与派生 Dockerfile）
                 │    └─ xmflow-cli/               ← 第二产品（纯 CLI，形态 none|cpu）：product.env + deps.txt + Containerfile.xmflow-cli + scripts/（relocate-cpython + install-torch）+ smoke/ + release/（无 Jupyter/SSH 端口面与凭证注入）
                 └─ tests/                           ← 交付骨架与 CLI 静态守卫测试（pytest，不建 Python 包）
```

**嵌套优先原则**：进入 `products/<产品>/` 后仍以本文件为最近入口；未覆盖规则按 本应用 → apps/containers → apps → SpecWeave 根 逐级回退。

## 上下文路由表（任务类型 → 入口）

| 任务类型 | 必读入口 |
|---------|---------|
| 新增交付产品 | [docs/01-quickstart.md](docs/01-quickstart.md)（「新增交付产品」）+ [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §7 |
| 改镜像定义与 Containerfile | `<产品>/product.env` + `<产品>/deps.txt` + `<产品>/Containerfile.<产品名>`（现有 `products/xmnn-runtime/` 与 `products/xmflow-cli/`）+ 本文件「P0 约束速览」 |
| 改依赖集 / 载荷（`deps.txt`、`release/payload/`） | [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §9-§10 + [docs/01-quickstart.md](docs/01-quickstart.md)（「更新交付（只换 whl）」） |
| 改打包 CLI（`bin/relpack*`） | [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §2-§6 §9-§12（CRLF 守卫/版本语义/形态 tag/归档原子性/release.json/底座与载荷分离/依赖闭包/守卫分段/清单解析） |
| 改交付骨架（客户契约，`release/`） | [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §1（对外契约冻结与零 `../`）+ 骨架内 `README.md` |
| 失败排障（缺 wheel/镜像/podman/podman-compose/端口占用） | [docs/01-quickstart.md](docs/01-quickstart.md)（「常见失败与处置」） |
| 全局提交与代码规范 | [../../../AGENTS.md](../../../AGENTS.md) → [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) |
| Skill 与七概念指令 | [../../../.agents/skills/README.md](../../../.agents/skills/README.md) / [../../../.agents/commands/README.md](../../../.agents/commands/README.md) |

## P0 约束速览（违反 = 打回）

| # | 约束 | 权威事实源 |
|---|------|-----------|
| 1 | **交付骨架对外契约冻结**：`release/` 内 `compose.yaml` 逐字不变，`xmnnctl` 命令面与 `.env` 键不变，不得出现指向仓库其他文件的相对路径（`../`）。本次重构已把**载荷目录 `payload/`（wheel + 派生 `Dockerfile`）**与**新增守卫脚本**纳入契约 | [delivery-pipeline.md](.agents/rules/delivery-pipeline.md) §1 |
| 2 | **CRLF shebang 守卫**：`pack` 前扫描骨架内 shebang 脚本，命中 CR 即 fail-fast，绝不产出坏字节 | 同上 §2 |
| 3 | **归档原子性**：`podman save \| gzip -1` → `gzip -t` → 原子 `mv`，不在交付目录留截断归档 | 同上 §5 |
| 4 | **版本语义**：默认取暂存载荷 wheel 版本；GA 交付用 `--version` 显式指定 | 同上 §3 |
| 5 | **底座形态感知 tag 且无 `:latest`**：`build` 只产 `<IMAGE_NAME>:base-<形态>`（形态白名单为各产品 `product.env` 可选键 `FLAVORS`，未声明回退全局缺省 `cpu\|cu130`；`xmflow-cli` 声明 `none\|cpu`，缺省形态取自其 `TORCH_DEFAULT=none`）；交付镜像 tag `<IMAGE_NAME>:<交付版本>` 由客户侧派生时下发 | 同上 §4 |
| 6 | **零 Python 与禁依赖**：CLI 仅需 bash 4+ / pwsh 7.4+ / podman；禁止依赖 `client/`、`shared/`；外部输入三项（载荷 wheel、基镜像、仅 `xmflow-cli` 构建期的构建器镜像，见 §7） | 同上 §7 |
| 7 | **Windows 一律 pwsh7**：禁止 Windows PowerShell 5.1；容器命令统一经 `wsl.exe` 桥接 | 同上 §8 |
| 8 | **载荷 wheel 与镜像归档不入 git**：`products/*/release/payload/*.whl`、`products/*/release/artifacts/*` 由 `.gitignore` 守卫（仅放行 `.gitignore` / `.keep` 例外） | [.gitignore](.gitignore) |
| 9 | **底座与载荷分离**：底座镜像**绝不安装 xmnn 载荷**（底座守卫含反断言 `import xmnn` 必须失败）；载荷只由交付侧 `release/payload/Dockerfile` 派生装入 | 同上 §9 |
| 10 | **依赖集变化必须重发底座**：`deps.txt` 是底座依赖面唯一事实源；派生安装走 `--no-index --no-deps`（**不会**补装缺失依赖），`deps`/`pack` 前置守卫不一致即 fail-fast | 同上 §10 |
| 11 | **守卫分段**：构建期底座守卫（6 项，root/devuser 双跑）拦底座缺陷；交付期载荷守卫（10 项 + `pip check`）在派生构建的 `RUN` 内执行，**任一不过即不产出 tag** | 同上 §11 |
| 12 | **清单 schema v2 双 `sha256` 按块解析**：`payload` 与 `archive` 两块各含 `sha256`，读取方必须按块定向取值，禁止抓「全局第一个 sha256」 | 同上 §12 |

## 变更日志

完整条目见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- 2026-09-21 | refactor | 底座/载荷分离：xmnn wheel 安装从镜像构建期拆到交付阶段（底座镜像 `<镜像名>:base-<形态>` 无 `:latest` 且不含载荷；交付包新增 `release/payload/` 与派生 `Dockerfile`，客户 `xmnnctl load` 幂等导入底座 + 派生构建交付镜像）；新增 `bin/relpack deps`（依赖集 `products/<产品>/deps.txt`）与底座守卫 `smoke/_base_guards.py`；`pack` 改写 schema v2 `release.json`
- 2026-09-21 | feat | 应用抽取：客户离线交付链路迁出 `apps/containers/client/overlays/xmnn-runtime/`，落为完全自包含应用 `offline-delivery/`（目录名不含 `xmnn`，多产品经 `products/<名>/` 扩展）；工具链改为 bash + pwsh7 双入口零 Python CLI（`bin/relpack*`）。规格：[.trae/specs/infra-env/extract-offline-delivery-app/spec.md](../../../.trae/specs/infra-env/extract-offline-delivery-app/spec.md)
- 2026-10-10 | feat | 新增第二个交付产品 xmflow-cli（纯 CLI 客户镜像，形态 none|cpu）：收编原 `client/overlays/native-dev/release/` 三份资产为 `products/xmflow-cli/`（product.env + Containerfile.xmflow-cli + deps.txt + scripts/ + smoke/ + release/ 交付骨架）；`bin/relpack` 形态白名单下放为 product.env 可选键 `FLAVORS`（唯一 CLI 改动）；`tests/` 参数化改造支持多产品；规格：[.trae/specs/infra-env/add-xmflow-cli-product/spec.md](../../../.trae/specs/infra-env/add-xmflow-cli-product/spec.md)