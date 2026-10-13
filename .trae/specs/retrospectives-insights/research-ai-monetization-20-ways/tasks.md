# AI 变现方式全景调研（20 种方案） - Implementation Plan

> 方法论链路：R→I→E→V→C（七概念 knowledge 场景，standard 深度）。上下文传递硬约束：Task 2 必须引用 Task 1 事实编号（Fxx），Task 3 必须引用 Task 2 洞察，Task 4 必须收到完整待审产出。

## Task 1: R·多源事实采集 — 20 种方案事实清单
- **Status**: `completed`
- **Completion Evidence**: [facts.md](facts.md) 含 20 方案 × 每方案 ≥3 条事实（约 95 条），编号前缀 F-CM/F-SW/F-AG/F-BE/F-PM/F-OS/F-SC/F-EC/F-XP/F-GA/F-VP，全部含信源 URL，单信源标注"待验证"；G1 门程序化检索（因为/所以/导致/错误/失误）零命中 → **TR-1.1/1.2 通过**
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按调研覆盖面分组执行网络检索（内容媒体/软件产品/服务咨询/电商交易/数据资产/新兴方向六大类），采集 ≥20 种 AI 变现方案的客观事实
  - 每种方案 ≥3 条事实：变现模式、真实案例（含信源 URL）、启动门槛证据、收入量级参考、平台政策约束
  - 每条事实 ≥2 个独立信源交叉验证；无法双源验证的标注"待验证"
  - 产出 `facts.md`（spec 目录内工作文件）：编号 F01-Fxx，无因果判断词
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 事实清单覆盖 ≥20 种方案，每种 ≥3 条事实，含信源标注；证据 = facts.md 逐条核对
  - `rule` TR-1.2: 全文无"因为/所以/导致/错误/失误"因果判断词（G1）；证据 = 程序化关键词检索结果
- **Notes**: 多类目检索可并行委托子代理；国内/海外平台信息兼顾

## Task 2: I·洞察分析 — 核心洞察四元组
- **Status**: `completed`
- **Completion Evidence**: [insights.md](insights.md) 含 4 条洞察（超出 ≥3 要求），每条含陈述/证据(Fxx)/反常识点/下次行动四元组；证据引用经 V-2/V-8 修正弱化过度概括表述；文末 G2 门自检通过 → **TR-2.1 通过**
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 facts.md 事实编号产出 ≥3 条核心洞察，每条含：陈述 / 证据(Fxx) / 反常识点 / 下次行动
  - 洞察方向（以事实为准，不预设）：AI 变现的真实门槛分布、平台依赖风险、收入量级与宣传话术的差距、竞争同质化规律
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-2.1: ≥3 条洞察，每条四元组完整且证据引用真实事实编号（G2）；证据 = 洞察逐条核对
- **Notes**: 必须引用 Fxx 编号，禁止脱离事实清单凭空洞察

## Task 3: E·模式萃取 — 可复用决策框架
- **Status**: `completed`
- **Completion Evidence**: [pattern-draft.md](pattern-draft.md) 含 2 个模式：①三维门槛匹配决策框架（资金×技能×时间，6 步骤+5 反模式，迁移验证 2 个非当前领域场景通过）；②平台依赖风险对冲（5 步骤，APP 商店场景迁移验证通过）；文末 G3 门自检通过 → **TR-3.1 通过**
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 基于洞察萃取 1-2 个结构化可复用模式（预期方向："AI 变现方案选型决策框架"——按资金/技能/时间三维门槛匹配方案；或"平台依赖风险对冲"模式）
  - 模式含四要素：触发场景 / 步骤 / 反模式 / 迁移验证（可迁移到 ≥1 个非 AI 变现领域）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 模式含触发场景/步骤/反模式/迁移验证四要素，且迁移验证通过 ≥1 个非当前领域场景（G3）；证据 = 模式文档迁移验证章节
- **Notes**: 模式为独立产出物，后续入库 `docs/retrospective/patterns/methodology-patterns/`

## Task 4: V·对抗审查 — 报告与模式多视角攻击
- **Status**: `completed`
- **Completion Evidence**: [V-review-record.md](V-review-record.md) 含 8 条具体审查意见（V-1~V-8，覆盖证据充分性/幸存者偏差/时效性/合规/可操作性五视角），全部采纳并留修正记录（facts.md 补 GEO 方案 F-SC-16~20 并重组方案清单、insights.md 3 处表述弱化、报告需落实 V-3/V-4/V-5/V-6 修正项）；V 门判定 3 项全部通过 → **TR-4.1 通过**
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 汇总 Task 1 事实清单 + Task 2 洞察 + Task 3 模式形成完整待审包，执行对抗审查
  - 审查视角 ≥3 类（如：证据充分性攻击/幸存者偏差攻击/时效性攻击/合规风险攻击/可操作性攻击）
  - 产出 ≥5 条具体审查意见，逐条判定采纳/驳回并留修正记录
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 审查意见 ≥5 条且具体，至少 2 条被采纳并留修正记录（V门）；证据 = 对抗审查记录章节
- **Notes**: 拒绝"写得很好"类客套意见；意见须指向具体段落/事实编号

## Task 5: 报告撰写 — 《AI 赚钱 20 种方案全景调研报告》
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 将审查修正后的事实/洞察/模式整合为最终报告，恰好 20 种方案，每方案含统一 8 字段模板（定义/变现模式/真实案例与信源/启动门槛/收入量级参考/风险与合规/适合人群/AI 杠杆点）
  - 报告结构：执行摘要 → 方案对比总表（按门槛层级分组）→ 20 方案详述（六大类分章）→ 核心洞察 → 可复用模式 → 风险总览与行动建议 → 信源附录
  - 修正 Task 4 采纳的审查意见
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 恰好 20 种方案，每方案 8 字段完整无缺；证据 = 逐条目字段核对
  - `rubric` TR-5.2: 报告实用性（证据强度/可操作性/覆盖均衡度）1-5 分，阈值 ≥4；锚点见 spec AC-6；证据 = 独立审查评分
- **Notes**: 报告超 1500 行时按 spec Open Question 拆分为原子化目录

## Task 6: C·落盘提交 — 报告入库与索引刷新
- **Status**: `in_progress`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 执行落盘前三查，确定报告在根 `docs/` 的规范位置（参照同类调研报告先例，预期 `docs/retrospective/reports/competitive-analysis/` 或 `docs/knowledge/learning/`）
  - frontmatter 携带 `source` 溯源字段；模式文档入库模式库并更新索引
  - 运行 link-check 验证无断链；运行 docgen 刷新看板；按 Conventional Commits 执行原子提交
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 报告位于根 `docs/`（非 `.agents/docs/`），frontmatter 含 `source`，link-check 无断链；证据 = 文件路径 + 检查命令输出
  - `rule` TR-6.2: 原子提交完成，提交信息符合 Conventional Commits；证据 = git log

# Task Dependencies

- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 严格串行（七概念上下文传递硬约束：每步依赖上一步完整产出）
- Task 1 内部的六大类目检索可并行委托子代理
- Review 阶段（队列清空后）：由独立上下文子代理对照 spec.md 全量 AC 复核，创建 review.md
