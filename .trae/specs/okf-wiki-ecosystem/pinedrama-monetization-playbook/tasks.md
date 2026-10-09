# Tasks — PineDrama 自动变现工作指南（OKF Wiki 扩展）

> 派生自 spec.md 验收标准 AC-1 ~ AC-10。状态取值：pending / in_progress / blocked / completed / cancelled。
> 任务标题不含状态标记；本地验证失败保持 `in_progress`，不设 `failed`。

## Task 1: 信源补充采集与登记（R）

- **Status**: `in_progress`
- **Priority**: high
- **Depends On**: None
- **Description**: 围绕"内容方如何接入 PineDrama/TikTok 短剧生态并获取分账"采集公开信源（官方创作者/合作入口、分账机制、内容要求、区域资质与税务合规、结算流程），在 `references/00-sources.md` 追加 S-27 起的登记（每源含级别/日期/获取方式）。P0 优先官方源；无法取得官方源的显式标注转引链，禁止伪造 URL。复用既有 S-01~S-26 体系。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-1.1: 00-sources.md 存在 S-27 起连续登记，新增 ≥3 个信源；证据：读取文件核对编号
  - `rule` TR-1.2: 官方源优先；无官方源处显式标注转引链；零伪造 URL；证据：抽查登记表与检索记录

## Task 2: 事实采集与核验（R）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 从新信源提取关键声明（分账比例、结算周期、内容要求、准入门槛、区域资质等），以 F 编号或 S 编号引用登记；P0 声明执行核验（官方源优先），无法核验项显式标注"单源/待验证"；数量陈述保留"机构+时间+口径"；G1 自检（无推断词污染）。
- **Acceptance Criteria Addressed**: AC-3, AC-9
- **Test Requirements**:
  - `rule` TR-2.1: 每条关键声明有编号/出处；P0 声明有核验记录或"单源"标注；证据：事实登记表
  - `rule` TR-2.2: G1 自检通过（登记与正文无推断词污染）；证据：grep 检查记录

## Task 3: 变现路径设计（I/F）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 第一性原理推导（可提供资产 × PineDrama 生态结构 × 时间/资金约束）；产出角色化路径矩阵（≥3 类：内容供给方主路径 / 广告投放方 / 生态服务方）；主路径五要素（起点条件、准入门槛、第 1 周/第 1 月/持续期行动清单、预期收益区间、退出/切换条件）；行动项原子化（单一职责、可独立验证、有验收标准）。设计稿可先落 spec 区再合入 playbook。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8, AC-9
- **Test Requirements**:
  - `rubric` TR-3.1: 每条路径五要素齐备，主路径通过"每日 ≤2 小时新人"可行性检验；scale 0-2；anchors 0/1/2；阈值 >= 1.5；证据：设计稿与检查记录
  - `rule` TR-3.2: 收益/门槛声明 100% 挂 S 编号或"待验证"；零承诺性表述；证据：正则/人工抽查

## Task 4: Playbook 文档生成（E）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 生成 `docs/knowledge/tech/pinedrama/concepts/09-monetization-playbook.md`：frontmatter 九字段（type/title/description/tags/generated/verified/status/stale_after/sources）；正文中文；mermaid 块遵守 check_mermaid.py 安全规范；全部声明挂 S 编号或"待验证"；不修改既有 8 篇 concepts。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7, AC-9
- **Test Requirements**:
  - `rule` TR-4.1: 文件存在、frontmatter 九字段齐备、文件名 kebab-case；证据：Read + 字段检查
  - `rule` TR-4.2: mermaid 禁用项清零；零 `file:///`；证据：check_mermaid.py 正则 + 链接检查

## Task 5: 索引与日志更新（E）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 更新 `concepts/index.md`（toctree +1 条、导航表 +1 行）与根 `index.md`（toctree +1、导航表 +1）；`log.md` 追加本任务 R/I/E 阶段记录。
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 两处索引的 toctree 新条目目标 Test-Path 可达；证据：脚本/手动检查
  - `rule` TR-5.2: log.md 有 R/I/E 阶段记录；证据：读取 log.md

## Task 6: 对抗审查（V）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 四视角（事实溯源/结构规范/读者可用性/时效边界）+ 魔鬼代言人证伪"画饼路径"（冷启动时长、分账实际到手、规则变动风险）；可行动发现回 Task 3/4 修复后复审；审查记录（发现→处理→残留风险）写入 log.md。
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `rubric` TR-6.1: 路径可达性阈值 >= 1.5/2，无未修复"画饼"发现；证据：log.md 审查记录
  - `rule` TR-6.2: 审查记录留痕（发现→处理→残留风险）；证据：读取 log.md

## Task 7: 机械验证（V）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 5, Task 6
- **Description**: 全量验证：相对链接可达、零 `file:///`、frontmatter 九字段、toctree 目标存在、mermaid 禁用项清零、S 编号连续、收益声明抽查（AC-3/AC-4）。失败项修复后复跑。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 全部检查项通过（或手动等效清单全勾且 log 注明）；证据：检查结果记录

## Task 8: 交付汇总（C）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 向用户汇总产物清单（新篇路径、索引改动、信源追加）与验证结果；不主动 git commit/push，除非用户明确要求。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-8.1: 交付汇报完成；无未授权 git 操作；证据：最终回复 + git status 核对

---

## Task Dependencies

```text
Task 1 → Task 2 → Task 3 → Task 4 → Task 7 → Task 8
                            └─→ Task 5 ──┘
                            └─→ Task 6 ──┘
```

- Task 5 与 Task 6 依赖 Task 4，二者互不写同一文件，可并行；
- Task 7 依赖 Task 5 与 Task 6 完成；
- Task 8 依赖全部完成项。

## Parallelizable Work

- Task 5（索引更新）与 Task 6（对抗审查）在 Task 4 完成后可并行派发；
- Task 1 的信源检索可按主题分组并行（独立子代理，每组给完整检索目标）。