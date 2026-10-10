---
type: Pattern
id: "behavior-characterization-freeze"
source: "../../../../../projects/xuanspace/libs/xuan-compose/docs/patterns/2026-09-16-refactor-patterns.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/behavior-characterization-freeze.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "no-touch-list"
  - "snapshot-parity-migration"
  - "fp-multi-dimensional-falsification"
  - "error-blacklist-monotonic-evolution"
tags:
  - characterization-testing
  - behavior-lock
  - legacy
  - refactoring
---
# 行为取证固化测试法

## 模式类型

方法论模式 → 治理策略（行为基线的建立与保护）

## 成熟度

L1（单案例：xuan-compose 翻译搬迁中 10+ 次怪癖纠正，2026-09-16）。
跨项目验证缺失前标 L1。

## 一句话

实际行为与"合理预期"冲突时，先怀疑测试、回代码取证；确认是真实行为后，
按真实输出写断言（特征测试）并登记台账——以测试固化"**是什么**"，不以
"**应该是什么**"改代码。

## 术语：特征测试（characterization test）

刻画系统**当前实际行为**、用于保护该行为不被意外改变的测试。断言对象是沿真实
入口观察到的具体输出（结果、退出码、副作用），而非规格、文档或直觉；它不回答
"对不对"，只回答"变没变"。

## 适用场景

**适用于：**

- 翻译式搬迁中遭遇上游怪癖，需要既保持对等又让怪癖可解释；
- 为无文档、无测试的遗留系统重构前补行为安全网；
- 跨版本迁移时锁定历史数据/单据的真实计算结果。

**不适用于：**

- 该行为是已确认缺陷、且本次任务目标就是修复它——修复后断言新行为，旧行为留作
  历史记录即可；
- 行为无法稳定复现（并发/时序/外部依赖）——先消除不确定性或用受控桩复现；
- 纯文档勘误类任务。

## 核心做法（5 步）

1. **冲突出现，先假设测试错**：不以直觉改生产代码，回到源代码沿**真实入口**取证，
   确认行为位点与触发条件。
2. **最小复现**：构造最小输入确认实际输出（源案例示例：`1m:30s` 非法、
   sub_dir 不剥 `./`、`--service-ports` 删端口后重建、bytes 被 is_list 判真、
   OverrideTag scalar 无类型解析等）。
3. **按真实输出写特征断言**：断言具体值（结果文本、退出码、命令行内容），
   禁止只断言"不抛异常"；怪行为同时命名登记台账（位点、触发条件、保留依据、
   标注"怪癖非设计契约"）。
4. **随片固化**：对等迁移中怪癖测试随对应切片移植，成为片门禁的一部分。
5. **修复分流**：若决定改变该行为，另立"偏离对等"变更与提交，与固化测试不在
   同一变更；先更新验收标准，再改代码。

## 反模式

- ❌ **为让断言符合直觉而改生产代码**：在对等迁移中即制造不对等；在遗留重构中
  可能改变大量历史数据的语义。
- ❌ **把怪癖当设计契约**：不标注、不登记，后续开发者据怪癖构建新逻辑。
- ❌ **断言空心化**：只验证"调用过/不报错"，行为改变时测试照样绿。
- ❌ **反复取证不留台账**：同一怪癖被多个会话重新发现、重新争论。
- ❌ **固化与修复混入一个提交**：无法独立审查、独立回滚。

## 与错误黑名单模式的区别

| 维度 | error-blacklist-monotonic-evolution | 本模式 |
|---|---|---|
| 固化对象 | 本系统曾犯、被人工拒绝的错误 case | 外部/遗留系统**现存**的真实（含怪癖）行为 |
| 目的 | 防止重犯已知错误 | 防止行为在不知情下被改变 |
| 断言立场 | 错误输出**不应**再出现 | 真实输出**确实**是这个值 |

## 检验标准

- 每个固化测试可由最小输入独立复现；
- 断言落在具体可观察输出，测试在行为改变时会变红；
- 台账含位点、触发条件与"怪癖非契约"标注；
- 对等迁移中，上游怪癖逐一可在测试与台账中双向查到。

## 迁移示例

- **法律修订**：修订前先以真实案例固化现行执行口径（即使口径间有张力），修订
  草案再针对被固化的具体行为逐条改动；新旧口径差异可审计。
- **财务系统替换**：以历史单据的真实计算结果（含历史规则怪癖）建立特征测试，
  新系统平行试算对拍；旧规则怪癖登记，不视为新系统设计。
- **待验证方向**：医疗诊疗流程数字化、海关申报系统升级。

## 失效条件与演进

- 取证依赖的真实入口消失（外部系统停服、数据不可达）时，固化测试只能基于存档
  输入维持，需注明证据级别；
- 怪癖被正式修复后，对应特征测试转为"修复确认测试"，台账条目标记关闭；
- 出现跨项目验证案例后可升 L2。

## 参考实现与关联

- 源案例：[单体重构可复用模式六则](../../../../../projects/xuanspace/libs/xuan-compose/docs/patterns/2026-09-16-refactor-patterns.md)；
- 边界纪律上位模式：[no-touch-list](no-touch-list.md)；
- 结构对等对拍：[snapshot-parity-migration](snapshot-parity-migration.md)；
- 多维终验：[fp-multi-dimensional-falsification](fp-multi-dimensional-falsification.md)；
- 防错近亲：[error-blacklist-monotonic-evolution](../ai-collaboration/error-blacklist-monotonic-evolution.md)。
