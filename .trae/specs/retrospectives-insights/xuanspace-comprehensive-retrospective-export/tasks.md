---
title: "xuanspace 全面复盘 + 报告导出 — 实施计划"
status: "draft"
id: "xuanspace-comprehensive-retrospective-export-tasks"
methodology: "seven-concepts (R→I→E→V→A→C)"
source: "./spec.md"
---

# xuanspace 全面复盘 + 报告导出 — Implementation Plan

> 链路：R（事实）→ I（洞察）→ E（模式萃取）→ V（对抗审查）→ A（行动项）→ C（原子提交）
> 质量门：G1（事实无因果词）→ G2（洞察四元组完整）→ G3（模式可迁移）→ G4（行动项原子化）
> 报告基准：`docs/retrospective/reports/project-reports/retrospective-xuanspace-comprehensive-20260826/`

## Task 1: R 阶段 — 事实采集（全量脉络 + 增量聚焦）
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 采集 xuanspace 全量 360 次提交的规模、节奏、类型/scope 分布等客观事实
  - **重点**采集 2026-08-26 之后 38 次提交的按主题聚类与关键 commit
  - 采集当前仓库状态事实（HEAD、工作区清洁度、子模块初始化状态、版本声明）
  - 输出 F-001 起连续编号的事实清单，纯客观描述，附来源
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7, AC-10
- **Test Requirements**:
  - `rule` TR-1.1: 事实清单 ≥30 条且通过 G1 门（因果推断词 Grep 为空或仅引述）—— 证据：清单文本 + Grep 输出
  - `rule` TR-1.2: 抽查 ≥10 条第 1 项事实，回溯命中率 100% —— 证据：抽查表（F 编号 → commit hash / 文件路径 → 结论）
  - `rule` TR-1.3: 增量事实可追溯到 `git -C projects/xuanspace log --since=2026-08-26 --oneline` 的 38 条记录 —— 证据：git log 输出与事实清单对照
- **Notes**: 本机 git 需全路径 `D:\Program Files\Git\mingw64\bin\git.exe`；`projects/xuanspace` 全程只读
- **Completion Evidence**:
  - 产出物：`facts.md`（F-001 ~ F-129 共 **129 条**事实，其中 F-128/F-129 为工作区状态复核补充事实）
  - TR-1.1 ✅：条数 129 ≥ 30；因果词 Grep（`因为|导致|所以|由于|因此`）命中 1 处，为 F-048 行内**逐字引述 commit subject**（`fix(doctor): 修正 Sphinx 检查硬编码 docs/ 导致恒为跳过`），属引述豁免 → G1 门 PASS
  - TR-1.2 ✅：抽查 12 条（F-001/003/004/006/007/008/010/012/075/078/082/104），命中率 **12/12 = 100%**，取证表见 `facts.md` 附录
  - TR-1.3 ✅：增量口径 `git log --since=2026-08-26 --oneline` 计数 = 38，与 F-010 一致；逐条清单 F-017 ~ F-054（38 条）与聚类核对 F-061（14+7+6+5+3+3=38）自洽
  - 事实边界修正：采集时点 F-070 记 13 行未提交改动；复核时点 F-128 记 20 行（19 ` M` + 1 `??`），全在 `libs/xuan-compose/`，归因并行会话在途工作（F-129）；spec.md 的 Why 与 AC-10 已按实同步修正，避免"工作区干净"的失真表述进入洞察

## Task 2: I 阶段 — 洞察萃取（根因分析）
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单做 5-Whys 根因分析
  - 提炼 ≥3 条洞察，每条含四元组（现象/根因/影响/建议）并引用 F 编号
  - 对增量与既有复盘基线做差异分析（新增 / 强化 / 反转）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 洞察 ≥3 条且四元组完整，每条引用 ≥2 个 F 编号 —— 证据：洞察清单原文
  - `rubric` TR-2.2: 洞察深度（是否触及系统性根因而非现象复述）；scale 1-5；anchors 1/3/5；threshold >= 4；证据：洞察条目与 5-Whys 推导链
