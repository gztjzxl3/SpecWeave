---
id: "xuanspace-comprehensive-retrospective-export-e-stage-pattern"
title: "xuanspace（玄境）全面复盘 E 阶段模式萃取与去重裁决"
source:
  - "./insights.md"
  - "./facts.md"
methodology: "seven-concepts E 阶段（模式萃取）+ 去重裁决"
content-sensitivity: public
---

# xuanspace（玄境）全面复盘 — E 阶段模式萃取草稿

> 输入：`insights.md`（I-1 ~ I-4；其附录给出候选 A「上游怪癖分级固化」、候选 B「迁入即治理检查单」）
> 比对对象：`docs/retrospective/patterns/methodology-patterns/governance-strategy/` 既有模式库
> 说明：本文件为 **Task 3 草稿**，只做模式萃取与去重裁决；正式模式入库（L1 文档 + TOML + toctree）为 Task 5 工作。

## 一、模式萃取（通过 G3 门的新模式）

### 模式 B：迁移窗口的结构约定对齐法（迁入即治理）

> 建议 id：`migration-triggered-convention-alignment`（英文 kebab-case，同目录风格）

**模式类型**：方法论模式 → 治理策略（外部单体迁入统一仓库时的结构一致性治理）

**一句话**：把外部单体或新包迁入统一仓库时，"私有约定暴露"与"公共约束对齐"必须在**同一迁移窗口内**一次完成，并以自动核验把一致性从"人肉复核"升级为"可量化复现"。

#### 1.1 触发场景（什么条件下适用）

**适用于：**

- 将第三方/上游单体整包、或新第一方包，迁入一个**已存在公共约定**的统一仓库（monorepo），公共约定至少覆盖：构建后端与构建参数、语言版本约束、版本声明来源、目录与文档形态；
- 迁入动作会**一次性暴露**被迁包内部此前"隐性、不显式"的私有约定（这些约定在单包内部不构成问题，进入统一仓库后才成为需对齐的公共约束）；
- 需要把对齐结果**可复核地固化**（人工检查单 + 自动核验）。

**不适用于：**

- 迁入目标为独立新仓库——无公共约定可比对；
- 单文件/少量函数搬迁——不存在结构性约定需要对齐；
- 迁入方**有意保留差异**（如许可隔离、独立发布节奏、上游强制目录约定）——此类差异应显式登记为"有意偏离"，而非强行拉平。

#### 1.2 核心步骤（按序可执行）

1. **盘点公共约定基线**：从仓库根与既有同类包提取"公共约定集"，逐项列明判定方式。
2. **迁移即对齐**：在迁入提交/切片内**同步完成**上述每一项对齐，不遗留到"以后统一"——即对齐构建后端与构建参数声明、对齐语言版本约束、统一版本声明单一源、对齐目录与文档形态。（V-2 校正：本步骤以通用动作表述，`wheel.cmake=false`、`>=3.14.6` 等 xuanspace 专有值仅作案例证据，见 §1.5，不写入模式步骤。）
3. **纳入自动核验**：把可机械判定的约定做成检查项，接入 `doctor`/CI，使一致性可量化、可复现、可回归。
4. **迁移窗口单列验收口径**：以"每包约定一致率 / 未解释偏离数"替代功能提交计数，作为该阶段健康度指标。
5. **关闭窗口前全局复核**：迁入完成后运行一次全量一致性扫描，产出可归档的复核报告。

#### 1.3 反模式（什么情况不该用 / 常见错误）

- ❌ **只迁不改**：把上游整包原样放入公共仓库，隐性私有约定进入公共面。
- ❌ **对齐留在"以后统一"**：治理债随包数累积，单点漂移的排查成本随包数线性上升。
- ❌ **对齐仅靠人肉复核、无自动核验**：一致性结论随人走、不可复现、无回归。
- ❌ **把"有意偏离"当缺陷强行拉平**：破坏许可隔离、独立发布等设计意图。
- ❌ **用功能产出度量迁移期成效**：以 feat 计数替代结构一致性指标，误判阶段价值。

