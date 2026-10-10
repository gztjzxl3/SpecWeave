---
id: wsl-vhdx-compact-cmd-retrospective-20261010
title: WSL2 VHDX 压缩 skill 门面里程碑复盘报告（2026-10-10）
date: 2026-10-10
type: retrospective
source: 七概念方法论 R→I→E→V→A→C（场景1·里程碑复盘，standard）
category: milestone
maturity: L1
tags: [方法论, 七概念, 里程碑复盘, WSL, VHDX, 脚本门面, 验收闭环]
---

# WSL2 VHDX 压缩 skill 门面里程碑复盘报告

> **周期**：2026-10-09 交付 → 2026-10-10 复测 | **方法**：七概念 R→I→E→V→A→C（场景1 里程碑复盘，depth=standard）| **对象**：`wsl-vhdx-compact-cmd` 门面（commit `83ab7cafa`）| **数据**：git 实测 + 文件实测 + 宿主 Win32_LogicalDisk 复测

---

## 一、事实（R · 复盘 · 纯客观，无判断词）

### 1.1 交付物（git 实测 `83ab7cafa`）

| 项 | 数值 | 验证方式 |
|------|------|---------|
| 提交哈希 | `83ab7cafa310cf4da409404f6fbafa08e2fcdf5d` | `git show` |
| 提交时间 | 2026-10-09 13:44:05 +0800 | `git show --format=%ad` |
| 作者 | xinzo `<xinzo@trae.cn>` | `git log` |
| 变更规模 | 4 文件，+690 / −2 行 | `git show --numstat` |
| 新增 skill | `.agents/skills/wsl-vhdx-compact-cmd/SKILL.md`（243 行） | 行数实测 |
| 新增脚本 | `.agents/scripts/compact-vhdx-with-baseline.ps1`（443 行，20116 字节，LastWrite 2026-10-09 12:14） | 文件实测 |
| 索引变更 | `.agents/capability-registry/02-skills.md` +2/−1；`.agents/skills/README.md` +2/−1 | `git show` |
| 复用脚本 | `.agents/scripts/compress-wsl-vhdx.ps1`（9899 字节，LastWrite 2026-08-03 12:27） | 文件实测 |

### 1.2 脚本结构（源文件实测）

- 声明 `#Requires -Version 7.4`。
- 输出对象含 10 字段：`BeforeVhdxGiB / AfterVhdxGiB / SavedVhdxGiB / BeforeFreeGiB / AfterFreeGiB / DeltaHostFreeGiB / FstrimSummary / OriginalStates / DegradedToAdminScript / ExitCode`。
- `private` 函数 7 个：`GiB / Write-Step / Write-Warn / Write-Err / Write-JsonOutIfNeeded / Get-WslStates / Infer-VhdxPath`。
- `ExitCode` 取值分支 5 处：`2 / 3 / 4 / 0 / 1`。
- 步骤标记 `'6/8 原生 wsl --manage --compact'`，脚本为主线 8 步闭环。
- 降级命令由 `DegradedToAdminScript` 字段构造输出。
- 恢复路径：podman → `podman machine start`（记录 ExitCode）；其他发行版 → `wsl -d <name> echo ready`（记录 ExitCode）。

### 1.3 技能文档要素（SKILL.md 实测）

- 方案数 2：方案A 原生 `wsl --manage --compact`（默认）；方案B 管理员 `compress-wsl-vhdx.ps1`（降级）。
- 8 步原子流程（§7.2 表格）。
- 输入参数 8 个：`Distro / VhdxPath / Mounts / DriveLetter / BaselineOnly / SkipFstrim / RestoreOriginalState / RestorePodman`。
- §12 Gotchas 共 12 条（Gotcha 1–8 归入 4 类：宿主-内层差值 / 状态恢复 / 工具使用 / 领域特定）。
- §11 常见错误 `COMPACT_001`–`COMPACT_007` 共 7 条。
- §14 长期演进方向 4 项；§15 Changelog 记 `v1.0.0`（2026-10-09）。
- 声明 `PCMClawUbuntu` 永久黑名单；声明姊妹技能 `wsl-ops-cmd` 的职责边界。

### 1.4 实战数据（源自 SKILL 文本与提交正文）

| 对象 | Before VHDX | After VHDX | Saved | 宿主 Win32 FreeGiB |
|------|------------|-----------|-------|-------------------|
| podman-machine-default | 79.02 GiB | 33.01 GiB | ≈46.01 GiB | 0.45 → 46.48（Delta ≈46.03）|
| openKylin-3.0-desktop | 48.84 GiB | 48.21 GiB | ≈0.66 GiB | — |
| 实战计数 | 提交正文与 §15 表述为"3 次实战"，仅 2 组 Before/After 数值 | — | — | — |

- 方案A/方案B 依赖声明：WSL 2.0.14+；方案B 需管理员 pwsh 7.4+。

### 1.5 今日复测（2026-10-10 本会话实测）

