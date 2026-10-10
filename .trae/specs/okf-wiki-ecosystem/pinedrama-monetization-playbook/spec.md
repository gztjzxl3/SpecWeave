---
status: draft
title: PineDrama 自动变现工作指南 · OKF Wiki 扩展
---

# PineDrama 自动变现工作指南 · OKF Wiki 扩展 Spec

## Overview

- **Summary**: 在既有 PineDrama OKF 知识束（`docs/knowledge/tech/pinedrama/`）上扩展一篇「变现工作指南」（`concepts/09-monetization-playbook.md`），系统回答"通过 PineDrama 实现自动变现需要做哪些工作"，包含角色化变现路径矩阵（≥3 类角色）与主路径（内容供给方分账变现）的完整工作清单。
- **Purpose**: 用户已完成 PineDrama 商业模式调研（既有 bundle），但缺少从"知道"到"行动"的转化——需要一份可溯源、防画饼、按角色组织的变现工作指南。
- **Target Users**: 主要用户为希望以内容供给/制作身份接入 PineDrama（及 TikTok 短剧生态）获取分账收益的个人或小团队创作者；次要用户为想了解短剧出海平台变现机制的 OKF 读者。

## Goals

- 新增一篇 OKF v0.2 合规的变现 playbook（`concepts/09-monetization-playbook.md`），角色化路径矩阵 ≥3 类角色；
- 主路径（内容供给方）包含五要素：起点条件、准入门槛、分阶段行动清单（第 1 周/第 1 月/持续期）、预期收益区间（带口径）、退出/切换条件；
- 全部收益/门槛声明可溯源（挂 S 编号或显式标注"无公开数据/待验证"），零承诺性表述；
- 扩展信源登记（S-27 起），更新索引与日志，机械验证通过。

## Non-Goals

- 不产出可运行代码/产品（本项目为知识沉淀任务，无仓库代码变更）；
- 不承诺任何收益；
- 不改动 bundle 既有 8 篇 concepts 正文（只追加新篇与索引更新）；
- 不 push、不主动 git commit（用户未要求时不提交）。

## Background & Context

- 既有 bundle：`docs/knowledge/tech/pinedrama/`（13 篇：references 2 篇、concepts 9 篇、根 index/log 及子目录 index），已注册进 `docs/knowledge/tech/index.md` toctree；
- 既有信源体系：`references/00-sources.md` 登记 S-01~S-26（Sensor Tower、DataEye、TechCrunch、澎湃、界面等），引用纪律为"机构+时间+口径"、单源标注 `[SINGLE-SOURCE]`、冲突口径并列不合并；
- 方法论：seven-concepts-cmd（场景 4 知识沉淀，链路 R→I→E→V→C，强制 V 阶段）。

## Functional Requirements

### FR1 信源补充采集与登记（R）

围绕"内容方如何接入 PineDrama/TikTok 短剧生态并获取分账"采集公开信源，在 `references/00-sources.md` 追加 S-27 起的登记。至少覆盖：官方创作者/合作入口、分账机制（分成比例/结算周期）、内容要求（格式/时长/版权）、区域资质与税务合规、结算流程。P0 优先官方源；无法取得官方源的显式标注"经媒体转引/单源"，禁止伪造官方 URL。

### FR2 事实采集与核验（R）

在既有引用体系上扩展事实登记（F 编号或 S 编号引用），关键声明执行 P0 核验；数量陈述保留"机构+时间+口径"三要素；冲突口径并列不合并；单源标注 `[SINGLE-SOURCE]`；G1 自检（无推断词污染）。

### FR3 变现路径设计（I / F）

第一性原理推导：从"可提供的资产（内容/流量/服务）× PineDrama 生态结构（平台/内容方/广告主）× 时间与资金约束"反推路径，而非堆砌入口。产出：

- 角色化路径矩阵（≥3 类角色：内容供给方（主路径）/ 广告投放方 / 生态服务方），每角色一条子路径；
- 主路径详解：内容供给方分账变现（起点条件 → 准入门槛 → 第 1 周/第 1 月/持续期行动清单 → 预期收益区间 → 退出/切换条件）；
- 行动项原子化（单一职责、可独立验证、有验收标准）。

