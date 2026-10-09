---
title: "第二交付产品 xmflow-cli 提案 - Implementation Plan"
status: "draft"
---

# 第二交付产品 xmflow-cli 提案 - Implementation Plan

> 方法链路：I（问题与证据）→ F（约束与方案）→ R（任务拆解）→ T（实施）→ V（验证）→ C（收编登记），场景 3「重构优化」；质量门 G1-G4 由 `TRAE-spec-mode` 批准门与 `review.md` 承担。
>
> 前置约束：本队列**全部任务属后续 feat**，须先通过 spec 批准门；Task 5 是本提案唯一允许的对外契约改动，任何额外 CLI 改动须回到 `delivery-pipeline.md` §7 尾注自查。
>
> 官方落地路径参照：`apps/containers/offline-delivery/docs/01-quickstart.md` §5「新增第二个交付产品」5 步。

## Task 1: 澄清阻塞性开放问题并定稿接入方案
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 就 `spec.md` 的 OQ-1（wheel 源目录与 §7 禁引用 `client/` 的矛盾）、OQ-2（`xmflow-cli` 形态集命名与 tag 影响）、OQ-3（Stage 0 可否移出交付链）取得人类裁定，并把结论回写进 `spec.md`（含必要的 Constraints 调整）。
  - 产出一页方案定稿：底座/载荷切分边界、deps.txt 生成口径、骨架命令面（沿用 `xmnnctl` 或改 `xmflowctl`）。
- **Acceptance Criteria Addressed**: AC-4、AC-8
- **Test Requirements**:
  - `rule` TR-1.1: `spec.md` 的 Open Questions 三条均为「已裁定」状态且有裁定依据（人类批复记录或条款引用）；Evidence = spec.md diff 与批复原文
  - `rule` TR-1.2: 定稿明确写出「底座不含 wheel、载荷只在 `payload/Dockerfile`」与 §9 条款号对应；Evidence = 方案文档片段
- **Notes**: 未完成本任务不得进入 Task 3 之后任何写代码动作。

## Task 2: 建 `products/xmflow-cli/` 与 `product.env`
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建目录，`product.env` 覆盖 `load_product_env` 必需 9 键（`PRODUCT IMAGE_NAME CONTAINERFILE WHEEL_GLOB WHEEL_PREFIX WHEEL_DIST BASE_IMAGE_DEFAULT TORCH_DEFAULT RELEASE_DIR`），`PRODUCT` 等于目录名，`BASE_IMAGE_DEFAULT` 取 `docker.io/library/ubuntu:26.04`。
  - 按 Task 1 裁定补 `FLAVORS` 可选键（Task 5 落地前可先写入并由本地校验容忍）。
- **Acceptance Criteria Addressed**: AC-3、AC-4
- **Test Requirements**:
  - `rule` TR-2.1: `bin/relpack -p xmflow-cli version`（或等价的上下文打印）成功打印「产品/形态/镜像/版本」四元组且无缺键报错；Evidence = 命令输出
  - `rule` TR-2.2: `PRODUCT` 与目录名一致、9 键齐全（静态断言用例）；Evidence = `tests/` 用例名与通过结果

## Task 3: 底座 Containerfile 阶段化改造
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 以 `assets/Containerfile.release` 为素材重写 `Containerfile.xmflow-cli`：只保留可重定位最小 CPython 制备与 venv 创建 + 依赖面安装，**删除构建期安装 xmnn 的 Layer**；构建上下文为产品目录且不含 wheel。
  - 新增 `.dockerignore`；不在 Containerfile 内内嵌 `xmnn` 版本常量（§7）。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 底座文件内不出现 `xmnn`/`xmflow` 安装语句与 wheel 文件名（`grep` 断言为空）；Evidence = grep 命令与输出
  - `rule` TR-3.2: 底座构建上下文内无 `*.whl`；Evidence = `podman build` 上下文上传日志或 `.dockerignore` 断言
  - `rubric` TR-3.3: 与 `Containerfile.xmnn-runtime` 的 Layer 结构一致性（注释口径、LABEL 键集、`org.specweave.*` 命名）；scale 1-5;anchors 1=结构随意、3=主要 Layer 对齐但 LABEL 缺失、5=结构/LABEL/注释三者与本应用惯例同构;threshold >= 4;evidence = 两文件对照