#### 1.4 迁移验证（如何验证模式应用成功）

- **可判定成功信号 1**：迁入完成后全仓一致性扫描中"未解释偏离数 = 0"，或每一偏离均有登记条目与理由。
- **可判定成功信号 2**：自动核验脚本可在**不检出上游**的环境独立运行，对每一项约定输出"包 → 项 → 期望 vs 实际"的字段级结论。
- **可判定成功信号 3**：检查单的每一项在目标包中可被逐条核对，且该检查单可被下一个迁入包直接复用。
- **可判定成功信号 4（V-3 校正：成本边界）**：模式收益以"一次性对齐成本 vs 漂移复发成本"核对——当包数 ≥N 或迁移发生频率高时，自动核验的收益为正；小规模一次性迁入可退化为人工检查单，不必强上自动核验。
- **补充证据与口径限定（V-5 校正）**：本项目 T9 门禁的 484 ≥ 478、skip=0、覆盖率 91%，T10 的 142 符号 100% 映射（F-113），均为 xuan-compose `CHANGELOG.md` **项目自报口径，未经本任务重跑验证**，仅作迁移完成度的规模量级参考；一致性判定须以仓库文件实体（各 `pyproject.toml` 实读，如 F-082、F-096）为准，不得以自报值充当一致性证据。

#### 1.5 xuanspace 案例证据（挂 F 编号，仅作证据，不进入模式正文推导）

- 迁移窗口触发：xuan-compose 迁入（F-024 ~ F-031、F-107）；纯 Python 打包后端双轨化 7 条（F-037 ~ F-044、F-056）；20 个 `pyproject.toml` 构建后端归一（F-096）。
- 一致性债残存：`requires-python` 不一致（xuan-compose `>=3.14` vs 其余 `>=3.14.6`，F-082、F-085）——**反例证据**：说明未在同一窗口内闭环即留债。
- 目录约定对齐：`docs/` → `doc/` 规避第三方路径约定冲突（F-019、F-059）。
- 自动核验雏形：`doctor` 子模块指针检查与 Sphinx 路径检查（F-047、F-048、F-060）。
- 文档形态对齐：对等文档原子化为十文件（F-050 ~ F-052）。

## 二、去重裁决（查证后裁定，三选一）

### 2.1 候选 A「上游怪癖分级固化」→ 裁定：**并入既有**（不新建）

**裁决依据（既有文档正文引文）**：`behavior-characterization-freeze.md` 已完整包含候选 A 的核心机制：

- `behavior-characterization-freeze.md:72` 标题即 `## 固化强度分级（L0-L3）`；
- `behavior-characterization-freeze.md:80-82` 逐级定义 `L0 精确断言` / `L1 弱断言` / `L2 注释固化` / `L3 清单固化`（与候选 A 四级口径逐字对应）；
- `behavior-characterization-freeze.md:85-86` 记录 "源案例 2026-10-10 已完成一次 L1→L0 升级"（即 F-115）；
- `behavior-characterization-freeze.md:67` 反模式含 "怪行为同时命名登记台账（位点、触发条件、保留依据、标注'怪癖非设计契约'）"；`behavior-characterization-freeze.md:110` 检验标准含 "台账含位点、触发条件与'怪癖非契约'标注"。

即：**怪癖台账 + L0-L3 分级 + 四级定义 + 台账登记纪律**均已在该模式中显式存在，候选 A 无不可替代的新机制。

**并入要点（应补充的差异点，V-1 校正：严格限于 3 条，避免既有文档膨胀）**：

1. 明确台账载体已落地为具体文件（`libs/xuan-compose/docs/parity/upstream-quirks.md`，F-114），并增设"上游同步时强制复核台账条目新增/升级/失效"的门禁（对应 F-110）；
2. 补充"分级应从单文件约定上升为仓库级规范"的演进建议（对应 I-3 建议 1）；
3. 补充一条与本复盘交织的检验标准：上游同步类 spec 须输出台账 diff 复核结论。

