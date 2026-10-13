# docs-as-product API - Implementation Plan

> 队列按依赖排序并原子化垂直切片：底座（模型/常量/发现）→ 四项能力 → 装配 CLI → Skill 与登记。每项完成后可独立验证。

## 完成证据汇总（2026-10-08）

- **测试**：`pytest test_docs_as_product.py` → 42 passed；覆盖率 TOTAL 93%（structure 100%、metadata_drift 98%）。
- **Skill 质量**：`check-skill-quality.py --path .agents/skills/docs-as-product-cmd` → 100 分，通过 34 项。
- **链接**：`check-links.py` → 所有链接均有效。
- **重复**：新模块单独扫描无重复命中（全仓库仅命中既有统一版本头样板）。
- **端到端**：`docs-as-product.py all --json` 对真实 docs 正常输出 `per_gate`/`findings`，退出码语义正确。
- **登记**：skills/README.md（13 个门面）、capability-registry/01-scripts.md 与 02-skills.md 均已登记；API 参考新增 `10-docs-as-product` 分片（注册表 `_api_modules_data.py` 中 `num=10`；同目录 `15-testing`、`16-sphinx-config` 为手写分片，非本 spec 产出）。

## Task 1: 搭建模块底座（模型、常量、发现）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建 `lib/docs_as_product/{__init__.py, constants.py, models.py, discovery.py}`。
  - `constants.py`：Diátaxis 四型映射、G1–G4 与 V 门定义、元数据稳定字段白名单、默认路径与门禁开关。
  - `models.py`：`Severity`、`Finding`、`CheckResult`、`DocNode`、`DocsTree`、`Report`（dataclass），含 JSON 序列化方法。
  - `discovery.py`：`scan_docs(root, config=None) -> DocsTree`，扫描 `docs/`、解析 frontmatter/head、解析 toctree 引用。
  - 文件头遵循 Python 红线：`from .python310_version_check import enforce_python310` + `enforce_python310()`（或按既有 lib 约定），禁止 `from __future__ import annotations`。
- **Acceptance Criteria Addressed**: AC-1（依赖）、AC-2（模型序列化基础）、AC-5（发现 head 字段）
- **Test Requirements**:
  - `rule` TR-1.1: `scan_docs` 对测试夹具目录返回非空 `DocsTree`，节点含 path/title/type 字段；证据：单元测试断言。
  - `rule` TR-1.2: 所有 dataclass 可 `asdict` 化并 JSON 序列化成功；证据：单元测试。
  - `rubric` TR-1.3: 常量定义的可读性与可配置性；scale 1-5；anchors 1=硬编码散落、3=集中但不可配置、5=集中且配置可覆盖；threshold >= 4；证据：code review。
- **Notes**: 复用 `lib/frontmatter.py`、`lib/project.py`，不得重复实现 frontmatter 解析。

## Task 2: 结构校验能力（Diátaxis 四型 + toctree/orphan）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `structure.py`，实现 `check_structure(tree) -> Report`。
  - 校验四型分区归属；detect `:orphan:`（逃逸页）；detect 未被任何 toctree 引用的孤儿页；报告四型错位。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 含 `:orphan:` 夹具 → 报出逃逸 finding（severity 正确）；证据：单元测试。
  - `rule` TR-2.2: 未挂载 toctree 页夹具 → 报出孤儿 finding；证据：单元测试。
  - `rule` TR-2.3: 正常四型目录夹具 → 无 error 级 finding；证据：单元测试。
  - `rubric` TR-2.4: 四型识别规则对别名/中文目录的鲁棒性；scale 1-5；anchors 1=仅英文硬编码、3=含别名表、5=别名表+unclassified 降级 WARN；threshold >= 4；证据：测试用例矩阵。
- **Notes**: 关键模块，覆盖率要求 ≥90%。

## Task 3: 元数据漂移检查（F-021）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `metadata_drift.py`，实现 `check_metadata_drift(tree) -> Report`。
  - 核对页面 head 元数据是否仅含跨版本稳定字段（白名单），检出漂移字段（如 `qw-pages:version`/`deployment-id`/`published-at`）；支持配置化 canonical 基准。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-3.1: head 含非白名单字段 → 精确报出该字段；证据：单元测试。
  - `rule` TR-3.2: head 仅含白名单字段 → 无 finding；证据：单元测试。
  - `rule` TR-3.3: canonical 与配置基准不一致 → 报出不一致 finding；证据：单元测试。