## Task 4: `deps.txt` 生成与离线化
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 用 `bin/relpack -p xmflow-cli deps --write` 生成产品 `deps.txt`（§10 语义：wheel METADATA 中无分号 marker 的 `Requires-Dist`，torch 除外），底座 Containerfile 改为 `pip install -r deps.txt`。
  - 记录与原 Stage 0 `pip download` 闭包的差异清单（原件产物为对照），并对差异作结论。
- **Acceptance Criteria Addressed**: AC-2、AC-3
- **Test Requirements**:
  - `rule` TR-4.1: `bin/relpack -p xmflow-cli deps` 校验通过（rc=0；若缺 unzip/bsdtar 只 `[WARN]` 则如实记录）；Evidence = 命令输出
  - `rule` TR-4.2: 断网（或 `--no-index`）条件下底座构建成功；Evidence = 构建日志中无索引 URL 访问记录
  - `rubric` TR-4.3: 与在线 `pip download` 闭包的差异解释质量；scale 1-5;anchors 1=未比对、3=列出差异未解释、5=差异逐条定位到 marker/extras/平台轮子原因并有处置结论;threshold >= 4;evidence = 差异表

## Task 5: 形态白名单下移（唯一对外契约修订）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 把 `bin/relpack` L27 的 `FLAVORS="cpu|cu130"` 改为「`product.env` 可选键 `FLAVORS` 优先、缺省回退全局常量」；确认 `xmnn-runtime` 行为逐字不变。
  - 同步 `tests/test_relpack_cli.py`、`docs/`（quickstart §5 与 overview 的形态表述）、`.agents/rules/delivery-pipeline.md` 中受影响的条款文字。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-5.1: 未声明 `FLAVORS` 的产品仍以 `cpu|cu130` 校验，非法形态仍 fail-fast 并打印白名单；Evidence = 用例输出
  - `rule` TR-5.2: `xmflow-cli` 用 Task 1 裁定的形态集通过校验，且 `BASE_REF`/`ARCHIVE_BASE` 按形态正确拼装；Evidence = `print_context` 输出
  - `rule` TR-5.3: `bin/` 与 `tests/` 的 diff 仅涉及本项语义（`git show --stat` 可复核）；Evidence = diff 摘要
- **Notes**: 若实施中发现必须第二处改 CLI，立即停止并按 §7 尾注把常量收回 `product.env`，而不是扩大改动。

## Task 6: 产品自有守卫（底座期 + 交付期）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新写 `products/xmflow-cli/smoke/_base_guards.py`（root 与 `xmnn` 双跑；含「载荷未安装」反断言、可重定位 CPython 关键扩展 import 断言、`deps.txt` 逐条已装、`pip check` 判据收窄）与 `smoke/_runtime_smoke.py`（`xmflow --help`、一次 `SIM_VTA2.0` 冒烟、产物文件存在性）。
  - 按 §11 末句把守卫项清单同步进骨架 README、`docs/` 与守卫测试。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 底座守卫在两用户下全绿，且反断言在「误装 xmnn」时确实失败（做一次故意污染验证）；Evidence = 两次运行输出对比
  - `rule` TR-6.2: 守卫项数量与文档列表一致（骨架 README / docs / 测试三处同步）；Evidence = 三处列表截图或行号
  - `rubric` TR-6.3: 守卫断言对客户契约风险的覆盖度（相对 `_base_guards.py` 6 项与 `_runtime_smoke.py` 10 项的等价映射）；scale 1-5;anchors 1=仅 --help、3=覆盖主要运行面但缺可重定位性与权限面、5=每项均有既有产品对应物且新增 CLI 特有断言（uid/挂载写权限/`--network host` 降级说明）;threshold >= 4;evidence = 断言对照表

## Task 7: `release/` 交付骨架新建
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 6
- **Description**:
  - 按 §1 不变量新建 `release/`：控制脚本（bash + `*.ps1` 同构命令面）、`payload/Dockerfile`（`--no-index --no-deps` 装载荷）、`payload/.gitignore` 忽略 `*.whl` 并保留 `.keep`、`.env.example`、`artifacts/.gitignore`、`workspace/.gitkeep`、`README.md`；挂载契约改为 `/workspace/models:ro` + `/workspace/temp`，无 Jupyter 端口/凭证面，`pull_policy: never`。
  - 骨架内零 `../`、零 Python。
