---
okf_version: "0.2"
type: spec
title: "Cua Computer-Use 开源全栈博文→OKF 知识包转化规划"
description: "将微信公众号博文《开源精选 | Cua：给 AI Agent 一台能用的电脑，Computer-Use 2.0 开源全栈》转化为 OKF 知识包，覆盖 Cua 项目身份、五大核心模块、Computer-Use 2.0 理念、Stars 趋势、许可证透明度、快速上手路径与适用场景/局限"
tags: [okf-bundle, blog-article, cua, computer-use, ai-agent, trycua, desktop-automation, open-source]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-10-10T10:30:00+08:00" }
---

# Cua 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg |
| 公众号 / 作者 | FinOps实战 | 原创，2026-09-26 15:53 发布 |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式，无 share?code=/token=/邀请码参数 |
| 敏感度级别 | **公开内容** | 开源项目推介文，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方综述（开源项目推介号）**，含官方 README 转述 | 非官方号、非一手实测；作者明确标注"以下内容全部来自官方 README，可以直接照抄执行"，未提供本人实测结果；关键命令经官方材料逐字核验 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 含 Cua Driver 安装（macOS/Linux/Windows）、Lume 安装、Cua Bench 安装（uv tool + playwright）、计算器 6×7 任务、Fleets 云端流程，步骤顺序完整 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | 作者明确声明所有命令"全部来自官方 README"，未提供本人实测结果、未给出预期输出截图或实测验证；流程为官方 README 转述而非一手验证 |

