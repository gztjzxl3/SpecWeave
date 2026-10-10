---
type: Pattern
id: "fp-multi-dimensional-falsification"
source: "../../../../../projects/xuanspace/libs/xuan-compose/docs/verification/2026-09-16-full-parity-verification.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/fp-multi-dimensional-falsification.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "snapshot-parity-migration"
  - "spec-stage7-independent-validation"
  - "knowledge-crystallization-second-validation-sop"
  - "batched-creation-independent-review"
  - "quality-assurance-three-layer-model"
  - "format-evidence-over-memory-pattern"
tags:
  - first-principles
  - falsification
  - completeness
  - acceptance
  - independent-verification
---
# 第一性原理多维证伪验收法

## 模式类型

方法论模式 → 治理策略（完备性主张的独立终验）

## 成熟度

L1（单案例：xuan-compose 交付后独立复验，2026-09-16）。
源案例含七维证据、5 攻击者四路并行与 1 轮回归对抗；跨项目验证缺失前标 L1。

## 一句话

终验"功能全集已交付"类主张时，先质疑验收维度本身是否充分：用第一性原理从
**用户可观察行为**倒推完备性标尺，再以静态穷尽对拍、运行时活体对拍、分发面干净
环境实证三类证据逐维证伪；差异按可达性定级。结论表述为"未发现丢失"，而非
"证明无丢失"。

## 适用场景

**适用于：**

- 翻译式搬迁、fork 合并、平台迁移后，需要对"无静默丢失"给出独立终验结论；
- 现有验收只有单维指标（测试数、名称映射率、覆盖率）且全绿，但主张覆盖"功能全集"；
- 交付方自审之外，需要 fresh-context 的第三方对利益相关者负责；
- 遗留系统替换的割接前验收。

**不适用于：**

- 低风险小改动、纯增量补丁——常规验收即可，多维证伪属过度工程；
- 验收标准已在多个项目被证伪检验、维度稳定的成熟场景——直接按既有 checklist 执行
  （参见 [spec-stage7-independent-validation](../ai-collaboration/spec-stage7-independent-validation.md)）；
- 纯创意类产出，"完备"无客观边界；
- 无法获得独立评审者时——独立性是本模式的前置条件，缺失则降级为普通对抗审查。

## 问题背景

单维全绿提供的是虚假安全感：名称全集只回答"叫得出的都在"，不回答私有逻辑、分派
归宿、字面量、断言强度与可安装性。验收维度若由交付方自定，还会系统性回避其实现
中的薄弱面。多维证伪以"先重建标尺、再攻击主张"的顺序同时处理这两类盲区。

## 核心做法（8 步）

1. **冻结主张与基线**：明确被验收的主张原文、pinned 基线与范围；声明独立复验，
   不引用交付期自审结论；全程只读，构建实证放临时目录，仓库零残留。
2. **F 重建标尺**：从"用户沿哪些公开路径能观察到什么行为"倒推功能全集，
   列出维度清单并为每维指定攻击方式与通过标准。维度选择原则是穷尽用户可观察面；
   源案例的七栏（公开符号 / 含私有顶层函数 / 逐类方法 / CLI 活体分派 / 常量字面量 /
   函数体忠实度与断言强度 / 动态机制与打包面）仅作示例，不是固定清单。
3. **静态穷尽对拍**：以两侧并集机械枚举（AST、正则、字面量差分等），输出
   "缺失/多余/差异"三列；机器告警逐一人工证伪并留痕（如转义假象、f-string 合并
   假象），未解释差异必须归零。**工具无关**：无 AST 工具时，以编号表格人工穷尽
   枚举同样有效，机械对拍是手段不是前提。
4. **运行时活体对拍**：不信快照，解开闭包与注册机制，沿真实入口验证分派归宿、
   配对关系、退出码与副作用；用注入桩（如返回码 42 的 handler）验证透传。
5. **假绿排查**：核对 skip/xfail/空体 mock 的数量；确认断言落在可观察结果
   （真实命令行、退出码、输出文本），而非仅断言"被调用过"。
6. **差异按可达性定级**（见下节）。
7. **分发面干净环境实证**：在隔离环境从源码做标准构建（如 PEP 517 wheel/sdist），
   核对产物标签、内容清单、入口脚本与声明依赖；本机预装工具造成的"能构建"不作数。
