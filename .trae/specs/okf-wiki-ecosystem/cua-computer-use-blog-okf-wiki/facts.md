---
okf_version: "0.2"
type: facts
title: "Cua Computer-Use 博文事实采集清单"
source: "https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg"
blog: { account: "FinOps实战", published: "2026-09-26T15:53:00+08:00", words: 4723 }
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-10T10:40:00+08:00" }
---

# 事实采集清单（F 编号）

> R 阶段唯一合法事实集。类型：`O`=客观事实，`V`=作者观点/体验，`S`=厂商自述（经博文转述）。
> 信源距离：博文一手 / 第三方综述 / 厂商自述 / 官方核验。核验级：P0 必核验 / P1 选核验 / P2 可单源。
> 核验结论：✅ 与官方一致 ｜ ⚠️ 口径/时效差异（见 verification.md 勘误）｜ ➖ 无需外部核验。
> F-001~F-053 来自博文（F-041~F-053 为作者评价/观点）；F-054~F-065 为 2026-10-10 官方核验补充事实。

## A. 博文元信息

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-001 | O | 博文标题：《开源精选 | Cua：给 AI Agent 一台能用的电脑，Computer-Use 2.0 开源全栈》 | 博文一手 | P2 | ➖ |
| F-002 | O | 发布公众号「FinOps实战」，发布时间 2026-09-26 15:53，正文约 4,723 字符 | 博文一手 | P2 | ➖ |
| F-003 | O | 博文推介项目 Cua，给出仓库地址 github.com/trycua/cua，栏目为「开源精选」 | 博文一手 | P0 | ✅ F-054 |

## B. 项目身份与理念（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-004 | O | Cua（读作 /kjuːə/）由 Cua AI, Inc. 开发，采用 MIT 协议，仓库位于 github.com/trycua/cua，官方口号「Give AI agents computers they can use」 | 第三方综述 | P0 | MIT✅ F-056；主体⚠️ F-054（GitHub owner 为 org trycua） |
| F-005 | O | Cua 不是大模型也不是聊天框架，而是一整套面向 Computer-Use 场景的基础设施：开源桌面自动化驱动、隔离云桌面集群、本地 macOS 虚拟机、专用决策小模型、评测基准 | 第三方综述 | P1 | ✅ F-062/F-063 |
| F-006 | O | 博文称 AI Agent 操作真实电脑面临三大难题：①没有安全隔离的执行环境；②缺少跨 macOS/Windows/Linux 的统一自动化接口；③没有标准化评测手段 | 第三方综述 | P1 | ✅（官方定位一致） |
| F-007 | O | Computer-Use 2.0 理念：Agent 应能在同一个任务中自由穿梭于代码、API 和图形界面之间 | 第三方综述 | P0 | ✅ F-062（官方 README 同义定义） |
| F-008 | O | 官方 README 副标题：Scale computer-use 2.0 with open-source drivers, cross-OS fleets, and benchmarks for training, evaluation, and data generation. | 厂商自述（经博文转述） | P0 | ✅ F-056（GitHub description 逐字一致） |
| F-009 | O | 博文称 Cua 同时服务三类人群：做 Agent 产品的工程师（Driver）、做模型训练的研究员（Fleets+Bench）、做安全隔离运维的团队（Lume/Fleets） | 第三方综述 | P1 | ✅ |

## C. 五大核心模块（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-010 | O | Cua Driver：跨系统桌面自动化驱动，让 Agent 检查并操作 macOS/Windows/Linux 原生应用和浏览器，支持 CLI、MCP、类型化 SDK 三种接入方式；「后台投递」能力在应用与平台支持前提下不抢占鼠标指针和窗口焦点 | 第三方综述 | P0 | ✅ F-062 |
| F-011 | O | Cua Fleets：隔离云桌面集群；Fleet 维护一池沙箱容量，代码从池中认领桌面，用 Sandbox SDK 跑命令/截屏/操作应用，用完即弃 | 第三方综述 | P0 | ✅ |
| F-012 | O | Lume：基于 Apple Virtualization.Framework 的本地虚拟机工具，在 Apple Silicon 上创建和管理 macOS/Linux 虚拟机，适合本地开发和数据生成 | 第三方综述 | P0 | ✅ F-062 |
| F-013 | O | CUA-S1：官方自研小型专用「System 1」决策模型家族，主打表单场景，对结构化界面元素和文档取值做快速打分决策而非逐 token 生成回复；源码 MIT 开源，模型权重托管在 Hugging Face | 第三方综述 | P0 | ✅ F-063 |
| F-014 | O | Cua Bench：评测基准工具，用于构建 computer-use 任务、评估 Agent 表现、导出训练轨迹，形成「数据生成→训练→评估」闭环 | 第三方综述 | P0 | ✅ |

