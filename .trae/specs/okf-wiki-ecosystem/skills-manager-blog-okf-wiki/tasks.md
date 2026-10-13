# 执行任务清单：Skills Manager 公众号文章 → OKF 知识包

工作流：Spec 批准后执行七概念知识沉淀 `R → I → E → V → C`；文章转化按 R（事实采集/核验）→ I（骨架/归属/拆分）→ E（信源先行生成）→ V（对抗审查/索引门禁）→ C（交付核对）推进。**未经另行授权不提交或推送。**

## Task 1: R 阶段：文章事实登记与官方核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 重新读取并核对公开文章全文，记录标题、账号、日期、文章结构及页面可读内容边界。
  - 建立 spec `facts.md`，F-001 起登记事实、观点/体验及核验补充，按来源距离和 P 级标注。
  - 使用官方官网、代码仓库、README、发布记录等一手来源核对数量、版本、平台、junction/WSL、安全、同步、备份限制等 P0 声明。
  - 对口径不一致项保留来源、定义和核验日期；不以不同渠道的数字拼成单一结论。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-1.1: 每条文章主张均登记来源和事实性质；所有 P0 均有结论，无法核实时明确标注未核实/仅文章单源。
  - `rule` TR-1.2: 版本、数量、平台、安全和限制类数据均可从核验记录定位到实际访问的来源及核验日期。
- **Notes**: 核验结果如显示文章核心声明未获证实，后续按规范决定 `status: flagged`。
- **Completion Evidence**:
  - TR-1.1 passed: Spec 与 bundle 各登记 32 条事实；文章“54”未获当前官方页面直接证实，Release 三视图差异、100 MiB 跟踪状态边界、凭证分支差异均有明确结论。
  - TR-1.2 passed: 数量、版本、平台、同步、阈值和凭证声明均关联到实际 README/API/Release/源码来源及 2026-10-10 核验日期；未把源码检查表述为实机测试或安全审计。

## Task 2: I 阶段：确认归属、骨架与知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 复查 `jishu/ai/products/` 与现有相邻 bundle，确认主线实体、bundle slug 和可用主题互链。
  - 基于文章及官方资料对操作可复现性两问作出有证据的结论。
  - 列出 concepts 篇目和各自覆盖的 F 编号；按判据决定 examples 的有无及篇目。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-2.1: spec 中记录目标分组理由、被排除候选和 examples 两问结论。
  - `rule` TR-2.2: 知识地图逐篇映射事实编号；若 examples 未通过两问，不创建 examples 目录或伪操作步骤。
- **Notes**: 若发现目标分组语义不符，仍优先选已有合适分组；不得为单篇文章新建分组。
- **Completion Evidence**:
  - TR-2.1 passed: 归属 `jishu/ai/products/` 的理由与排除候选已记录；未新建分组。
  - TR-2.2 passed: examples 两问结论为不通过；未创建 `examples/`；知识地图覆盖 F-001~F-032，无遗漏或重复。

## Task 3: E 阶段：信源先行并生成 OKF bundle
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在 `jishu/ai/products/skills-manager/`（最终 slug 以 Task 2 结果为准）按确定骨架生成 references、concepts、可选 examples、各层 index 和 log。
  - 先完成 `references/article-source.md` 与 `references/verification.md`，再写 concepts/examples，最后写各级索引。
  - 在具体声明旁引用 F 编号，表达版本/平台和来源边界；完成后更新 spec `facts.md` 与 bundle 双份事实登记。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 全部非保留 Markdown 均有有效 OKF v0.2 frontmatter；bundle 根索引含 `sources`、`status`、`stale_after` 及已知边界。
  - `rule` TR-3.2: references 先于概念文档形成；全部具体产品声明可追溯至 F 编号，无文章全文复制或无来源补写。
  - `rubric` TR-3.3: 教程可理解性；scale 1-5；anchors 1 = 结构不可导航且边界缺失，3 = 主要主题覆盖但局部上下文需补足，5 = 初学读者可理解产品机制、核验边界和适用限制；threshold >= 4；evidence 为四视角审查记录。
- **Completion Evidence**:
  - TR-3.1 passed: bundle 共 10 个 Markdown 文件；根索引具备 OKF v0.2 必需元数据，子级索引与普通内容未声明 `okf_version`。
  - TR-3.2 passed: references、3 篇 concepts、索引和日志均在 bundle 内；具体产品事实标注 F 编号，文章正文未镜像，未创建伪操作示例。
  - TR-3.3 score: 4/5. 主题、证据边界、版本/平台/凭证限制和未实测范围均可查；因文章不提供可复现流程，文档明确不是操作教程，不承诺读者可按步骤完成安装或恢复。

