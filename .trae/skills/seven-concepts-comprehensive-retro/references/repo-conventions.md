# 仓库约定参考（repo-conventions）

> 本文件承载 seven-concepts-comprehensive-retro 所需的本仓库精确路径与格式事实。
> 路径均以工作区根 `d:\AI` 为基准；执行前如环境有变化，以实际探测为准。

## 1. 工具全路径（PATH 可能被裁剪）

| 工具 | 全路径（实测，使用前先探测确认） |
|---|---|
| git | `D:\Program Files\Git\mingw64\bin\git.exe` |
| python | `D:\AI\.venv\Scripts\python.exe` |

常用只读命令：

- 全量提交数：`git -C <repo> rev-list --count HEAD`
- 增量清单：`git -C <repo> log --since=YYYY-MM-DD --oneline`
- 子模块指针：`git -C <repo> submodule status`（无 +/- 前缀即无漂移）
- 工作区：`git -C <repo> status --porcelain`

## 2. Spec 目录与产物

- Spec 根：`.trae/specs/retrospectives-insights/<project>-comprehensive-retrospective-export/`
- 允许文件：`spec.md`、`tasks.md`、`review.md`、`facts.md`、`insights.md`、`e-stage-pattern.md`、`v-adversarial-review.md`。
- **禁止** `checklist.md`（`AGENTS.md` 与 spec-creation-precheck RULE-SCP-002）。
- tasks.md 结构：`## Task N: 标题`，任务字段含 Status / Priority / Depends On / Description / AC Addressed / Test Requirements / Notes / Completion Evidence；勾选写在 Status 行：`- [x] **Status**: `completed``。

## 3. 报告落点与四文件

- 目录：`docs/retrospective/reports/project-reports/retrospective-<project>-comprehensive-<YYYYMMDD>/`
- 四文件：`README.md`、`insight-extraction.md`、`actionable-items.md`、`index.md`。
- index.md 样例（纯 toctree、无 frontmatter）：

````markdown
# Retrospective <Project> Comprehensive <YYYYMMDD>

```{toctree}
:maxdepth: 2
:hidden:

insight-extraction
actionable-items
```
````

- 三件套 frontmatter 样例：

```yaml
---
type: Report
id: "retrospective-<project>-comprehensive-<YYYYMMDD>"
version: "1.0.0"
source: "<project> full history retrospective (<起止日期>; incremental window <窗口>, N commits)"
---
```

## 4. 模式入库四处（缺一不可）

### 4.1 模式文档
路径：`docs/retrospective/patterns/methodology-patterns/<域>/<pattern-id>.md`

frontmatter 字段样例：

```yaml
---
type: Pattern
id: "<pattern-id>"
title: "<模式中文名>"
source: "<相对路径，指向复盘报告 insight-extraction.md#I-x>"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/<pattern-id>.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
related_patterns:
  - "<id-1>"
tags:
  - "<tag>"
---
```

正文骨架（对齐同域既有模式）：模式类型 / 成熟度 / 一句话 / 适用场景（适用+不适用）/ 问题背景 / 核心做法 / 反模式 / 检验标准 / 迁移示例 / 案例证据 / 失效条件与演进 / 参考实现与关联。

### 4.2 伴生 TOML
路径：`.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/<pattern-id>.toml`
（伴生 TOML **不在** `docs/` 子树，由 frontmatter `x-toml-ref` 引用。）

```toml
id = "<pattern-id>"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/patterns/methodology-patterns/<域>/<pattern-id>.md"

[bindings]
rules = []
references = ["<id-1>"]
skills = []
```

### 4.3 域 toctree
文件：`docs/retrospective/patterns/methodology-patterns/<域>/index.md`
在 `{toctree}` 列表按字母序插入 `<pattern-id>`（无 `.md`、4 空格缩进）。

### 4.4 主索引总表（最易遗漏）
文件：`docs/retrospective/patterns/methodology-patterns/index.md`
「模式清单」表新增一行，列：`模式ID | 模式名称(相对链接) | 成熟度 | 验证次数 | 复用次数 | 触发场景`。
该文件「模式入库流程」第 5 步明确要求更新本索引。

### 4.5 域 README 生成区块
- 生成器：`.agents/scripts/generate-readme.py`（带 `--update`/`--target-dir` 参数，先看脚本帮助）。
- 域 `README.md` 的 `<!-- README_INDEX_START -->` ~ `<!-- README_INDEX_END -->` 区块禁止手改。

## 5. 报告索引两处

| 文件 | 登记形式 |
|---|---|
| `docs/retrospective/reports/project-reports/index.md` | toctree 增 `<report-dir>/index` |
| `docs/retrospective/reports/project-reports/README.md` | 报告清单表增一行（报告目录链接 / 日期 / 主题 / 关键产出） |

`docs/retrospective/reports/index.md` 已含 `project-reports/index`，传递可达，不改。

## 6. 质量门命令

- 链接检查：
  - `python .agents/scripts/check-links.py --path docs/retrospective/reports/project-reports/<report-dir>`
  - `python .agents/scripts/check-links.py --path docs/retrospective/patterns/methodology-patterns`
  - 可加 `--check-frontmatter-paths --check-x-toml-ref` 一并校验 frontmatter 与伴生引用。
- 禁用项 Grep：`file:///`、`.temp/`。
- frontmatter/TOML 解析：用 python 的 `yaml.safe_load` 与 `tomllib.load` 实测。

## 7. 参照实例

- 报告：`docs/retrospective/reports/project-reports/retrospective-xuanspace-comprehensive-20260826/`（同项目先例）。
- 模式：`.../governance-strategy/snapshot-parity-migration.md`（L1 文档样板）与其 `.meta/.../snapshot-parity-migration.toml`。
- 并入样板：`.../governance-strategy/behavior-characterization-freeze.md`（含追加的台账门禁、检验标准、仓库级规范演进条目）。