## D. 许可证透明度（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-015 | O | 主项目 MIT；第三方组件逐一列明：Kasm 是 MIT、OmniParser 是 CC-BY-4.0、可选的 cua-agent[omni] 包含 AGPL-3.0 的 ultralytics | 厂商自述（经博文转述） | P0 | ✅ F-064（AGPL 系经多方确认；Kasm/OmniParser 为官方 README 声明） |

## E. Stars 趋势与热度（博文口径，采集于 2026-09-20）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-016 | O | 总 Stars：24,432（GitHub API 与 Trending 页面，采集于 2026-09-20） | 第三方综述 | P0 | ⚠️ F-055（2026-10-10 实测 29,189，时点差异） |
| F-017 | O | Forks：1,681 | 第三方综述 | P0 | ⚠️ F-055（2026-10-10 实测 2,061） |
| F-018 | O | 今日新增 +859，GitHub Trending 日榜第 2 名 | 第三方综述 | P0 | ⚠️ 时点数据无法事后复核；多方报道佐证当时在 Trending 前列 |
| F-019 | O | 创建时间：2025 年 1 月 31 日，至今约一年半 | 第三方综述 | P0 | ✅ F-054（2025-01-31T15:02:49Z） |
| F-020 | O | 开放 Issues：1,032 个，社区讨论活跃 | 第三方综述 | P0 | ⚠️ F-055（2026-10-10 实测 1,149） |
| F-021 | V | 单日 +859 star 约占总量的 3.5%，作者判断该增速在 AI 基础设施类项目中属于高位 | 作者观点 | P2 | ➖（作者推算） |
| F-022 | V | 项目一年半攒下 2.4 万 star，平均每月超 1,300，属于稳步爬升后借势爆发的典型曲线 | 作者观点 | P2 | ➖（作者推算） |
| F-023 | O | cua-driver-rs 组件保持每日 nightly 发布（2026-09-14 到 09-19 一天不落），最近正式版为 2026-09-15 发布的 sandbox v0.8.0 | 第三方综述 | P0 | ✅ F-058/F-060 |
| F-024 | O | sandbox v0.8.0 于 2026-09-15 发布 | 第三方综述 | P0 | ✅ F-058 |
| F-025 | O | 项目获 Trendshift 趋势徽章，Discord 社区、官方博客、文档站一应俱全 | 第三方综述 | P1 | ✅ |
| F-026 | O | 语言构成：主语言标记为 HTML（文档站与演示页）；核心组件横跨 Rust（cua-driver-rs）、Swift（Lume）、Python（Sandbox SDK、CUA-S1、Bench） | 第三方综述 | P0 | ⚠️ F-057（2026-10-10 API 主语言为 Rust，时点差异） |