**不新建的理由**：若就候选 A 新建 L1，将产生与 `behavior-characterization-freeze.md` 大面积重复的两份模式文档（L0-L3 四级定义、台账登记纪律逐字重叠），违背模式库去重原则；差异点总量可用 3 条以内补充表达，不足以独立成篇。

### 2.2 候选 B「迁入即治理检查单」→ 裁定：**新建 L1**

**裁决依据（既有文档正文比对）**：逐一核查下列既有模式，均未覆盖候选 B 的核心机制——

| 既有模式 | 关注点 | 与候选 B 的差异 |
|---|---|---|
| `convention-driven-creation.md`（`convention-driven-creation.md:9-17`） | 在成熟体系内**新建**模块时"先读范例、提取模板" | 管的是"创建新模块"，非"迁入外部包时的结构对齐" |
| `structure-first-extension.md`（`structure-first-extension.md:17-21`） | 扩展时判断"追加到现有文件 vs 新建独立模块" | 文件级归属决策，非包级约定对齐 |
| `dependency-ordered-slice-gates.md`（`dependency-ordered-slice-gates.md:33-54`） | 单体拆包沿依赖逆拓扑序切片 | 管"切片顺序与片门禁"，不含"公共约定对齐检查单" |
| `snapshot-parity-migration.md`（`snapshot-parity-migration.md:41-53`） | 以快照对拍证明与上游**逐字段对等** | 管"对等性证明"，非"迁入触发的结构一致性对齐" |
| `dual-track-progressive-evolution.md`（`dual-track-progressive-evolution.md:29-34,73`） | 依赖成熟度渐进切换；检验标准含"仓库骨架先行统一" | **最接近**，但其机制是"依赖就绪度切换轨道"，"构建后端先行统一"仅作检验标准一句带过，未展开操作闭环 |
| `vendor-lifecycle-governance.md`（`vendor-lifecycle-governance.md:18-42`） | 第三方 API/服务全生命周期 | 服务供应商治理，非代码包迁入的结构对齐 |
| `three-tier-governance.md`（`three-tier-governance.md:32-48`） | 文档治理"原子化→自动化→验证" | 候选 B 第 3 步与其第三层同源，但对象是**迁移窗口的一次性约定对齐**，非文档治理三层 |
| `technical-debt-workaround-tracking.md`、`no-touch-list.md`、`dual-env-drift-reconciliation.md`、`docs-as-product.md` | 债务追踪 / 边界 / 双实例漂移 / 文档产品化 | 均不同域，无覆盖 |

**结论**：候选 B 的核心机制——"外部单体迁入统一仓库时，同一窗口内完成私有约定→公共约束的对齐，并纳入自动核验"——在既有模式库中无等价覆盖。**判"新建 L1"**。

### 2.3 新建 L1 的 frontmatter 草案（供 Task 5 使用）

```yaml
---
type: Pattern
id: "migration-triggered-convention-alignment"
title: "迁移窗口的结构约定对齐法（迁入即治理）"
source: "../../../reports/project-reports/retrospective-xuanspace-comprehensive-20261010/insight-extraction.md#I-2"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "convention-driven-creation"
  - "dual-track-progressive-evolution"
  - "three-tier-governance"
  - "dependency-ordered-slice-gates"
  - "snapshot-parity-migration"
tags:
  - migration
  - monorepo
  - convention-alignment
  - consistency-governance
---
```

**说明**：

- `source` 指向本次复盘报告（Task 4 产出）；底层证据为 `insights.md#I-2` 与 `facts.md` 的 F-037~F-044、F-082、F-096、F-107、F-112。若 Task 5 实施时报告尚未落盘，可临时改指 `.trae/specs/.../insights.md#I-2`，报告落盘后回填。

**伴生 TOML 落点与建议字段**（本仓库实际约定：伴生 TOML **不在** `docs/` 子树内）：

- 落点：`d:\AI\.meta\toml\docs\retrospective\patterns\methodology-patterns\governance-strategy\migration-triggered-convention-alignment.toml`
- 字段（参照 `behavior-characterization-freeze.toml` / `snapshot-parity-migration.toml` 现有约定）：

