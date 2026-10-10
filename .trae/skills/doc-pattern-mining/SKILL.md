---
name: doc-pattern-mining
description: 对用户指定的独立文档直接执行七概念 R→I→E→V 全链路模式萃取，产出方法论模式库 L1 条目（模式文档＋伴生 TOML＋单 toctree 字母序登记＋链接/文件名门禁），C 提交等待明确指令。当用户给出文档路径并要求模式沉淀、萃取、按七概念提炼模式时使用；模式已在知识包 E 阶段成型时改用 pattern-to-methodology-library；纯问答与单篇文档顺手修改不要使用。
---

# doc-pattern-mining

把一份独立技术文档（复盘报告、模式汇编、交付总结等）中的可迁移做法，沿七概念
R→I→E→V 链路直接萃取为方法论模式库正式条目。本技能沉淀自三次同构交付：
快照对拍迁移法、第一性原理多维证伪验收法、单体重构六则（一次三篇）。

## 0. 启动与边界

先按工作区 `AGENTS.md` 启动协议完成磁盘回读与内容敏感度预检：公开技术文档入根
`docs/`；源文件位于 submodule（projects/vendor）时只读引用，产出仍落根库。
禁止写入已废止的 `.agents/docs/`。

**与相邻技能的分工**：

| 维度 | pattern-to-methodology-library | 本技能 |
|---|---|---|
| 输入 | 已建成知识包 E 阶段的成型模式 | 任意独立文档（可含多则候选） |
| 链路 | 入库独立化（无 R/I） | 完整 R→I→E→V |
| 索引 | 三处登记＋回写知识包 | 仅子区域 toctree 一处，无回写 |
| 成熟度口径 | L1-draft | L1（正文注明单案例与演进条件） |

不适用：私域内容未判级；用户只要求顺改某篇文档；输入是知识包（改用相邻技能）。

## 1. R：磁盘回读与事实登记（G1）

1. 用 Read 从磁盘原文读取源文档，禁止只凭系统注入副本；
2. 逐条登记事实：模式名称、步骤、计数、事故编号、文件名、命令名等可核验信息；
   G1 纪律——事实句不得出现"因为/导致/所以"等因果词，案例数字照抄不换算；
3. 源文档引用的二级台账（differences.md、quirks 清单等）按需回读取证。

## 2. 机械去重（硬门，不可跳过）

1. 读 `docs/retrospective/patterns/methodology-patterns/index.md` 总表初筛候选；
2. Grep 每则候选的核心动作关键词于 `docs/retrospective/patterns/`，补捞异名近邻；
3. Read **全部**候选模式全文，按作用对象／核心动作／所处层级三维对齐；
4. 对每则候选出具裁决，四类去向：
   - **新建**：根库无覆盖且具备跨域可迁移性；
   - **并入/补变体**：既有模式的时序或场景变体，补小节并双向链接；
   - **仅交叉引用**：边界相关但机制不独立；
   - **不收录**：纯操作层细节且已被既有模式覆盖（如具体 Git 操作约定）。
   单案例事故（如 D13）只能作反模式提示，措辞标"孤证"，不作统计结论。

## 3. I：四元组洞察（G2）

至少 3 条，每条含 现象＋根因＋影响＋建议 四元组；洞察须能机械对应到 R 的事实，
不引入源文档之外的新事实。

## 4. E：模式稿与落盘

### 4.1 新建模式文档

路径：`docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.md`

frontmatter（字段名与取值照此，勿自创）：

```yaml
---
type: Pattern
id: "<kebab-id>"
source: "../../../../../<源文档相对路径>"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns: ["<sibling-id>"]
tags: ["<kebab-tag>"]
---
```

正文十段，缺段视为 G3 未过：模式类型、成熟度（注明单案例、跨项目验证缺失前
保持 L1）、一句话、适用场景（适用/不适用分列）、问题背景、核心做法（分步编号）、
反模式、（可选）与近邻模式对比表、检验标准（checkbox）、迁移示例（≥2 域，
未验证方向显式标注）、失效条件与演进、参考实现与关联。

抽象纪律：步骤用通用动作表述，案例仅作证据；断言落到具体可观察输出；
去重裁定相关的边界必须在对比表或关联段写清。

