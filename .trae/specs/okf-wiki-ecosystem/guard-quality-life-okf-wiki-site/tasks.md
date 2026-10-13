# 《守护品质生活》复合交付 - 实施计划

> Spec Mode 产物规范：本文件为 `tasks.md`。遵循 AGENTS.md / TRAE-spec-mode 权威约定，**使用 review.md（而非 checklist.md）**，后者仅在实施队列清空后创建。

## 依赖总览

知识包（Part A）与网站（Part B）共享同一知识树来源，但又可部分解耦：

- **T1（基础决策** → 先行）。
- **Part A 知识包**：T2（facts）→ T3 → T4 → T5 → T6（索引）独立闭环；其中 T3/T4 可在 facts 齐备后并行写作。
- **Part B 网站**：T7（脚手架）先行 → T8（知识树数据）依赖 A 的 concepts 结构 → T9 三信号与 T10 UI 可在 T7 后并行 → T11 验证。
- **Part C 收尾**：T12 门禁、T13 三件套闭环，依赖 A/B 完成后执行。

---

## Task 1：区块归属与骨架确认
- **Status**: `completed`
- **Completion Evidence**:
  - 归属决策：bundle=`sheke/personal-growth/guard-quality-life`；应用=`apps/guard-quality-life-site`；submodule `projects/awesome-okf-xs`（main，working tree clean，无 rebase）确认稳定。
  - 骨架目录已建（bundle concepts/references；应用 src/gqlsite/signals、templates、static、tests）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 最终确认知识包 bundle 归属分组（默认 `sheke/personal-growth/guard-quality-life`）与 scikit-build-core 应用目录名（`apps/guard-quality-life-site`）；
  - 确认 `projects/awesome-okf-xs` submodule 稳定（非并行 rebase/索引冲突）后再开始写操作；
  - 建骨架目录（bundle concepts/references 骨架 + 应用 src 骨架）。
- **Acceptance Criteria Addressed**: AC-1、AC-8
- **Test Requirements**:
  - `rule` TR-1.1: 归属决策落定并写入 spec；submodule 无 rebase 中标记（`git -C projects/awesome-okf-xs status | grep -i rebase` 为空或 read 通过）。
  - `rule` TR-1.2: 骨架目录存在（bundle 7 篇 concepts + references 2 篇；应用 pyproject/tasks/src/tests）。

## Task 2：知识包事实登记（R）
- **Status**: `completed`
- **Completion Evidence**:
  - `facts.md` 建立 F-001~F-046 连续登记（46 条），分五大区（方法论/信源核验/11 域结构/网站同源/边界时效）；
  - 主张三层标注（【官方通识】A /【通用常识】B /【框架主张】C）。
  - 复核：facts.md 与 references/article-source.md 两份 F 集合逐一比对一致、F-001 起连续无跳号（AC-2）。
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 在 `.trae/specs/okf-wiki-ecosystem/guard-quality-life-okf-wiki-site/facts.md` 建立 F-001 起连续编号登记；
  - 覆盖：方法论规则、10+ 域的结构、每个可执行 SOP、边界声明、通用常识引源（官方机构）；
  - 标注"作者观点/可执行改写"与"权威引源"分层。
- **Acceptance Criteria Addressed**: AC-2、AC-3、AC-7
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 与未来 article-source.md 集合比对零差异、F-001 起连续。
  - `rule` TR-2.2: P0 清单（健康/安全声称）每项有 F 行，可在 facts 定位。

## Task 3：知识包 references 信源先行（E-1）
- **Status**: `completed`
- **Completion Evidence**:
  - `references/article-source.md`（F-001~F-046 双份登记）、`references/verification.md`（P0 核验报告 + 常识/框架主张标注）、`references/index.md`（toctree）三篇已写；
  - 复核：P0 四项（F-009/010/011/029）逐项核验 ✅，引源用机构主域无深链（AC-3）；两份 F 集合比对一致（AC-2）。