- **Notes**: 关键模块，覆盖率要求 ≥90%。

## Task 4: 质量门集成（G1–G4 + V 门）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 新建 `quality_gates.py`，实现 `check_quality_gates(root, *, run_external=True) -> Report`。
  - 集成 G1（vale 事实/文风）、G2（结构：每页首段+标题层级）、G3（组件复用）、G4（原子性：一文件一单元）、V 门（`sphinx-build -W --keep-going` + doctest + sphinx-lint）。
  - 外部工具缺失/不可用时降级 WARN，不抛异常。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-4.1: mock 外部工具缺失 → 输出 WARN 且无异常；证据：单元测试（monkeypatch）。
  - `rule` TR-4.2: G2 对缺首段页面报 finding；证据：单元测试夹具。
  - `rule` TR-4.3: `run_external=False` 跳过外部命令，仅做内置检查；证据：单元测试。
  - `rubric` TR-4.4: 降级策略的清晰度（WARN 文案是否指明缺失工具与安装方式）；scale 1-5；anchors 1=静默吞错、3=报 WARN、5=WARN+工具名+建议；threshold >= 4；证据：输出截取。
- **Notes**: 严禁在检查中写入文件；外部命令超时应可控。

## Task 5: 读者契约与指标脚手架
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 新建 `reader_contract.py`，实现 `check_reader_contract(root) -> Report`：校验读者契约表（四类读者各一条可执行验收任务、Tutorial <15 分钟、Reference docstring 覆盖率 ≥90% 的可核验部分）。
  - 新建 `metrics.py`，实现 `scaffold_metrics(root, out_dir) -> list[Path]`：生成 M1–M5 面板脚手架（含字段契约与 owner 占位），输出 JSON 数据 + Markdown 面板。
- **Acceptance Criteria Addressed**: AC-1（contract 分节）、AC-2
- **Test Requirements**:
  - `rule` TR-5.1: `check_reader_contract` 对缺验收任务的契约表报 finding；证据：单元测试。
  - `rule` TR-5.2: `scaffold_metrics` 在临时目录生成文件且返回路径列表，文件含 M1–M5 全部条目；证据：单元测试（tmp_path）。
  - `rubric` TR-5.3: 脚手架字段契约的完备性（M1–M5 各有定义/owner/采集说明）；scale 1-5；anchors 1=仅标题、3=有字段无 owner、5=字段+owner+采集说明齐全；threshold >= 4；证据：生成文件检查。
- **Notes**: `scaffold_metrics` 是唯一允许写文件的路径。

## Task 6: 统一输出与 CLI 装配
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 新建 `reporter.py`：统一文本/JSON 输出，复用 `lib/quality_report.py` 的 `build_json_output`。
  - 新建 `cli.py`：argparse + `add_common_args`（`--path`/`--json`）+ `--config`/`--run-external|--no-external`/`--scaffold`，装配 `structure|gates|metadata|contract|metrics|all` 子命令，`setup_safe_output()` + `print_header/print_pass/print_warn/print_error`，退出码 0/1。
  - 新建入口脚本 `.agents/scripts/docs-as-product.py`。
  - `__init__.py` 导出公共 API（`scan_docs`/`check_structure`/`check_quality_gates`/`check_metadata_drift`/`check_reader_contract`/`scaffold_metrics`）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-6.1: `docs-as-product.py all --path docs` 退出码 ∈ {0,1} 且含四类分节标题；证据：命令输出。
  - `rule` TR-6.2: 任一子命令 `--json` 输出含 `per_gate` 与 `findings[]`（含 `severity`）；证据：JSON 解析断言。
  - `rule` TR-6.3: `__init__.py` 导出六个公共 API 可 import；证据：单元测试。
- **Notes**: 结构对齐 `lib/check_pattern_quality/cli.py` 风格。