### FR4 Playbook 文档生成（E）

在 `docs/knowledge/tech/pinedrama/concepts/` 新增 `09-monetization-playbook.md`：frontmatter 遵循 OKF v0.2 九字段（type/title/description/tags/generated/verified/status/stale_after/sources）；正文中文；mermaid 块遵守 `check_mermaid.py` 安全规范（禁 `<br/>` 等禁用模式）；全部收益/门槛声明挂 S 编号或标注"待验证"。

### FR5 索引与日志更新（E）

更新 `concepts/index.md`（toctree +1 条、导航表 +1 行）与根 `index.md`（toctree +1、导航表 +1）；`log.md` 追加本任务 R/I/E/V/C 各阶段记录。

### FR6 对抗审查（V）

四视角（事实溯源/结构规范/读者可用性/时效边界）+ 魔鬼代言人证伪"画饼路径"；可行动发现回 FR3/FR4 修复后复审；审查记录（发现→处理→残留风险）留痕 `log.md`。

### FR7 机械验证（V）

全量检查：相对链接可达、零 `file:///`、frontmatter 九字段齐备、toctree 目标存在、mermaid 禁用项清零、S 编号连续、收益声明抽查。

## Non-Functional Requirements

| 编号 | 需求 |
|---|---|
| NFR1 | **可溯源**：一切具体声明（数字/规则/门槛）挂 S 编号或显式"待验证"，禁止编造 |
| NFR2 | **时效管理**：`stale_after` 与既有束一致或按新数据调整；收益/规则声明标注时点 |
| NFR3 | **治理合规**：遵守 Spec Mode 产物规范（spec.md + tasks.md + review.md，禁 checklist.md）；OKF frontmatter 九字段齐备；中文正文、kebab-case 文件名 |
| NFR4 | **引用纪律**：冲突口径并列；单源标注；规模数字带地理范围与年份 |
| NFR5 | **门禁纪律**：依赖不可用时执行手动等效验证清单并在 log.md 注明，禁止谎报 |

## Constraints

- 只追加不改写：既有 8 篇 concepts 正文零改动；
- 新信源必须登记到 `references/00-sources.md`（S-27 起连续编号）；
- 收益承诺红线：无 S 编号/官方口径支撑的数字不得作为承诺性收益呈现。

## Dependencies

- 既有 bundle `docs/knowledge/tech/pinedrama/`（已存在）；
- seven-concepts-cmd 技能（实现阶段加载）；
- `check_mermaid.py`、`.agents/scripts/check-links.py` 等验证脚本可用。

## Assumptions

- "通过 PineDrama 实现自动变现"的主路径解释为**内容供给方分账变现**（制作短剧供给 PineDrama/TikTok 短剧生态，按播放/分账获取收益）；广告投放方、生态服务方为次要路径；
- 用户具备内容生产能力但无既定渠道与现成商务关系；
- 不要求 push、不要求 git commit。

## Open Questions

- [ ] 新篇是否需要独立 `examples/` 子目录 → 按"操作可复现性两问"判定（预期不需要，行动清单并入 playbook 单篇）；
- [ ] 是否需要在 `docs/` 下另出独立个人路径报告 → 默认合并进 playbook，避免范围膨胀。

## Impact

| 对象 | 影响 |
|---|---|
| `docs/knowledge/tech/pinedrama/concepts/09-monetization-playbook.md` | 新增 |
| `docs/knowledge/tech/pinedrama/concepts/index.md` | toctree +1、导航表 +1 |
| `docs/knowledge/tech/pinedrama/index.md` | toctree +1、导航表 +1 |
| `docs/knowledge/tech/pinedrama/references/00-sources.md` | 追加 S-27 起登记 |
| `docs/knowledge/tech/pinedrama/log.md` | 追加记录 |
| 既有 8 篇 concepts | 零改动 |

## Acceptance Criteria

