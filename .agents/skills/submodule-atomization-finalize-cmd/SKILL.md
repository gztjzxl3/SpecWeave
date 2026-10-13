---
name: submodule-atomization-finalize-cmd
version: 1.0.0
description: "当用户要求在 projects/ 第一方 git 子模块内做文档原子化/拆分收尾、子模块文档断链与锚点检查、子模块 GitHub slug 中文锚点门禁、子模块文件移动后引用核对，或主仓 atomization-finalize 在子模块内不适用时，必须使用此技能。固化子模块等价收尾六步 SOP（边界确认→入站引用盘点→slug 链接门禁→git HEAD 事实守恒 diff→残留与导航→清理与证据），内置 check_doc_links.py 检查器。vendor/ 只读第三方子模块禁止修改，不适用本技能的写操作。"
argument-hint: "<docs-root> [<docs-root> ...]"
user-invocable: true
paths:
  - ".agents/skills/submodule-atomization-finalize-cmd/**"
  - ".agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py"
title: "Submodule Atomization Finalize 子模块文档原子化收尾 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/submodule-atomization-finalize-cmd/SKILL.toml"
---
# Submodule Atomization Finalize 子模块文档原子化收尾 Skill

> ⚠️ **本Skill是命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（触发词+决策树+六步 SOP+安全清单）
> - L2：[scripts/check_doc_links.py](scripts/check_doc_links.py)（链接/锚点门禁源码）

## 1. Skill ID
`submodule-atomization-finalize-cmd`

## 2. 功能描述

`projects/` 第一方 git 子模块内文档原子化、文件移动、目录重构后的**等价收尾工具**。
主仓 [atomization-finalize-cmd](../atomization-finalize-cmd/SKILL.md) 的三个动作
（check-links 断链修复、docgen 导航表、Spec 看板刷新）均是主仓设施，**作用域不覆盖子模块**；
本Skill用子模块内可执行的六步 SOP 达成同等收尾质量：

| 步骤 | 功能 | 手段 |
|------|------|------|
| S1 边界与变更面 | 确认变更只在预期文档、判定子模块读写权限 | 子模块 `git status --porcelain` + 嵌套 AGENTS.md 路由 |
| S2 入站引用盘点 | 移动/删除锚点前找出全部旧引用 | 子模块与主仓两侧 grep（含跨边界） |
| S3 链接锚点门禁 | 相对链接文件存在性 + Markdown 锚点（GitHub slug） | [check_doc_links.py](scripts/check_doc_links.py) |
| S4 事实守恒 | 迁移内容与 git HEAD 旧章节逐字节比对 | `git show HEAD:<file>` + `diff` |
| S5 残留与导航 | 已删标题零残留、索引页登记新文件 | grep + 文档地图核对 |
| S6 清理与证据 | 临时脚本/中间文件删除，输出三类数字证据 | 人工核对 + 不提交纪律 |

> **为什么不能在子模块里直接跑主仓 finalize？** `finalize-atomization.py` 的链接修复以主仓
> 目录树为作用域，docgen 只扫描主仓 `docs/` 与根 README 的 `NAV` 标记区，看板只认主仓
> `.trae/specs/`。在子模块内执行要么扫不到目标、要么把主仓无关文件卷入变更。子模块收尾必须
> 换用本 SOP——这与主仓技能不是重复，而是按目录边界路由的互补关系。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "子模块文档原子化/拆分收尾"、"projects 下文档拆完了检查一下"
- "子模块断链/锚点检查"、"子模块中文锚点/标题锚点校验"、"GitHub slug 校验"
- "子模块文件移动后引用核对"、"子模块文档事实守恒 diff"
- 在 `projects/<submodule>/` 内完成 atomization-cmd 拆分后需要收尾
- 主仓 finalize/docgen/check-links 在子模块目录内不适用或扫不到文件时

