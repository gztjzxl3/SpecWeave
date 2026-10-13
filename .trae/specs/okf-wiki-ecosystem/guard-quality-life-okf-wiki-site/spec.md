# 《守护品质生活》复合交付（OKF Wiki 知识包 + FastAPI 变现 MVP 网站）- 产品需求文档

## Overview

- **Summary**：以「守护品质生活」为自有主题，用 seven-concepts-cmd「知识沉淀」链路（R→I→E→V→C）全面调研并产出两部分交付物：① 一个结构完整、事实可溯源的 OKF v0.2 知识包（bundle），系统讲透「生活方式方案库」维度下家居/健康/饮食/效率等 10+ 域的可操作建议方法论；② 一个基于 Python 3.14+ / FastAPI 的动态 Web 服务 MVP 网站，承载该知识树，并埋入订阅/兴趣登记、推荐位占位、访问埋点三项验证信号，用于验证可变现方向。
- **Purpose**「守护品质生活」是用户的自有宣传口号/主题（非单一文章），首期定位为**生活方式方案库**：把"如何守护日常品质生活"做成有证据支撑、可按域检索、可执行的方案知识树。知识包负责"硬核、可溯源、方法论"；网站负责"可访问、可交互、可验证变现"。二者共享同一来源知识树：网站渲染知识包的域与条目，知识包反哺网站的内容权威性。
- **Target Users**：① 追求可操作、有依据的生活方式建议的普通人（家居/健康/饮食/效率等领域）；② 想系统理解"守护品质生活"方案体系的中文读者；③ 潜在付费订阅用户（网站验证信号的目标人群）。

## Goals

- G1：产出一个结构完整、事实可溯源的 OKF v0.2 bundle，落位于 `projects/awesome-okf-xs/doc/bundles/` 下的合适分组（归属判定见 Background）。
- G2：知识树覆盖 10+ 个域（家居、健康、饮食、效率、睡眠、财务、关系、心理、出行、数字生活等），每域给出可操作建议条目，且事实有 F 编号支撑。
- G3：方法轮讲透——每域给出"证据分级 + 可执行 SOP + 成本收益 + 禁忌/边界"的表达框架，读者能迁移框架评估任意生活建议。
- G4：产出 FastAPI 动态 Web 服务 MVP（Python 3.14+，scikit-build-core，src 布局，invoke 管理），独立应用落于 `apps/`。
- G5：网站承载知识树（按域浏览 + 条目详情），支持搜索/检索，阅读体验遵循用户"暖灰纸感"偏好。
- G6：埋入三项验证信号——订阅/兴趣登记、推荐位占位、访问埋点（轻量、可扩展、不依赖重型外部服务）。
- G7：P0 关键事实完成权威交叉核验；机械门禁（UTF-8、双份 F 编号、相对链接、toctree）逐项留痕。

## Non-Goals

- N1：**不复制任何第三方文章/书籍全文**——「守护品质生活」是自有主题，产出的知识都是原创整合与通用生活常识的可执行表达，不搬运受版权保护内容。
- N2：不做医学/法律/财务**专业建议**——所有健康/法律/理财条目均为"通用生活常识的可执行转述 + 边界声明"，重大决策指引读者咨询专业人士与官方渠道。
- N3：MVP 网站**不接重型外部服务**（不强制数据库、不做登录体系、不做支付集成）——验证信号用轻量本地文件/SQLite + 静态占位实现，便于后续替换。
- N4：不实现完整商业化（无真实订阅计费、无推荐算法、无付费墙）——本期只验证"有没有人感兴趣"。
- N5：不执行任何 git commit / push（延续当前并行工作区约定）；C 阶段仅在 log.md 记录交付清单。
- N6：不修改 submodule `projects/awesome-okf-xs` 之外无需变更的内容；不动任何 `.agents/` 规范。

## Background & Context

### 内容敏感度预检（步骤 2.3）

- 「守护品质生活」为**用户自有主题**（公开、非敏感），不涉及私域/内部/含访问控制的素材 → **公开内容，标准工作流**。
- spec 落 `.trae/specs/okf-wiki-ecosystem/guard-quality-life-okf-wiki-site/`；知识包产出落 `projects/awesome-okf-xs/doc/bundles/`；网站产出落 `apps/`（均为仓库内可直接维护的公开位置）。

