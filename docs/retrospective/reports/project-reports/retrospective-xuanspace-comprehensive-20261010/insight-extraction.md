---
type: Report
id: "insight-extraction-xuanspace-comprehensive-20261010"
version: "1.0.0"
source: "xuanspace 360 commits full history retrospective (2026-07-24 ~ 2026-10-10; incremental window 2026-08-26 ~ 2026-10-10, 38 commits)"
---

# 洞察萃取：玄境（Xuanspace）全面复盘

> 本文件承载本轮复盘的核心中间产出：第一节为四条洞察的完整四元组（G2 PASS），第二节为对照既有基线的差异分析，第三节为模式萃取与去重裁决（G3 PASS），第四节为 V 阶段对抗审查摘要，附录为事实清单 F-001 ~ F-129（G1 PASS）。主报告见 [README.md](README.md)，行动项见 [actionable-items.md](actionable-items.md)。

## 第一节：四条洞察（G2 PASS）

### I-1 增量节奏从"单峰冲刺"细化为"多段事件脉冲"——协作模型缺少常驻使命

- **现象描述**：全量 360 次提交中，2026-08-26 之后的增量仅 38 次，占 10.56%（F-010），且未匀速铺开而是集中于 8 个活跃日期（F-062）；09-15 + 09-16 两日合计 22 次，09-16 单日 14 次为增量峰值（F-063），区间内存在四段完全无提交的时段、末段跨度约 15 天（F-064）。此形态与全量期高度同构：全量峰值落在 07-31 单日 69 次（F-007），活跃日仅 25 天（F-006），360 次中约 89.4% 发生于 08-25 之前（F-011、F-102）。
- **根因分析（5-Whys）**：①增量呈"多段脉冲"而非匀速，因 38 次提交由若干离散任务事件驱动——xuan-compose 分层重构 14、纯 Python 打包双轨化 7、子模块同步 6、文档原子化与怪癖分级 5、文档配置治理 3、doctor 子系统 3（F-055 ~ F-061），事件内部密集、事件之间零提交；②工作以"任务事件"为单位，因提交单位绑定到带 Session 标识的 spec 会话（F-107、F-110）；③提交绑定 spec 会话，因第一开发执行主体是 AI Agent（Trae Agent 253 / xinetzone 107，F-012），以"被指派→执行→交付"为工作单元，不具备自主发起能力；④会话结束即停止，因协作模型缺少"常驻待办池"，下一步动作依赖人再次指派；⑤**系统性根因**：该节奏是"agent 执行 + spec 会话驱动"协作模型的产物——提交粒度被人机交接节奏决定，全量"阶段冲刺"与增量"多段脉冲"是同构的，根因不是"缺乏纪律"，而是协作模型缺少 standing backlog。（**限定**：见 README 附录第 1 条，此根因属"与现有事实一致的一种解释"，存在竞争假设）
- **影响评估**：时间上交付节奏不可预测，出现最长约 15 天空窗（F-064）；质量上单事件内部质量高（F-113，自报口径）但事件之间缺少回归接力、上下文冷却；风险上重复代价显现（上游怪癖"10+ 次此类纠正"，F-116）。
- **改进建议**：①建立"常驻待办池 + 定时唤醒"，把可独立执行的小任务登记为 backlog 由定时任务触发消费；②为每个 spec 会话在结束报告中强制登记"后继可执行项"，形成会话间任务链；③把"提交节奏观察"升级为空窗期自动从 backlog 派发。
- **证据**：F-010、F-062、F-063、F-064、F-055、F-061、F-012、F-107、F-007、F-006、F-011

### I-2 治理重心从"功能扩张"迁移为"结构治理与移植对齐"——"迁入即治理"规律

- **现象描述**：全量口径 feat 以 93 次居首（F-013），但增量口径 feat 仅 9 次，docs 以 10 次反超为第一大类型（F-014）；build 类增量占比 18.4%（7/38）对全量 2.5%（9/360），抬升约 7 倍（F-016）；增量 scope 高度收敛于 xuan-compose 系——compose 13 + xuan-compose 7 合计 20/38（F-015）。对照基线 322 条类型分布（F-101），增量期类型结构已明显位移。
- **根因分析（5-Whys）**：①增量中 feat 不再第一、docs/build 反超，因主要工作是"把已有上游单体重构进 monorepo 并治理"（F-055、F-056、F-058）；②工作是重构/治理而非新增，因项目已从"从零搭建"转入"整合与对齐"（F-107、F-112）；③整合阶段集中产生 build/docs，因 monorepo 化成本集中在"结构合规"——20 个 `pyproject.toml` 需统一构建后端（F-096、F-037 ~ F-044）、文档需原子化拆分（F-050 ~ F-052）、目录需规避第三方 `docs/` 约定冲突（F-019）；④结构合规成本一次性释放，因"整包迁入"会一次性触发该单体此前全部隐性私有约定（构建后端、目录约定、版本声明、文档形态）；⑤**系统性根因**：这是"迁入即治理"的内在规律——把外部单体纳入统一仓库，会把其私有约定升级为公共约束，治理类提交（build/docs/chore）于是在迁入窗口集中爆发；功能扩张与结构治理在不同成熟度阶段此消彼长。
- **影响评估**：时间上治理提交不直接产出行用户可见功能，短期"功能吞吐"下降（增量 feat 仅 9）；质量上结构统一降低长期多包维护成本（F-077、F-096）；风险上治理尚未闭环——`requires-python` 仍有 xuan-compose `>=3.14` 与其余 `>=3.14.6` 的不一致（F-082、F-085），说明一致性复核未覆盖全部 20 个 `pyproject`。
- **改进建议**：①把"迁入即治理"固化为检查单（构建后端对齐、`requires-python` 与根一致、版本声明单一源、文档原子化，缺一不得合并）；②将检查纳入 `xs doctor` 自动核验（复用并扩展 F-047、F-048、F-060）；③为"整合阶段"单列验收口径（一致率、原子化完成率），避免用 feat 计数误判阶段成效。
- **证据**：F-013、F-014、F-016、F-055、F-107、F-112、F-096、F-037、F-019、F-082、F-101

### I-3 上游依赖策略从"依赖外部"升级为"对外部行为分级建模锁定"