### 4.2 伴生 TOML

路径：`.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.toml`

```toml
id = "<kebab-id>"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/patterns/methodology-patterns/<sub-area>/<kebab-id>.md"

[bindings]
rules = []
references = ["<related-id>"]
skills = []
```

TOML 与 frontmatter 的 id/maturity/validation_count 必须一致。

### 4.3 相对路径深度（从 <sub-area>/ 出发，实测）

| 目标 | 相对路径 |
|---|---|
| 仓库根 / 源文档 | `../../../../../<path>` |
| 伴生 TOML | `../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<id>.toml` |
| 同区兄弟模式 | `<id>.md` |
| 跨区模式 | `../<other-sub-area>/<id>.md` |

禁止 `file:///` 绝对路径；禁止凭记忆数层级，落盘后以链接脚本实证。

## 5. V：四视角对抗审查

| 视角 | 必查攻击点 |
|---|---|
| 魔鬼代言人 | 去重裁定是否成立；新模式间是否互相重叠；成熟度是否虚高；有无幸存者偏差 |
| 新人 | 术语是否定义；脱离案例能否执行；断言是否空心化 |
| 老板 | 门禁/步骤成本是否失控；检验标准对准结果还是流程完整 |
| 未来 | 前提消失后退化为什么；技术更替后的复查触发器 |

每次萃取意见不少于 4 条且至少一条触及失效条件；每条给裁定（采纳/部分采纳/不
采纳＋理由），采纳项当场改稿并注明改了哪份文件哪一处。

## 6. 登记：仅子区域 toctree

在 `<sub-area>/index.md` 的 toctree 中按**文件名字母序**为每个新 id 插入一行；
只追加不重排既有条目。并入/补变体类裁决不产生新行。不登记总表、不回写上游
（无知识包）；如用户额外要求，再参照 pattern-to-methodology-library 补做。

## 7. 门禁（参数为实测，勿改）

按顺序执行；凡本次编辑触及的其他子区域目录，链接检查逐一补跑：

```powershell
# 链接检查：必须传目录（传单文件会得到 0 个 Markdown）
python .agents/scripts/check-links.py --path docs/retrospective/patterns/methodology-patterns/<sub-area>

# 文件名规范：--directory 直接接目录，不要加位置参数
python .agents/scripts/check-filename-convention.py --directory docs/retrospective/patterns/methodology-patterns/<sub-area>

# TOML 可解析
python -c "import tomllib; d=tomllib.load(open('.meta/toml/docs/retrospective/patterns/methodology-patterns/<sub-area>/<id>.toml','rb')); print(d['id'], d['maturity'])"
```

链接报告只修本次新增链接引入的断链；存量断链列入报告、不扩散修改。
Shell 间 PATH 不稳定时改用全路径：
Python `C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`；
Git `D:\Program Files\Git\mingw64\bin\git.exe`。

## 8. 汇总与 C 纪律

- 向用户输出 R/I/E/V 汇总：事实清单、四元组洞察、裁决表（每则去向）、V 意见
  采纳记录、门禁结果；交付物一律用 `computer://` 链接；
- **默认不执行任何 git 操作**。明确声明 C 待指令，并给出提交方案（多篇时建议
  一篇模式一笔 `docs(patterns)`、index.md 随末笔，或合并为一笔，由用户选择）；
- 用户下达提交指令后：显式 add 每个文件（禁止 `git add .`），中文信息写
  "为什么"，推送前 fetch 并用 `rev-list --left-right --count origin/main...HEAD`
  确认纯 ahead，再 fast-forward 推送。

## 9. 反模式（三次实战教训）

1. 不做机械去重直接建文件——双权威入库，返工成本最高；
2. 事实句写因果词、数字凭印象换算——G1 失效，后续洞察无地基；
3. 去重/对等核对只放最后——重复翻译贯穿多 Task 才暴露（D13 教训）；
4. 为让断言符合直觉而改生产代码——对等迁移中即制造不对等；
5. 链接检查传单文件、文件名命令加位置参数——脚本行为已实测，勿再试错；
6. toctree 不按字母序或顺手重排既有条目；
7. V 门只写好评、无失效条件攻击——视为 V 未执行；
8. 未经用户明确指令自行 commit/push。
