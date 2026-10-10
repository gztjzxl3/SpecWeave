---
type: Tutorial
title: dsh-context 插件定位与四类入口
description: dsh-context 是 DeepSeek Harness 开源插件，用于把 AI Agent 上下文生命周期可视化；本页讲插件定位、四类查看入口与仓库体量。
sources:
  - id: wechat-article
  - id: github-repo
status: stable
stale_after: "2026-12-31"
---

# dsh-context 插件定位与四类入口

## 前置：DeepSeek Harness（DSH）是什么

DSH（DeepSeek Harness，npm 包 `@deepseek-ai/dsh`）是 DeepSeek 的 AI Agent 宿主运行时，支持插件扩展。dsh-context 就是运行在 DSH 上的一个插件，通过 `dsh plugin` 或 Add plugin 安装（详见 [01-install-and-support.md](01-install-and-support.md)）。如果你还没用过 DSH，本教程的"插件怎么做上下文可视化"对理解"Agent 上下文由什么组成"仍有启发。

## 插件是什么

`dsh-context` 是 **DeepSeek Harness（DSH）** 的一个开源插件，核心能力是**把 AI Agent 会话的上下文生命周期可视化**[F-001](../references/facts.md)。装上它，一次会话的上下文**由什么组成、后来怎么变、什么时候被压缩或剪枝**，都能直接看[F-003](../references/facts.md)。它不触碰模型的推理路径，只改变"看上下文的方式"（见解 M-1）。

仓库 `bowenliang123/dsh-context` 采用 Apache-2.0 许可证，验证时点约 **2.0k star、59 forks、902 commits**，处于高频活跃迭代[F-033](../references/facts.md)[F-043](../references/facts.md)。

## 四类查看入口

dsh-context 现在提供四个查看入口[F-004](../references/facts.md)[F-035](../references/facts.md)：

| 入口 | 面向场景 |
|------|---------|
| **Context Insights 页面** | 跨会话：看一段时间内所有会话的用量与画像 |
| **Context 标签页** | 单会话：钻进某个会话看完整上下文仪表盘 |
| **Context 面板（右侧栏）** | 对话同时从侧栏查看当前组成 |
| **`/context` 命令** | 聊天中临时弹窗看当前组成 |

这几个入口有重合，区别在**什么时候用**[F-004](../references/facts.md)：平常看当前会话用 Context 标签页；要看最近所有会话用量打开 Context Insights；`/context` 适合聊到一半随手看一眼（观点推进，四入口共享同一事实源，见见解 M-2）。

## 信源分层

- **事实**：安装命令、四入口、各观测面描述（已由 GitHub README 核验，见 [facts.md](../references/facts.md) 的 verified 部分）。
- **发布者观点**：文中"我感觉可以让 DSH 体验上升一个档次"、省 token 从工具数量/提示词/注入/任务拆分下手等，为公众号「AI开源无界」作者观点（author_claim，单源），不作为事实引用。
- **机制假设**：见 [knowledge-map.md](../references/knowledge-map.md) 的 Mechanism 层（hypothesis）。

## 一句话记忆

> dsh-context = DeepSeek Harness 的**上下文观测层插件**——四入口、共享官方 token-meter 投影，把黑箱 token 占用摊开成可审计的结构化视图。