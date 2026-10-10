---
type: spec
title: "Skills Manager 公众号文章 → OKF Wiki 知识包"
status: draft
created: 2026-10-10
skill: blog-article-to-okf-wiki
methodology: "seven-concepts: R→I→E→V→C"
content-sensitivity: public
source_url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg?from=industrynews&color_scheme=light#rd"
---

# Spec：Skills Manager 公众号文章 → OKF Wiki 知识包

## Why

将公开文章中对 Skills Manager 桌面产品的介绍转化为可追溯、可复核并带时效边界的 OKF v0.2 知识包。文章中的产品覆盖数量、版本、平台兼容性、备份与同步安全等信息存在不同来源口径，知识包必须区分文章陈述、官方资料和作者体验，不把未经核验的说法升级成确定事实。

## 1. 内容敏感度预检

- 来源为 `mp.weixin.qq.com` 公开文章；URL 不含 `share?code=`、`token=`、邀请码或其他访问控制特征。
- **判定：公开内容（Public）**。按标准文章转化流程规划；最终 bundle 写入用户指定的 `projects/awesome-okf-xs/doc/bundles/`。
- 文章原文仅作事实核对来源；产出以原创改写、短引文必要性控制和来源链接为原则，不镜像全文或未核验图片。

## 2. 归属位置分析

**暂定位置：** `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/skills-manager/`

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/products/` | 暂定选定 | 主线实体是面向 AI Skills 管理的桌面产品；现有分组已收录多种 AI 桌面工具、Agent 产品和任务型工具，语义匹配。 |
| `jishu/ai/practice/` | 不优先 | 文章主体是产品及其使用/管理能力，而非跨产品通用工程实践。 |
| 新建分组 | 否决 | 单篇文章不新建分组；遵循最小变更。 |

落盘前再次核对同名 bundle、产品分组语义及父级导航现值。当前子模块索引文件已有其他未提交修改；实施时必须保留并整合这些修改，不得覆盖或回滚。

## 3. 内容性质与骨架判定

文章涉及产品能力与操作场景；独立复核文章及官方资料后判定：

| 判据 | 当前结论 | 实施要求 |
|---|---|---|
| 读者是否能依文章照做安装、配置、备份或同步？ | 部分可以：文章提及平台、macOS 安装入口和界面路径，但没有完整逐平台流程。 | 只登记文章实际提供的路径；官方文档补充不冒充文章步骤。 |
| 操作是否有足够信息可复现（步骤顺序、输入/输出或可观察结果）？ | 否：未给版本、完整输入输出、测试环境、冲突处理及恢复验证步骤；作者未声明亲测。 | 不将概览扩写成实测示例或复现承诺。 |

两问未同时通过，**不创建 `examples/`**；采用产品机制与适用边界的概念型知识包。

## 4. What Changes

- 新建一个 Skills Manager OKF bundle，暂定路径为 `jishu/ai/products/skills-manager/`。
- 以独立事实登记和官方核验支撑概念文档；文章与核验来源均写入 frontmatter `sources`。
- 在本 Spec 中维护 `facts.md` 与 `knowledge-map.md`；bundle references 中保存来源清单、与 Spec 编号一致的 `article-source.md` 及核验报告。
- 按骨架判定结果创建或省略 `examples/`，不为满足“教程”字样而制造不可复现步骤。
- 更新 `jishu/ai/products/index.md` 的导航表、toctree 和分组数量。
- 更新 `doc/bundles/index.md` 中实际受影响的总数、域/组计数及描述；先读取届时磁盘现值并机械对账，兼容工作区中其他已存在的并行变更。
- 不修改其他既有 bundle 的正文，不提交 Git、不推送。

## 5. 事实核验重点

R 阶段至少核验并记录以下主题；最终范围以文章逐条事实登记为准：

- 产品名称、开发/维护主体、开源状态、当前发布版本与支持平台。
- 文章所称“54 个工具”等覆盖数量，与产品官网、仓库元数据、README 和 Releases 的统计口径差异。
- Windows junction 的使用条件、权限要求及 WSL 支持边界。
- 技能安装/管理界面与 CLI 的能力范围。
- Git 备份、跨设备同步、冲突处理、快照和设备认证/凭证存储机制。
- 文章提及的备份大小限制及其适用范围。
- 作者个人经历、体验或对产品成熟度的评价，均标为作者观点/体验，不写成官方事实。

截至 2026-10-10 的复核快照中，GitHub 仓库 API 描述为“50+ coding tools”，官方英文 README 的 `Supported Tools` 明确称支持“54 agents ... out of the box”，与文章的 54 数字相互支持；但 API 的 “coding tools” 与 README 的 “agents” 术语不同，不推断其统计对象完全相同。README 快照对应提交 `9e03d833829bc5e004263f61dec75f3bc8e39062`。同日重新读取的 `/releases/latest` API、Release 列表首项和网页 `/releases/latest` 均指向 `v1.40.3`（发布于 2026-10-01）；旧 Spec/bundle 中 `v1.22.1`、`v1.28.3`、`v1.17.0` 的差异记录已被本轮新快照取代。动态接口的结论仅代表本次观测，不构成长期版本保证。

## 6. ADDED Requirements

### Requirement: 事实登记与核验可追溯

- spec `facts.md` 从 F-001 开始登记文章事实、作者观点和核验补充，逐条记录来源距离、原文位置/主题及 P 级。
- spec `knowledge-map.md` 记录归属判断、examples 两问、概念篇目映射及有四元组的执行者洞察。
- bundle references 包含 `source-manifest.md`、`article-source.md` 与 `verification.md`；bundle 与 spec 的事实编号集合必须连续且完全一致。
- 数字、日期、版本、兼容性、安全机制与限制均作为 P0 核验对象；查无权威证据时标注“仅文章单源”或“未能核实”，禁止编造来源。
- `references/article-source.md` 与 spec `facts.md` 的编号集合必须连续且完全一致；若采用显式跳号，须注明原因。

### Requirement: 知识结构与可复现边界

- concepts 至少覆盖：产品定位与已核实事实、Skills 管理/备份同步机制、平台兼容与安全边界。
- 是否创建 examples 严格由“操作可复现性两问”决定；任何未实测流程不得表述成亲测结果。
- 作者观点、产品官方说明、第三方页面和本次推断须在正文中清晰区分。

### Requirement: 时效与来源声明

- bundle 根索引及相关内容使用 OKF v0.2 frontmatter；`sources` 同时包含文章 URL 与实际用于核验的官方来源。
- `status`、`stale_after` 与已知边界反映核验结果和产品版本快速变化风险。
- 对无法裁决的版本/数量口径差异，保留并列证据和时间戳；若文章核心声明出现 P0 失败，按转化规范设置 `status: flagged` 并在索引顶部警示。

### Requirement: 导航、计数与质量门

- bundle 每个目录索引均以 `{toctree}` 覆盖全部内容文件；无孤立文档、无不可达相对链接、无 `file:///`。
- 产品分组导航表与 toctree 一致；全库 frontmatter、正文计数及分组/域计数须与届时目录树一致。
- 实施结束执行 `invoke gates.toctrees`、`invoke gates.utf8` 和 `invoke gates.bundles`；命令不可用时执行文章转化规范要求的手动等效检查，并如实记录未运行的门禁。