- **现象描述**：`libs/xuan-compose/docs/parity/upstream-quirks.md` 建立上游怪癖固化四级口径——L0（精确断言）/ L1（弱断言）/ L2（注释固化）/ L3（清单固化），并逐条标注级别（F-114）；`create_secrets` 条目由 L1 补全文断言升级为 L0（F-115）；文档开篇声明"本项目有 10+ 次此类纠正"（F-116）。同期 xuan-compose 将对等目标锁定为 containers/podman-compose v1.6.0（F-112），T9 门禁记 484 ≥ 478、skip=0、覆盖率 91%，T10 记 142 符号 100% 映射（F-113，自报口径）。依赖面亦为全外部：4 个子模块全部为外部仓库且均已初始化、指针无漂移（F-074、F-075）。
- **根因分析（5-Whys）**：①需要 L0-L3 分级，因迁移上游时存在大量"非标准但已被依赖"的怪癖，弱断言无法察觉行为漂移；②产生"10+ 次纠正"，因编写测试时按"合理行为"假设而上游真实行为是怪癖（如报错串漏 `f` 前缀，F-115），断言与真实输出冲突需反复回改；③断言与真实行为反复冲突，因上游怪癖未被任何规约显式记录，只能靠"测试失败→读上游源码→回改"的试错链发现；④要"分级"而非统一 L0，因全部 L0 会锁死实现细节、上游一改即大面积失败，全部弱断言又会漏检，分级是"检出能力 vs 抗变更脆弱性"的显式权衡；⑤**系统性根因**：把"依赖外部代码"升级为"对外部行为建模并分级锁定"——面对不可控外部依赖，用"行为契约台账 + 分级断言"把外部不确定性内部化，L0/L1 是强契约、L2/L3 是低成本弱记录，按稳定性分工，可迁移到任何 fork / vendor / 对等重构场景。
- **影响评估**：质量上对等性可量化验证（F-113，自报口径），迁移风险收敛；风险上怪癖台账使上游升级时能快速定位受影响断言（F-110 即以该台账为比对基底）；复杂度上分级增加了断言维护心智成本，换取脆弱性可控与可审计。
- **改进建议**：①将 L0-L3 分级从单文件约定（F-114）上升为仓库级规范，使新迁入包默认遵循；②对上游同步类 spec 强制增设"怪癖台账 diff 复核"验收门；③把"怪癖发现→回改断言→登记级别"试错链沉淀为可复用的"对等重构检查单"。
- **证据**：F-114、F-115、F-116、F-113、F-112、F-074、F-075、F-110

### I-4 结构由"单包极化"迁移为"多库扩张"，与全局一致性债并存

- **现象描述**：`libs/` 现为 8 个条目（caffe-ffi、demo-ffi、mystx、npu-ffi、tvm-book、xuan-compose、xuan-core、xuan-ext-demo，其中 mystx/tvm-book 为子模块，F-090），较基线所述 6 个子项目新增 xuan-compose 与 mystx；`apps/` 仅 `.gitkeep` 与 README（F-089）、`attic/` 为空壳（F-093）。子模块面由基线"3 个均未初始化"变为"4 个全部初始化且指针无漂移"（F-074、F-075），与增量期 6 次子模块同步（F-057）一致。同时一致性债仍在：xuan-compose `requires-python >=3.14` 与其余 `>=3.14.6` 不一致（F-082、F-085）；工作区采集时点 13 行、复核时点 20 行（F-070、F-128）。
- **根因分析（5-Whys）**：①结构重心转向"多库扩张"，因增量期迁入 xuan-compose 并新增 mystx，`libs/` 由 6 增至 8（F-090）；②新增库同时 `apps/` 仍为空壳，因项目定位为"库 monorepo"，PDM workspace 仅声明 apps/libs/tools 三来源（F-127），apps 为预留容量（F-089）；③子模块由"未初始化"变"全部初始化"，因增量期持续执行上游同步（F-057）；④结构扩张同时仍残留一致性债，因结构变更由多个独立会话分散完成，缺少"结构变更后的全局一致性复核"环节；⑤**系统性根因**：monorepo 的"结构扩张"与"全局一致性"由不同机制驱动——扩张是局部会话事件（分布式），一致性需全局视图（集中、需统一扫描），当扩张速度快于全局复核频率时一致性债必然累积，这是"分布式增量变更 vs 集中式全局约束"的结构性张力。
- **影响评估**：质量上第二方库落地提升复用面（xuan-compose 自带 53 个测试文件，F-118）；风险上版本声明不一致（F-082）与持续 in-flight 的工作区（F-070、F-128）使"仓库当前状态"不能作为确定性依赖；复杂度上 20 个 `pyproject.toml`（F-096）放大一致性维护面。
- **改进建议**：①引入"结构变更后全局复核"节点（`requires-python`、构建后端、版本声明、文档形态），产出可归档复核报告；②将 in-flight 工作区视为常态，凡涉及工作区事实一律双时点标注（本复盘已在 F-070/F-128 落实）；③为"空壳目录"（apps、attic）明确"预留 / 孵化 / 归档"状态标注。
- **证据**：F-090、F-089、F-075、F-082、F-085、F-070、F-128、F-096、F-118、F-057、F-127、F-024

## 第二节：差异分析（对照既有基线三洞察）

> 基线：`retrospective-xuanspace-comprehensive-20260826` 的 I-1（冲刺式节奏）/ I-2（质量前置）/ I-3（结构重心）；补充对照 `2026-08-25-xuanspace-milestone-retro` 的"AI Agent 为第一开发执行主体"洞察。

| 对照项 | 基线结论 | 本次结论 | 判定 | 依据 |
|---|---|---|---|---|
| 节奏形态 | I-1：322 次中 93.2% 集中 13 天，单峰 69 次，后接 11 天空窗 | I-1：38 次散于 8 个活跃日，09-16 单日 14 次，存在四段空窗（最长约 15 天） | **强化** | 节奏规律（冲刺-空窗）未变且延续至增量期；形态由"单峰大冲刺"细化为"多段小脉冲"。F-007 → F-063、F-064 对照 |
| 质量投入 | I-2：test+fix 123 次占 38.2%，反超 feat 84（26.1%） | I-2：增量 test+fix 仅 3 次（7.9%），docs 10（26.3%）居首，feat 9（23.7%） | **反转（计数口径）** | 按类型计数，质量类提交占比骤降，"质量前置"结论在增量期不成立；但质量活动以"对等门禁/覆盖率补齐/独立验证报告"形式内嵌于重构提交（F-032、F-039、F-113），实为形态迁移而非质量停摆。F-101 → F-013/F-014 对照 |
| 结构重心 | I-3：caffe-ffi 独占 122 次（37.9%），前三/前五极化，3 子模块未初始化 | I-4：caffe-ffi 在增量 scope 中几近消失，xuan-compose 系 20/38 主导；libs 6→8；4 子模块全部初始化 | **反转** | 单点极化被多库扩张取代，且子模块由"未初始化"转为"全部初始化"。F-015、F-090、F-075 vs 基线 F-014 对照 |
| 依赖治理视角 | 基线三洞察均未涉及"上游依赖行为锁定"主题 | I-3：L0-L3 分级固化 + 怪癖台账 + 对等门禁 | **新增** | 基线未覆盖该主题面；本主题由增量期的 F-114、F-115、F-116、F-113 支撑 |
| 开发主体 | 里程碑报告：Trae Agent 219/314 = 69.7% | 全量 Trae Agent 253/360 = 70.3% | **无变化** | 占比稳定（+0.6pp），"AI Agent 为第一开发执行主体"结论持续成立。F-012 vs 基线 F-4 对照 |