## F. 快速上手（博文口径，全部转述自官方 README）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-027 | O | Cua Driver 安装（macOS/Linux）：`/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"` | 官方 README 转述 | P0 | ✅ F-062 |
| F-028 | O | Cua Driver 安装（Windows PowerShell）：`irm https://cua.ai/driver/install.ps1 | iex` | 官方 README 转述 | P0 | ✅ F-062 |
| F-029 | O | 首个任务：连接 Agent（Claude Code、Codex、Cursor 都有官方集成指引），让它打开计算器算 6×7，并验证应用界面显示 42 | 官方 README 转述 | P0 | ✅ F-061 |
| F-030 | O | Lume 安装：`/bin/bash -c "$(curl -fsSL https://cua.ai/lume/install.sh)"` | 官方 README 转述 | P0 | ✅ F-062 |
| F-031 | O | Lume 从 Apple 恢复镜像直接创建原生 macOS Tahoe 虚拟机，启动后通过 SSH 连接，全程无人值守，需要 Apple Silicon 芯片的 Mac | 官方 README 转述 | P1 | ✅ |
| F-032 | O | Cua Bench 需要 Python 3.12/3.13 和 uv | 官方 README 转述 | P1 | ✅ |
| F-033 | O | Cua Bench 安装：`uv tool install 'cua-bench[browser]'` | 官方 README 转述 | P0 | ✅ F-062 |
| F-034 | O | `uv tool run --from 'cua-bench[browser]' playwright install chromium` | 官方 README 转述 | P1 | ✅ |
| F-035 | O | 第一个评测任务不需要虚拟机、Docker 或模型 API Key：创建小任务，运行参考解法，验证评估器给出 reward=1.0 | 官方 README 转述 | P1 | ✅ |
| F-036 | O | 云端 Fleets：直接使用 run.cua.ai 的 Cua Fleets，从池中认领隔离 Linux 云桌面，用 Sandbox SDK 跑命令/截屏，用完销毁 | 官方 README 转述 | P1 | ✅ |
| F-037 | O | 本地沙箱与云端 Fleet 共享同一套 Sandbox SDK，代码可无缝迁移 | 官方 README 转述 | P1 | ✅ |
| F-038 | O | 官方提醒：Fleet 池在认领结束后可能保留付费容量，教程含完整清理步骤 | 官方 README 转述 | P1 | ✅ |
| F-039 | V | 作者建议上手顺序：先 Cua Bench 模拟任务（零依赖）→ 再装 Cua Driver 操作计算器 → 有 Apple Silicon 用 Lume 拉本地虚拟机 → 最后评估是否上云端 Fleets | 作者观点 | P2 | ➖ |
| F-040 | O | 官方文档站 cua.ai/docs 对每个模块都有「Your first result」式入门教程 | 官方 README 转述 | P1 | ✅ |

## G. 评价、适用场景与局限（博文口径）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-041 | V | 作者评价：Cua 是 computer-use 赛道里覆盖面最全的开源项目，从执行层（Driver/Fleets/Lume）到模型层（CUA-S1）再到评测层（Bench）一套 MIT 组合拳全给齐 | 作者观点 | P2 | ➖ |
| F-042 | V | 作者评价：Cua 不跟大模型厂商抢「大脑」生意，专心做「手和脚」，可与 Claude Code、Codex、Cursor 等任何 Agent 搭配，生态位聪明 | 作者观点 | P2 | ➖ |
| F-043 | V | 适用场景 1：构建能操作桌面应用/浏览器的 AI Agent（自动化办公、RPA 升级） | 作者观点 | P2 | ➖ |
| F-044 | V | 适用场景 2：为 computer-use 模型做数据生成与强化学习训练（Fleets + Bench 导出轨迹） | 作者观点 | P2 | ➖ |
| F-045 | V | 适用场景 3：跨平台自动化测试（macOS/Windows/Linux 统一接口） | 作者观点 | P2 | ➖ |
| F-046 | V | 适用场景 4：在 Apple Silicon 上快速拉起 macOS 虚拟机做隔离实验 | 作者观点 | P2 | ➖ |
| F-047 | V | 局限 1：1,032 个开放 issue 说明项目还在高速演进期，API 可能有破坏性变更 | 作者观点 | P2 | ➖（基于 F-020 快照） |
| F-048 | V | 局限 2：云端 Fleets 是付费服务，重度使用要算成本账 | 作者观点 | P2 | ➖ |
| F-049 | V | 局限 3：CUA-S1 目前只是早期研究性发布（source-only），生产环境慎用 | 作者观点 | P1 | ✅ F-063（source-only 口径一致） |
| F-050 | V | 局限 4：Driver 的「后台投递」能力有平台边界，具体支持范围要查官方文档 | 作者观点 | P2 | ➖ |
| F-051 | V | 展望：2026 年是 Computer-Use Agent 爆发之年（OpenAI Operator、Anthropic Computer Use、各家浏览器 Agent 抢入口） | 作者观点 | P2 | ➖ |
| F-052 | V | 作者评价：Cua 押注「卖水人」逻辑——无论谁家 Agent 胜出，都需要安全、隔离、可评测的执行环境 | 作者观点 | P2 | ➖ |
| F-053 | V | 作者评价：每日 nightly 迭代节奏和单日 859 star 的热度说明社区已用脚投票 | 作者观点 | P2 | ➖ |