### Requirement: 保留并行工作区修改

- 对 `projects/awesome-okf-xs` 现有未提交文件只做必要的局部合并；不重置、不覆盖、不提交与本任务无关的修改。
- 总量变更以实施时重新扫描的磁盘状态为准，不以当前暂存/未提交计数推算。

## 7. Constraints

- 产出语言为中文，Markdown 文件名使用 kebab-case。
- 只使用原文中必要的短引文；以原创结构化表达替代逐段改写，不复制文章全文或图片。
- 所有具体产品声明均须关联 F 编号；操作说明须给出相应来源和适用版本。
- C 阶段做交付完整性核对；未经用户另行明确授权，不执行提交或推送。

## Acceptance Criteria

### AC-1: 来源和事实可追溯
- **Type**: `rule`
- **Given**: bundle 的事实与概念文档已完成
- **When**: 对照 spec `facts.md`、`article-source.md` 与文内声明
- **Then**: 每条具体声明有 F 编号，双份编号集合连续且一致，作者观点和未核实声明有明确标签
- **Pass Condition**: 所有具体声明可回溯到登记事实及对应来源；不存在无依据的数字、版本、功能或兼容性断言
- **Evidence**: 机械编号比对结果与逐篇审查记录

### AC-2: 结构符合内容性质
- **Type**: `rule`
- **Given**: 文章操作内容已完成两问判定
- **When**: 生成 bundle 骨架
- **Then**: 仅在两问皆为“是”时包含 `examples/`，否则在 spec 与 bundle 中记录不设该目录的理由
- **Pass Condition**: 实际目录结构与两问判定一致；没有伪造的步骤或未经标注的未实测教程
- **Evidence**: facts、spec 知识地图、bundle 文件树及 examples（若适用）

### AC-3: 导航和计数一致
- **Type**: `rule`
- **Given**: bundle 与索引更新已完成
- **When**: 运行子项目质量门或等效手动验证
- **Then**: 所有 toctree、相对链接、UTF-8 和 bundles 计数核验通过
- **Pass Condition**: 三项 invoke gates 全部通过；若环境不支持 invoke，则等效检查逐项通过且 log 明确说明替代方式
- **Evidence**: 命令输出或逐项手动验证记录

### AC-4: 内容可信度和时效边界清晰
- **Type**: `rubric`
- **Dimension**: 事实准确性、来源分级、冲突口径和时效限制的表达质量
- **Scale**: 1-5
- **Anchors**: 1 = 核心产品事实无来源或照搬矛盾口径；3 = 主要事实有来源但存在遗漏/边界含混；5 = P0 逐项核验，冲突并列且有时点，观点、官方事实和推断清晰分层
- **Pass Threshold**: >= 4
- **Evidence**: verification.md、bundle 根索引已知边界及 V 阶段独立检查

## Open Questions

- [ ] R 阶段核验后确认产品分组与最终目录名；若发现产品官方品牌写法要求不同，仅调整 bundle slug，不新增分组。
- [x] 根据文章全文和核验来源最终决定是否有可复现 examples：两问未同时通过，不创建 `examples/`。
- [x] 更新版本与数量口径：记录仓库 API“50+ coding tools”、README“54 agents”及文章“54”；三个 Release 视图经 2026-10-10 复核均指向 `v1.40.3`，保留字段口径和动态快照边界。
