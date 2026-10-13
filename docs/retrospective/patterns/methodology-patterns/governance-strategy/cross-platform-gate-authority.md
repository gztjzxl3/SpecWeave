---
type: Pattern
id: "cross-platform-gate-authority"
source: "../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/patterns/2026-09-16-refactor-patterns.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/cross-platform-gate-authority.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "template-cross-platform-validation"
  - "dual-mode-submodule-governance"
  - "orchestration-execution-layering"
tags:
  - cross-platform
  - quality-gate
  - authority
  - crlf
---
# 跨平台门禁权威分工法

## 模式类型

方法论模式 → 治理策略（多平台开发环境的门禁归属）

## 成熟度

L1（单案例：xuan-compose Windows 主机 + WSL 双环境，2026-09-16）。
跨项目验证缺失前标 L1。

## 一句话

多平台混合开发时，按"**检查类型 × 平台语义匹配度**"为每类门禁指定**唯一权威
平台**：POSIX 语义测试与上游 CI 对齐（WSL），lint/类型归工具链稳定的平台
（Windows）；平台原生失败登记差异而非强改代码。

## 适用场景

**适用于：**

- 在 Windows 主机开发含大量 POSIX 假设（路径、信号、权限、shell）的项目；
- 团队跨操作系统协作，同一仓库在多环境执行检查；
- 需要对"哪个环境的结果说了算"给出无歧义裁决。

**不适用于：**

- 检查已全部由容器化/CI 在统一环境执行——环境本身即权威，无需分工；
- 平台间无语义差异的检查（如纯 AST 规则），任一平台均可；
- 项目只在单一操作系统构建与运行。

## 核心做法（6 步）

1. **清点检查项及语义前提**：列出全部门禁（语义测试、lint、类型、构建等）及其
   依赖的平台前提（POSIX 路径与信号、文件编码、工具链版本）。
2. **指定唯一权威平台**：语义匹配度为第一原则——行为语义测试与上游 CI 环境对齐；
   lint/类型检查选择工具链最稳定、团队最易复现的平台。一类检查只有一个权威，
   避免双权威冲突。
3. **非权威结果只作参考**：非权威平台的失败不直接判红；登记为平台差异，注明
   权威出处与判定理由。
4. **差异不强改**：不为让原生 Windows 通过而改写 POSIX 假设或塞入平台条件分支；
   平台适配如确有必要，另立变更并在权威平台复测。
5. **行尾翻转处置**：检出操作导致整树出现 CRLF 翻转时，先以
   `git diff --ignore-cr-at-eol` 取证；判定为零语义差异即 restore，不提交、不评审。
6. **权威结论文档化**：复现命令按平台分组，记录"权威/参考"归属；环境或工具链
   变更时重新评估匹配度。

## 反模式

- ❌ **两个平台都设权威**：结论冲突时无裁决依据，开发者择利而从。
- ❌ **在语义不匹配的平台强红**：POSIX 路径假设失败被当作产品缺陷。
- ❌ **为跨平台全绿污染代码**：大量 `if os.name` 分支进入核心逻辑。
- ❌ **CRLF 整树翻转直接提交**：评审被行尾噪音淹没，真实差异不可见。
- ❌ **权威归属只存在于口头**：新成员/CI 无法复现裁决。

## 与模板跨平台验证的区别

| 维度 | template-cross-platform-validation | 本模式 |
|---|---|---|
| 关注问题 | 产物/模板在多个目标平台**都要可用**（矩阵验证） | 同一套检查**在哪里算数**（权威分工） |
| 典型动作 | 多平台矩阵全覆盖 | 检查类型与平台语义匹配、唯一归属 |
| 对差异 | 逐平台修复 | 登记差异，不强改 |

## 检验标准

- 每类门禁有唯一权威平台，归属理由可由语义前提推出；
- 非权威平台失败均有差异登记与权威出处；
- 核心代码中无为本机平台通过而新增的条件分支（或另有独立变更记录）；
- 行尾翻转未进入提交历史；
- 文档含按平台分组的复现命令。

## 迁移示例

- **跨国/跨辖区合规**：同一制度在多辖区执行时，按事项类型指定主辖区为解释与
  验收权威，他辖区差异登记口径，不各自修改制度文本。
- **多实验室质检**：检测项按设备与标准匹配度归至权威实验室，其他实验室结果作
  参考，方法差异登记。
- **待验证方向**：混合架构团队（x86/ARM）的门禁分工。

## 失效条件与演进

- 容器化、远程统一 CI 普及后，平台语义差异被环境封装吸收，本模式退化为"环境即
  权威"，仅保留行尾纪律；
- 项目正式声明多平台为一等目标时，转用
  [template-cross-platform-validation](template-cross-platform-validation.md) 的矩阵思路；
- 出现跨项目验证案例后可升 L2。

## 参考实现与关联

- 源案例：[单体重构可复用模式六则](../../../../../projects/xuanspace/libs/xuan-compose/doc/dev/patterns/2026-09-16-refactor-patterns.md)；
- 多平台矩阵：[template-cross-platform-validation](template-cross-platform-validation.md)；
- 子模块纪律配套：[dual-mode-submodule-governance](dual-mode-submodule-governance.md)；
- 执行分工：[orchestration-execution-layering](orchestration-execution-layering.md)。