**判定分布小结**：强化 1 条（节奏）、反转 2 条（质量计数口径、结构重心）、新增 1 条（依赖治理）、无变化 1 条（开发主体）。

## 第三节：模式萃取（G3 PASS）

### 3.1 新模式：迁移窗口的结构约定对齐法（迁入即治理）

> 已入库（L1，单案例验证，待二次案例升级 L2）：[migration-triggered-convention-alignment](../../../patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.md)（方法论模式 → 治理策略，同目录 kebab-case 风格）。

**一句话定义**：把外部单体或新包迁入统一仓库时，"私有约定暴露"与"公共约束对齐"必须在**同一迁移窗口内**一次完成，并以自动核验把一致性从"人肉复核"升级为"可量化复现"。

#### 触发场景

- **适用于**：①将第三方/上游单体整包、或新第一方包，迁入一个已存在公共约定的统一仓库（公共约定至少覆盖构建后端与构建参数、语言版本约束、版本声明来源、目录与文档形态）；②迁入动作会一次性暴露被迁包内部此前"隐性、不显式"的私有约定；③需要把对齐结果可复核地固化（人工检查单 + 自动核验）。
- **不适用于**：迁入目标为独立新仓库（无公共约定可比对）；单文件/少量函数搬迁（无结构性约定需对齐）；迁入方有意保留差异（许可隔离、独立发布节奏、上游强制目录约定——应显式登记为"有意偏离"）。

#### 核心步骤（5 步）

1. **盘点公共约定基线**：从仓库根与既有同类包提取"公共约定集"，逐项列明判定方式。
2. **迁移即对齐**：在迁入提交/切片内同步完成上述每一项对齐（对齐构建后端与构建参数声明、对齐语言版本约束、统一版本声明单一源、对齐目录与文档形态），不遗留到"以后统一"。（xuanspace 专有值 `wheel.cmake=false`、`>=3.14.6` 仅作案例证据，见下节，不写入模式步骤。）
3. **纳入自动核验**：把可机械判定的约定做成检查项，接入 `doctor`/CI，使一致性可量化、可复现、可回归。
4. **迁移窗口单列验收口径**：以"每包约定一致率 / 未解释偏离数"替代功能提交计数，作为该阶段健康度指标。
5. **关闭窗口前全局复核**：迁入完成后运行一次全量一致性扫描，产出可归档的复核报告。

#### 反模式（5 条）

- **只迁不改**：把上游整包原样放入公共仓库，隐性私有约定进入公共面。
- **对齐留在"以后统一"**：治理债随包数累积，单点漂移的排查成本随包数线性上升。
- **对齐仅靠人肉复核、无自动核验**：一致性结论随人走、不可复现、无回归。
- **把"有意偏离"当缺陷强行拉平**：破坏许可隔离、独立发布等设计意图。
- **用功能产出度量迁移期成效**：以 feat 计数替代结构一致性指标，误判阶段价值。

#### 迁移验证（4 个可判定成功信号）

- **信号 1**：迁入完成后全仓一致性扫描中"未解释偏离数 = 0"，或每一偏离均有登记条目与理由。
- **信号 2**：自动核验脚本可在不检出上游的环境独立运行，对每一项约定输出"包 → 项 → 期望 vs 实际"的字段级结论。
- **信号 3**：检查单的每一项在目标包中可被逐条核对，且可被下一个迁入包直接复用。
- **信号 4（成本边界）**：模式收益以"一次性对齐成本 vs 漂移复发成本"核对——当包数 ≥N 或迁移频率高时自动核验收益为正；小规模一次性迁入可退化为人工检查单。
- **证据口径限定**：F-113 的 484 ≥ 478、skip=0、覆盖率 91%、142 符号 100% 映射均为 CHANGELOG **项目自报口径、未经本任务重跑验证**，仅作规模量级参考；一致性判定须以仓库文件实体（各 `pyproject.toml` 实读，如 F-082、F-096）为准。

#### xuanspace 案例证据（挂 F 编号）

- 迁移窗口触发：xuan-compose 迁入（F-024 ~ F-031、F-107）；纯 Python 打包后端双轨化 7 条（F-037 ~ F-044、F-056）；20 个 `pyproject.toml` 构建后端归一（F-096）。
- 一致性债残存：`requires-python` 不一致（F-082、F-085）——**反例证据**：未在同一窗口内闭环即留债。
- 目录约定对齐：`docs/` → `doc/` 规避第三方路径约定冲突（F-019、F-059）。
- 自动核验雏形：`doctor` 子模块指针检查与 Sphinx 路径检查（F-047、F-048、F-060）。
- 文档形态对齐：对等文档原子化为十文件（F-050 ~ F-052）。

### 3.2 非当前场景迁移验证

- **组织/职能整合**：两个团队合并进统一工程体系时，在同一整合窗口内对齐代码规范、构建口径、版本发布口径与文档形态，并将可机械判定项纳入统一检查（CI/门禁）。
- **数据仓库多源接入**：多个上游数据集接入统一数仓时，在同一接入窗口内对齐分区命名、字段类型口径、时间粒度与元数据登记。
- **前端多包仓库引入新组件库**：组件库迁入 monorepo 时，在同一窗口内对齐构建配置、TypeScript 版本约束、包版本来源与文档形态。

### 3.3 G3 门判定表

| 候选 | 触发场景 | 核心步骤 | 反模式 | 迁移验证 | 可迁移到非当前场景 | 判定 |
|---|:---:|:---:|:---:|:---:|---|---|
| 候选 A 上游怪癖分级固化 | ✅ | ✅ | ✅ | ✅ | ✅（法律修订/财务系统替换） | 四要素齐备，但**机制已被 [behavior-characterization-freeze](../../../patterns/methodology-patterns/governance-strategy/behavior-characterization-freeze.md) 覆盖** → 并入既有，不单独过门 |
| 候选 B 迁移窗口的结构约定对齐法 | ✅ | ✅ | ✅ | ✅ | ✅（组织整合/数仓接入/前端 monorepo） | **[G3 PASS（新建 L1，已入库）](../../../patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.md)** |

