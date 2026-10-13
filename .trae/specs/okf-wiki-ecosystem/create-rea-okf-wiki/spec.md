---
okf_version: "0.2"
type: spec
title: "REA（Reverse Engineer Anything）OKF Wiki 知识包创建 Spec"
status: draft
source:
  - https://rea.run/zh/
  - https://zhuanlan.zhihu.com/p/2091916182064456398
  - https://github.com/ringozzt/rea-research
  - https://rea.tools/zh-CN/
  - external/dao/rea (local source checkout, main @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a)
---

# REA（Reverse Engineer Anything）OKF Wiki 知识包创建 Spec

## Overview

- **Summary**: 系统化学习 REA（Reverse Engineer Anything，逆向一切）——一个本地优先、通过单一 MCP 服务将 AI 智能体连接到逆向工程工具链（Ghidra / IDA / Hopper / JEB / ADB-Android / EVM / WASM / 原生二进制 / JavaScript-Electron / .NET 程序集 / 网站分析）的逆向分析套件；并结合其五行信源（官网、知乎专栏、研究仓库、官方文档站、本地源码），生成一份 OKF v0.2 规范的 Wiki 知识包（bundle），落盘到 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/rea/`。
- **Purpose**: 让读者能用中文系统地理解 REA 是什么、如何工作、能分析什么，并能自助安装与使用它对常见应用做逆向分析。
- **Target Users**: 逆向工程学习者、AI 智能体开发者、想要"看懂喜欢功能如何工作"的开发者，以及本知识库（awesome-okf-xs）的中文技术读者。

## Goals

- 从五行公开信源 + 本地源码中采集零推测的编号事实（F-xxx），建立 REA 的可验证事实基础。
- 提炼 3-5 个核心架构洞察（证据支撑），形成知识地图与学习路径。
- 产出符合 OKF v0.2 规范的完整 bundle（`index.md` + `log.md` + `concepts/` + `examples/` + `references/`），含 toctree 导航、交叉引用、frontmatter。
- 通过独立验证（Grep API 真实性、链接、toctree、frontmatter、计数断言）后交付。

## Non-Goals

- 不实测 REA 逆向任意目标应用（环境未安装 Ghidra/IDA/Hopper 等原生引擎；安装需用户批准）。
- 不创建多束扩展；本任务单轮建束。
- 不在 `docs/knowledge/` 或根 `docs/` 重复建一套副本（bundle 属于 awesome-okf-xs 子项目文档库）。
- 不修改 `external/dao/rea` 源码本体（只读引用）。

## Background & Context

- REA 的本地源码位于 `external/dao/rea`（npm 包 `rea-agents`，MIT 许可），当前 `main` 分支 @ `eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a`（浮动分支，须以 commit hash 固定追溯）。
- 知识库目标结构遵循 awesome-okf-xs 的 bundle 规范（`doc/bundles/jishu/ai/products/<bundle>/`），参考同域既有束（如 `octop`）的结构。
- 工作流采用 `seven-concepts-cmd`（场景 4 知识沉淀：R→I→E→C）编排，细化为 `source-code-to-okf-wiki` 的 R→I→E→V→C 五阶段链路。
- 派生产物须在 frontmatter 标注 `sources`（信源登记指向 `references/`）。

## Functional Requirements

- **FR-1**: 采集并登记 REA 的事实清单（`F-xxx`），每条事实指向具体信源/源码路径，无推断性表述。
- **FR-2**: 生成 OKF v0.2 规范的 bundle，包含 `concepts/`（概念）、`examples/`（示例）、`references/`（信源）、`index.md`（根索引 + toctree）、`log.md`（变更日志）。
- **FR-3**: 所有 `references/sources` 字段须指向 `references/` 下实际存在的信源登记文件。
- **FR-4**: 包含 REPL 可照做的 `examples/`（安装、`npx rea-agents setup`、CLI/分析调用示例）。
- **FR-5**: 更新选中主题索引（`jishu/ai/products/index.md`）的束导航表与 toctree，登记新束 `rea`。

## Non-Functional Requirements

- **NFR-1**: 全部文档中文撰写；英文技术术语首次出现括号注释。
- **NFR-2**: 交叉链接使用 `/` 开头的 bundle-relative 路径（不用 `../`、不用 `file:///`）。
- **NFR-3**: 每个 index.md（根 + 子目录）必须含 `{toctree}` 指令块，且收录本目录全部内容文档。
- **NFR-4**: 每个内容文档 frontmatter 必填字段齐全（type/title/description/tags/generated/verified/status/stale_after/sources）。
- **NFR-5**: 数量类陈述（"X 个工具/命令/提供方"等）须经独立脚本/搜索计数复核，避免目测失真。