### 归属位置分析（知识包步骤 3 决策树）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| **sheke/personal-growth（推荐）** | ✅ | 主线是"用可执行方案提升生活品质"，跨家居/健康/饮食/效率/睡眠/财务/心理，与既有 personal-growth 分组（female-charm-eq / male-charm-eq / how-to-live-better）主题簇一致，可互链 |
| sheke/workplace | ❌ | 仅当效率域占主导时，但主线远超职场 |
| yixue 医学与养生 | ❌ | 该域为中医经典/养生元典，本书是现代可执行生活方式，语义不符 |
| 新建生活域分组 | ❌ | 技能铁律：单主题禁止新建分组（过度工程），先并 personal-growth |

- bundle 目录名：`guard-quality-life`（kebab-case，与主题口号一致）。
- 组内互链：与 how-to-live-better / female-charm-eq / male-charm-eq 互链（同属"用证据优化个人生活"主题簇）。

### 骨架判定（知识包步骤 2：操作可复现性两问）

- 本知识包主题是**生活方式方案库**（可操作建议集合），核心交付是"框架 + 分域条目 + 可执行 SOP"，非"安装/配置/代码/实测"类硬核流程。
- 两问之一（有无读者可照做的安装/配置/实测 SOP）→ 部分满足（网站本身可作为可复现产物），但知识包主体是建议而非操作手册。
- **结论**：知识包**不设 examples/**（属知识沉淀场景，操作细节写进 concepts 作为可执行条目）；网站部分则以 `apps/` 内可运行 FastAPI 应用作为"可复现操作"的载体。

### 知识树骨架（I 阶段三层拆分）

```
guard-quality-life/                          # bundle 目录（projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/）
├── index.md                        # 根索引：性质声明/知识结构/信任与边界/互链
├── log.md                          # 生成日志（R→I→E→V→C 链路记录）
├── concepts/
│   ├── index.md                    # 学习路径 + toctree
│   ├── 00-framework.md             # 事实层：守护品质生活的核心理念、证据分级、成本收益框架
│   ├── 01-domains.md               # 导航层：10+ 域总览（Mermaid 域图 + 每域一行：主题/SOP/代表条目）
│   ├── 02-home.md                  # 应用层：家居域（清洁/收纳/安全/舒适）可执行方案
│   ├── 03-health.md                # 应用层：健康域（睡眠/饮食/运动/筛查，非医疗建议边界）
│   ├── 04-efficiency.md            # 应用层：效率域（时间/习惯/数字生活）
│   ├── 05-finance-relations-mind.md# 应用层：财务+关系+心理域（非投资/沟通边界/非心理诊断）
│   └── 06-how-to-use.md            # 迁移层：如何用这套框架评估任意生活建议 + 网站导引
└── references/
    ├── index.md                    # toctree
    ├── article-source.md           # F 编号事实登记（自有主题原创整合 + 通用常识引源）
    └── verification.md             # P0 核验报告（边界声明 + 常识性主张的审慎标注）
```

### 网站 MVP 骨架（Python 3.14+ FastAPI）

```
apps/guard-quality-life-site/       # 独立应用（Apps 区域，scikit-build-core，src 布局）
├── pyproject.toml                  # scikit-build-core 构建后端 + Python >=3.14（禁止 __future__ annotations）
├── tasks.py                        # invoke 任务：run / check / setuptest 等
├── src/
│   └── gqlsite/
│       ├── __init__.py
│       ├── main.py                 # FastAPI 应用入口（路由/静态/模板）
│       ├── knowledge.py            # 知识树数据加载（读取 bundle concepts 或内置结构化数据）
│       ├── signals/
│       │   └── track.py            # 访问埋点 + 订阅/兴趣登记（SQLite 轻量存储）
│       └── templates/  static/     # 暖灰纸感 UI（Jinja2 + 最小 CSS，无重型前端框架）
├── tests/                          # pytest 覆盖（>=80%，关键 >=90%）
└── README.md                       # 应用说明 + 启动方式
```

## Functional Requirements

### A. 知识包（OKF Wiki bundle）

- **FR-1（R 事实）**：spec 配 `facts.md`（与既有 okf-wiki 规格一致），完成 F-001 起连续编号登记，覆盖自有主题的方法论规则、分域条目结构、每个可执行 SOP 与边界声明；通用生活常识引源标注（官方机构/权威指南）；作者观点/价值判断显式标注。
- **FR-2（R 核验）**：P0 清单逐项核验并记录 ✅/⚠️/❌：① 健康/安全类声称（如睡眠时长指南、疾控洗手/饮食建议、安全检查频率）对照权威机构（WHO/CDC/各国官方健康指南）；② 强时效数字（若有）带"截至 2026-10"时点；③ 边界声明齐备（非医疗/法律/财务建议）。
- **FR-3（E 信源先行）**：先写 references/ 两篇，再写 concepts/，各级 index 最后写；具体数字/机构名必须可回溯到 F 编号，禁止 facts 集外生造。
- **FR-4（E 分域执行）**：concepts 按"框架→域总览→每域可执行 SOP"递进；每域条目含"目的/可执行步骤/成本收益/证据级/禁忌边界"五要素。
- **FR-5（V 门禁）**：执行七概念技能 §7 手动等效验证清单（UTF-8 strict、双份 F 编号集合比对、toctree 逐一 Test-Path、相对链接全可达、frontmatter 齐备），结果写入 log.md。
- **FR-6（索引）**：personal-growth/index.md（束数更新）、sheke/index.md（域计数）、bundles/index.md（total_bundles/mermaid/导航表）三面对账。
- **FR-7（边界与前端）**：bundle index 顶部含性质声明（原创整合/非专业建议/时点声明）；frontmatter 含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources。
- **FR-8（语言与格式）**：正文中文、文件名 kebab-case 英文；Mermaid 遵守安全编码；不使用 `file:///`；不使用 `from __future__ import annotations`。

### B. 网站（FastAPI MVP）

- **FR-9（应用落地）**：独立应用落 `apps/guard-quality-life-site/`，scikit-build-core 构建后端，src 布局，invoke 任务管理，Python >=3.14。
- **FR-10（知识树呈现）**：网站按域浏览 + 条目详情，内容与知识包同源（由知识包 concepts 结构化数据源生成或引用）。
- **FR-11（三验证信号）**：① 订阅/兴趣登记（表单 POST → SQLite 落库存 root）；② 推荐位占位（页面预留推荐/赞助位，静态配置占位）；③ 访问埋点（每次访问/浏览写入轻量日志表，前端打点或中间件埋点）。
- **FR-12（UI 视觉）**：遵循用户"暖灰纸感"偏好（暖灰底色、米白卡片、深灰褐文字、柔和层级、留白节奏，贴合 Notion/Obsidian 工作台感）；**不使用纯黑/高对比深色模式**。
- **FR-13（可运行性）**：`inv run` 可本地启动服务并访问首页；README 给出启动/测试/停止说明。

## Non-Functional Requirements

- **NFR-1 可审计性**：知识包每个具体声明可在 2 跳内到达信源（正文 → article-source F 行 → 引源/边界）。
- **NFR-2 忠实度**：数字与常识引源一致；"可执行改写"须可识别为改写而非新事实；不虚构研究/数据。
- **NFR-3 防过期设计**：易变数字带"截至 2026-10"时点；提供"返回官方来源核对"的明确链接。
- **NFR-4 网站轻量可扩展**：无重型外部服务；SQLite 存储 + 静态占位；验证信号为独立模块，未来可替换为真实订阅/推荐/分析服务。
- **NFR-5 最小变更**：除新 bundle/新应用/三处索引计数外不改动既有文件内容；不动任何 `.agents/` 规范。
- **NFR-6 代码红线**：Python 3.14+；新建 Python 文件禁止 `from __future__ import annotations`；pytest 覆盖不低于 80%（关键 ≥90%）。

## Constraints

- **Technical**：知识包产出在 git submodule `projects/awesome-okf-xs/` 内（遵循 OKF v0.2 规范）；网站产出在 `apps/` 主仓库内（scikit-build-core）；当前 submodule 可能处于并行 rebase 状态，**写操作前须确认其稳定**（见 Assumptions A3）。
- **Business / 合规**：独立主题原创整合，不搬运受版权内容；健康/法律/财务内容加免责声明。
- **Dependencies**：Python 3.14+（本地 `py314` conda 环境）；FastAPI/Uvicorn/Jinja2/Starlette（模板）+ httpx/pytest 测试栈；无需重型数据库/云服务。
- **流程**：Spec Mode 五阶段（Specify→Plan→Approve→Implement→Review）；七概念场景 4（R→I→E）+ 强制 V；review.md 仅 Review 阶段创建（遵循 AGENTS.md 权威，**不创建 checklist.md**）。

## Assumptions

- A1：用户已确认五项决策——主题为"自有主题·守護品质生活"（非文章）；首期定位"生活方式方案库"；深度"较完整知识树（10+ 域）"；验证信号三项全埋（订阅/兴趣登记、推荐位占位、访问埋点）；技术栈"纯 Python 栈（FastAPI）"。
- A2：部署形态按"动态 Web 服务"默认（纯 Python FastAPI 可本地运行，供后续部署）。
- A3：知识包写操作须在 `projects/awesome-okf-xs` submodule 稳定（非 rebase/非索引冲突）后进行；若处并行 rebase 状态，先暂停相关写操作并等待解除（延续此前 session 教训）。
- A4：P0 核验中若个别常识性声称仅能建立单链引源，明确标"单源（官方机构）"，不硬编。

## Acceptance Criteria

### AC-1：知识包结构与 OKF 规范完整（rule）

- **Given**：bundle 落位于 `projects/awesome-okf-xs/doc/bundles/<归属>/guard-quality-life/`
- **When**：列目录并读取每个 index.md
- **Then**：存在 index.md、log.md、concepts/index.md + 7 篇概念文档（00–06）、references/index.md + article-source.md + verification.md；不存在 examples/；根 index 与两个子目录 index 均含 toctree 块且条目逐一对应实际文件
- **Pass Condition**：目录树与骨架清单逐文件一致；每个 toctree 条目（排除 `:` 指令行）Test-Path 全部为真
- **Evidence**：目录清单 + toctree 核对记录（写入 log.md 与 review.md）

### AC-2：F 编号双份一致且覆盖关键事实（rule）

- **Given**：spec facts.md 与 bundle references/article-source.md
- **When**：用正则 `^\|\s*F-(\d{3})\s*\|` 分别提取两份编号集合
- **Then**：两集合相等、从 F-001 连续无跳号（跳号须有显式注记）；FR-2 的 P0 声明在 facts.md 均有对应 F 行
- **Pass Condition**：集合比对零差异；P0 清单逐项可在 facts.md 定位
- **Evidence**：比对输出附入 verification.md/log.md

### AC-3：P0 核验闭环（rule）

- **Given**：FR-2 的 P0 清单（健康/安全类声称 + 时点 + 边界）
- **When**：逐项检索权威机构（WHO/CDC/各国官方健康指南）
- **Then**：verification.md 给出每项 ✅/⚠️/❌ 结论、引源 URL、口径差异；无法外部核验项明确标"仅单源/常识性"，无硬编 URL
- **Pass Condition**：P0 清单每项有结论与引源（无法核验项明确标注，数量与原因可见）
- **Evidence**：verification.md P0 总表 + 正文落点抽查

### AC-4：三级索引接入与计数同步（rule）

- **Given**：新增 1 个 bundle
- **When**：读取 personal-growth/index.md、sheke/index.md、bundles/index.md
- **Then**：personal-growth total_bundles 递增且 toctree 含 guard-quality-life/index；sheke 域束数递增；bundles/index.md total_bundles 与 mermaid/导航表一致
- **Pass Condition**：三面（frontmatter total_bundles / 计数行 / 分组表束数列 / toctree）三角对账无差异
- **Evidence**：计数前后对照

### AC-5：链接、编码与卫生门禁（rule）

- **Given**：全部新增/修改 .md
- **When**：执行手动等效验证
- **Then**：UTF-8 strict 无乱码；Markdown 相对链接逐一可达；零 `file:///`；零家目录绝对路径；无 `.temp/` 引用
- **Pass Condition**：清单逐项打勾并在 log.md 留痕
- **Evidence**：log.md 门禁段

### AC-6：边界与时效声明落实（rule）

- **Given**：bundle 根 index 与 concepts 相应篇
- **When**：检查声明内容
- **Then**：含"非医学/法律/财务专业建议、重大决策咨询专业人士"声明；易变数字带 2026-10 时点；frontmatter 含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources
- **Pass Condition**：声明要素逐项可指认
- **Evidence**：index.md/concepts 篇/frontmatter 片段

### AC-7：知识树完整性与分域执行（rule）

- **Given**：concepts 域篇
- **When**：逐域核对
- **Then**：域总数 ≥10（家居/健康/饮食/效率/睡眠/财务/关系/心理/出行/数字生活等）；每域条目含五要素（目的/步骤/成本收益/证据级/禁忌边界）；条目与 F 编号对应；不出现超出源范围的硬断言
- **Pass Condition**：域数达标；抽查 5 个条目五要素齐备且引源逐字一致
- **Evidence**：域计数表 + 抽查记录

### AC-8：网站应用可构建可运行（rule）

- **Given**：`apps/guard-quality-life-site/`
- **When**：执行 `python -c "import gqlsite"` 并运行 `inv run`（或等价 pytest 冒烟）
- **Then**：应用可导入；本地服务可启动且首页返回 200；README 文档完整
- **Pass Condition**：导入无异常；首页 HTTP 200；无 `from __future__` 残留（grep 空）
- **Evidence**：pytest 输出 + 启动访问记录 + grep 结果

### AC-9：三验证信号可用（rule）

- **Given**：网站跑起
- **When**：POST 订阅表单 + 浏览页面
- **Then**：订阅/兴趣登记写入 SQLite；推荐位占位渲染且配置可读；访问埋点记录可见
- **Pass Condition**：三信号各自可验证（表存在且有记录）
- **Evidence**：SQLite 表查询记录

### AC-10：UI 视觉合规（rubric）

- **Type**：rubric
- **Dimension**：阅读优先与暖灰纸感（非纯黑/高对比深色；层级柔和、留白舒适）
- **Scale**：1–5
- **Anchors**：1 = 默认白/黑模板无定制；3 = 有基础暖色调但层级生硬；5 = 完整暖灰纸感（暖灰底、米白卡片、深灰褐文字、柔和层级、留白节奏，贴近 Notion/Obsidian 工作台）
- **Pass Threshold**：≥ 4
- **Evidence**：浏览器预览 + 独立评审截图

### AC-U1：教程与方案质量（rubric）

- **Type**：rubric
- **Dimension**：知识包教学质量（读者能否理解框架→会用每域 SOP→能迁移框架评估任意生活建议）
- **Scale**：1–5
- **Anchors**：1 = 资料堆砌/无框架；3 = 信息完整但需自行串联；5 = 七篇形成"框架→域总览→分域 SOP→使用"清晰路径，示例真正教会方法
- **Pass Threshold**：≥ 4
- **Evidence**：独立评审通读意见

### AC-U2：事实与观点分层质量（rubric）

- **Type**：rubric
- **Dimension**：可信度表达（事实/常识/作者观点分层，数字时点与边界标注）
- **Scale**：1–5
- **Anchors**：1 = 观点混入事实、数字无时点；3 = 主要分层正确但偶有混淆；5 = 每条断言层级清晰，来源/边界/反方齐备
- **Pass Threshold**：≥ 4
- **Evidence**：独立评审抽查 + verification.md 对照

## Open Questions

- 无阻塞性开放问题（关键决策已由用户确认）。实施中若 P0 出现"核心声称❌"，按技能 flagged 管理：frontmatter `status: flagged` + 顶部明示，并在通知用户后继续。
- 网站部署形态默认"本地可运行动态服务"，具体线上部署（域名/托管）后续再定，本期不纳入。