- **Notes**: 通过 G2 门后方可进入 Task 3
- **Completion Evidence**:
  - 产出物：`insights.md`（187 行）；未写入 `projects/xuanspace`，未创建其他文件
  - TR-2.1 ✅：洞察 **4 条**（I-1 增量事件脉冲缺常驻使命 / I-2 迁入即治理规律 / I-3 外部行为分级锁定 / I-4 分布式增量 vs 集中式约束）；每条四元组完整（现象/5-Whys 根因/影响/建议），引用 F 编号分别为 11/11/8/12 个，均 ≥2 → G2 门 PASS
  - TR-2.2 ✅：深度自评 I-1=5、I-2=4、I-3=5、I-4=5，全部 ≥4 阈值；5-Whys 均追至系统性根因（standing backlog 缺失 / 私有约定升级为公共约束 / 外部不确定性内部化 / 分布式增量 vs 集中式全局约束）
  - 差异分析 ✅：对照基线三洞察得出「强化 1（节奏形态）、反转 2（质量计数口径、结构重心）、新增 1（依赖治理视角）、无变化 1（开发主体 70.3% vs 69.7%）」，逐条附 F 编号依据
  - 事实张力处理 ✅：单列专节呈现 F-070（13 行）与 F-128（20 行）时点差异，采双时点标注、不作确定性结论，并声明只读归因（F-129）

## Task 3: E 阶段 — 模式萃取 + V 阶段 — 对抗审查
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 从增量变化中萃取 ≥1 个可迁移模式（触发场景/核心步骤/反模式/迁移验证），通过 G3 门
  - 与既有模式库做去重裁决（新建 L1 / 并入既有 / 不入库）
  - 执行四视角对抗审查（魔鬼代言人/新人/老板/未来），产出 ≥5 条意见并采纳 ≥2 条修正
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `rule` TR-3.1: 模式文档四要素齐备且去重裁决结论已记录 —— 证据：模式文档 + 裁决段落
  - `rule` TR-3.2: 对抗审查覆盖四视角，意见 ≥5 条，采纳 ≥2 条并有修正痕迹 —— 证据：意见清单 + 采纳对照表
- **Notes**: 可通过 `pattern-to-methodology-library` 技能执行入库流程
- **Completion Evidence**:
  - 产出物：`e-stage-pattern.md`（190 行）、`v-adversarial-review.md`（122 行）；均只写入 spec 目录，未触达 `docs/`、`.meta/` 与 `projects/xuanspace`
  - TR-3.1 ✅：候选 B「迁移窗口的结构约定对齐法（迁入即治理）」四要素齐备（触发场景/5 步核心步骤/5 条反模式/4 个可判定成功信号）→ **G3 门 PASS**，可迁移至组织整合、数仓多源接入、前端 monorepo 三场景；去重裁决已记录：候选 A「上游怪癖分级固化」→ **并入既有** `behavior-characterization-freeze.md`（经实测该文档 `:72` 标题即"固化强度分级（L0-L3）"、`:80-82` 四级定义、`:85-86` L1→L0 升级记录、`:67`/`:110` 台账登记纪律，机制已被完整覆盖，差异点仅 3 条，不足以独立成篇）；候选 B → **新建 L1**（建议 id `migration-triggered-convention-alignment`，已给出 frontmatter 草案、TOML 落点与 toctree 插入位置）
  - TR-3.2 ✅：对抗审查意见 **7 条**（V-1~V-7），四视角全覆盖（魔鬼代言人 V-1/V-5/V-6、新人 V-2/V-7、老板 V-3、未来 V-4）；**采纳 5 条**（V-1 并入加 3 条硬上限 → §2.1；V-2 步骤去专有值通用化 → §1.2；V-3 新增成本边界成功信号 4 → §1.4；V-5 F-113 降级为自报口径 → §1.4；V-6 新增 §4.1 I-1 竞争假设限定），5 处修正痕迹均可核验；不采纳 2 条（V-4 价值锚在流程非工具、V-7 触发场景已界定）各附理由；含 1 条指向"事实证据强度不足"（V-5）
  - 附带发现 ✅：修正 F-104 的口径不完整——`governance-strategy` 的 TOML 伴生文件不在 `docs/` 子树内，实际位于根 `.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/`，经 frontmatter `x-toml-ref` 引用；该澄清带入 Task 4 报告与 Task 5 入库

## Task 4: 报告三件套撰写与归档
- [x] **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 撰写 `README.md`（主报告：事实 + 洞察 + 问题 + 优化）
  - 撰写 `insight-extraction.md`（洞察与模式萃取）
  - 撰写 `actionable-items.md`（原子行动项，含优先级与验收标准）
  - 归档至 `docs/retrospective/reports/project-reports/retrospective-xuanspace-comprehensive-20261010/`
- **Acceptance Criteria Addressed**: AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: 三件套文件齐备且各 frontmatter 含 `source` 字段 —— 证据：目录列举 + frontmatter 片段
  - `rule` TR-4.2: 全部文件落于根 `docs/`，未向 `.agents/docs/` 写入 —— 证据：写入路径清单
  - `rubric` TR-4.3: 增量聚焦度；scale 1-5；anchors 1/3/5；threshold >= 4；证据：增量章节与 git 增量对照表
  - `rubric` TR-4.4: 行动项原子化与可验证性；scale 1-5；anchors 1/3/5；threshold >= 4；证据：`actionable-items.md` 条目结构