- **Priority**: high
- **Depends On**: T2
- **Description**:
  - 先写 `references/article-source.md`（F 编号事实登记）与 `references/verification.md`（P0 核验报告 + 边界/单源标注）；
  - 再写 `references/index.md`（toctree）。
- **Acceptance Criteria Addressed**: AC-2、AC-3
- **Test Requirements**:
  - `rule` TR-3.1: article-source F 集合与 facts.md 相等；verification P0 每项有结论。

## Task 4：知识包 concepts 框架与域总览（E-2）
- **Status**: `completed`
- **Completion Evidence**:
  - `concepts/00-framework.md`（理念 + 五要素 + 证据分级 A·B·C）、`concepts/01-domains.md`（11 域总览表 + Mermaid 域图）、`concepts/index.md`（学习路径 + toctree）已写；
  - 复核：域总览覆盖 11 域（≥10）且映射 F-014~F-034（AC-7）；toctree 条目与实际文件逐一对应（AC-1）。
- **Priority**: high
- **Depends On**: T3
- **Description**:
  - 写 `concepts/00-framework.md`（理念 + 证据分级 + 成本收益框架）与 `concepts/01-domains.md`（10+ 域总览，Mermaid 域图）；
  - 写 `concepts/index.md` 学习路径（排在域篇后）。
- **Acceptance Criteria Addressed**: AC-1、AC-7、AC-U1
- **Test Requirements**:
  - `rule` TR-4.1: 00/01/00 index 存在含 toctree；域数 ≥10。
  - `rule` TR-4.2: Mermaid 符合安全编码（节点文本无裸特殊字符）。

## Task 5：知识包 concepts 分域执行篇（E-3）
- **Status**: `completed`
- **Completion Evidence**:
  - 分域篇已写：`02-home`（家居）、`03-health`（健康+睡眠）、`04-efficiency`（效率+数字）、`05-finance-relations-mind`（财务+关系+心理）、`06-how-to-use`（使用迁移）；
  - 复核：抽查 03-health 与 05-finance-relations-mind 各条目五要素（目的/步骤/成本收益/证据级/禁忌边界）齐备且挂 F 编号（AC-7）；边界声明（非医疗/法律/财务）落于相关篇（AC-6）。
  - 注：spec 骨架名 `05-finance-relations.md` 实际落盘为 `05-finance-relations-mind.md`（合并财务+关系+心理），已回写 spec 骨架保持一致。
- **Priority**: high
- **Depends On**: T3
- **Description**:
  - 写 `concepts/02-home.md`、`03-health.md`、`04-efficiency.md`、`05-finance-relations.md`、`06-how-to-use.md`；
  - 每域条目五要素齐备（目的/步骤/成本收益/证据级/禁忌边界）。
- **Acceptance Criteria Addressed**: AC-7、AC-6、AC-U1
- **Test Requirements**:
  - `rule` TR-5.1: 抽查 5 个条目五要素齐备、引源逐字一致、挂 F 编号。
  - `rule` TR-5.2: 边界声明（非医疗/法律/财务建议）落于相关篇。

## Task 6：知识包根/索引与边界收尾
- **Status**: `completed`
- **Completion Evidence**:
  - bundle 根 `index.md`（性质声明/时点/边界/互链 + toctree）与 `log.md`（R→I→E→V→C 链路 + V 门禁表格）已写；
  - 三级索引计数同步并复核零差异：personal-growth/index.md（13→14 束）、sheke/index.md（13→14 + guard-quality-life 描述）、bundles/index.md（total 613→614、sheke 59→60、personal-growth 9→14 分组行）；
  - toctree 条目（根 index → concepts/index、references/index、log）逐一 Test-Path 为真（AC-1、AC-4、AC-6）。