**判定：Q1 是、Q2 否 → 任一为"否"→ 技术综述/产品资讯类骨架，不设 examples/**

**骨架**：
```
jishu/ai/frameworks/ai-agent/cua/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-project-overview.md               # 项目身份、Computer-Use 2.0 理念、三大难题
│   ├── 01-five-core-modules.md              # 五大核心模块详解（Driver/Fleets/Lume/CUA-S1/Bench）
│   ├── 02-ecosystem-and-licensing.md        # 许可证透明度、语言构成、工程化成熟度
│   ├── 03-stars-and-momentum.md             # Stars 趋势、社区活跃度、发布节奏
│   ├── 04-getting-started.md                # 快速上手路径（安装命令、三步骤、Fleets、建议顺序）
│   └── 05-scenarios-and-limitations.md      # 适用场景、局限与风险、展望
└── references/
    ├── index.md
    ├── article-source.md                    # 博文事实清单（F 编号双份登记之一）
    └── verification.md                      # P0 核验报告（含时点勘误清单）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/frameworks/ai-agent/cua/`（选定） | ✅ | ① 主线实体 Cua 是 AI Agent 的 Computer-Use 基础设施项目，归 ai-agent 框架分组；② 组内"📰 产品资讯"分类先例充分（a2a-mcp-convergence、agora-gemini-transcribe、ai-app-survival、agent-knowledge-base 等博文转化束均入本组）；③ 单篇博文归入既有分组，不新建分组 |
| `jishu/ai/ecosystems/cua/` | ❌ | 无既有 ecosystems/cua 分组先例；单篇博文禁止新建分组（归属判定决策树） |
| 新建顶级分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-09-26 |
| 官方核验时间 | 2026-10-10（GitHub API + newreleases.io + piwheels + 官方文档页） |
| `stale_after` | **2026-12-31**（项目每日 nightly、组件版本高频迭代，年末复核） |
| 高时效字段 | Star/Forks/Issues 数（动态）、组件版本号、CUA-S1 发布状态、Fleets 定价政策、Driver 平台支持边界 |
| 已知边界声明 | ① Stars/Forks/Issues/主语言为 2026-09-20 博文快照，bundle 采用官方 2026-10-10 时点数据标注差异；② 安装命令转述自官方 README，作者未实测；③ CUA-S1 为 source-only 早期研究性发布；④ Fleets 为付费服务，池保留容量需清理 |

## 5. P0 必核验清单与结论摘要

| 核验对象（F 编号） | 类型 | 权威信源 | 结论 |
|--------------------|------|----------|------|
| 仓库存在/创建时间（F-019/F-054） | 日期身份 | GitHub API `repos/trycua/cua` | ✅ 创建时间 **2025-01-31T15:02:49Z**，与博文"2025年1月31日"一致 |
| MIT 协议（F-004/F-056） | 许可证 | GitHub API license 字段 | ✅ license = MIT License（spdx MIT） |
| README 副标题引语（F-008） | 官方引文 | GitHub API description | ✅ **逐字一致**："Scale computer-use 2.0 with open-source drivers, cross-OS fleets, and benchmarks for training, evaluation, and data generation." |
| 开发者主体 Cua AI, Inc.（F-004） | 身份 | GitHub API owner + 官网 | ⚠️ GitHub owner 为 Organization `trycua`；博文"由 Cua AI, Inc. 开发"为官网主体口径，GitHub API 无法直接证实法律实体名称 |
| sandbox v0.8.0 发布日期（F-024/F-058） | 日期 | newreleases.io + piwheels | ✅ 2026-09-15（GitHub release `sandbox-v0.8.0`；cua-sandbox 0.8.0 于 2026-09-15 16:49:04 UTC 发布）双重确认 |
| Stars 24,432（F-016） | 动态数字 | GitHub API stargazers_count | ⚠️ 博文 2026-09-20 快照；2026-10-10 实测 **29,189**（时点差异，非硬错） |
| Forks 1,681（F-017） | 动态数字 | GitHub API forks_count | ⚠️ 博文快照；2026-10-10 实测 **2,061** |
| 开放 Issues 1,032（F-020） | 动态数字 | GitHub API open_issues_count | ⚠️ 博文快照；2026-10-10 实测 **1,149** |
| 主语言 HTML（F-026） | 语言构成 | GitHub API language | ⚠️ 博文 2026-09-20 快照称 HTML；2026-10-10 API 显示 **Rust**（时点差异，文档站/演示页字节占比变动所致） |
| 每日 nightly 发布（F-023/F-060） | 发布节奏 | newreleases.io releases 列表 | ✅ nightly-cua-driver-rs 连续 20260917/20260918/20260919 发布，与"9月14日到19日一天不落"一致 |
| 安装命令（F-027/F-028/F-030/F-033/F-034） | 命令 | 官方文档（libraries.io PyPI 页） | ✅ Driver/Lume 安装脚本 URL 与命令逐字一致；cua-bench uv 安装与多方报道一致 |
| 6×7 计算器教程（F-029） | 官方教程 | 官方 README/教程页 | ✅ "connect your agent, ask it to compute 6 × 7 in Calculator, and have it verify that the app displays 42" 逐字一致 |
| CUA-S1 开源/source-only（F-013/F-049/F-063） | 产品动态 | 第三方报道 + 官方材料 | ✅ CUA-S1 于 2026-09-19 前后被报道开源；权重托管 Hugging Face；source-only 口径一致 |
| 第三方组件许可证（F-015/F-064） | 许可证 | 官方 README + 多方报道 | ✅ AGPL-3.0（cua-agent[omni] 含 ultralytics）经多方报道确认；Kasm MIT、OmniParser CC-BY-4.0 为官方 README 声明 |
| 日增 +859 / Trending 第 2（F-018） | 曝光数据 | 多方报道 | ⚠️ 时点数据无法事后精确复核；多方 2026-09-19~21 报道确认 Cua 在 GitHub Trending 前列（+1018/日、25.2k），博文快照合理 |
| run.cua.ai / cua.ai/docs（F-036/F-040） | 官方产品 | 官方材料 | ✅ cua.ai 官网存在，homepage=cua.ai；Fleets 云服务与文档站确认 |

**汇总**：P0/P1 核验 18 项 —— ✅ 12、⚠️ 6、❌ 0。无核心声明失败 → `status: stable`，6 项 ⚠️ 均为时点/口径差异，在 verification.md 完整勘误并在正文标注时点。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 事件/发布事实层（项目是什么、谁做的、什么许可、何时创建） | concepts/00-project-overview.md | F-001~F-009、F-054~F-057 |
| 机制/架构层（五大核心模块） | concepts/01-five-core-modules.md | F-010~F-014、F-061~F-063 |
| 生态/格局层（许可证、语言、工程化成熟度） | concepts/02-ecosystem-and-licensing.md | F-015、F-025~F-026、F-064~F-065 |
| 生态/格局层（Stars 趋势、社区活跃度、发布节奏） | concepts/03-stars-and-momentum.md | F-016~F-024、F-058~F-060 |
| 可照做层（安装命令、三步骤、Fleets、建议顺序） | concepts/04-getting-started.md | F-027~F-040、F-062 |
| 判断/评价层（适用场景、局限、展望） | concepts/05-scenarios-and-limitations.md | F-041~F-053 |

## 7. ADDED Requirements（验收标准）

- bundle 11 个文件齐备（index + log + concepts 7 文件 + references 3 文件），每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（数字/命令/版本/日期/许可证）携带 F 编号，无 facts.md 之外编造
- 6 项 ⚠️ 在正文呈现官方正确值并标注博文时点口径；CUA-S1 标注 source-only 性质
- frontmatter 双信源（博文 URL + GitHub 仓库/官方材料），stale_after=2026-12-31
- 双份 F 编号一致（facts.md ↔ article-source.md 均为 F-001~F-065，连续无跳号）
- ai-agent 组 index 导航表 + toctree 接入（54→55 束）；bundles/index.md 计数同步（ai 域 218→219、total 597→598、组 61 不变）
- V 阶段执行四视角审查与 8 项机械门禁；invoke gates 不可用时执行手动等效清单并在 log.md 注明