## Task 4: V 阶段：对抗审查、索引整合和质量门
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 以事实溯源、结构规范、初学者可用性、时效/安全边界四视角审查全文并修正。
  - 正则比对 spec `facts.md` 与 bundle `article-source.md` 的编号集合。
  - 合并更新产品组与总索引；保留当前工作区已有的并行编辑，根据实施时实际目录计数更新所有计数。
  - 运行 `invoke gates.toctrees`、`invoke gates.utf8`、`invoke gates.bundles`；依赖不可用时执行等效手动检查并在 log 中如实记录。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: F 编号集合连续一致，所有 toctree 指向存在文件，Markdown 相对链接可达且 `file:///` 为零。
  - `rule` TR-4.2: 分组导航表、toctree、分组数量与目录树一致；总索引 frontmatter、正文、域/组计数与当前全库一致。
  - `rule` TR-4.3: UTF-8 严格解码通过；三项质量门结果和任何既有基线失败均在交付说明中准确区分。
- **Notes**: 不处理本任务无关的 bundle 或原有质量门问题；若其影响全库门禁，记录为外部现状，不代为修改。
- **Completion Evidence**:
  - TR-4.1 passed locally: 双份 F 表逐行一致、连续 32 条；知识地图完整；bundle 10/10 文件可达；本地链接及 frontmatter 路径检查通过，`file:///` 为零。
  - TR-4.2 passed: 产品组导航表/toctree/目录均为 29 项且集合一致；全库 bundles 索引门禁通过（9 域、61 组、612 束）。
  - TR-4.3 passed locally: Spec 与 bundle 共 14 个 Markdown 文件严格 UTF-8 解码通过。全库 toctree 门禁被无关并行目录 `deepseek-harness/concepts` 缺少 `index.md` 拦截；`invoke gates.*` 此前因缺少 `invocations` 依赖未能启动，均已在 bundle log 记录，未虚报通过。
  - 四视角审查的具体发现、修正与边界见 bundle `log.md` 的 V 阶段记录。

## Task 5: C 阶段：交付核对
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 核对最终文件清单、bundle 入口、索引接入、事实溯源、质量门输出及 Git 工作区差异。
  - 仅报告本任务涉及的文件与验证结果；不得把其他会话/既有未提交变更归为本任务产物。
  - 不执行 Git commit 或 push，除非用户另行明确授权。
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-5.1: 最终交付清单与实际新增/修改文件一致，索引与链接可达，未提交任何代码或文档。
  - `rule` TR-5.2: 交付报告说明 gates 实际执行情况、未解决的口径冲突和工作区中既有修改边界。
- **Completion Evidence**:
  - TR-5.1 passed: 交付范围为 Skills Manager bundle 与对应 Spec 文件；bundle 已接入产品组索引。没有执行 commit 或 push。
  - TR-5.2 passed: Release 与数量口径冲突、未执行的 Invoke 门禁、全库 toctree 的并行目录阻塞及工作区并行修改边界均已明确记录。

## Issue I-1: 复核并协调官方仓库与 Release 动态快照
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**:
  - R1 重新读取官方 GitHub 来源后，报告仓库描述为“50+ coding tools”、latest release 为 `v1.40.3`（2026-10-01），与 Spec/bundle 中 F-021、F-030 及依赖这些事实的正文不一致。
  - 在同一轮重新获取仓库 API、README、latest Release API、Release 列表 API 与网页入口，登记带时间戳的原始观察结果；若端点仍冲突则并列保留，不推定单一当前版本或数量口径。
  - 更新 Spec 与 bundle 两份事实表及所有依赖声明，确保来源清单、核验报告、概念页、根索引和日志一致。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-I-1.1: 每个动态值可定位到本轮实际读取的官方来源、响应值和观察时间；所有受影响正文陈述与事实表相符。
  - `rule` TR-I-1.2: Spec 与 bundle F 表仍连续、逐条一致；检索旧版本/数量口径时，不存在未经解释的冲突残留。
- **Notes**: 独立审查者的实时读取作为待复核发现，不直接替代原始来源证据。
- **Completion Evidence**:
  - TR-I-1.1 passed: `facts.md` F-021（“50+ coding tools”、`updated_at 2026-10-10T04:32:24Z`）、F-023（README“54 agents ... out of the box”，固定 commit `9e03d833…`）、F-030（三 Release 视图均 v1.40.3，2026-10-10）均已更新并同步至重建的 bundle 双份事实表；source-manifest/verification 及全部概念页采用一致快照。
  - TR-I-1.2 passed: Spec 与 bundle F 表均连续 F-001~F-044 且逐条一致（机械比对无差异）；旧值 v1.22.1/v1.28.3/v1.17.0 作为不可复现历史保留并列（F-030），无未经解释的冲突残留。

