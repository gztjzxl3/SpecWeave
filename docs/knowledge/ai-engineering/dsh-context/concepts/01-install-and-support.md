---
type: Tutorial
title: dsh-context 安装方式与兼容矩阵
description: dsh-context 的两种安装方式（Add plugin 向导 / CLI）、更新命令、兼容矩阵与 Node 要求、装前安全提醒；含兼容矩阵时效口径。
sources:
  - id: wechat-article
  - id: github-repo
status: stable
stale_after: "2026-12-31"
---

# dsh-context 安装方式与兼容矩阵

## 两种安装方式

README 提供了两种安装方式，均与 GitHub 官方 README 逐字一致[F-021~F-024](../references/facts.md)。

**方式一：Web/桌面端 Add plugin**

在 DeepSeek Harness Web 或桌面端里，打开 **Add plugin**，搜索 `dsh-context`，点击 **Install**[F-021](../references/facts.md)。

**方式二：`dsh` CLI**

```bash
dsh plugin --profile web add dsh-context
```

更新命令：

```bash
dsh plugin --profile web update dsh-context@latest
```

装完用 `dsh web` 启动 Web UI。README 说**无需手动构建，也无需额外重启**[F-024](../references/facts.md)。

## 兼容矩阵与 Node 要求

关于运行环境，文章与 README 给出两条约束[F-025][F-026](../references/facts.md)：

- **DSH 版本兼容矩阵**：覆盖 `@deepseek-ai/dsh` 0.1.5-rc.1、0.1.7-rc.2、0.2.0-rc.2 三条版本线。
- **Node 要求**：`^22.19.0` 或 `>=24.0.0`。

> ⚠️ **时效口径（双口径）**：文章所述的"覆盖 0.1.5-rc.1"是**文章时点**口径。验证时点（2026-10-10）仓库最近提交显示：上游官方已于 **2026-10-07** 起"drop dsh 0.1.5-rc.1，把支持矩阵下限移到 0.1.7-"[F-043](../references/facts.md)。因此**若你还在更旧 DSH 版本上，建议先升级**，并以前述验证时点为准。Node 要求为单源（未取 npm manifest 独立复核），标 `single-source`，见 [verification.md](../references/verification.md)。

## 装前安全提醒

插件本身是本机跑的**第三方代码**。官方 README 与文章都提醒：装之前最好**翻翻源码、依赖，看仓库还活不活跃**[F-027](../references/facts.md)。这个提醒不只针对 dsh-context，其他 DSH 插件也一样。

## 结论速览

| 议题 | 结论 |
|------|------|
| 推荐安装方式 | Web 端 Add plugin 搜索最省事；CI/脚本身用 CLI |
| 版本核对要点 | 用 `dsh plugin update dsh-context@latest` 拉新；留意兼容矩阵下限（2026-10-07 起 0.1.7-） |
| 前置检查 | Node ≥ 22.19（推荐 ≥ 24）+ 翻源码看活跃度 |