- **Notes**: frontmatter 与章节结构对齐 `retrospective-xuanspace-comprehensive-20260826/README.md`
- **Completion Evidence**:
  - 产出物（4 文件，全部落于根 `docs/`）：
    - `docs/retrospective/reports/project-reports/retrospective-xuanspace-comprehensive-20261010/README.md`（175 行，主报告 S1~S4 + 质量门记录 + 限定说明附录）
    - `.../insight-extraction.md`（306 行，I-1~I-4 四元组 + 差异分析 + 模式萃取 + V 摘要 + F-001~F-129 附录）
    - `.../actionable-items.md`（101 行，ACT-01~ACT-08 + AC-8 自评表）
    - `.../index.md`（9 行，纯 toctree，依 20260826 实例约定，无 frontmatter）
  - TR-4.1 ✅：三件套齐备；`README.md`/`insight-extraction.md`/`actionable-items.md` frontmatter 均含 `type: Report` 与 `source` 字段（README `source: "xuanspace 360 commits full history retrospective..."`；另两份同源），`index.md` 依既有实例无 frontmatter
  - TR-4.2 ✅：4 文件全部写入根 `docs/retrospective/reports/...`；未创建 `.agents/docs/`（已废止路径）；Grep 确认新目录无 `file:///`、无 `.temp/` 引用
  - TR-4.3 ✅（增量聚焦度自评 **5**）：报告以独立章节呈现增量 38 条主题聚类表（S1）、增量脉冲期时间线（S2 mermaid 第五子图）、四条增量主题线索，并逐条对照 git 增量（F-010、F-055~F-064）；全量脉络作背景对照而非主体 → 达"增量聚焦"高锚点
  - TR-4.4 ✅（行动项原子化，**最低 4 分、整体 ≥4**）：8 条行动项均单一职责、含优先级/Owner/触发条件/验收标准；AC-8 自评表详列各条评分（5/5/5/5/4/4/4/5）
  - 已落实 V 阶段限定说明：README 附录三条（I-1 竞争假设、F-113 自报口径、工作区双时点）与 `v-adversarial-review.md` §五遗留项对齐

## Task 5: 模式入库方法论模式库
- [x] **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 在 `docs/retrospective/patterns/methodology-patterns/governance-strategy/` 新增 L1 模式文档
  - 生成 TOML 元数据伴生文件（遵循既有命名与字段约定）
  - 更新 toctree 登记（`governance-strategy/README.md` 与/或 `methodology-patterns/index.md`）
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: 模式文档 + TOML + toctree 登记三项齐备 —— 证据：路径列举 + 登记行原文
- **Notes**: 待决问题——toctree 落点需对照既有模式文件登记惯例确定（见 spec.md Open Questions）
- **Completion Evidence**:
  - 产出物 1（模式文档）：`docs/retrospective/patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.md`（142 行）；frontmatter 采 `e-stage-pattern.md` §2.3 草案（`type: Pattern` / `id: "migration-triggered-convention-alignment"` / `maturity: "L1"` / `x-toml-ref` 五级相对路径 / `related_patterns` 5 项 / `tags` 4 项）；正文按样板骨架展开（模式类型/成熟度/一句话/适用场景/问题背景/核心做法 5 步/反模式 5 条/检验标准 4 信号/迁移示例/案例证据/失效条件与演进/参考实现与关联）
  - 产出物 2（TOML 伴生）：`.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.toml`（13 行）；字段集对齐样板，`references` 与 frontmatter `related_patterns` 一致、`skills = []`
  - 产出物 3（toctree 登记）：`governance-strategy/index.md` **第 88 行**插入 `migration-triggered-convention-alignment`，位于 `methodology-reflexivity-test`（87 行）与 `milestone-breakthrough-assetization-process`（89 行）之间，字母序正确
  - 产出物 3b（**模式库主索引登记，初次遗漏已补**）：`methodology-patterns/index.md`「模式清单」总表第 45 行新增新模式一行（ID/名称/L1/验证 1/复用 0/触发场景），落实该文件「模式入库流程」第 5 步「更新本索引」要求；该表是模式库主索引，仅改域 toctree 不构成完整入库
  - 产出物 4（候选 A 并入）：`behavior-characterization-freeze.md` 追加 3 处差异点且保留全部既有内容——①`72-74` 行「台账载体与同步门禁」（载体落为 `libs/xuan-compose/docs/parity/upstream-quirks.md` + 上游同步强制复核 diff）；②`116-117` 行检验标准新增「上游同步类 spec 须输出 `upstream-quirks.md` 台账 diff 复核结论」；③`132-133` 行失效条件与演进新增「分级口径上升为仓库级规范」
  - V 阶段采纳项落实：V-4「工具原生支持可降级」登记入新模式「失效条件与演进」（`123-125` 行）；V-5 口径限定以旁注形式写入新模式「检验标准」后（`96-99` 行，F-113 自报值仅作量级参考）
  - README 刷新：运行 `.agents/scripts/generate-readme.py --update`，`governance-strategy/README.md` 生成区块更新为 165 个文档，新条目第 107 行（未手改生成区块）
  - TR-5.1 ✅：三项齐备（模式文档 + TOML + toctree 登记），路径与登记行原文如上
  - 校验 ✅：Grep 确认新模式文档与两个改动文件**无 `file:///`、无 `.temp/`**；`check-links.py --path docs/.../governance-strategy` 通过（178 文件、782 条本地引用全部有效）；全程未触碰 `projects/xuanspace`，未向 `.agents/docs/` 写入