## H. 官方核验补充事实（2026-10-10）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-054 | O | GitHub API 实测：仓库 trycua/cua 存在，id 925270205，创建时间 **2025-01-31T15:02:49Z**，owner 为 Organization `trycua`（id 191107687），默认分支 main，homepage=https://cua.ai | 官方核验 | P0 | ✅ |
| F-055 | O | GitHub API 时点快照（2026-10-10T00:41Z）：stargazers_count **29,189**、forks 2,061、open_issues 1,149、subscribers 94；最近 push 2026-10-10T00:58Z（活跃维护） | 官方核验 | P0 | ✅（动态数字，引用须带时点） |
| F-056 | O | GitHub API license = **MIT License**（spdx MIT）；description 与博文引用的 README 副标题**逐字一致** | 官方核验 | P0 | ✅ |
| F-057 | O | GitHub API language 字段 2026-10-10 为 **Rust**（博文 2026-09-20 快照称 HTML）；GitHub 主语言字段随时间点/字节占比变动 | 官方核验 | P0 | ⚠️ 时点差异 |
| F-058 | O | sandbox v0.8.0 发布日期经双重确认：newreleases.io 记录 GitHub release `sandbox-v0.8.0`（0.8.0 (2026-09-15)）；piwheels 记录 cua-sandbox 0.8.0 于 2026-09-15 16:49:04 UTC 发布 | 官方核验 | P0 | ✅ |
| F-059 | O | cua-sandbox **0.9.0** 于 2026-10-01 发布（piwheels）——博文快照后的组件演进 | 官方核验 | P2 | ✅（快照后演进） |
| F-060 | O | nightly 发布节奏确认：newreleases.io 显示 `nightly-cua-driver-rs-v0.28.3-nightly.20260917/20260918/20260919` 连续发布 | 官方核验 | P0 | ✅ |
| F-061 | O | 官方教程页逐字确认首个任务：`Your first result: connect your agent, ask it to compute 6 × 7 in Calculator, and have it verify that the app displays 42` | 官方核验 | P0 | ✅ |
| F-062 | O | 官方文档页逐字确认安装命令：macOS/Linux `curl -fsSL https://cua.ai/driver/install.sh`、Windows `irm https://cua.ai/driver/install.ps1 | iex`、Lume `curl -fsSL https://cua.ai/lume/install.sh`；Computer-Use 2.0 定义为 "an agent moving between code, APIs, and graphical interfaces within the same task" | 官方核验 | P0 | ✅ |
| F-063 | O | CUA-S1 于 2026-09-19 前后被第三方报道开源（openai-hub.com 2026-09-19）；报道确认其为 System 1 决策模型、面向高频桌面操作；模型权重托管 Hugging Face、按各自卡片条款授权（source-only 口径与博文一致） | 官方核验+第三方报道 | P0 | ✅ |
| F-064 | O | 第三方组件许可证交叉验证：闲人野鹤/腾讯云等报道确认「可选的感知扩展（OmniParser 套件）是 AGPL 系」、CUA-S1 权重单独在 Hugging Face 按条款授权；Kasm MIT、OmniParser CC-BY-4.0 为官方 README 声明 | 第三方报道 | P1 | ✅ |
| F-065 | O | Cua Spaces 桌面应用（Cua Spaces 0.1.0，source-available 于 FSL-1.1-MIT）为 2026-09/10 前后新增产品线，博文未涉及——快照后演进 | 官方核验 | P2 | ➖（快照后演进） |

## G1 自检

- 事实总数：65（博文 53 + 核验补充 12），编号 F-001~F-065 连续无跳号
- 因果/判断词：事实栏纯客观陈述；评价与因果表述均标 V/S 并归入观点/自述
- 数字/命令/版本：24,432、1,681、1,032、2025-01-31、2026-09-15、v0.8.0、Python 3.12/3.13、6×7、42 等均带 F 出处与时点
- 核验记录：✅ 12 项 P0 核心硬事实、⚠️ 6 项时点/口径差异（F-016/F-017/F-018/F-020/F-026/F-057）、❌ 0