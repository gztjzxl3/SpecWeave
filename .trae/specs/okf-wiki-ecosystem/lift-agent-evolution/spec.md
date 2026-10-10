---
type: research-spec
title: "LIFT Agent 自我进化评测知识包"
source: "用户指定的微信公众号文章及 LIFT 官方仓库、论文和相关基准"
status: completed
---

# LIFT Agent 自我进化评测知识包

## 目标

把公众号文章《Agent 会越用越聪明吗？这个开源项目开始量化「自我进化」！》转化为可追溯的 OKF v0.2 中文教程。正文以 LIFT 的配对 Holdout 评测机制为主线，并明确区分页面事实、作者主张、官方实现和分析性洞察。

## 范围与边界

- 主题实体：LIFT（Loaded Impact on Holdout Final Task）评测框架。
- 来源范围：用户提供的公开文章、LIFT 官方 GitHub 仓库及其文档/论文、相关 Agent 自进化评测论文。
- 不复刻文章全文，不把作者观点升级为领域共识，不宣称 LIFT 是首个或唯一的 Agent 自进化基准。
- 排行榜、仓库状态和论文版本均按 2026-10-10 可见内容描述；旧数据快照与当前仓库状态分开。
- 文章没有提供可独立复现的完整运行步骤，因此不建立 `examples/`。

## 归属判断

目标位置为 `projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/agent-self-evolution-evaluation/`。AI 工程实践分类已收录 Agent 评测方法论和 Agent 平台/工具散篇；本包聚焦“加载演化产物后，Holdout 最终任务是否改善”的特定评测问题，作为独立评测专题，不重复替代已有方法论包。

## 质量验收

- facts.md 中 F 编号连续，页面事实、作者主张、官方事实和相关工作分层。
- `references/article-source.md` 与 facts.md 的 F 编号及声明逐项一致。
- 关键统计、日期、官方定位和普遍性表述在 verification.md 中有 P0 核验结论。
- 至少三条 I 洞察具备结论、F 证据、反常识点和建议。
- 四视角 V 审查在知识包内留档，意见均有裁定；采纳项回归到正文。
- Bundle 各级 toctree、父级索引、总索引计数和链接通过项目门禁。

## 执行链路

七概念场景为知识沉淀，采用 `R→I→E→V`。用户未要求 Git 提交，因此不执行 C/commit。

## 补充核验

- 最终事实范围为 F-001 至 F-031；新增条目区分仓库与论文的 LIFT 缩写展开，记录 Warmup/Holdout requirements 约 75% 重合、`n_repeats` 与配对 task-repeats 的样本层级、`turns` 字段语义及核验时仓库提交。
- 排行榜聚合点估计按配对 task-repeats 汇总后计算；95% CI 按 repeat 级比例变化，以 `ddof=0` 标准差及正态近似计算。两种估计量不应混称。
- GitHub API 的 `license` 为 `null`，检查的仓库树未见 LICENSE 文件。因此 bundle 根状态为 `flagged`；已核验的单篇事实与概念页维持 `stable`，且根索引明确提示整体边界。
- V 审查记录 11 项针对性攻击及回归结果；本包未创建 `examples/`，因为文章不含独立执行者可照做并复核的完整剧本。
- 目录树门禁当前复算为 9 域、61 组、611 包；其中 `jishu` 456 包、`jishu/ai` 232 包、`practice` 20 包。最终门禁结果待执行后回填。