## Task 6: 索引登记与质量门验证
- [x] **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 在 `docs/retrospective/reports/project-reports/README.md` 登记新报告（含日期、主题、要点）
  - 在 `docs/retrospective/reports/index.md` 登记新报告
  - 运行链接检查，确认无新增断链
  - 确认 `projects/xuanspace` 工作区仍干净
- **Acceptance Criteria Addressed**: AC-6, AC-10
- **Test Requirements**:
  - `rule` TR-6.1: 两处索引均登记且 `check-links.py` 对变更范围 0 新增断链 —— 证据：登记行 + 链接检查输出
  - `rule` TR-6.2: `git -C projects/xuanspace status --porcelain` 输出为空 —— 证据：命令输出
- **Completion Evidence**:
  - 索引登记 1：`project-reports/index.md` toctree 第 21 行新增 `retrospective-xuanspace-comprehensive-20261010/index`（位于 20260826 与 mono-repo-20260724 之间）
  - 索引登记 2：`project-reports/README.md` 报告清单表第 32 行新增新报告一行（日期 2026-10-10 / 主题 / 关键产出）
  - `reports/index.md` 说明：该文件 toctree 已含 `project-reports/index`（其第 34 行），新报告经 project-reports toctree **传递可达**，无需在该纯 toctree 文件内直接登记
  - TR-6.1 ✅：链接检查对两段变更范围均通过——①报告目录 4 文件、12 个本地引用全部有效；②方法论模式库 565 文件、2849 个本地引用全部有效（含 Task 5 新增模式与主索引登记行）→ **0 新增断链**
  - TR-6.2 ✅（第三时点，如实归因）：复核时 `git -C projects/xuanspace status --porcelain` **输出为空（0 行）**；但 HEAD 已由复盘基线 `587da1c` 推进至 `f453bad`——并行会话（`.trae/specs/sync-upstream-delta/`）已把 F-070/F-128 所记在途改动提交为 **3 个新提交**（`3f586de` feat !override 语义链 / `efef29e` fix 运行时与 CLI 增量 / `f453bad` docs 上游基线对等证据），全量提交数 360 → **363**
  - AC-10 ✅ 落盘边界：本复盘任务自始未在 `projects/xuanspace` 写入或回滚任何文件；工作区三时点（T1 采集 13 行 / T2 复核 20 行 / T3 现 0 行且 HEAD +3）差异全部归因于并行会话，未计入本任务；报告与模式结论仍以基线 `587da1c`（360 次提交）为准，并行新增 3 提交不纳入本次复盘范围

# Task Dependencies

- Task 2 依赖 Task 1（事实不清则洞察失真）
- Task 3 依赖 Task 2（洞察未成则模式无根）
- Task 4 依赖 Task 3（模式与审查结论须先进报告）
- Task 5 依赖 Task 3、Task 4（入库内容源自报告萃取章节）
- Task 6 依赖 Task 4、Task 5（索引需覆盖全部产出物）
- Task 1 与其余任务串行；Task 5 内部三子项可并行推进，但 toctree 登记须最后执行

# 质量门检查点

| 门 | 阶段 | 判定 | 未通过时动作 |
|---|---|---|---|
| G1 | Task 1 产出 | 事实无因果推断词、条数 ≥30 | 回到 Task 1 重采集 |
| G2 | Task 2 产出 | 洞察四元组完整、≥3 条 | 回到 Task 2 补全 |
| G3 | Task 3 产出 | 模式四要素齐备、可迁移 | 回到 Task 3 重萃取 |
| G4 | Task 4 产出 | 行动项单一职责、可独立验证 | 回到 Task 4 重写