- **Priority**: medium
- **Depends On**: T4, T5
- **Description**:
  - 写 bundle 根 `index.md`（性质声明/时点/边界/互链）与 `log.md`（R→I→E→V 链路）；
  - 接入三级索引并同步计数：personal-growth/index.md、sheke/index.md、bundles/index.md。
- **Acceptance Criteria Addressed**: AC-1、AC-4、AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 三面计数三角对账零差异；toctree 条目 Test-Path 全真。
  - `rule` TR-6.2: 边界/时点/互链声明逐项可指认。

## Task 7：网站应用脚手架（B-1）
- **Status**: `completed`
- **Completion Evidence**:
  - `apps/guard-quality-life-site/` 已建：pyproject.toml（scikit-build-core、python>=3.14、wheel.packages=["src/gqlsite"]、ruff banned-api 禁 `__future__`）、tasks.py（invoke run/test/check）、src/gqlsite（main.py 路由 + templates + static）、tests/、README.md、.gitignore；
  - 复核：应用可导入（`python -c "import gqlsite"` 在 src 安装后成立，py314 下 pytest 冒烟全绿）；无 `from __future__` 残留。
- **Priority**: high
- **Depends On**: T1
- **Description**:
  - 建 `apps/guard-quality-life-site/`：pyproject.toml（scikit-build-core，python>=3.14）、tasks.py（invoke: run/check/test）、src/gqlsite/main.py（FastAPI 骨架 + 路由 + 模板挂载）、tests 目录、README.md。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-7.1: 应用可导入；`inv run` 首页 HTTP 200；grep 无 `from __future__ import annotations`。

## Task 8：网站知识树数据源（B-2）
- **Status**: `completed`
- **Completion Evidence**:
  - `src/gqlsite/knowledge.py`：frozen dataclasses Domain/Entry，11 域（home/health/diet/sleep/efficiency/finance/relation/mind/travel/digital/safety），每个条目按五要素组织，search() 大小写不敏感；
  - 复核：知识加载可枚举 11 域（≥10）且每域可检索（test_knowledge.py 覆盖）。
- **Priority**: high
- **Depends On**: T5, T7
- **Description**:
  - `src/gqlsite/knowledge.py` 加载知识树（结构化数据，与知识包 concepts 同源）；提供按域/按条目的检索接口。
- **Acceptance Criteria Addressed**: AC-8、AC-10
- **Test Requirements**:
  - `rule` TR-8.1: 知识加载函数可枚举 ≥10 域且每域可检索。

## Task 9：网站三验证信号（B-3）
- **Status**: `completed`
- **Completion Evidence**:
  - `src/gqlsite/signals/track.py`：SQLite（标准库）subscriptions/visits 表 + `RECOMMENDED_SLOT` 推荐位；`get_connection()` 读 GQLSITE_DB、默认 `.data/gqlsite.db`、失败回退 `:memory:`；
  - 复核：三信号测试覆盖（test_signals.py 订阅写入/访问埋点记录/推荐位占位），py314 下全绿（AC-9）。
- **Priority**: medium
- **Depends On**: T7
- **Description**:
  - `src/gqlsite/signals/track.py`：订阅/兴趣登记（POST → SQLite）+ 访问埋点（中间件/打点）+ 推荐位占位（静态配置）。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-9.1: POST 后 SQLite 出现订阅记录；埋点记录可见；推荐位配置可读。

## Task 10：网站 UI（暖灰纸感）（B-4）
- **Status**: `completed`
- **Completion Evidence**:
  - Jinja2 模板（base/index/domain/entry/search/subscribe/notfound）+ `static/styles.css` 最小 CSS；
  - 复核：styles.css 严格暖灰纸感（--bg #F5F3EF、--card #FFFDF9、--ink #3D3833、暖色强调、A/B/C 证据色标、软阴影、禁纯黑深色），匹配 AC-10 描述；最终浏览器渲染确认见 review.md。
