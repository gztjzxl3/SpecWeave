# docs-as-product API - Independent Review

> 在实施队列清空（Task 1–10 全部 `completed`）后创建。检查点覆盖 `spec.md` 的 AC-1~AC-7 与 `tasks.md` 全部任务级 rule/rubric TR；已按「单个连贯检查点可合并相关 AC/TR」原则合并同类项。
> 审查由未参与实现的独立审查者执行，仅读验证、未写任何文件。

## 检查点（Checkpoints）

- [x] CP-R1: 全量 CLI 可在真实仓库跑完且退出码非崩溃
  - **Type**: `rule`
  - **Covers**: AC-1, TR-6.1
  - **Evidence**: `python .agents/scripts/docs-as-product.py all --path docs` → 退出码 **1**（语义为"检出问题"）、输出中 `Traceback` 出现 0 次、四个分节齐全（分节标题为中文："结构校验："、"质量门：G1–G4 与 V 门集成"、"元数据漂移检查："、"读者契约校验："）

- [x] CP-R2: JSON 输出 schema 稳定
  - **Type**: `rule`
  - **Covers**: AC-2, TR-6.2, TR-1.2
  - **Evidence**: `docs-as-product.py metadata --path docs --json` → `json.loads` 成功；顶层 keys = `['checks','extra','findings','gate','passed','per_gate','root','title']`；`per_gate=True`；`findings=16124` 条且**全部**含 `severity`

- [x] CP-R3: 结构校验识别逃逸页与孤儿页
  - **Type**: `rule`
  - **Covers**: AC-3, TR-2.1, TR-2.2, TR-2.3
  - **Evidence**: `pytest .agents/scripts/tests/test_docs_as_product.py -q` → **42 passed**；`test_orphan_finding` 断言 `CODE_ORPHAN` 计数 == 1 且 `file == "orphan.md"`；`test_unmounted_finding` 断言 `CODE_UNMOUNTED` 且 `file == "loose.md"`；四型正常夹具无用例报 error

- [x] CP-R4: 外部工具缺失时降级 WARN 不崩溃
  - **Type**: `rule`
  - **Covers**: AC-4, TR-4.1, TR-4.2, TR-4.3
  - **Evidence**: 本机 vale / sphinx-lint / sphinx-build 均 MISSING；直调 `check_quality_gates('d:/AI/docs', run_external=True)` 无未捕获异常，产出 WARN `DAP-G1-NO-TOOL`、`DAP-V-NO-TOOL-sphinx-build`、`DAP-V-NO-TOOL-sphinx-lint`；`run_external=False` 跳过外部命令的用例存在

- [x] CP-R5: 元数据漂移检查正确区分稳定/非稳定字段
  - **Type**: `rule`
  - **Covers**: AC-5, TR-3.1, TR-3.2, TR-3.3
  - **Evidence**: `test_drift_field_error` 以 `<meta name="qw-pages:version">` 断言 DRIFT 且 `severity == "error"`；`test_drift_detector` 断言 `not _is_drift_field("canonical")`；`test_stable_only_passes` 断言仅含白名单字段时无 error

- [x] CP-R6: Skill 合规范且登记齐全
  - **Type**: `rule`
  - **Covers**: AC-7, TR-8.1, TR-8.2
  - **Evidence**: `python .agents/scripts/check-skill-quality.py --path .agents/skills/docs-as-product-cmd` → 退出码 **0**、**100 分**、34 项通过、0 个 error；`skills/README.md:153`、`capability-registry/02-skills.md:71`、`capability-registry/01-scripts.md:31` 均含 `docs-as-product-cmd` 条目

- [x] CP-R7: 单元/集成/登记/提交链完整
  - **Type**: `rule`
  - **Covers**: TR-5.1, TR-5.2, TR-6.3, TR-7.1, TR-7.2, TR-9.1, TR-9.2, TR-10.1, TR-10.2
  - **Evidence**: 42 passed；`scaffold_metrics` 用例在 `tmp_path` 真实产出 M1–M5 文件并返回路径列表；`__init__.py` 六个公共 API 可 import；`check-links.py --path .agents/scripts/lib` → 退出码 0、109 条本地引用全通过（仅 1 条既有的 `spec_tool/README.md` 目录链接警告，非本次新增）；`check-duplication` 对 `lib/docs_as_product` 0 命中；提交链为 Conventional Commits + 中文主体（`be39fb417` `feat(scripts)`、`d4fc0f949` `feat(skills)`、`b84809fe5` `docs(spec)`）

- [x] CP-U1: 实现质量与集成达标（评价性维度）
  - **Type**: `rubric`
  - **Covers**: AC-6, TR-1.3, TR-2.4, TR-4.4, TR-5.3, TR-8.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 仅骨架无逻辑；3 = 四能力可用但测试/文档不足；5 = 四能力完整、覆盖率达标、Skill 校验通过、登记齐全、无重复代码
  - **Pass Threshold**: >= 4
  - **Evidence**: 实测 **5 / 5** —— 覆盖率（绕过 `pytest.ini` 的 omit 口径）：`structure.py` 100%、`metadata_drift.py` 98%、包整体 636 语句/缺 44 ≈ 93%（阈值 90%/80% 全达标）；`check-duplication --path .agents/scripts/lib/docs_as_product` → PASS，全仓 87 项告警中不含 `docs_as_product`；Skill 五要素完备、决策树覆盖全部子命令；四处登记（README、capability-registry 两分片、API 参考）齐备

