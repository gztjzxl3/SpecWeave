# docs-as-product API - Product Requirements Document

## Overview
- **Summary**: 为 `.agents` 主权区新增一套 Python API 与命令行工具，把《文档即产品经营法》（`docs-as-product`）模式中的六步核心做法固化为可执行的自动化校验与脚手架能力，并包装为脚本命令门面 Skill `docs-as-product-cmd`。
- **Purpose**: 模式文档目前仅为人类可读的方法论描述，缺少可执行的机器校验。落地为 Python API 后，Diátaxis 四型分区、质量门、元数据漂移、读者契约与指标面板均可被 CI/脚本直接调用，使"文档即产品"从主张变为可观测、可回归的工程资产。
- **Target Users**: 本仓库维护者（治理/文档工程师）、CI 流水线、后续复用该模式的其他项目维护者。

## Goals
- 提供覆盖四项能力的只读校验 API：① 结构校验（Diátaxis 四型分区 + toctree/orphan 一致性）；② 质量门集成（G1–G4 + V 门：vale / `sphinx-build -W` / doctest / sphinx-lint）；③ 元数据漂移检查（canonical 与跨版本稳定字段，对应反模式 F-021）；④ 读者契约与指标（读者-验收任务表校验 + M1–M5 面板脚手架）。
- 提供统一 CLI 入口 `docs-as-product.py`，支持 `structure|gates|metadata|contract|metrics|all` 子命令，输出稳定 JSON schema 与人类可读文本，退出码 0/1。
- 创建脚本命令门面 Skill `docs-as-product-cmd`，与 `docgen-cmd`、`check-duplication-cmd` 同级，符合 SpecWeave Skill 五要素模型与渐进式披露规范。
- 复用既有 `lib/cli.py`、`lib/quality_report.py`、`lib/frontmatter.py` 等共享能力，不重复实现。

## Non-Goals
- 不实现文档内容自动改写、迁移或修复（本工具只读，唯一例外是 `metrics --scaffold` 生成面板模板）。
- 不替代 Sphinx 构建本身，不接管 `docs/conf.py` 的扩展装配与主题配置。
- 不修改 `vendor/`、`projects/` 子模块内任何资产。
- 不实现指标数据采集后端（M1–M5 真实埋点/日志摄取），仅提供面板脚手架与字段契约。
- 不新建外部依赖包进入运行期依赖（外部工具 vale/sphinx-lint 等按可选处置）。

## Background & Context
- **功能来源（唯一依据）**：`docs/retrospective/patterns/methodology-patterns/governance-strategy/docs-as-product.md`，frontmatter `id: "docs-as-product"`、`maturity: "L1-draft"`、`source: "七概念知识沉淀(sc-20261008-docs-as-product)——QwenWork Canvas 主张页…V6 发布态（22 条事实/4 洞察/6 条 V 意见）"`。
- **模式关键事实（挂 F 编号）**：最小公理集合在 `docs/conf.py`（F-012）；自有 `quality_gate` directive（F-013）；CI V 门 + 预览（F-014）；linkcheck 分诊脚本（F-015）；V6 发布修复记录元数据漂移（F-021、F-022）。
- **模式的检验标准 6 条**：① 读者契约可验收；② 结构无逃逸（全站无 `:orphan:`）；③ 门禁真实生效；④ 元数据无漂移；⑤ 指标闭环；⑥ V 门达标（每轮 ≥5 条实质对抗意见且采纳 ≥2 条）。
- **重复性排查结论**：`Grep "docs-as-product|文档即产品|docs_product"` 命中 12 文件，全为模式文档/索引/TOML/HTML/案例，无既有 Python 实现或 Skill → 全新实现。
- **七概念编排**：本任务判定为场景 5 创新突破（F→V→I→C，depth=standard），session `sc-20261008-docs-as-product-api`；方案已获用户批准进入 C 阶段。

## Functional Requirements
- **FR-1**: `scan_docs(root, config=None)` 扫描 `docs/` 目录，构建文档树模型，解析每页 frontmatter、head 元数据与 toctree 引用关系。
- **FR-2**: `check_structure(tree)` 校验 Diátaxis 四型分区（tutorial/how-to/reference/explanation）归属与 toctree/orphan 一致性；报告逃逸页（`:orphan:`）、孤儿页（未被任何 toctree 引用）、四型错位。
- **FR-3**: `check_quality_gates(root, *, run_external=True)` 集成 G1–G4 与 V 门；外部工具（vale / sphinx-build / doctest / sphinx-lint）缺失时降级为 WARN 而非崩溃。
- **FR-4**: `check_metadata_drift(tree)` 核对页面 head 中元数据字段是否仅保留跨版本稳定字段（url/domain/canonical 等白名单），与线上 canonical 一致；检出漂移字段。
- **FR-5**: `check_reader_contract(root)` 校验读者契约表（四类读者各一条可执行验收任务、Tutorial <15 分钟、Reference docstring 覆盖率 ≥90% 等断言的可核验部分）。
- **FR-6**: `scaffold_metrics(root, out_dir)` 生成 M1–M5 指标面板脚手架文件（含字段契约与 owner 占位）。
- **FR-7**: CLI 入口 `docs-as-product.py` 装配 `structure|gates|metadata|contract|metrics|all` 子命令，支持 `--path`/`--json`/`--config`/`--run-external|--no-external`/`--scaffold`。
- **FR-8**: 创建 Skill `docs-as-product-cmd`，含决策树、渐进式披露、五要素与安全检查清单，并在 `skills/README.md` 与 `capability-registry.md` 登记。