> **不适用（反场景）**：
> - 根 `docs/`、`.agents/`、`apps/` 等主仓直接管理目录 → 用
>   [atomization-finalize-cmd](../atomization-finalize-cmd/SKILL.md)；
> - `vendor/` 第三方只读子模块 → **禁止任何修改**，仅可只读核验，改动走上游反馈流程
>   （见 [VENDOR-INTEGRATION.md](../../VENDOR-INTEGRATION.md)）；
> - 代码文件原子化或功能重构验证 → 本Skill只管文档。

## 4. 方案选择决策树

```
原子化/移动的文档在哪里？
├─ 根 docs/、.agents/（主权区） → atomization-finalize-cmd（finalize-atomization.py）
├─ apps/（主仓普通目录）        → 主仓 finalize 优先；不适用时用本 Skill S3+S4
├─ projects/<sub>/（第一方子模块）→ 本 Skill（先读该子模块 AGENTS.md，嵌套优先）
│   └─ 子模块有自己的检查脚本/门禁？ → 先跑子模块门禁，本 Skill S2-S6 补充
└─ vendor/（第三方只读子模块）   → 禁止修改；仅只读核验，反馈走 upstream
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出 CMD_START 日志（session 前缀 `subfin-YYYYMMDD-<topic>`）：

```
[CMD-LOG] | level=INFO | cmd=submodule-atomization-finalize | step=S0 | event=CMD_START | session=subfin-... | msg=开始子模块文档收尾：<简述> | ctx={"docs_root":"...","submodule":"projects/<name>"}
```

## 5. 六步收尾 SOP

### 执行模式：预览确认门（dry-run，强制）

首轮一律以**预览模式（dry-run）**执行：S1–S5 的所有手段（`git status`、`git show`、
grep、check_doc_links.py）本身均为只读，产出的是**变更计划清单**而非改动——包括
「拟修复的断链/锚点列表（文件+链接+去向）」「拟更新的入站引用点列表」
「S6 拟删除的临时文件列表（`[待删除]` 前缀逐条列出）」。清单交用户确认后才允许写动作；
禁止未列清单直接修改文件或 `rm`。写动作完成后必须以同一检查器复跑（post-verify），
broken=0 才算闭环。

> **为什么需要预览门？** 子模块内的"修复"可能跨子模块/主仓边界，批量 sed 式替换极易
> 误伤时点快照中的历史路径；删除临时文件在证据报告需要复跑时会丢失现场。dry-run 让所有
> 副作用在发生前可审、可拒、可缩小范围。

### S1 边界与变更面

1. 按启动协议读子模块自身的 `AGENTS.md`（嵌套优先）与文档目录惯例
   （如是否使用 frontmatter、是否用显式 `<a id>` 锚点），**不得套用主仓格式强改**。
2. 在子模块根执行 `git status --porcelain -- <docs 相对路径>`，确认变更面仅限预期文件。
3. 明确 gitlink 边界：子模块内提交不会进入主仓，主仓只追踪 gitlink；**未经用户明确要求不提交**。

### S2 入站引用盘点（移动/删除锚点之前）

- 在子模块全仓 grep：旧文件路径、被移动/删除章节的标题文字与 slug；
- **跨边界在主仓全仓再 grep 一次同样的关键词**（主仓 docs/、.agents/skills/ 可能有
  `projects/<sub>/...` 形式的入站引用）；
- 对每个命中点预先设计去向：保持 slug 不变、更新链接、或确认属时点快照保持原样。

> **为什么锚点盘点必须在动手前？** 文件拆分后旧锚点会静默 404，而引用点可能跨 git 仓库
> 边界。事后补救的成本随引用点数量线性增长，事前 grep 是一次性机械操作。

### S3 链接锚点门禁

```bash
# WSL（本机 PATH 被裁剪时用全路径 wsl.exe，见 §7）
python3 .agents/skills/submodule-atomization-finalize-cmd/scripts/check_doc_links.py \
  /mnt/d/AI/projects/<submodule>/path/to/docs
# 支持多个根目录；退出码非 0 即存在断链，禁止进入 S6 报告完成
```

检查器规则：递归扫描 `*.md` 行内链接与引用式链接定义；跳过 http(s)/mailto；
文件不存在判 broken；fragment 仅对 **`.md` 目标**按 GitHub slug 校验
（小写、去 `` `*~ `` 等标点、空白转 `-`、保留中日韩文字，兼容显式 `<a id|name>`）。