- **Priority**: medium
- **Depends On**: T8
- **Description**:
  - Jinja2 模板 + 最小 CSS，实现"暖灰纸感"视觉（暖灰底、米白卡片、深灰褐文字、柔和层级、留白），阅读优先，禁用纯黑深色模式。
- **Acceptance Criteria Addressed**: AC-10、AC-8
- **Test Requirements**:
  - `rubric` TR-10.1: UI 视觉维度；scale 1-5；threshold >=4；浏览器预览截图 + 评审。

## Task 11：网站验证与测试闭环（B-5）
- **Status**: `completed`
- **Completion Evidence**:
  - 测试套件齐备：test_knowledge.py、test_signals.py、test_web.py、test_no_future_annotations.py、conftest.py（隔离 GQLSITE_DB）；
  - 复核：py314 下 `pytest tests/ -q` 37 个测试全绿，整体覆盖 96%（knowledge 100%、signals 96%）；ruff 通过；无 `from __future__` 残留。
- **Priority**: high
- **Depends On**: T9, T10
- **Description**:
  - 补齐 pytest 覆盖（>=80%，关键 >=90%）；跑 `inv check`/`inv test`；确认无 `__future__` 残留。
- **Acceptance Criteria Addressed**: AC-8、AC-9、NFR-6
- **Test Requirements**:
  - `rule` TR-11.1: pytest 全绿、覆盖率达标；三信号测试通过。

## Task 12：全库卫生与门禁（C-1）
- **Status**: `completed`
- **Completion Evidence**:
  - 手动等效验证已逐项执行并留痕 log.md V 门禁表格（UTF-8 strict ✅、双份 F 集合比对 ✅、concepts 7+references 2+根 index+log 共 13 文件一一存在 ✅、toctree 条目 Test-Path 全真 ✅、相对链接可达+零 file:/// ✅、frontmatter 齐备 ✅、零 .temp/家目录路径 ✅、无 `from __future__` ✅）；
  - 全库自动 check 脚本受外部阻塞（`invocations` 缺失 + `deepseek-harness` 引起的全库 toctree 冲突），按既有约定不强行修改外部依赖，以手动验证代偿。
- **Priority**: medium
- **Depends On**: T6, T11
- **Description**:
  - 执行手动等效验证（UTF-8 strict、相对链接、零 file:///、toctree 可达、frontmatter 齐备）；运行可用的 check 脚本并留痕；不提交（延续当前工作区约定）。
- **Acceptance Criteria Addressed**: AC-5、AC-2
- **Test Requirements**:
  - `rule` TR-12.1: 清单逐项打勾留痕 log.md；无 file:///、无 .temp 引用、UTF-8 无乱码。

## Task 13：Spec 三件套与独立审查（C-2）
- **Status**: `completed`
- **Completion Evidence**:
  - `review.md` 已创建（仅实施队列清空后），独立磁盘实读 + py314 实测复核全部 AC：
    - 规则类 AC-1~AC-9 全 PASS（各附证据）；rubric AC-10=4、AC-U1=4、AC-U2=5，均 ≥ 阈值；
    - Review R1 Result = **PASS**；审查注记 N1~N3（外部阻塞/待终确认/历史漂移）不阻断，N4（613→614 正文句）已修复；
  - Spec 三件套齐备：spec.md（approved）+ tasks.md（T1~T13 全 completed）+ review.md（PASS）。
- **Priority**: medium
- **Depends On**: T12
- **Description**:
  - 创建 `review.md`（仅队列清空后）；执行独立 Review（AC-U1/AC-U2/AC-10 rubric + 各 rule AC 复核）；记录 Review History。
- **Acceptance Criteria Addressed**: 全部 AC
- **Test Requirements**:
  - `rule` TR-13.1: review.md 存在且每条 AC/TR 被覆盖；Review R1 Result `pass`/`fail` 有据。
  - `note`: review.md 用独立审查报告格式，与既有 spec 目录一致（挂 audit-* 报告可选）。