## Non-Functional Requirements
- **NFR-1**: 只读安全——除 `metrics --scaffold` 外不得写入任何文件；不得修改 `docs/` 内容。
- **NFR-2**: 统一契约——文本与 JSON 双输出，JSON schema 稳定（含 `per_gate`/`findings[]`/`severity`），退出码 0（通过）/1（有问题）。
- **NFR-3**: 缺失即降级——外部工具不可用时输出 WARN 并继续，不得抛出未捕获异常。
- **NFR-4**: 兼容性——遵循仓库 Python 红线（禁止 `from __future__ import annotations`）与既有 `lib/cli.py` 约定；`setup_safe_output()` 三层编码防御。
- **NFR-5**: 可测试——单元测试覆盖率 ≥80%，`structure` 与 `metadata_drift` 关键模块 ≥90%。
- **NFR-6**: 无重复——新增脚本前通过 `check-duplication` 校验，不得重复实现 `lib/` 既有功能。

## Constraints
- **Technical**: 入口脚本须置于 `.agents/scripts/`，库代码须置于 `.agents/scripts/lib/docs_as_product/`；遵循 `lib/<name>/{__init__,cli,constants,models,...}` 结构约定；文件头使用 `from .python310_version_check import enforce_python310` + `enforce_python310()`。
- **Business**: 产出物为公开内容（Public），规划落 `.trae/specs/`，实现落 `.agents/` 主权区；遵循 Conventional Commits（主体中文）。
- **Dependencies**: 复用 `lib/cli.py`、`lib/quality_report.py`、`lib/frontmatter.py`、`lib/project.py`；可选外部工具 vale / sphinx-build / sphinx-lint / pytest-doctest；不新增运行期第三方依赖。

## Assumptions
- `docs/` 目录结构可通过 Sphinx `conf.py` 与 toctree 解析获得完整文档树。
- 四型分区可通过目录命名约定（tutorial/how-to/reference/explanation 或其等价中文/别名）识别，无法识别时归入 unclassified 并 WARN。
- 线上 canonical 信息在离线场景不可直接获取，故 `metadata_drift` 以本地 head 字段白名单与配置化 canonical 基准为准。
- 外部工具由调用方环境提供；CI 中真实生效，本地可降级。

## Acceptance Criteria

### AC-1: CLI 全量可运行并给出明确结论
- **Type**: `rule`
- **Given**: 在仓库根执行 `python .agents/scripts/docs-as-product.py all --path docs`
- **When**: 命令运行完成
- **Then**: 输出包含各子检查的结论摘要，且退出码为 0 或 1（非崩溃）
- **Pass Condition**: 退出码 ∈ {0, 1}，且文本输出含 `structure`/`gates`/`metadata`/`contract` 分节标题
- **Evidence**: 命令输出截取

### AC-2: JSON 输出 schema 稳定
- **Type**: `rule`
- **Given**: 执行任一子命令并附加 `--json`
- **When**: 解析输出
- **Then**: JSON 顶层含 `per_gate`、`findings[]`（每项含 `severity`）字段
- **Pass Condition**: `json.loads` 成功且关键字段存在
- **Evidence**: JSON 片段

### AC-3: 结构校验识别逃逸与孤儿
- **Type**: `rule`
- **Given**: 构造含 `:orphan:` 与未挂载 toctree 页的测试夹具
- **When**: 调用 `check_structure`
- **Then**: 报告对应 finding，severity 正确
- **Pass Condition**: 测试断言 finding 数量与类型匹配
- **Evidence**: 单元测试通过输出

### AC-4: 外部工具缺失时降级不崩溃
- **Type**: `rule`
- **Given**: 环境未安装 vale / sphinx-lint
- **When**: 调用 `check_quality_gates(run_external=True)`
- **Then**: 输出 WARN finding，进程正常结束
- **Pass Condition**: 无未捕获异常，finding severity 为 WARN
- **Evidence**: 测试或命令输出

### AC-5: 元数据漂移检查正确区分稳定/非稳定字段
- **Type**: `rule`
- **Given**: 页面 head 含 `qw-pages:version`（非白名单）与 `canonical`（白名单）
- **When**: 调用 `check_metadata_drift`
- **Then**: 仅对非白名单字段报漂移
- **Pass Condition**: finding 精确指向 `qw-pages:version`，不含 canonical
- **Evidence**: 单元测试输出

### AC-6: 实现质量与集成达标
- **Type**: `rubric`
- **Dimension**: 实现完整性、可测试性、与既有规范的契合度
- **Scale**: 1-5
- **Anchors**: 1 = 仅骨架无逻辑；3 = 四能力可用但测试/文档不足；5 = 四能力完整、覆盖率达标、Skill 校验通过、登记齐全、无重复代码
- **Pass Threshold**: >= 4
- **Evidence**: pytest 覆盖率报告、`check-skill-quality.py` 输出、`check-duplication` 输出、登记文件 diff

### AC-7: Skill 合规范
- **Type**: `rule`
- **Given**: 执行 `python .agents/scripts/check-skill-quality.py docs-as-product-cmd`
- **When**: 校验完成
- **Then**: 通过（无 error 级问题）
- **Pass Condition**: 退出码 0 且无 error
- **Evidence**: 命令输出

## Open Questions
- [ ] `metadata_drift` 的 canonical 基准是否需要在配置中显式声明线上域名，还是仅按白名单校验？（默认按白名单 + 可选配置）
- [ ] M1–M5 面板脚手架的输出形态：Markdown 表格还是 JSON + Markdown 双份？（默认 JSON 数据 + Markdown 面板）