### 3.4 去重裁决

#### 候选 A「上游怪癖分级固化」→ 裁定：并入既有（不新建）

**依据**：[behavior-characterization-freeze.md](../../../patterns/methodology-patterns/governance-strategy/behavior-characterization-freeze.md) 已完整包含候选 A 的核心机制——其「固化强度分级（L0-L3）」节逐级定义 `L0 精确断言`/`L1 弱断言`/`L2 注释固化`/`L3 清单固化`；同节记录"源案例 2026-10-10 已完成一次 L1→L0 升级"（即 F-115）；核心做法与检验标准含怪癖台账登记纪律。即"怪癖台账 + L0-L3 分级 + 四级定义 + 台账登记纪律"均已在该模式中显式存在，候选 A 无不可替代新机制。

**并入要点（严格限于 3 条）**：①明确台账载体已落地为 `libs/xuan-compose/docs/parity/upstream-quirks.md`（F-114），并增设"上游同步时强制复核台账条目新增/升级/失效"门禁（对应 F-110）；②补充"分级应从单文件约定上升为仓库级规范"的演进建议（对应 I-3 建议 1）；③补充检验标准：上游同步类 spec 须输出台账 diff 复核结论。

**不新建理由**：就候选 A 新建 L1 会与 `behavior-characterization-freeze.md` 大面积重复（L0-L3 四级定义、台账登记纪律逐字重叠），差异点可用 3 条以内表达，不足以独立成篇。

#### 候选 B「迁入即治理检查单」→ 裁定：[新建 L1（已入库）](../../../patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.md)

**依据（既有模式逐一比对）**：`convention-driven-creation.md`（管"成熟体系内新建模块时先读范例"）、`structure-first-extension.md`（文件级归属决策）、`dependency-ordered-slice-gates.md`（切片顺序与片门禁）、`snapshot-parity-migration.md`（对等性证明）、`dual-track-progressive-evolution.md`（依赖就绪度切换轨道，"仓库骨架先行统一"仅作检验标准一句带过）、`vendor-lifecycle-governance.md`（服务供应商治理）、`three-tier-governance.md`（文档治理三层）、`technical-debt-workaround-tracking.md`/`no-touch-list.md`/`dual-env-drift-reconciliation.md`/`docs-as-product.md`（不同域）——**均无等价覆盖**"外部单体迁入统一仓库时在同一窗口内完成私有约定→公共约束对齐并纳入自动核验"这一核心机制。**判"新建 L1"**。

## 第四节：V 阶段对抗审查摘要

> 完整审查记录（含意见正文与逐条采纳理由）见 V 阶段产物；本节摘要 7 条意见与采纳结论。

### 4.1 意见清单（7 条，四视角全覆盖）

| 编号 | 视角 | 针对对象 | 意见要点 | 严重度 | 处置 |
|------|------|---------|---------|:------:|------|
| V-1 | 魔鬼代言人 | E 阶段候选 A 裁决 | "并入"若无边界，既有文档会膨胀为大杂烩；并入上限在哪？ | 中 | **采纳** |
| V-2 | 新人 | E 阶段模式 B 步骤 2 | 初稿写入 `wheel.cmake=false` 等专有值，致模式不可迁移 | 中 | **采纳** |
| V-3 | 老板 | E 阶段迁移验证 + I-2 建议 | 自动核验未给 ROI 边界，小规模一次性场景可能治理为负 | 中 | **采纳** |
| V-4 | 未来 | E 阶段步骤 3 / 模式存续性 | 若工具原生提供一致性校验，模式第 3 步是否被淘汰 | 低 | 不采纳 |
| V-5 | 魔鬼代言人 | F-113 自报值 / I-3 / E §1.4 | 以未重跑的 CHANGELOG 自报值支撑结论，证据强度不足 | **高** | **采纳** |
| V-6 | 魔鬼代言人 | I-1 根因 | "提交少"存在更简解释（维护期工作量下降），是否过度归因 | 中 | **采纳** |
| V-7 | 新人 | E 阶段触发场景 | "外部单体"与"新第一方包"并列，新人难判断适用性 | 低 | 不采纳 |

### 4.2 采纳 5 条与修正痕迹

| 意见 | 修正位置 | 修正内容 |
|------|---------|---------|
| V-1 | E 阶段 §2.1 | "并入要点"加边界约束"严格限于 3 条"，锁死增量规模；未新建候选 A 独立文档 |
| V-2 | E 阶段 §1.2 步骤 2 | 由专有值改为通用动作表述，专有值降为案例证据 |
| V-3 | E 阶段 §1.4 | 新增"可判定成功信号 4（成本边界）"，给出自动核验的阈值判据 |
| V-5 | E 阶段 §1.4 | 将 F-113 降级为"项目自报口径、未经重跑验证"，并新增"以仓库文件实体为准"的自律条款 |
| V-6 | E 阶段 §4.1 / 本报告 README 附录 | I-1 根因限定为"与现有事实一致的一种解释"，显式标注竞争假设与证据缺口 |

### 4.3 不采纳 2 条与理由

- **V-4（不采纳）**：本模式价值锚在**流程性检查单**与**判定纪律**（未解释偏离数、字段级证据），而非某个具体核验脚本；工具原生支持只会降低第 3 步执行成本，不会取消"识别隐性私有约定→同一窗口对齐→单列验收口径"的流程判断。
- **V-7（不采纳）**：触发场景已通过"适用于 / 不适用于"两栏界定，两类迁入共享的判定条件是"迁入是否一次性暴露被迁包的隐性私有约定"，差异项由反模式第 4 条与"有意偏离登记"覆盖，拆分反而稀释模式主机制。

### 4.4 审查覆盖度自检（对照 AC-9 / G5）

| 要求 | 达成情况 |
|---|---|
| 覆盖四视角 | ✅ 魔鬼代言人 V-1/V-5/V-6；新人 V-2/V-7；老板 V-3；未来 V-4 |
| 意见 ≥ 5 条 | ✅ 共 7 条 |
| 采纳 ≥ 2 条且有修正痕迹 | ✅ 采纳 5 条，5 处修正落于 E 阶段（§2.1/§1.2/§1.4×2/§4.1） |
| ≥ 1 条指向事实证据强度不足 | ✅ V-5 |