## Constraints

- **Technical**: 信源版本不可追溯漂移——本地源码以 commit hash `eaf88aca...` 固定，官网/文章信源以采集时 URL 与日期登记。
- **Business**: 不安装原生逆向引擎（Ghidra/IDA/Hopper）；安装示例标注"需用户自行准备/批准"。
- **Dependencies**: `invoke gates.toctrees` / `invoke gates.bundles`（子项目质量门）用于到货验证；`python .agents/scripts/check-links.py` 用于链接检查。

## Assumptions

- REA 的公开信源（网站/专栏/文档）在采集时可达。
- `external/dao/rea` 本地源码是可读的当前源码快照（main 分支），以其为事实裁定的最高优先级之一。
- 目标 bundle 在 `jishu/ai/products/` 域新建为单束，不合并既有束。

## Acceptance Criteria

### AC-1: Bundle 结构完整符合 OKF v0.2
- **Type**: `rule`
- **Given**: 知识生成完成后
- **When**: 检查 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/rea/`
- **Then**: 存在 `index.md`、`log.md`、`concepts/`（含 `index.md`）、`examples/`（含 `index.md`）、`references/`（含 `index.md` 与信源登记文件）
- **Pass Condition**: 目录与文件全部存在；根 index.md 的 toctree 收录 concepts/index、examples/index、references/index、log
- **Evidence**: LS 目录；读根 index.md

### AC-2: 事实基础可溯源无虚构
- **Type**: `rule`
- **Given**: `references/facts.md` 及其衍生概念文档
- **When**: 对文档中引用的每个关键类名/方法名/命令/工具进行源码 Grep 验证，并对每条事实核对信源
- **Then**: 引用的 API/命令在 `external/dao/rea` 源码或采信信源中真实存在；无虚构 API
- **Pass Condition**: Grep 命中 100%，零虚构；每条 F-xxx 有信源指向
- **Evidence**: Grep 输出；facts.md 信源字段

### AC-3: 导航与交叉链接完整
- **Type**: `rule`
- **Given**: bundle 全部文档
- **When**: 运行 `python .agents/scripts/check-links.py --path <bundle>` 与子项目 `invoke gates.toctrees`
- **Then**: 无断链、无孤立文档、所有 index.md toctree 完整
- **Pass Condition**: check-links 零错误；gates.toctrees 通过（或本束零命中）
- **Evidence**: 脚本输出

### AC-4: 内容覆盖质量
- **Type**: `rubric`
- **Dimension**: 学习价值的完整性与准确性
- **Scale**: 1-5
- **Anchors**:
  - 1 = 仅翻译合集，无概念分层，含明显事实错误
  - 3 = 覆盖"是什么/怎么工作/能分析什么"主体，含安装与一两个示例，偶有口径待核
  - 5 = 分层清楚（概念/示例/信源）、覆盖架构与工具矩阵、含可照做示例与边界/局限、事实高可信
- **Pass Threshold**: >= 4
- **Evidence**: 审读 concepts/examples/references 各文档的章节与事实密度

### AC-5: 主题索引登记
- **Type**: `rule`
- **Given**: 新束 `rea` 生成后
- **When**: 更新 `jishu/ai/products/index.md`
- **Then**: 束导航表新增 rea 一行，toctree 新增 `rea/index`
- **Pass Condition**: 表格行与 toctree 条目均在；提交后与父级索引一致
- **Evidence**: 读 products/index.md

## Open Questions

- [ ] `rea.run/zh/` 与 `rea.tools/zh-CN/` 是否为同一站点的不同域名/版本？采集后核实并统一登记。
- [ ] `github.com/ringozzt/rea-research` 与 `morluto/rea` 的关系（研究仓库 vs 主仓库）需在信源登记中说明。