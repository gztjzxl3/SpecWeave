---
name: seven-concepts-comprehensive-retro
description: 以七概念方法论对项目或子项目执行全面复盘并导出 Markdown 报告、同步模式入库的端到端编排。当用户要求全面复盘某项目、复盘并导出报告、或复盘加模式沉淀时使用；不用于单点缺陷修复、纯问答或单个模式的独立入库。
---

# seven-concepts-comprehensive-retro

对一个项目或子项目执行全面复盘的端到端编排：R 事实 → I 洞察 → E 萃取 → V 对抗审查 → A 行动项 → 报告归档 → 模式入库 → 独立审查 →（用户指令后）C 原子提交。

沉淀自三次同构交付：xmtools、caffe、xuanspace 全面复盘。

## 0. 分工边界

- **seven-concepts-cmd**：方法论引擎（场景判定、概念链路、质量门、CMD-LOG）。
- **本技能**：全面复盘这一完整场景的编排、产物落点与易错点。
- **pattern-to-methodology-library**：第 9 节「模式入库」子步骤可委托其执行。
- **knowledge-pack-builder**：当用户要的是知识包而非复盘报告时改用它。
- **atomic-commit-cmd**：C 阶段提交规范。

**不使用**：单点缺陷修复、随口问答、单个模式独立入库（无复盘上下文）、私域内容未判级。

## 1. 启动三前置（按序完成）

1. **内容敏感度预检**：公开内容 → 标准流，产物入根 `docs/`，Spec 在 `.trae/specs/`；私域内容 → 跳公共规划区，入 `playground/`。就高不就低。
2. **区域与只读边界**：`projects/`、`vendor/` 为 git submodule，全程只读、不回滚并行改动；进入子区域先读其 `AGENTS.md`。
3. **环境事实**：禁止假设 PATH；git、python 先探测全路径并在全程复用（本机实测 git `D:\Program Files\Git\mingw64\bin\git.exe`、python `D:\AI\.venv\Scripts\python.exe`，以实际探测为准）。

## 2. Spec 化（用户以 /spec 发起时）

- Spec 目录：`.trae/specs/retrospectives-insights/<project>-comprehensive-retrospective-export/`。
- 产物以磁盘 `AGENTS.md` 为唯一权威：`spec.md` + `tasks.md` + `review.md`；**禁止创建 checklist.md**；tasks.md 用「`## Task N:` + Status 字段」结构，不用纯 checkbox 列表。
- 三问澄清的推荐默认：①范围 = 全量脉络 + 增量聚焦；②形态 = Markdown 归档 + 索引登记；③E 产物 = 同步入库方法论模式库。
- AC 写成 `rule`（二元可验）或 `rubric`（含维度/量表/锚点/阈值）。

## 3. R 事实采集

- F-001 起连续编号、纯客观陈述、逐条附来源；G1 门 Grep 因果词（因为/导致/所以/由于/因此），逐字引述 commit subject 的命中须标注豁免。
- 全量规模节奏 + 增量逐条清单（`git log --since=<增量起点>`），聚类计数须自洽（分项之和 = 总数）。
- 抽查 ≥10 条回溯，命中率 100%，抽查表归档。
- **工作区事实多时点标注**：采集时点与复核时点分别编号（如 F-070 / F-128），数值不一致时不作确定性结论；并行会话在途改动如实归因、禁止回滚，并以一条事实声明本任务只读（如 F-129）。

## 4. I 洞察萃取

- ≥3 条，每条四元组完整（现象 / 5-Whys 根因 / 影响 / 建议），各引用 ≥2 个 F 编号、无悬空引用；深度自评 ≥4。
- 差异分析对照既有复盘，逐条标注 强化 / 反转 / 新增 / 无变化并附 F 依据。
- 系统性根因表述为「与现有事实一致的一种解释」，竞争假设与证据缺口显式列出，不写「必然产物」。

## 5. E 模式萃取

- 四要素过 G3：触发场景（适用/不适用）/ 核心步骤（**通用动作表述，专有值降为案例证据**）/ 反模式 / 迁移验证（含成本边界信号）。
- 去重裁决三选一：**新建 L1 / 并入既有 / 不入库**。判并入时差异点须设硬上限（如 ≤3 条），防止既有文档膨胀。
- 未经重跑的自报数据（CHANGELOG/自述中的计数、覆盖率、映射率）降级为规模量级参考；一致性判定以文件实体（如各 `pyproject.toml` 实读）为准。

## 6. V 对抗审查

- 四视角（魔鬼代言人/新人/老板/未来）、意见 ≥5、采纳 ≥2 且每条采纳有可定位的修正痕迹。
- 必含 ≥1 条指向事实证据强度不足。
- 不采纳意见须附理由；E 阶段不改写 I 结论，相关限定以「报告限定说明」下传。

## 7. A 原子行动项

- 每条单一职责、可独立验证，含 优先级 / Owner / 触发条件 / 可判定验收标准；G4/AC-8 自评全部 ≥4。
- 杜绝「加强沟通」「持续关注」式空话。

## 8. 报告归档

- 落点：`docs/retrospective/reports/project-reports/retrospective-<project>-comprehensive-<YYYYMMDD>/`。
- 四文件：`README.md`（主报告 S1~S4 + 质量门记录 + 限定说明附录）、`insight-extraction.md`、`actionable-items.md`、`index.md`（纯 toctree、无 frontmatter，对齐同项目既有实例）。
- 三件套 frontmatter 含 `type: Report` 与 `source`。报告须含三条限定：I-1 竞争假设、自报口径、工作区时点。

## 9. 模式入库 — 四处登记缺一不可（核心教训）

1. 域目录新建模式 `.md`（Pattern frontmatter，含 `x-toml-ref` 指向 `.meta`）。
2. `.meta/toml/docs/retrospective/patterns/methodology-patterns/<域>/` 下同名 `.toml`（**伴生 TOML 不在 docs 子树内**）。
3. 域 `index.md` toctree 按字母序插入。
4. `methodology-patterns/index.md`「模式清单」**主索引总表**新增一行——仅改域 toctree 不构成完整入库，这是最易遗漏项。
5. 域 `README.md` 生成区块只能运行 `generate-readme.py` 刷新，禁止手改。
6. 裁决为「并入既有」时只追加、保留全部原内容，并核对无既有内容损失。

具体路径、字段与样例见 [references/repo-conventions.md](references/repo-conventions.md)。

## 10. 报告索引登记

- `project-reports/index.md` toctree 增一行；`project-reports/README.md` 清单表增一行（日期/主题/关键产出）。
- `reports/index.md` 已含 `project-reports/index`，新报告经 toctree 传递可达，无需直接登记。

## 11. 质量门

- `check-links.py` 分别对报告目录与模式库运行，0 新增断链（既有无关文件的 frontmatter 警告须用 git log 证明非本次引入）。
- Grep 确认无 `file:///`、无 `.temp/`；新 YAML/TOML 实际解析通过；Completion Evidence 的行数须以实测填写。

## 12. 独立审查（Review）

- 委派 fresh-context 只读子代理，逐条对照 AC 打开一手文件取证，**不轻信 tasks.md 自述**。
- 在 `review.md` 勾选全部检查项并回填 P0/P1/P2 与总体判定；P0 必须修复并回归，P1 明确处置，P2 记录。

## 13. C 阶段原子提交

- 未经用户明确请求不创建提交。用户指令后走 atomic-commit-cmd，按单一职责拆分（建议：报告归档 / 模式入库与并入 / 索引登记），默认不推送。