### S4 事实守恒（git HEAD 对拍）

```bash
cd /mnt/d/AI/projects/<submodule>
git show HEAD:<old_path> | sed -n '<起>,<止>p' > /tmp/old_section.md
sed -n '<起>,<止>p' <new_path>             > /tmp/new_section.md
diff /tmp/old_section.md /tmp/new_section.md
```

只允许三类预期差异，其余逐条解释或回退：

1. **自指显式化**：拆出独立文件后"本页"语义失效，须改为显式文件名链接；
2. **相对路径重定基**：目录深度变化导致的 `../` 层数调整；
3. **导航性文字**：标题、文首导航语、文档地图条目的必要增删。

关键数字、编号集合、结论措辞不在允许差异内（时点快照须原样守恒）。

### S5 残留与导航

- grep 已删除章节标题、旧导航提示语（如"文末有…表"）：**零匹配**；
- 索引页文档地图/导航表已登记新文件，性质标注（常青台账/时点快照/冻结档案）；
- 源索引页不保留已迁走的深度内容（重复内容也算残留）。

### S6 清理与证据报告

- 删除全部临时检查脚本与 `/tmp` 中间文件（`.temp/` 内容按保留期自动清理，不留引用）；
- 报告三类证据：链接门禁（checked_files/links/broken 三数字）、守恒 diff（逐条预期差异）、
  变更面（git status 文件清单）；
- 停在工作区不提交，等待用户指令；如需提交，在**子模块内**走 atomic-commit-cmd。

## 6. 关键设计手法（实证沉淀）

| 手法 | 要点 |
|------|------|
| slug 稳定性迁移 | 标题**文字不变、仅层级 h2→h3 变化时 GitHub slug 不变**；把短节降级为子节可零断链并入相邻章节，外部引用无需改动 |
| 冻结历史分离 | 索引页中"随项目演进的常青内容"与"一次性动作档案（迁移表/验证记录）"变化原因不同，后者应拆为日期前缀时点文件 |
| 自指重定向 | 迁出内容中的"本页"必须替换为显式文件名链接，否则在新位置指向错误 |
| 双端 grep | 入站引用盘点同时覆盖子模块与主仓，跨 git 边界引用是最易漏点 |

## 7. 环境纪律（Windows 本机实证）

- 本机 PowerShell 的 PATH 可能被裁剪（无 `python`/`py`/`git`）：统一经
  `$env:WSL_UTF8=1` + `& "$env:WINDIR\System32\wsl.exe"` 在 WSL 中执行，
  WSL 内主仓路径为 `/mnt/d/AI/...`；
- PowerShell here-string 管道给 `wsl.exe bash -s` 前必须 CRLF→LF
  （`-replace "`r`n","`n"`），否则远端命令尾部携带 `$'\r'` 导致路径找不到；
- 删除临时文件若 DeleteFile 回收站失败，用 WSL `rm -f` 兜底；
- `set WSL_UTF8=1` 可消除中文输出乱码；D:\WSL 是 podman machine 数据目录，禁止当临时目录。

## 8. 安全检查清单

- [ ] 已读子模块 AGENTS.md 并确认目标在 `projects/`（第一方，可开发）而非 `vendor/`（只读）
- [ ] 首轮已按 dry-run 预览模式产出变更计划清单，所有写动作经用户确认后才执行
- [ ] S2 入站引用盘点在动手前完成，跨主仓边界 grep 无遗漏
- [ ] S3 链接门禁 `broken=0`（非零退出码已处理，不带病进入下一步）
- [ ] S4 守恒 diff 每条差异都归入三类允许项，关键数字/编号零变化
- [ ] S5 已删标题与旧导航语零残留，索引页已登记新文件
- [ ] 临时脚本与中间文件已删除，未在任何文档中留下 `.temp/` 引用
- [ ] 未执行 git commit/push（子模块提交需用户明确指令，且在子模块内进行）
- [ ] 变更面与批准范围一致，未顺手修改无关文件