## Task 7: 单元测试与覆盖率
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 在 `.agents/scripts/tests/` 新增 `test_docs_as_product_*.py`：覆盖结构/元数据/质量门/契约/指标/CLI。
  - 使用测试夹具（临时目录构造 docs 树）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: `pytest .agents/scripts/tests/ -k docs_as_product` 全通过；证据：pytest 输出。
  - `rule` TR-7.2: 覆盖率 `structure` 与 `metadata_drift` ≥90%，整体 ≥80%；证据：`pytest --cov` 报告。
- **Notes**: 覆盖率不达标不得进入 Review。

## Task 8: Skill 创建与登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 新建 `.agents/skills/docs-as-product-cmd/SKILL.md`（15 节骨架 + 五要素：Trigger-Ready Description / Decision Tree / Progressive Disclosure / Why-Explanation / Safety Checklist）。
  - 在 `.agents/skills/README.md`「脚本命令门面」表格登记。
  - 在 `.agents/capability-registry.md` 登记 scripts/skills 条目。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-8.1: `python .agents/scripts/check-skill-quality.py docs-as-product-cmd` 退出码 0 且无 error；证据：命令输出。
  - `rule` TR-8.2: README 与 capability-registry 均含 `docs-as-product-cmd` 条目；证据：grep/文件 diff。
  - `rubric` TR-8.3: 五要素完整度与决策树可用性；scale 1-5；anchors 1=仅描述、3=含决策树缺 Why、5=五要素齐全且决策树覆盖全部子命令；threshold >= 4；证据：SKILL.md 审阅。
- **Notes**: 参考 `docgen-cmd/SKILL.md` 结构；`../` 相对路径按子目录层级调整为 `../../`。

## Task 9: 文档与 API 参考登记
- **Status**: `completed`
- **Priority**: low
- **Depends On**: Task 6
- **Description**:
  - 在 `lib/_api_modules_data.py` 追加 `docs_as_product` 模块 dict（num/slug/title/filename/body），并提供 `lib/docs/` 对应分片内容，使 API 参考可生成。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-9.1: 运行 API 文档生成脚本后 `docs_as_product` 出现在输出中；证据：命令输出/文件。
  - `rule` TR-9.2: 无断链（`check-links.py --path .agents`）通过；证据：命令输出。
- **Notes**: 若 API 文档机制不适用本模块可直接在 `__init__.py` 补齐 docstring 满足 Reference ≥90% 目标。

## Task 10: 质检与原子提交
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 7, Task 8, Task 9
- **Description**:
  - 运行 `check-duplication`（无重复）、`check-skill-quality`、`pytest --cov`、`docs-as-product.py all` 自检。
  - 以 Conventional Commits（主体中文）原子提交。
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: `check-duplication` 对新增脚本无重复告警；证据：命令输出。
  - `rule` TR-10.2: 提交信息符合 Conventional Commits 且主体为中文；证据：`git log -1`。
- **Notes**: 提交前确保无 `.temp/`、`__pycache__/` 入库。

## Issue I-1: 完成证据陈述与磁盘事实不符（Review R1 / F1）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**:
  - 本文件「完成证据汇总」原称"API 参考新增 `15-docs-as-product` 分片"，实际文件为 `.agents/scripts/lib/docs/10-docs-as-product.md`（注册表 `num=10`），`15` 对应 `15-testing` 手写分片。
  - 同段"Skill 质量"一行记录的命令 `check-skill-quality.py docs-as-product-cmd` 缺 `--path`，照抄执行会报退出码 2（即 Review R1 的 F2 同源缺陷）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-I-1.1: 本文件记述的分片编号与实际 `lib/docs/` 文件名、注册表 `num` 一致；证据：文件列表 + 注册表 grep。
  - `rule` TR-I-1.2: 本文件记述的校验命令可照抄执行成功；证据：命令退出码 0。
- **Completion Evidence**:
  - 分片编号更正为 `10-docs-as-product` 并注明 15/16 手写分片归属；Skill 质量命令补 `--path`（复制自 Review R1 的 CP-R6 实证命令）。
  - 由 Review R2 独立复核一致性与检查点未回归。
- **Notes**: 属文档证据陈述失真，未涉及实现代码改动。