- **Acceptance Criteria Addressed**: AC-1、AC-3、AC-5、AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 骨架不变量用例全绿（清单、无 `../`、无 `.py`、`pull_policy: never`、`.env.example` 无 CR、shebang 全 LF、两端命令同构）；Evidence = pytest 输出
  - `rule` TR-7.2: `./xmnnctl init → load → up → smoke → down`（或新命名等价四步）全部 rc=0；Evidence = `smoke` 命令输出
- **Notes**: 与本应用 `xmnn-runtime/release/` 并存的两份骨架属预期（客户面不同），不构成 G4 双写；但公共控制逻辑若出现第三次复制，须先抽公共再取第三产品。

## Task 8: 客户契约文本迁移
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 把 `assets/USAGE.zh-CN.md` 7 节逐节迁入 `release/README.md`（客户面）与 `docs/`（厂商面），命令示例改用最终镜像名与形态 tag；保留三条 FAQ 口径与真机网络/NFS 边界表述。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rubric` TR-8.1: 客户文档对原件 7 节的信息覆盖度（判据同 AC-5）；scale 1-5;anchors 1=多节缺失、3=细节丢失、5=全覆盖且可执行;threshold >= 4;evidence = 逐节对照表
  - `rule` TR-8.2: 文档内所有命令示例的镜像名/挂载路径与实际骨架一致（无残留 `xmflow-release` 旧名）；Evidence = grep 断言为空

## Task 9: 测试多产品参数化
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 7
- **Description**:
  - `tests/conftest.py` 的 `PRODUCT_NAME` 改为按 `products/*/` 发现并参数化；`tests/test_release_skeleton.py` 内 `xmnn-runtime` 字面量断言改为产品参数驱动；为 `xmflow-cli` 增加产品专属用例。
  - `xmnn-runtime` 既有断言语义**不得**改动。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-9.1: `pytest` 全绿，且 `--collect-only -q` 用例数随产品数变化；Evidence = 前后 collect 计数
  - `rule` TR-9.2: 临时新增假产品（仅 `product.env` + 骨架清单）即被自动覆盖，删除后结果复原；Evidence = 两次运行输出
- **Notes**: 本任务与 Task 5 均触 `tests/`，实施顺序上 Task 9 应在 Task 5 之后合并，避免同一测试文件两笔交叉改动。

## Task 10: 端到端真机验证与体积实测
- **Status**: `pending`
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

## Task 11: 治理文档与变更日志登记
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 8, Task 10
- **Description**:
  - 按 §5 第 5 步登记新产品：`docs/README.md`、`docs/00-overview.md`、`docs/01-quickstart.md`；`.agents/CHANGELOG.md` 追加 `日期 | type | 摘要` 条目（含「关联七概念场景」「背景与动机（I）」「本任务落地」块）；应用 `AGENTS.md` 产品清单同步。
  - 如新增无 `.sh` 后缀 CLI（如 `xmflowctl`），在根 `.gitattributes` 追加 `**/<name> text eol=lf` 并沿用该文件注释体例。
  - `.trae/specs` 看板经 `docgen` 刷新（不手改生成区）。
- **Acceptance Criteria Addressed**: AC-1、AC-7
- **Test Requirements**:
  - `rule` TR-11.1: 三处 docs 与 CHANGELOG 均出现 `xmflow-cli`，且 CHANGELOG 条目格式与既有条目同构；Evidence = 文件行号
  - `rule` TR-11.2: `git check-attr -a` 对新增 CLI 返回 `text: set / eol: lf`；Evidence = 命令输出

## Task 12: 清理原件与留档
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 3, Task 8, Task 10
- **Description**:
  - 确认内容已全部落地后删除 `apps/containers/client/overlays/native-dev/release/`（若本 feat 之前未删）与本 spec 的 `assets/` 留档；核对仓库内客户镜像定义唯一。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-12.1: 删除前完成 `assets/` 三文件与目标文件的内容去向对照表（每处内容落到哪个文件哪个章节）；Evidence = 对照表
  - `rule` TR-12.2: 删除后 `git grep` 命中集合只落在 `offline-delivery/`（历史条目与本 spec 正文除外）；Evidence = grep 输出

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