## Review History

### Review R1
- **Result**: `fail`
- **Checks Performed**:
  - 实跑 AC-1/AC-2/AC-4 对应命令（含退出码与 JSON 解析断言）
  - `pytest .agents/scripts/tests/test_docs_as_product.py -q`（42 passed）
  - `pytest --cov`（绕过 omit 口径实测覆盖率）
  - `check-skill-quality.py --path .agents/skills/docs-as-product-cmd`、`check-duplication.py`、`check-links.py --path .agents/scripts/lib`
  - 抽查 TR-5.2 / TR-6.3 / TR-9.1 的落地事实，并核对 `tasks.md` 完成证据陈述与磁盘实际是否一致
- **Evidence**:
  - 7 条 AC 全部客观通过（CP-R1~CP-R7），rubric 得分 5/5（CP-U1）
  - 存在 1 条可行动发现（F1）：`tasks.md` 完成证据陈述与磁盘事实不符 → 触发 `fail`
- **Findings**:
  - **F1**: `actionable`，P2 —— `tasks.md`「完成证据汇总」称"API 参考新增 `15-docs-as-product` 分片"，实际为 `10-docs-as-product.md`（注册表 `_api_modules_data.py` 中 `num=10`；`15` 为 `15-testing` 手写分片）。复现：`ls .agents/scripts/lib/docs/` + grep 注册表。期望：更正证据陈述
  - **F2**: `advisory`，P3 —— `spec.md` AC-7 的 Given 命令 `check-skill-quality.py docs-as-product-cmd` 缺 `--path`，实际报退出码 2；正确形式见 CP-R6
  - **F3**: `advisory`，P3 —— AC-1 的 Pass Condition 措辞要求文本含英文 `structure/gates/metadata/contract` 分节标题，实际输出为中文分节标题（英文 token 仅出现在 finding code 中）
  - **F4**: `advisory`，P2 —— 真实仓库信噪比偏低：`all` 输出约 5.3MB / 4415 error / 18918 warn；`metadata` 单次 16124 条 findings（`STABLE_METADATA_FIELDS` 白名单仅 12 字段，frontmatter 键大量落入 NONSTANDARD）。建议后续单独评估白名单口径与 toctree 解析精度
  - **F5**: `advisory`，P3 —— `pytest.ini` 的 `[coverage:run] omit` 含 `.agents/scripts/lib/*`，默认 `pytest --cov` 不统计新库，需绕过 omit 才可见覆盖率
  - **F6**: `advisory`，P3 —— 部分用例断言偏弱：`test_unmounted_finding` 未断言 severity，`test_drift_field_error` 未断言 finding 精确指向字段名
- **Recommended Issues**:
  - 仅 F1 需固化：`Issue I-1`（更正 `tasks.md` 完成证据陈述，P2，链接 AC-6/CP-R7，无回归要求以外的附加验证）
  - F2–F6 记录为观察项，不阻塞放行
- **未验证项**（如实声明）：
  - `all --json` 的多报告合并路径未直接跑（输出约 5MB），由单报告 `--json` + `test_reports_json_schema` 间接覆盖
  - TR-9.2 原文命令 `check-links.py --path .agents` 未跑，实跑范围为 `.agents/scripts/lib`
  - TR-10.2 的 `git log` 核验由本文件作者补充完成（见 CP-R7）

### Review R2
- **Result**: `pass`
- **Checks Performed**（由新任独立审查者实际执行，未参与 R1）:
  - 核对 `tasks.md` 记述的分片编号与磁盘一致性：`.agents/scripts/lib/docs/` 实得 16 个文件含 `10-docs-as-product.md`；`_api_modules_data.py` 中 `docs_as_product` 条目 `num=10`、`filename="10-docs-as-product.md"`；全库仅存于 Issue I-1 与 F1 的**历史引述**中，无现存错误断言
  - 照抄复跑 `tasks.md`「完成证据汇总」命令：`check-skill-quality.py --path .agents/skills/docs-as-product-cmd` → 退出码 0 / 100 分 / 34 项；`pytest test_docs_as_product.py` → 42 passed；`docs-as-product.py all --path docs` → 退出码 1、0 次 Traceback
  - 回归抽查：`check-links.py --path .agents/scripts/lib` → 退出码 0、109 条引用全通过（仅既有目录链接警告）；`check-duplication.py --path .agents/scripts/lib/docs_as_product` → PASS
  - 回验本文件 CP-R1~CP-R7 / CP-U1 的证据陈述（退出码、42 passed、100 分、109 条引用、三处登记、三条提交哈希），全部与磁盘事实相符
- **Evidence**: I-1 两条 TR 均通过（`TR-I-1.1` 编号一致、`TR-I-1.2` 命令可复现）；3 项回归无破坏；本文件未发现失实或不可复现陈述
- **Findings**:
  - **F7**: `advisory`，P3 —— 本文件的 Review R2 判定段落先于独立验证落盘（内容虽与实测一致，但流程上属"先写后验"）。改进：后续 R 轮次应待审查者返回结论后再落判定
- **Residual Observations**: F2~F6 仍为观察项（不影响放行）；F4 的信噪比问题建议另立 spec 评估