```toml
id = "migration-triggered-convention-alignment"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/patterns/methodology-patterns/governance-strategy/migration-triggered-convention-alignment.md"

[bindings]
rules = []
references = ["convention-driven-creation", "dual-track-progressive-evolution", "three-tier-governance", "dependency-ordered-slice-gates", "snapshot-parity-migration"]
skills = []
```

**toctree 登记落点**（Task 5 执行）：

- `governance-strategy/index.md` 的 toctree（字母序）中插入 `migration-triggered-convention-alignment`，位置在 `methodology-reflexivity-test` 与 `milestone-breakthrough-assetization-process` 之间（`mig` < `mil`）。
- `governance-strategy/README.md` 的 `<!-- README_INDEX_START -->` 区块由 `generate-readme.py` 自动生成，**不得手动编辑**，任务完成后运行生成器刷新。

## 三、G3 门判定表

| 候选 | 触发场景 | 核心步骤 | 反模式 | 迁移验证 | 可迁移到非当前场景 | 判定 |
|---|:---:|:---:|:---:|:---:|---|---|
| 候选 A 上游怪癖分级固化 | ✅ | ✅ | ✅ | ✅ | ✅（法律修订/财务系统替换） | 四要素齐备，但**机制已被 `behavior-characterization-freeze` 覆盖** → 并入既有，不单独过门 |
| 候选 B 迁移窗口的结构约定对齐法 | ✅（§1.1） | ✅（§1.2，5 步） | ✅（§1.3，5 条） | ✅（§1.4，3 个可判定信号） | ✅ 见下 | **G3 PASS（新建 L1）** |

**候选 B 的非当前场景迁移验证**：

- **组织/职能整合**：两个团队合并进统一工程体系时，在同一整合窗口内对齐代码规范、构建口径、版本发布口径与文档形态，并将可机械判定项纳入统一检查（CI/门禁）。
- **数据仓库多源接入**：多个上游数据集接入统一数仓时，在同一接入窗口内对齐分区命名、字段类型口径、时间粒度与元数据登记。
- **前端多包仓库引入新组件库**：组件库迁入 monorepo 时，在同一窗口内对齐构建配置、TypeScript 版本约束、包版本来源与文档形态。

**G3 结论**：候选 B 四要素齐备且可迁移到组织整合、数仓接入、前端 monorepo 三个非当前场景 → **通过 G3 门**；候选 A 并入既有模式，不新增文档。

## 四、上游输入限定与 V 阶段衔接

### 4.1 上游洞察限定（V-6 校正，须带入 Task 4 报告）

V-6 质疑 I-1 将增量"多段脉冲"节奏归因于"协作模型缺少 standing backlog"是否为**过度归因**，并提出竞争假设：项目可能已进入维护期，可执行工作量本身下降。经复核——I-1 的核心证据（全量峰值 F-007 与增量峰值 F-063 的**同构性**、全量 89.4% 提交集中于 08-25 前 F-011）**支持**"同一协作模型贯穿两期"的解释，但**无法排除**"维护期工作量下降"这一竞争假设（facts.md 未采集"可执行工作量"类事实）。

**处理**：本复盘**不修改** `insights.md`（其已声明只读引用 `facts.md`）；改为将该限定作为**报告限定说明**带入 Task 4：I-1 的系统性根因应表述为"与现有事实一致的一种解释"，并显式标注竞争假设与"缺可执行工作量事实"这一证据缺口。本文件为 E 阶段产物，仅记录该限定，不越界改写 I 阶段结论。

### 4.2 与 V 阶段的衔接

本文件是 V 阶段对抗审查的输入；V 阶段采纳意见对 `e-stage-pattern.md` 的 5 处修正已在文中以"（V-x 校正）"就地标注（V-1 §2.1、V-2 §1.2、V-3 §1.4、V-5 §1.4、V-6 §4.1），逐条修正痕迹与不采纳理由见 `v-adversarial-review.md`。