## 附录：R 阶段事实清单（F-001 ~ F-129，G1 PASS）

> 忠实转写自 `facts.md`；全部事实来自 `git log`/仓库文件直接验证，无因果推断词、无判断词，可复验。**双时点标注**：F-070（采集时点）与 F-128（复核时点）为不同时点的工作区状态，不作为当前状态的确定性结论。

| 编号 | 事实 | 来源 |
|------|------|------|
| F-001 | 仓库全量提交总数为 360 次 | `git rev-list --count HEAD` → `360` |
| F-002 | 提交日期范围为 2026-07-24 ~ 2026-10-10 | `git log --format=%ad --date=short` 首末项 |
| F-003 | 首提交为 `bb9ecce`（2026-07-24），subject 为「feat: 初始化 Xuanspace（玄境）Python monorepo 项目」 | `git log --reverse --format="%h\|%ad\|%s" --date=short` 首行 |
| F-004 | 最新提交（HEAD）为 `587da1c`（完整 SHA `587da1cb283e5ffad9a326568287378ba74f27cd`），2026-10-10 16:14:39 +0800，subject「test(xuan-compose): 加固 create_secrets 报错全文断言」 | `git log -1 --format="%H\|%ad\|%s" --date=iso` |
| F-005 | 当前分支为 `main` | `git rev-parse --abbrev-ref HEAD` → `main` |
| F-006 | 全量活跃日期数为 25 天 | `git log --format=%ad --date=short \| Sort-Object -Unique` 计数 → `25` |
| F-007 | 峰值日期为 2026-07-31，当日 69 次提交 | `git log --format=%ad --date=short \| Group-Object \| Sort-Object Count -Descending` |
| F-008 | 次高峰日期依次为 08-04（41）、08-05（37）、07-28（32）、07-24（23）、07-30（21）、08-03（21）、08-01（15） | 同 F-007 |
| F-009 | 全量按月份分布：2026-07 = 168、2026-08 = 154、2026-09 = 33、2026-10 = 5 | `git log --format=%ad --date=format:"%Y-%m" \| Group-Object` |
| F-010 | 2026-08-26 之后（增量口径）提交数为 38 次，占全量 360 次的 10.56% | `git log --since=2026-08-26 --oneline` 计数 → `38`；占比为计算值 |
| F-011 | 截至 2026-08-19 提交数为 314；截至 2026-08-25 为 322 | `git rev-list --count --until=... HEAD` |
| F-012 | 全量作者分布：`Trae Agent` 253、`xinetzone` 107（合计 360） | `git log --format=%an \| Group-Object` |
| F-013 | 全量 type 分布：feat 93、test 63、fix 62、docs 58、chore 43、refactor 15、build 9、perf 9、ci 5、merge 1；另有 2 条 subject 不符合 `type(scope):` 前缀 | `git log --format=%s` 正则分组统计 |
| F-014 | 增量 type 分布：docs 10、feat 9、build 7、chore 6、refactor 2、test 2、fix 1、merge 1 | `git log --since=2026-08-26 --format=%s` 正则分组 |
| F-015 | 增量 scope 分布：compose 13、xuan-compose 7、submodule 4、doctor 3、submodules 2、conf 1、doc 1、okf 1、readme 1、root 1、scripts 1、templates 1、xs 1、xuan-core 1 | `git log --since=2026-08-26 --format=%s` 提取括号内容分组 |
| F-016 | 增量 build 7 条占 18.4%（7/38）；全量 build 9 条占 2.5%（9/360） | 由 F-013、F-014 计算 |
| F-017 | `89eedf5` 2026-09-03 chore(submodule): 新增 libs/mystx 子模块统筹 MystX Sphinx 主题与扩展共享库 | `git log --since=2026-08-26 --format="%h\|%ad\|%s" --date=short --reverse` |
| F-018 | `e893b25` 2026-09-03 docs(conf): 新增 setup() 声明 parallel_read_safe=True + Fail-Fast 并行守卫钩子 [prevent: fail-fast-assertion] | 同 F-017 |
| F-019 | `4d4a6cd` 2026-09-03 refactor(doc): 统一 Sphinx 文档目录名为 doc/，规避与第三方工具的 docs/ 路径约定冲突 | 同 F-017 |
| F-020 | `31c28b5` 2026-09-04 chore(submodule): 子模块 URL 协议从 HTTPS 切换为 SSH | 同 F-017 |
| F-021 | `9e39435` 2026-09-04 docs(readme): 修正 Python 版本徽章为 3.14+ | 同 F-017 |
| F-022 | `35e8b58` 2026-09-04 chore(submodule): 更新 libs/mystx 指针至 P1-A 审计落地提交 | 同 F-017 |
| F-023 | `98dcaa6` 2026-09-04 chore(submodule): 更新 libs/mystx 指针至并行构建环境分流提交 | 同 F-017 |
| F-024 | `7edfda0` 2026-09-15 feat(compose): 新增 xuan-compose 包脚手架，确立 GPL-2.0 对等重构基线 | 同 F-017 |
| F-025 | `d2f9992` 2026-09-15 feat(compose): 迁入基础层 compat/types/interpolation 等六模块 | 同 F-017 |
| F-026 | `aca51fa` 2026-09-15 feat(compose): 迁入规范层 normalize/merge/discovery 三模块 | 同 F-017 |
| F-027 | `cc6a49e` 2026-09-15 feat(compose): 迁入执行层 runner/model/dependencies 及镜像拉取 | 同 F-017 |
| F-028 | `7ce078a` 2026-09-15 feat(compose): 迁入翻译层 translate 子包完成服务描述到 podman 参数的对等翻译 | 同 F-017 |
| F-029 | `39c2538` 2026-09-15 feat(compose): 迁入引擎层 ComposeEngine 完成 compose 文件解析与引擎状态装配 | 同 F-017 |
| F-030 | `245f9ad` 2026-09-15 feat(compose): 迁入命令层 24 个 handler 与显式注册表 | 同 F-017 |
| F-031 | `9d91a3e` 2026-09-15 feat(compose): 迁入 CLI 层 parser/main 与 python -m 入口 | 同 F-017 |
| F-032 | `43f7812` 2026-09-16 test(compose): T9 全量对等门禁——argparse 快照零差异与覆盖率补齐 | 同 F-017 |
| F-033 | `1c40e44` 2026-09-16 docs(compose): T10 对等审计与文档收尾并去除重复依赖检查 | 同 F-017 |
| F-034 | `5f73292` 2026-09-16 refactor(compose): T11 对抗审查修复——下沉 resolve_extends 消除规范层环 | 同 F-017 |
| F-035 | `9a39ddf` 2026-09-16 docs(compose): T11 独立对抗审查报告与 README 架构图校正 | 同 F-017 |
| F-036 | `8868a6d` 2026-09-16 docs(compose): T1-T12 分层重构交付总结报告 | 同 F-017 |
| F-037 | `4b4c082` 2026-09-16 build(scripts): 纯 Python 包构建门禁双轨化并同步构建规范文档 | 同 F-017 |
| F-038 | `448d729` 2026-09-16 build(xuan-compose): 纯 Python 打包改用 wheel.cmake=false 产出通用 wheel | 同 F-017 |
| F-039 | `dc3d365` 2026-09-16 docs(xuan-compose): 新增功能完整性七概念独立验证报告 | 同 F-017 |
| F-040 | `46b1601` 2026-09-16 build(templates): python 脚手架改用 wheel.cmake=false 纯 Python 模式 | 同 F-017 |
| F-041 | `0a64553` 2026-09-16 build(xuan-core): 纯 Python 打包改用 wheel.cmake=false 产出通用 wheel | 同 F-017 |
| F-042 | `20f2a33` 2026-09-16 build(xs): 纯 Python 打包改用 wheel.cmake=false 并清理 sdist 清单 | 同 F-017 |
| F-043 | `e1213bf` 2026-09-16 build(okf): 纯 Python 打包改用 wheel.cmake=false 并清理 sdist 清单 | 同 F-017 |
| F-044 | `f293ed6` 2026-09-16 build(root): 枢纽包改用 wheel.cmake=false 去除根 CMake 占位 | 同 F-017 |
| F-045 | `94c565d` 2026-09-16 chore(submodules): 前进 mystx 指针至 ninja/cmake 无效依赖清理提交 | 同 F-017 |
| F-046 | `401d51d` 2026-09-21 chore(submodules): 同步 tvm-ffi 结构遍历与策略支持 | 同 F-017 |
| F-047 | `ef18da7` 2026-09-22 feat(doctor): 新增子模块指针一致性检查 | 同 F-017 |
| F-048 | `fc45aef` 2026-09-23 fix(doctor): 修正 Sphinx 检查硬编码 docs/ 导致恒为跳过 | 同 F-017 |
| F-049 | `294772f` 2026-09-23 merge(doctor): 合入 fix/doctor-sphinx-doc-path 分支 | 同 F-017 |
| F-050 | `e4b2a74` 2026-10-10 docs(xuan-compose): 对等文档原子化为索引、台账与快照十文件 | 同 F-017 |
| F-051 | `8289395` 2026-10-10 docs(xuan-compose): 库内引用改指原子化文档新路径 | 同 F-017 |
| F-052 | `dea3e6b` 2026-10-10 docs(xuan-compose): 移除原子化前的四份长文档 | 同 F-017 |
| F-053 | `88e3ea7` 2026-10-10 docs(xuan-compose): 建立上游怪癖固化级别分级口径 | 同 F-017 |
| F-054 | `587da1c` 2026-10-10 test(xuan-compose): 加固 create_secrets 报错全文断言 | 同 F-017 |
| F-055 | 增量主题：xuan-compose 分层重构交付（脚手架 + 七层迁入 + T9/T10/T11 + 验收/总结报告），14 次，代表 7edfda0、9d91a3e、43f7812 | 对 F-017 ~ F-054 归类计数 |
| F-056 | 增量主题：纯 Python 打包门禁双轨化（wheel.cmake=false），7 次，代表 4b4c082、f293ed6 | 同上 |
| F-057 | 增量主题：子模块指针与上游同步，6 次，代表 89eedf5、401d51d | 同上 |
| F-058 | 增量主题：2026-10-10 xuan-compose 对等文档原子化与上游怪癖分级，5 次，代表 e4b2a74、88e3ea7 | 同上 |
| F-059 | 增量主题：文档与配置治理（doc/ 目录改名、conf 并行守卫、README 徽章），3 次 | 同上 |
| F-060 | 增量主题：doctor 子系统（子模块指针检查 + Sphinx 路径修复），3 次 | 同上 |
| F-061 | 增量聚类合计核对：14 + 7 + 6 + 5 + 3 + 3 = 38，与 F-010 一致 | 同上 |
| F-062 | 增量 38 条集中于 8 个活跃日期：09-03（3）、09-04（4）、09-15（8）、09-16（14）、09-21（1）、09-22（1）、09-23（2）、10-10（5） | `git log --since=2026-08-26 --format=%ad --date=short \| Group-Object` |
| F-063 | 增量区间单日峰值日期为 2026-09-16（14 次）；次高为 2026-09-15（8 次） | 同 F-062 |
| F-064 | 增量覆盖区间中，08-26~09-02、09-05~09-14、09-17~09-20、09-24~10-09 各时段无提交 | 由 F-062 活跃日期集合与区间对照 |
| F-065 | 里程碑提交 1：`7edfda0`（2026-09-15，「新增 xuan-compose 包脚手架，确立 GPL-2.0 对等重构基线」） | F-024 |
| F-066 | 里程碑提交 2：`9d91a3e`（2026-09-15，「迁入 CLI 层 parser/main 与 python -m 入口」，分层迁入链末环） | F-031 |
| F-067 | 里程碑提交 3：`43f7812`（2026-09-16，「T9 全量对等门禁——argparse 快照零差异与覆盖率补齐」） | F-032 |
| F-068 | 里程碑提交 4：`88e3ea7`（2026-10-10，「建立上游怪癖固化级别分级口径」） | F-053 |
| F-069 | 里程碑提交 5：`587da1c`（2026-10-10，HEAD，「加固 create_secrets 报错全文断言」） | F-004 |
| F-070 | 工作区非干净：采集时点 `git status --porcelain` 输出 13 行，全部为 ` M`（已修改未暂存） | `git status --porcelain` |
| F-071 | 13 个已修改文件全部位于 `libs/xuan-compose/`，含 8 个 src 文件与 5 个 tests 文件 | `git status --porcelain` |
| F-072 | 未提交改动规模为 13 files changed，145 insertions(+)，14 deletions(-) | `git diff --stat` |
| F-073 | 暂存区为空（`git diff --cached --stat` 无输出）；无 stash 记录 | `git diff --cached --stat`、`git stash list` |
| F-074 | `.gitmodules` 声明 4 个子模块：vendor/tvm-ffi、libs/tvm-book、vendor/caffe、libs/mystx | 文件 `projects/xuanspace/.gitmodules` |
| F-075 | `git submodule status` 显示 4 个子模块均已初始化（无 `-` 前缀）且指针无漂移（无 `+`）：libs/mystx @ ba6f0b1、libs/tvm-book @ 3ddcefe、vendor/caffe @ f938d88、vendor/tvm-ffi @ aef2d00 | `git submodule status` |
| F-076 | 根 `pyproject.toml`：`version = "0.1.0"`、`requires-python = ">=3.14.6"`、build-backend = `scikit_build_core.build`（requires `scikit-build-core>=0.10`） | 文件 `projects/xuanspace/pyproject.toml` 第 2-11 行 |
| F-077 | 根 `pyproject.toml` 声明 `[tool.scikit-build.wheel] cmake = false` 与 `minimum-version = "0.10"` | 同 F-076 第 140-144 行 |
| F-078 | 根 `CHANGELOG.md` 最新条目为 `## [0.1.0] - 2026-07-23`，含 Added 段 10 条 | 文件 `projects/xuanspace/CHANGELOG.md` 第 8-19 行 |
| F-079 | 根 `README.md` frontmatter 声明 `id: "xuanspace-readme"`、`version: "0.1.0"`、`x-toml-ref: ".meta/toml/README.toml"` | 文件 `projects/xuanspace/README.md` 第 1-5 行 |
| F-080 | 根 `README.md` 徽章声明 Python 3.14+、Build: CMake+Ninja、Docs: Sphinx+MyST | 同 F-079 第 11-13 行 |
| F-081 | `libs/xuan-core/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 文件 `libs/xuan-core/pyproject.toml` 第 7、9 行 |
| F-082 | `libs/xuan-compose/pyproject.toml`：version 0.1.0、requires-python >=3.14（与其他 libs 的 >=3.14.6 不同） | 文件 `libs/xuan-compose/pyproject.toml` 第 9、13 行 |
| F-083 | `libs/caffe-ffi/pyproject.toml`：version 1.2.0、requires-python >=3.14.6 | 文件 `libs/caffe-ffi/pyproject.toml` 第 7、23 行 |
| F-084 | `libs/demo-ffi`、`libs/npu-ffi`、`libs/xuan-ext-demo`：version 0.1.0、requires-python >=3.14.6 | 各 `pyproject.toml` 对应行 |
| F-085 | 子模块 `libs/tvm-book/pyproject.toml`：requires-python >=3.14；子模块 `libs/mystx/pyproject.toml`：requires-python >=3.14 | 文件 `libs/tvm-book/pyproject.toml` 第 34 行、`libs/mystx/pyproject.toml` 第 11 行 |
| F-086 | `tools/xs/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`tools/okf/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 各文件对应行 |
| F-087 | `tools/templates/{python,native,native-ffi}/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 各模板 `pyproject.toml` 对应行 |
| F-088 | 顶层目录（排除 `.git`）：`.agents`、`.github`、`.meta`、`.mypy_cache`、`.pytest_cache`、`.ruff_cache`、`.trae`、`apps`、`attic`、`doc`、`libs`、`scripts`、`tests`、`tools`、`vendor` | `Get-ChildItem -Directory` |
| F-089 | `apps/` 内容仅为 `.gitkeep` 与 `README.md`（无实际应用子项目） | `Get-ChildItem apps` |
| F-090 | `libs/` 内容为 8 个条目（caffe-ffi、demo-ffi、mystx、npu-ffi、tvm-book、xuan-compose、xuan-core、xuan-ext-demo）+ `.gitkeep` + `README.md`（mystx/tvm-book 为子模块） | `Get-ChildItem libs` |
| F-091 | `tools/` 内容为 okf、templates、xs + `.gitkeep` + `README.md` | `Get-ChildItem tools` |
| F-092 | `scripts/` 内容为 `.gitkeep`、`check_pyproject_style.py`、`README.md` | `Get-ChildItem scripts` |
| F-093 | `attic/` 内容仅为 `.gitkeep` 与 `README.md` | `Get-ChildItem attic` |
| F-094 | `tests/`（顶层）内容为 `__pycache__`、`__init__.py` 与 5 个测试文件（test_affected/config/discovery/doctor_sphinx/doctor_submodules） | `Get-ChildItem tests` |
| F-095 | `doc/` 内容为 `_static`、`adr`、`cli`、`okf`、`user-guide` 目录，以及 conf.py、index.md、intro.md、architecture.md、build-system.md、contributing.md、dependency-report.md、quickstart.md、README.md、Makefile、make.bat、`.gitkeep` | `Get-ChildItem doc` |
| F-096 | 全仓 `pyproject.toml` 共 20 个（含 vendor 子系统与子模块内） | `Glob **/pyproject.toml` |
| F-097 | 仓库根存在文件：pyproject.toml、README.md、CONTRIBUTING.md、AGENTS.md、.gitmodules、.gitignore、CHANGELOG.md、LICENSE、CMakePresets.json、.gitattributes | `Glob projects/xuanspace/*` |
| F-098 | 既有复盘 1（阶段一里程碑）：`docs/retrospective/reports/2026-08-25-xuanspace-milestone-retro.md` 存在；覆盖 2026-07-24 ~ 08-19、314 次；作者 Trae Agent 219、xinetzone 95 | 该文件第 1-27 行 |
| F-099 | 既有复盘 2（初始化阶段）：`retrospective-xuanspace-mono-repo-20260724/` 存在（含 index.md、README.md、insight-extraction.md）；复盘日期 2026-07-24、周期 07-20 ~ 07-24、任务 20/20 | 该目录 README.md 第 1-12 行 |
| F-100 | 既有复盘 3（首次全量）：`retrospective-xuanspace-comprehensive-20260826/` 存在；07-24 ~ 08-25、322 次、活跃 17 天、峰值 07-31（69） | 该目录 README.md 第 1-26 行 |
| F-101 | 基线报告 3 全量 type 分布：feat 84、test 62、fix 61、docs 48、chore 37、refactor 13、perf 9、ci 5、build 2、merge 1（合计 322） | 该目录 README.md 第 30-39 行 |
| F-102 | 本次增量区间 2026-08-26 ~ 2026-10-10、增量 38 条；与基线 322 拼接后为全量 360 | 由 F-010、F-011 计算 |
| F-103 | 基线报告 1 的 314 经复核一致；基线报告 3 的 322 经复核一致 | `git rev-list --count --until=... HEAD` |
| F-104 | `docs/retrospective/patterns/methodology-patterns/governance-strategy/` 下无任何 `.toml` 伴生文件 | `Glob` 该目录 `*.toml` → 无匹配 |
| F-105 | 该 governance-strategy 目录 `index.md` 第 17、136、146 行分别登记 `behavior-characterization-freeze`、`snapshot-parity-migration`、`submodule-directory-convention` | `Grep index.md` |
| F-106 | governance-strategy 目录存在 `snapshot-parity-migration.md`、`submodule-directory-convention.md`、`behavior-characterization-freeze.md`（另含 docs-as-product.md、three-tier-governance.md 等） | `Glob` 该目录 `*` |
| F-107 | `.trae/specs/xuan-compose-refactor/` 存在（含 spec.md、tasks.md）；spec 标题「xuan-compose：podman-compose 单体重构进 xuanspace/libs」，七概念场景 3『重构优化』链路 I→F→A→V→C，Session `sc-20260915-podman-compose-refactor` | 该 spec.md 第 1-5 行 |
| F-108 | `.trae/specs/workspace-governance/xuanspace-mono-repo/` 存在（含 spec.md、tasks.md、review.md）；spec frontmatter status draft、id xuanspace-mono-repo-spec、version 1.4 | 该 spec.md 第 1-7 行 |
| F-109 | `.trae/specs/workspace-governance/consolidate-xuanspace-governance/` 存在；spec 标题「xuanspace 治理加固 Spec」，source `"../../.agents/docs/retrospective/2026-08-25-xuanspace-milestone-retro.md"` | 该 spec.md 第 1-7 行 |
| F-110 | `.trae/specs/sync-upstream-delta/` 存在（含 spec.md、tasks.md、checklist.md）；spec 标题「xuan-compose 上游增量同步（e3df104 → 1f1cb09）」，链路 R→I→A→V→C，Session `sc-20261010-sync-upstream-delta`，基线 `e3df104`（v1.6.0）→ `1f1cb09`，区间含 11 个非合并提交 | 该 spec.md 第 1-10 行 |
| F-111 | `libs/xuan-compose/docs/` 在 HEAD 状态含 10 个文件（README、findings-ledger、parity/{README,differences,symbol-map,upstream-quirks}、delivery/、verification/、review/、patterns/） | `Glob libs/xuan-compose/docs/**/*`；`git show --stat e4b2a74` |
| F-112 | `libs/xuan-compose/CHANGELOG.md` 声明版本号独立于上游，重构切片 T1-T12 保持对 containers/podman-compose v1.6.0（`e3df104`）行为对等；最新版本段「0.1.0 — 初始分层重构（T1-T10）」 | 该文件第 1-8 行 |
| F-113 | `libs/xuan-compose/CHANGELOG.md` 记录 `__version__="1.6.0+xuan.1"`、容器标签 `1.6.0+xuan.1`、T9 门禁「上游 26 个单元测试文件全量移植（484 ≥ 478，skip=0）、覆盖率整体 91%」、T10「142 个上游公开符号 100% 映射」 | 该文件第 15-34 行 |
| F-114 | `libs/xuan-compose/docs/parity/upstream-quirks.md` 声明上游怪癖固化级别为 L0（精确断言）、L1（弱断言）、L2（注释固化）、L3（清单固化）四级并逐条标注；文末含「T7 清单固化段（L2/L3）」 | 该文件第 1-63 行 |
| F-115 | `upstream-quirks.md` 文末登记条目「create_secrets 报错串第二个片段漏 f 前缀（2026-10-10 由 L1 补全文断言升级）【L0】」 | 该文件第 47 行 |
| F-116 | `upstream-quirks.md` 开篇声明「本项目有 10+ 次此类纠正」 | 该文件第 5 行 |
| F-117 | 顶层 `tests/` 含 5 个 `test_*.py` 文件 | `Get-ChildItem tests -Filter test_*.py` 计数 → 5 |
| F-118 | 各 libs 子项目 `tests/` 下 `test_*.py` 数：caffe-ffi 104、demo-ffi 2、mystx 6、npu-ffi 7、tvm-book 0、xuan-compose 53 | 逐目录 `Get-ChildItem -Recurse -Filter test_*.py` 计数 |
| F-119 | `tools/okf/` 含 19 个 `test_*.py`；`tools/xs/` 无 tests 目录 | `Get-ChildItem tools\okf\tests`、`tools\xs` 检查 |
| F-120 | 全仓（含 vendor）`test_*.py` 总数为 277；排除 `\vendor\` 后为 199 | `Get-ChildItem -Recurse -Filter test_*.py` 计数 |
| F-121 | `.github/workflows/` 含 2 个文件：ci.yml、release.yml | `Get-ChildItem .github\workflows` |
| F-122 | `.agents/` 含 checklists、prompts、protocols、rules、templates 子目录，以及 context-routing.md、global-core-rules.md、ONBOARDING.md、README.md、`.gitkeep` | `Get-ChildItem .agents` |
| F-123 | `.meta/toml/` 含 `AGENTS.toml`、`CONTRIBUTING.toml`、`README.toml`、`doc/dependency-report.toml` 与 `.gitkeep` | `Get-ChildItem .meta\toml -Recurse` |
| F-124 | 仓库根 `AGENTS.md` 声明「Xuanspace（玄境）是一个 Python 3.14.6+ monorepo 项目」，验收基线表列：覆盖率核心 ≥90%/一般 ≥80%、每 Bug 修复 ≥1 防回归用例、每新功能 ≥1 测试、mypy 零新增告警、ruff check 零错误 | 文件 `projects/xuanspace/AGENTS.md` |
| F-125 | 仓库根存在 `.trae/` 目录 | 命令输出：F-088 |
| F-126 | 根 `pyproject.toml` pytest `testpaths = ["tests"]`；ruff `line-length = 120`、`target-version = "py314"`，exclude 含 vendor、libs/tvm-book、attic、.agents、tools/templates；mypy `python_version = "3.14"` | 该文件第 146-194 行 |
| F-127 | 根 `pyproject.toml` 声明 `[tool.pdm.workspace]` packages 为 apps、libs、tools 三个来源 | 该文件第 128-133 行 |
| F-128 | 复核时点 `git status --porcelain` 输出 20 行：19 行 ` M` + 1 行 `?? libs/xuan-compose/tests/test_override_environment.py`（未跟踪）；与 F-070 的 13 行不一致，表明工作区处于并行会话持续写入状态 | `git status --porcelain`（复核） |
| F-129 | 本复盘任务对 `projects/xuanspace` 全程只读，未写入任何文件；F-070 与 F-128 所列改动均归因于并行会话（`.trae/specs/sync-upstream-delta/`）的在途工作 | 本任务写入路径清单 |