## Issue I-2: 补齐文章主张覆盖或记录排除理由
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**:
  - R1 指出文章中关于 marketplace/presets、默认技能库路径、冲突处理选项及作者背景等具体内容，未在当前 F-001~F-020 中逐项登记。
  - 对照可访问的完整文章逐项盘点页面事实、产品主张、作者背景/观点；每项要么加入带来源定位与性质标记的新 F 编号，要么记录明确的范围排除理由。
  - 将新增事实同步到 Spec `facts.md`、bundle `references/article-source.md`、knowledge map 和相关 concepts（仅当正文采用该声明时）；保持编号连续和双表逐项一致。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-2.1: 每条纳入 bundle 的文章具体主张均有 F 编号；未纳入的具体主张有可审计的排除理由。
  - `rule` TR-I-2.2: 全文 claim checklist 与 F 表逐项核对完成；双份事实表连续、编号集合及陈述完全一致。
- **Notes**: 不为追求覆盖率而复制文章段落；仅保留必要、可溯源的原创摘要。
- **Completion Evidence**:
  - TR-I-2.1 passed: 新增 F-033~F-044 逐项登记市场导入（F-033）、默认 `~/.skills-manager` 路径（F-034）、首次启动（F-035）、独立工作区（F-036）、`manage-skills`/CLI 路径（F-037）、WSL 软链接主张（F-038）、安装资产格式（F-039）、预设（F-040）、冲突选项（F-041）、作者履历（F-042）、体验转述（F-043）与第三方价值判断（F-044）；均标来源定位与类型，无伪填充。
  - TR-I-2.2 passed: 全文 claim 检查清单与 F-001~F-044 逐项核对完成；Spec 与 bundle 双份 F 编号集合连续、完全一致（机械比对无差异），且陈述逐条一致。

## Issue I-3: 更正 UTF-8 验证清单数量
- **Status**: `completed`
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**:
  - `log.md` 将严格 UTF-8 解码范围记为 14 个 Markdown 文件；R1 对明确 Spec 与 bundle 路径执行检查时覆盖 15 个文件。
  - 重新运行显式路径 UTF-8 检查，记录准确文件清单、数量和命令，并同步更正 bundle log 与 Spec 验证证据。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-I-3.1: 对本任务 Spec 与 bundle 的明确文件集严格 UTF-8 解码全部通过，日志中的数量与实际输入文件数一致。
- **Notes**: 不将全库或并行子模块文件计入本任务 UTF-8 清单。
- **Completion Evidence**:
  - TR-I-3.1 passed: 明确文件集 = Spec 5 个（spec/facts/knowledge-map/review/tasks）+ bundle 10 个 = 15 个 Markdown 文件全部严格 UTF-8 解码通过；bundle `log.md` 已更正为“Spec 5 + bundle 10 = 15”，数量与输入一致。

## Issue I-4: 精化知识地图概念-事实映射（R2-N1，P2）
- **Status**: `completed`
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R2（R2-N1）
- **Description**:
  - Review R2 指出 `knowledge-map.md`「概念篇目与事实映射」中：概念 `00` 声明覆盖含 F-001~F-008，但 F-001/F-002/F-003/F-004 为文章身份元数据，未出现在概念 `00` 正文中；区间 `F-030~F-035` 隐式包含 F-032，而 F-032 实际仅在概念 `02` 被引用。
  - 建议：将概念 `00` 覆盖清单精化为其正文实际引用的 F（如 F-005~F-008…），并将 `F-030~F-035` 改写为逐项列明（F-030/F-031/F-033/F-034/F-035）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-4.1: 知识地图的篇目-事实映射与其对应概念正文的实际引用一一对应，无隐式区间误含、无声明覆盖但正文未用。
- **Notes**: R2 判定为非阻塞（P2，文档精度），不影响事实表与验收；修复后由新审查者按需回归。
- **Completion Evidence**:
  - TR-I-4.1 passed: `knowledge-map.md` 概念 `00` 覆盖清单已由 `F-001~F-008` 精化为 `F-005~F-008`（移除文章身份元数据 F-001~F-004，与概念正文实际引用一一对应），并将隐式区间 `F-030~F-035` 拆分为显式 `F-030、F-031、F-033~F-035`（移除此处未引用的 F-032）。对照概念 `00`/`02` 正文逐条核实：概念 `00` 实际引用 F-005/006/007/008/017~024/030/031/033/034/035/040/042/044，概念 `02` 引用 F-032——映射与正文无声明覆盖却未用、也无隐式区间误含。