### AC-1: Playbook 存在且结构合规
- **Type**: `rule`
- **Given**: 实施完成
- **When**: 检查 `concepts/09-monetization-playbook.md`
- **Then**: 文件存在，frontmatter 九字段齐备，正文中文，文件名 kebab-case
- **Pass Condition**: 文件存在且字段齐全
- **Evidence**: Read 文件 + 字段检查

### AC-2: 角色化路径矩阵与主路径五要素
- **Type**: `rule`
- **Given**: playbook 内容
- **When**: 检查矩阵与主路径章节
- **Then**: ≥3 类角色；每条路径含起点/门槛/分阶段行动/收益区间/退出条件五要素；主路径为内容供给方
- **Pass Condition**: 矩阵 + 主路径五要素齐备
- **Evidence**: Read + 抽查

### AC-3: 收益声明零承诺
- **Type**: `rule`
- **Given**: playbook 全部收益/门槛声明
- **When**: 逐条核对出处
- **Then**: 每条声明挂 S 编号或标注"无公开数据/待验证"；无承诺性表述
- **Pass Condition**: 抽查 100% 有出处或显式标注
- **Evidence**: 人工/正则抽查

### AC-4: 信源登记追加且连续
- **Type**: `rule`
- **Given**: `references/00-sources.md`
- **When**: 检查 S 编号
- **Then**: S-27 起连续登记；playbook sources 字段与正文引用一致；零伪造 URL
- **Pass Condition**: 编号连续、正文引用均在登记表
- **Evidence**: 读取核对

### AC-5: 既有内容零改动
- **Type**: `rule`
- **Given**: 既有 8 篇 concepts
- **When**: git diff 检查
- **Then**: 无对既有篇目的内容改写（仅新增/追加）
- **Pass Condition**: diff 仅新增
- **Evidence**: git diff

### AC-6: 索引同步
- **Type**: `rule`
- **Given**: `concepts/index.md` 与根 `index.md`
- **When**: 检查 toctree 与导航表
- **Then**: 新篇条目存在且目标可访问
- **Pass Condition**: toctree 目标 Test-Path 存在
- **Evidence**: 脚本/手动检查

### AC-7: 机械验证通过
- **Type**: `rule`
- **Given**: 全量产物
- **When**: 运行检查
- **Then**: 相对链接可达、零 `file:///`、mermaid 禁用项清零、frontmatter 九字段齐备
- **Pass Condition**: 全部通过
- **Evidence**: check-links.py / 手动清单

### AC-8: 路径可达性（防画饼）
- **Type**: `rubric`
- **Dimension**: 主路径在"新人视角 + 每日 ≤2 小时资源约束"下的可行性
- **Scale**: 0-2
- **Anchors**: 0 = 存在未证伪的"画饼"路径；1 = 部分路径通过证伪但有未修复发现；2 = 全部路径通过证伪
- **Pass Threshold**: >= 1.5
- **Evidence**: log.md 对抗审查记录

### AC-9: 七概念质量门
- **Type**: `rubric`
- **Dimension**: G1 事实无推断词 / G2 洞察四元组（现象+根因+影响+建议）/ G3 模式含触发场景+核心步骤+反模式+迁移验证 / G4 行动项原子化
- **Scale**: 0-2
- **Anchors**: 0 = 严重混层或缺阶段；1 = 基本达标但有缺层；2 = 完全达标
- **Pass Threshold**: >= 1.5
- **Evidence**: log.md 阶段记录 + 抽查

### AC-10: 交付汇总
- **Type**: `rule`
- **Given**: 任务完成后
- **When**: 向用户交付
- **Then**: 汇总产物清单与验证结果；不主动 git commit/push（除非用户明确要求）
- **Pass Condition**: 交付汇报完成；无未授权的 git 操作
- **Evidence**: 最终回复

## 关联资产

- 方法论：seven-concepts-cmd（本任务元编排）→ 既有 bundle `docs/knowledge/tech/pinedrama/` 的 log.md 记录为先例
- 先例 Spec：`.trae/specs/create-zhihu-monetization-okf-wiki/`（变现路径类 OKF Wiki 的体例参考）
- OKF 规范：`docs/knowledge/tech/pinedrama/` 既有 frontmatter 与 toctree 体例