| 项 | 实测值 | 命令 |
|----|--------|------|
| `D:\WSL\podman-machine-default\ext4.vhdx` | 33.02 GiB，LastWrite 2026-10-10 10:16:09 | `Get-Item ... -Force` |
| `D:\WSL\openKylin-3.0-desktop\ext4.vhdx` | 48.40 GiB，LastWrite 2026-10-09 13:36:50 | 同上 |
| D: 盘 FreeSpace | 50.33 GiB | `Win32_LogicalDisk` |
| `wsl --version` 输出 | UTF-16 编码，控制台出现 `�` 与 `\x00` 交错字符 | 直接执行 |

### 1.6 一致性事项（本会话实测）

- SKILL.md frontmatter `x-toml-ref` 指向 `.meta/toml/.agents/skills/wsl-vhdx-compact-cmd/SKILL.toml`；`Test-Path` = **False**（文件不存在）。
- 姊妹技能 `jpman-podman-ops / wsl-ops-cmd / atomic-commit-cmd / artifact-consistency-audit` 的 `SKILL.toml` 均存在（`Test-Path` = True）。
- 门面计数在两个索引文件中同步由 12 改为 13。
- 提交正文为 UTF-8 中文，含 4 条前置规则与"Before/After/Saved + 宿主 FreeGiB 闭环"验收声明。

> 事实计数：**30 条**（1.1=8、1.2=7、1.3=6、1.4=3、1.5=4、1.6=4，去重后口径见各表行数）。

---

## 二、洞察（I · 四元组）

### 洞察 1：写操作门面应把"预期收益"前置为只读基线

- **陈述**：把"油水"量级用只读基线在写操作之前摊开，比事后解释收益落差更能守住用户预期。
- **证据**：`F-1.4`（openKylin 48.84→48.21 仅 0.66 GiB）；`F-1.3`（SKILL §4 明确 `BaselineOnly` 为默认第一道闸）；`F-1.2`（脚本含 `-BaselineOnly` 只读分支）。
- **反常识**：默认心智是"压缩=大释放"；当 `df Used ≈ VHDX Length` 时收益实际落在 GiB 级，期望差可达 10 倍以上。
- **行动**：凡"写操作型"门面，默认提供只读 dry-run 基线模式，并把预期收益写进输出。

### 洞察 2：验收判据必须锚定在被操系统之外的独立权威量

- **陈述**：只信"操作返回值 + 外部权威量变化"，把被工具自身的文本输出降级为不可解析，是跨工具可靠验收的关键。
- **证据**：`F-1.5`（`wsl --version` 实测 UTF-16 乱码）；`F-1.3`（`COMPACT_001` 规定乱码但 ExitCode=0 时忽略 stdout）；`F-1.2`（脚本注释"只信数值 + ExitCode；绝不解析 wsl.exe 的 UTF-16 stdout"）。
- **反常识**：常规做法把"执行成功/退出 0"当作完成；本门面把文本输出主动排除在判据之外。
- **行动**：门面验收统一定义"双独立证据"，并禁止对被操工具的本地化/编码文本做解析。

### 洞察 3：带全局副作用的命令必须"原态快照 + 幂等恢复"

- **陈述**：凡是会顺带影响非目标对象的操作，都必须快照原态并在收尾按原态恢复。
- **证据**：`F-1.3`（Gotcha 3 记 `wsl --shutdown` 为全局命令）；`F-1.2`（`OriginalStates` 字段 + `podman machine start` 幂等恢复）；`F-1.3`（`RestoreOriginalState/RestorePodman` 开关）。
- **反常识**：命令名 `wsl --shutdown` 不显式带对象，易被当作"只关目标发行版"。
- **行动**：对共享/全局资源操作，默认实现"快照→执行→按原态幂等恢复"三段式。

---

## 三、对抗审查（V · 四视角）

| # | 视角 | 攻击点 | 处置 |
|---|------|--------|------|
| V1 | 魔鬼代言人 | "3 次实战"仅给出 2 组可核验 Before/After（podman/openKylin），第 3 次缺数据 | **采纳** → 行动 A-3 |
| V2 | 魔鬼代言人 | "双基线闭环为唯一验收"与 `COMPACT_004` 承认其他进程可致 >1 GiB 偏差之间存在口径张力 | 记录，暂不改判据（符号+量级一致已覆盖）|
| V3 | 新人视角 | 触发词 20+ 但缺少"最小可跑示例"（一次 `-BaselineOnly` 的输入/输出样例） | **采纳** → 行动 A-5 |
| V4 | 新人视角 | `SKILL.toml` 缺失（`x-toml-ref` 断链），工具链消费方读不到元数据 | **采纳** → 行动 A-1 |
| V5 | 老板视角 | `PCMClawUbuntu` 黑名单仅写在 Gotcha 文档，脚本参数校验未硬 ABORT（§14 长期4 自述） | **采纳** → 行动 A-2 |
| V6 | 老板视角 | 方案B 复用 `compress-wsl-vhdx.ps1` 需管理员权限，其输出无 FreeGiB 闭环，需人工回填 | 记录，纳入后续批量模式需求 |
| V7 | 未来视角 | 443 行脚本无测试，无 CI 守护（§14 长期1 自述） | **采纳** → 行动 A-4 |
| V8 | 未来视角 | 与 `wsl-ops-cmd` 的边界靠文档约定，未机制化，存在漂移风险 | 记录为长期观察项 |