## 9. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| 大量 `xxx.py#L85 [锚点缺失]` | 误把 GitHub 源码行锚点当 Markdown 锚点 | 检查器只对 `.md` 目标校验锚点；若仍报此错确认检查器版本 |
| 中文标题锚点误报 | slug 规则未保留中日韩文字或大小写处理错误 | 使用本 Skill 自带检查器，勿手写简化版 |
| 主仓 grep 命中跨边界引用 | 主仓 docs/skills 引用了子模块文件 | 列入 S2 清单逐项处理；时点快照中的历史路径保持原样并注明 |
| 守恒 diff 出现大段差异 | 迁移时改写了原文或截取行号错误 | 回退新文件重新迁移；导航性文字外的改写须单独提案 |
| 子模块无 HEAD 基线（全新未跟踪目录） | 无法 git show 对拍 | 拆分前手工留底旧文件副本至临时位置，用副本替代 HEAD 对拍 |
| `python: 术语无法识别` | PATH 裁剪 | 改用 §7 的 WSL 全路径方式执行 |

## 10. Gotchas（陷阱与反直觉行为）

- **主仓 finalize "跑成功了"不等于子模块收尾完成**：脚本作用域不匹配时可能零改动退出，
  造成已收尾假象；以本 SOP 三类证据为准。
- **检查器必须复用本 Skill 脚本，不要每次重写一次性版本**：一次性版本最容易漏掉
  引用式链接、显式 `<a id>` 与非 `.md` 锚点豁免三类边界（本 Skill 的初版一次性检查器
  就曾产生 32 条 `.py#Lxx` 误报）。
- **子模块文档格式惯例可能与主仓不同**（实证：xuan-compose doc 不使用 frontmatter、
  锚点用显式 `<a id>`）。以子模块 AGENTS.md 与同目录现有文件为准。
- **h2→h3 保 slug 是零断链迁移的核心技巧**，但反向（h3→h2 跨文件迁走）会断链；
  移动到新文件时锚点路径必然变化，S2 盘点不可省。
- **"本页/本节内"等相对指称在内容迁走后全部失效**，守恒 diff 中应能看到对应的显式化改动；
  一条都没有反而要怀疑迁移不完整或留下了错误自指。
- **子模块内 `git status` 必须带子模块路径在子模块根执行**；在主仓根只能看到 gitlink
  状态变化，看不到文档级变更面。
- **成熟度 L1**：两个实证案例（2026-10-10、2026-10-12 xuan-compose/doc）来自同一文档集，
  非独立案例；第二个子模块复用成功后可升 L2 并回填 reuse_count。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 主仓原子化拆分 | L1 | [atomization-cmd](../atomization-cmd/SKILL.md) | 执行拆分本身（本Skill只管收尾） |
| 主仓一键收尾 | L1 | [atomization-finalize-cmd](../atomization-finalize-cmd/SKILL.md) | 主权区/apps 收尾 |
| 链接检查门面 | L1 | [link-check-cmd](../link-check-cmd/SKILL.md) | 主仓作用域断链修复 |
| 原子化完整规范 | L2 | [commands/atomization.md](../../commands/atomization.md) | RACI/拆分策略/质量验收 |
| 子模块协同规范 | L1 | [VENDOR-INTEGRATION.md](../../VENDOR-INTEGRATION.md) | vendor 边界与上游回馈 |

## 12. Changelog

- **v1.0.0** (2026-10-12): 初始版本。萃取自 xuan-compose/docs 两轮原子化实证
  （2026-10-10 四长文档原子化、2026-10-12 索引页二次拆分）：六步收尾 SOP、
  GitHub slug 检查器（中文锚点/显式 a id/非 .md 锚点豁免/引用式链接）、
  h2→h3 保 slug 与"本页"自指重定向两条迁移手法、WSL 裁剪环境执行纪律、
  dry-run 预览确认门（S3 质量门 100/100）。
