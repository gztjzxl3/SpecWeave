---
type: Tutorial
title: dsh-context 观测面详解
description: dsh-context 的五大观测面——Context Insights、Context 标签页、Current Context、Context Trend、Context Browser，以及 File Activity 与 Agent Network；含估算与精确值的边界。
sources:
  - id: wechat-article
  - id: github-repo
status: stable
stale_after: "2026-12-31"
---

# dsh-context 观测面详解

本页逐一说明 dsh-context 的核心观测面。大部分描述来自公众号文章并经 GitHub 官方 README 核验[F-037~F-042](../references/facts.md)。

## 1. Context Insights — 跨会话用量总览

看一段时间内所有会话的情况[F-005](../references/facts.md)[F-037](../references/facts.md)：

- **KPI band**：会话数、计费 token、估算费用、缓存命中率（范围 7d / 30d / all）。
- **7 天用量图**：最近 7 天每天的计费 token 与估算费用柱状对。
- **活动热力图**：近几周每日活跃度，点某天可筛选当天活跃会话。
- **会话卡片**：每个会话的上下文组成环、token 数、轮次、估算费用，可按时间/token/上下文大小排序、按工作区分组。

> **费用精度边界**：费用按 models.dev 目录价估算，虽把 DeepSeek 峰谷价算入，"也就是看个大方向"，不一定绝对精准[F-007](../references/facts.md)。

## 2. Context 标签页 — 单会话完整仪表盘

单会话的 Context 标签页内容更全[F-008](../references/facts.md)[F-038](../references/facts.md)：上半部分是轮次、步数、工具调用、缓存命中率、token 去向和时间分配；往下还有当前窗口、趋势、浏览器、事件、文件活动和 Agent 网络。这些数据在同一页，不用来回切换。

**头部占用率/组成用的是 DSH 官方 token meter 的同一组投影数据**（`contextPressure` / `contextBreakdown`），所以和输入框旁的上下文环数字对得上[F-009](../references/facts.md)[F-039](../references/facts.md)。

## 3. Current Context — 当前窗口由什么组成

Current Context 用一条**多色堆叠条**展示当前上下文窗口[F-010](../references/facts.md)：系统提示、工具 schema、用户消息、注入内容、助手回复、工具结果分别占了多少，剩余空间用斜纹表示。

> 经常的情况是：上下文不够用时，**工具定义和工具结果经常占掉一大半，不一定是我们自己输入太多**[F-011](../references/facts.md)（发布者观点，但属实发场景）。插件会单独列出并标出占用最高的工具 schema。

## 4. Context Trend — 上下文如何随请求演变

Context Trend 把**每次模型请求**画成一根堆叠条[F-013](../references/facts.md)：可切 Step/Turn 粒度、总量/增量；**压缩和剪枝会标在对应柱子上**，上下文在哪一步变小、回收多少都能对齐位置。趋势图下有 step 摘要，写出用户发了什么、新进入上下文的内容、模型回复或调用的工具。

Delta 模式下，增长堆在基线上方，压缩往下掉——长会话发生过几次压缩，看图基本能对上[F-014](../references/facts.md)。

## 5. Context Browser — 打开任意请求"看内部"

Context Browser 可打开保留下来的请求，查看该次请求实际由哪些内容组成[F-015](../references/facts.md)：系统提示原文、工具 JSON schema、消息正文、工具结果参数/状态/返回值。助手回复可按 Thinking / Tools / Answer 筛选；图片以卡片展示（缩略图、尺寸、存储大小、DeepSeek 图像 token 估算）[F-016/F-042](../references/facts.md)。

- **工具来源标记**：工具 schema 尽量标出来源——官方 `tool-*` 包、`dsh-*` 能力包、某 MCP server、或插件注册的工具[F-017](../references/facts.md)[F-041](../references/facts.md)。工具多时能确认"每个工具来自哪里"。
- **Skill Injections 独立类目**：技能注入有独立分类，避免技能占用的上下文藏进注入/工具结果桶里蒙混[F-040](../references/facts.md)。
- **跨轮 diff**：可与上一轮做 diff，类目增减条数与 token 用徽标标出；压缩前的步骤从被移除消息归档重建，界面标"近似"，只能当参考[F-018](../references/facts.md)。

## 6. File Activity 与 Agent Network

- **File Activity**：按文件列出 Agent 操作（读/写/搜/处理图片），写操作估算新增删除行数，点开看完整操作记录，并跳回 Context Browser 对应工具结果。比自己翻一整串工具调用方便[F-019](../references/facts.md)。
- **Agent Network**：展示主 Agent、父级 Agent 与所有子 Agent。每个节点对应一个会话，环大小按窗口占用缩放，悬停看 token/请求数/费用/活跃时间，点进对应会话的 Context 标签页。多 Agent 会话可先看各 Agent 占用与调用关系[F-020](../references/facts.md)。

## 估算与精确值的边界（重要）

dsh-context 的组成分类数字**多为 DSH 固定密度启发式的估算值，不能当成精确测量**[F-012](../references/facts.md)。**钉住某一步**后，面板才会把 provider 上报的实际 prompt / output / cache 数字放在估算值旁边。需要准确数字时，**provider 上报的那部分更可靠**。这类工具想精准，只能官方出直调后端的工具，否则一律会有细微差别（见解 M-3）。