8. **修复实证与回归**：验收中修复的问题须同轮实证；跑完修复前同一套门禁，确认
   主指标与基线一致；产出含复现命令的报告，差异全部进入台账。

### 关键子规则：可达性定级

- 定级前先回答："**用户走哪条公开路径能观察到这个差异？**"
- 存在公开可观测路径：按影响范围与后果定 P0/P1；
- 在所有公开入口不可达（死分支、不可满足前提）：降为登记项，注明不可达证据，
  不夸大严重性；
- 可达性结论随代码变更可能失效，登记时注明前提，后续改动触发复核。

## 反模式（均来自实际教训）

- ❌ **名称全绿即宣告完备**：私有符号、分派链、字面量与断言强度均未被覆盖。
- ❌ **静态可疑直接定高级**：不查可达路径，最强"嫌疑"可能在真实入口完全不可达。
- ❌ **运行时对等等同可分发**：平台钉死产物、未声明构建依赖等发布缺陷只能靠干净
  环境构建实证发现，代码审查不可见。
- ❌ **复用交付方自审结论**：共享上下文产生共享误解，独立性即证据力。
- ❌ **以快照代替活体**：快照证明"结构一致"，不证明"运行时真的走那条路"。
- ❌ **为让结论好看排除告警维度**：豁免须显式、有依据并登记。
- ❌ **表述"已证明无丢失"**：证伪只能支撑"按既定标尺未发现丢失"，过度断言透支信任。
- ❌ **验收修复不留回归证据**：修复可能改变主指标，须与修复前基线对拍。

## 检验标准

- 标尺在对拍之前重建，维度可追溯到"用户可观察行为"，每维有攻击方式与通过标准；
- 静态差异三列齐备，机器告警全部有证伪结论，未解释差异为 0；
- 至少一条活体证据沿真实入口产生；skip/xfail/空体 mock 已清点；
- 每个定级差异有可达性论证；不可达项有证据并登记；
- 分发面在隔离环境构建成功，产物标签与内容清单经核对；
- 报告含复现命令；总结论使用证伪式表述。

## 迁移示例

- **法规/制度改版（非软件领域）**：条款名称全集不等于义务全集——须核对每条义务的
  执法触发路径、文书字面表述与生效范围；差异按"相对人或执法者沿哪条公开程序能
  触发"定级；"发布可用"另需验证公报、归档与检索渠道。
- **数据平台割接**：表名列名全映射之外，须做视图/存储过程逐对象对拍、抽样活体
  查询、报表固定数值差分；下游消费链路用干净环境重放，验证"可接入"。
- **组织流程移交**：岗位名单全在之外，沿真实业务单据走端到端签批链，核对表单
  模板字面量与系统权限，差异以"哪类业务、哪个角色能观察到"定级。
- **待验证方向**：教学大纲改版、会计科目体系切换。

## 失效条件与演进

- 被验收对象的"可观察面"本身无法穷举（如开放生成式行为）时，标尺不成立，应改用
  基于性质/抽样的验收；
- 标尺在同类项目中被反复验证后，维度可固化为标准 checklist，本模式退化为常规
  独立验证，避免重复支付标尺重建成本；
- 单维对拍的自动化实现可复用 [snapshot-parity-migration](snapshot-parity-migration.md)；
- 出现跨项目验证案例后可升 L2。

## 参考实现与关联

- 源案例：[独立验证报告](../../../../../projects/xuanspace/libs/xuan-compose/docs/verification/2026-09-16-full-parity-verification.md)；
- 执行工具：单维对拍用 [snapshot-parity-migration](snapshot-parity-migration.md)
  及其技能 vendor-snapshot-parity；
- checklist 已固化时走 [spec-stage7-independent-validation](../ai-collaboration/spec-stage7-independent-validation.md)；
- 对已入库知识产物的复审走
  [knowledge-crystallization-second-validation-sop](knowledge-crystallization-second-validation-sop.md)；
- 独立性原则见 [batched-creation-independent-review](../ai-collaboration/batched-creation-independent-review.md)；
- 质量体系分工上位模式：[quality-assurance-three-layer-model](quality-assurance-three-layer-model.md)、
  [format-evidence-over-memory-pattern](format-evidence-over-memory-pattern.md)。