> V 门：意见 **8 条**（≥5），采纳 **4 条**（V1/V3/V4/V5），满足"≥5 条且采纳 ≥2"。

---

## 四、模式萃取（E · 可迁移模式，L1）

### 模式候选：写操作门面三基线验收法（baseline-gated destructive façade）

- **触发场景**：适用于需要执行会改变系统/磁盘/全局状态的命令（压缩、清理、迁移、批量改写）且结果需可验证的任务；不适用于纯读操作或不可回滚的一次性动作。
- **核心步骤**：
  1. 先做只读基线（外部权威量，如宿主盘 FreeSpace + 目标文件精确长度），并向用户展示预期收益；
  2. 定义双独立证据（操作返回值 + 外部权威量变化），禁用被操对象的文本输出作判据；
  3. 若操作有全局副作用，快照受影响对象原态；
  4. 执行操作；
  5. 用同口径复测基线；
  6. 按原态幂等恢复；
  7. 输出结构化结果对象（可管道 JSON），供下游聚合。
- **反模式（≥3）**：
  1. 只信"执行成功/退出 0"就收工，不做外部权威量复测；
  2. 解析被操工具的本地化/编码文本（如 UTF-16 stdout）作为判据；
  3. 跳过只读基线直接写，事后解释收益落差；
  4. 全局副作用命令不做原态恢复，把非目标对象留在停用态。
- **检验标准**：操作后至少两条独立证据符号一致、量级一致（允许簇对齐误差，本案例 ≤0.05 GiB）；原态恢复后与快照一致。
- **跨场景迁移示例**：数据库 `VACUUM`/重建 —— 用"宿主盘空闲 + 表文件大小"双基线验收；CI 缓存清理 —— 用"缓存目录大小 + 构建时长"双基线验收。
- **成熟度**：**L1**（单案例：本次 VHDX 压缩门面），待第 2 个独立案例验证后可升 L2。

---

## 五、行动项（A · 原子化）

| # | 优先级 | 行动 | 验收标准 | Owner | 可独立交付 |
|---|:---:|------|---------|-------|:---:|
| A-1 | 高 | 补建 `.meta/toml/.agents/skills/wsl-vhdx-compact-cmd/SKILL.toml`，对齐 `x-toml-ref` | `Test-Path` = True，字段与 SKILL frontmatter 一致 | 维护者 | ✅ |
| A-2 | 高 | 在 `compact-vhdx-with-baseline.ps1` 参数校验中对 `PCMClawUbuntu`（及 PCManager BasePath）硬 ABORT | 传入该 Distro 时退出码非 0 并打印 `ABORT` | 维护者 | ✅ |
| A-3 | 中 | 澄清"3 次实战"计数：补齐第 3 次可核验 Before/After，或修正表述与已核验数据一一对应 | 文档中实战计数与可核验数据条数相等 | 维护者 | ✅ |
| A-4 | 中 | 为脚本增加 CI 守护测试（用空 `.vhdx` 文件做长度差分断言） | CI 用例在无 WSL 环境可回归 8 步数值逻辑 | 维护者 | ✅ |
| A-5 | 低 | 在 SKILL 增补"最小可跑示例"（一次 `-BaselineOnly` 的完整输入/输出样例） | 示例可直接复制执行并复现输出字段 | 维护者 | ✅ |

---

## 六、质量门记录

| 门 | 检查项 | 结果 |
|:--:|--------|:--:|
| G1 | 事实无因果/判断词、数量 ≥20、数据可验证 | ✅ 30 条 |
| G2 | 洞察四元组完整（陈述/证据/反常识/行动）、数量 ≥3 | ✅ 3 条 |
| G3 | 模式含触发/步骤/≥3 反模式/检验/迁移，标注成熟度 | ✅ 1 条（L1）|
| G4 | 行动项单一职责/可验证/有 Owner/可独立交付 | ✅ 5 项 |
| V 门 | 意见 ≥5、覆盖 4 视角、采纳 ≥2 | ✅ 8 条 / 采纳 4 条 |

---

> **报告编制**：本文档由七概念方法论 R→I→E→V→A→C 链路生成，事实均标注验证命令或来源文件；结论可追溯至事实编号。
> **链路**：R（`83ab7cafa` 交付物实测）→ I（3 四元组洞察）→ V（4 视角 8 意见采纳 4）→ E（1 个 L1 模式）→ A（5 原子行动项）→ C（原子提交）。
