# REA OKF Wiki 知识包创建 - Implementation Plan

> 遵循 `seven-concepts-cmd`（场景 4 知识沉淀）+ `source-code-to-okf-wiki`（R→I→E→V→C 五阶段链路）执行。产物唯一权威参考：`source-code-to-okf-wiki` §6 OKF 文档规范。

## Task 1: 信源采集与稳定性登记（阶段 0 + R 前）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集五行公开信源内容：`rea.run/zh`、知乎专栏 `2091916182064456398`、GitHub `ringozzt/rea-research`、`rea.tools/zh-CN` 文档站、本地源码 `external/dao/rea`（main @ `eaf88aca`）。
  - 核实 `rea.run/zh` 与 `rea.tools/zh-CN` 关系、`ringozzt/rea-research` 与 `morluto/rea` 关系。
  - 在 `references/` 生成信源登记文件（source-manifest.md），记录每份信源的 URL、类型、采集日期、版本（源码固定 commit hash）。
  - G0 门：确认信源皆 stable/可追溯（源码以 commit hash 固定）。**风险**：源码为 env-bound `main` 浮动分支，登记 commit hash `eaf88aca` 即可追溯。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 五行信源均被读取并登记；`references/source-manifest.md` 存在且含每份信源的 URL + 采集日期 + 版本信息。证据：读 source-manifest.md、抓取/读取记录。
  - `rule` TR-1.2: 本地源码版本以 commit hash `eaf88aca` 登记（不锚定浮动 `main` 名）。证据：source-manifest.md 的 commit 字段。

## Task 2: R 阶段事实采集（facts.md）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通读源码核心目录（`src/domain`/`src/server`/`src/cli` 语义层、`src/ghidra`/`src/ida`/`src/hopper`/`src/jeb`/`src/adb`/`src/evm`/`src/wasm` 提供方适配器）与 README/docs，提取可验证事实。
  - 每条事实编号 `F-xxx`，写入 `references/facts.md`，指向上游来源（源码路径 / 信源 URL）。
  - G1 门：facts 中零推断词（"用于/目的是/设计为"）。
  - 数量类事实（工具数、提供方数、CLI 命令数、分析目标类型数等）对固定 commit blob 用独立脚本/Grep 计数，人工枚举不得为唯一来源。
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-2.1: `references/facts.md` 存在，含 ≥30 条 F-xxx 事实，每条含来源指向。证据：读 facts.md。
  - `rule` TR-2.2: facts.md 无推断词（不含"用于/目的是/设计为"等）。证据：Grep 扫描 facts.md。
  - `rule` TR-2.3: 每条数量类断言有独立计数依据（脚本/Grep 输出），写于 facts 或留痕。证据：计数脚本输出与该数字。

## Task 3: I 阶段架构洞察（insights.md + 知识地图）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 基于 facts 提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组），写入 `references/insights.md`。
  - 设计知识地图与学习路径（入门→架构→工具矩阵→实践），确定 concepts 文档分组与每篇覆盖的 F-xxx。
  - G2 门：洞察四元组完整。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-3.1: `references/insights.md` 存在，含 3-5 个洞察，每个含证据引用具体 F-xxx。证据：读 insights.md。
  - `rubric` TR-3.2: 知识地图合理性与覆盖度；scale 1-5；anchors：1=无分层、3=覆盖是什么/怎么工作/能分析什么、5=分层清楚+架构+工具矩阵+学习路径；threshold ≥ 4。证据：知识地图章节。

## Task 4: E 阶段批量生成 OKF 文档（信源先行）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 先完成 `references/`（source-manifest、facts、insights、index），再分批生成 `concepts/`（每批 ≤7 文件，约 4-7 篇：是什么/工作原理/架构/支持的分析目标与工具矩阵/安装与入门/CLI 与 MCP/证据与局限），后生成 `examples/`（安装、setup、CLI 分析示例）。
  - 最后写各级 `index.md`（根 + 子目录，均含 toctree）。
  - G3 门：references 先于 concepts；分类生成；index 最后写。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: bundle 目录结构 = index.md + log.md + concepts/(index+内容) + examples/(index+内容) + references/(index+source-manifest+facts+insights)。证据：LS。
  - `rule` TR-4.2: 每个 index.md 含 `{toctree}` 并收录本目录全部内容文档；子目录 index.md 不含 frontmatter。证据：读 index.md。
  - `rule` TR-4.3: 每篇概念/示例文档 frontmatter 字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）。证据：抽查 3+ 文档。
  - `rule` TR-4.4: 交叉链接用 `/` 开头 bundle-relative 路径。证据：Grep 无 `../concepts`/`file:///` 残留。

## Task 5: 主题索引登记
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 在 `jishu/ai/products/index.md` 束导航表新增 rea 行、toctree 新增 `rea/index`。
  - （CI 由子项目 gate 负责，本任务只登记索引入口。）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-5.1: products/index.md 的束导航表含 rea 行，toctree 含 `rea/index`。证据：读 products/index.md。

## Task 6: V 阶段独立验证与修复
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - Grep 级 API 真实性验证：文档引用的每个关键类/方法/命令/工具在 `external/dao/rea` 源码中验证存在。
  - 链接检查（check-links.py）+ toctree 完整性（子项目 gates.toctrees）+ frontmatter 完整性 + 计数断言复核。
  - 修复发现的问题，勘误在 facts/束内留痕。
  - 委托一次独立只读 Review（全新上下文）复核。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 对 ≥10 个关键 API/命令进行 Grep 验证，回归源码全部命中，零虚构。证据：Grep 输出。
  - `rule` TR-6.2: check-links.py 对 bundle 路径零错误；子项目 toctrees 门通过或本束零命中。证据：脚本输出。
  - `rule` TR-6.3: 计数断言与 facts 一致（V 手段独立于 R）。证据：复核记录。

## Task 7: C 阶段提交与模式沉淀
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 在 `projects/awesome-okf-xs` 子模块内原子提交新束 + 索引变更（`git add` 与 `git commit` 分两次；commit 前 `git show :<file>` 核暂存 blob；消息用 `git commit -F`）。
  - 检查是否存在可沉淀的模式（本次知识沉淀流程的反模式/迁移验证）；如适用，登记到模式库（不新建不需要的模式文档）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 子模块 `git log -1` 显示本次提交，含 rea 束与 products/index.md 变更。证据：git log。
  - `rubric` TR-7.2: 模式沉淀必要性；scale 1-5；anchors 1=无新模式、3=可复用流程、5=含反模式与迁移验证的新模式；threshold ≥ 4（若判定无新模式则记为 N/A 并说明）。证据：模式文档或说明。
- **TR-7.2 判定**: **N/A（无新独立模式）**。本次为 `source-code-to-okf-wiki-workflow` 方法论的既有模式的忠实执行（R→I→E→V→C 于固定 commit 的本地源码镜像 + 网络信源）；已存在 `ai-collaboration/source-code-to-okf-wiki-workflow.md` 与 `ai-collaboration/source-stability-gate.md` 覆盖信源固定与五阶段链路。本任务的「本地 external/ 固定 commit（非 git submodule）作为信源」与「Q-A/Q-B 多信源权威裁决」均属既有 source-manifest / P0 核验实践范畴，不构成可独立沉淀的新模式。为避免冗余模式文档，按 N/A 记录。

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 5
- Task 7 depends on Task 6