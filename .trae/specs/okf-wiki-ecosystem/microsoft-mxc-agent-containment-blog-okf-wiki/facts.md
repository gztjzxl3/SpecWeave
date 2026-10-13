---
type: facts
title: "微软 MXC / Agent 执行隔离博文事实集"
---

# 事实集（Facts）

> 信源：微信公众号"腾讯科技"《微软给Agent立规矩，Windows要管AI了》（作者晓静，编辑徐青阳，2026-10-08 发布）。
> 编号规则：F-001 起为博文事实，F-02X ~ F-03X 为权威核验补充。P0=必核验；P1=选核验；P2=可单源。作者观点显式标注"作者观点"。

## 博文客观事实（F-001 ~ F-025）

| F编号 | 类别 | 声明 | 原文位置 | 核验级别 |
|-------|------|------|---------|---------|
| F-001 | 事件 | 北京时间 2026-10-08 微软宣布 MXC（Microsoft Execution Containers）在 Windows 11 上正式开放 | 开头 | P0 ⚠️时区口径 |
| F-002 | 事件 | MXC 可限制 Agent 访问的文件、网络等资源，并在运行过程中执行这些规则 | 开头 | P0 |
| F-003 | 能力 | MXC 支持多种隔离程度：进程隔离、独立会话、WSL 容器、虚拟机、Windows 365 云端执行环境 | §01 | P1 |
| F-004 | 名单 | 首批支持 MXC 产品：OpenAI Codex、GitHub Copilot、OpenClaw、英伟达 OpenShell；Claude Code、Manus、Perplexity 计划接入；Meta Muse 将推集成 MXC 的 Windows 原生应用 | 开头 | P0 ⚠️名单口径 |
| F-005 | 身份 | 微软 Windows 与设备业务执行副总裁 Pavan Davuluri（EVP Windows + Devices） | 开头 | P1 |
| F-006 | 事件 | 微软 10 月 7 日官方文章：传统沙箱并非专为 Agent 设计，Agent 隔离需求随每次提示词输入与工具调用变化 | §01 | P2 |
| F-007 | 能力 | 微软将 MXC 方向概括为三关键词：隔离（Containment）、身份（Identity）、可管理性（Manageability） | 开头 | P0 |
| F-008 | 能力 | 微软希望将 Agent 活动纳入 Microsoft Agent 365、Intune 等企业管理体系 | §01 | P1 |
| F-009 | 概念 | Simon Willison（独立开发者、安全研究者）2025 年提出"致命三要素"（Lethal Trifecta）：Agent 能访问私人数据 + 接触不可信内容 + 具备向外部发送信息能力，三者同时存在时攻击者可通过恶意指令诱导 Agent 泄露数据 | §02 | P1 |
| F-010 | 数字 | Anthropic 今年（2026）5 月发布《How we contain Claude across products》：Claude Code 用户约批准 93% 权限请求 | §02 | P0 |
| F-011 | 能力 | Anthropic 因 93% 批准问题转向执行隔离：沙箱、虚拟机、文件系统边界、网络出口控制；区分"监督 Agent 实际做了什么"与"通过执行环境限制其能做什么" | §02 | P1 |
| F-012 | 能力 | Anthropic 披露：随模型能力增强，Agent 可能找到开发者未预料到的路径，在某些测试场景中绕过既有隔离设计（沙箱逃逸） | §02 | P1 |
| F-013 | 观点 | Agent 安全无法靠单一机制完成——模型识别恶意指令、应用限制工具调用、操作系统在实际访问资源时执行权限规则（作者观点） | §02 | P2 |
| F-014 | 名单 | 10 月 7 日微软公布名单：OpenAI Codex、GitHub Copilot、OpenClaw、Replit、英伟达 OpenShell 已支持；Claude Code、Manus、Perplexity 计划接入；Meta Muse 将推 Windows 原生应用 | §03 | P0 ⚠️名单口径 |
| F-015 | 观点 | 名单既含微软自己产品也含竞争者；Windows 上 Agent 越丰富，微软越有机会推动 MXC 成为广泛采用的执行基础设施（作者观点） | §03 | P2 |
| F-016 | 观点 | 接入 Windows 隔离机制可减少模型公司自建本地执行环境的成本；双方有合作空间但用户入口与系统控制权划分待观察（作者观点） | §03 | P2 |
| F-017 | 概念 | 微软提出"混合智能"（Hybrid Intelligence）方向——Agent 根据任务在本地模型与云端模型间选择执行位置 | §03 | P1 |
| F-018 | 数字 | 微软披露 Copilot+ PC 每月已在本地执行超 2 万亿次推理；GitHub 计划测试本地与云端模型的智能路由 | §03 | P1 |
| F-019 | 观点 | 微软希望 Windows 同时承担 Agent 执行环境与本地 AI 计算平台；操作系统在计算资源调度、数据保护与权限管理中的作用可能增加（作者观点） | §03 | P2 |
| F-020 | 观点 | 微软未必能成为所有 Agent 的权限管理者——越来越多 Agent 直接运行在云端，通过 API 连接企业软件，无需操作用户本地电脑（作者观点） | §03 | P2 |
| F-021 | 能力 | 微软表示 MXC 可跨操作系统使用，只是在 Windows 上提供更深入集成 | §03 | P1 |
| F-022 | 观点 | 苹果和 Google 同样争夺 Agent 时代系统入口——苹果有软硬件协同与端侧隐私，Google 掌握 Android、浏览器、云端 AI 生态（作者观点） | §03 | P2 |
| F-023 | 观点 | 类比移动互联网应用商店：未来 Agent 执行环境可能成为新的平台控制点（作者观点） | §03 | P2 |
| F-024 | 观点 | 若限制过多，开发者可转向浏览器、云电脑或其他执行方式（作者观点） | §03 | P2 |
| F-025 | 观点 | 随着 Agent 接管软件操作，Windows 传统界面重要性可能下降，但安全可靠执行环境仍有价值；结尾发问"约束 AI 的权力一定属于操作系统吗？"（作者观点） | §03 | P2 |

## 核验补充事实（F-026 ~ F-032）

| F编号 | 类别 | 声明 | 来源 | 核验级别 |
|-------|------|------|------|---------|
| F-026 | 事件 | 微软 Windows Developer Blog 发布《Microsoft Execution Containers: Policy-driven containment for AI agents》，作者 Logan Iyer（CVP, Windows Platform + Developer），2026-10-07，确认 MXC generally available | 官方博客 | ✅ P0 通过 |
| F-027 | 名单 | 官方"已支持 MXC"名单：GitHub Copilot、OpenClaw、OpenAI Codex、Replit、LM Studio、Unsloth AI；NVIDIA OpenShell 已集成（补充凭证管理 + OCSF 审计）；"即将支持"：Anthropic Claude Code、Box、Egnyte、Heidi Health、Hermes Agent（Nous Research）、Manus、Perplexity、Raycast、Simular。⚠️与博文 F-004/F-014 名单有出入 | 官方博客 | ✅ P0 通过（勘误博文名单） |
| F-028 | 能力 | 官方 MXC 四种隔离后端：Process container（Win/macOS/Linux，AppContainer/Seatbelt/Bubblewrap）、Session container（仅 Win11，独立账户+隔离桌面）、WSL container（仅 Win11）、MicroVM（Win11/Linux 实验性，硬件虚拟化）；Windows 365 云端执行 GA | 官方博客 | ✅ P0 通过 |
| F-029 | 能力 | 官方 MXC 三种运行模式：Enforcement（拦截，无活动报告）、Learning（拦截+记录 JSON 活动报告）、Permissive（允许+记录） | 官方博客 | ✅ P0 通过 |
| F-030 | 能力 | 官方 MXC 政策五领域：Containment、Process、File system、Network、User interface | 官方博客 | ✅ P0 通过 |
| F-031 | 身份 | Pavan Davuluri 确认为 EVP Windows + Devices；Windows Experience Blog 10-07 发布其署名《Building Windows for hybrid intelligence》 | 官方博客 | ✅ P1 通过 |
| F-032 | 数字 | Anthropic 官方《How we contain Claude across products》确认 containment 方法（sandboxes/VMs/egress）；93% 批准数字获 singularity.kiwi 等多源转述确认 | Anthropic 官方 + 第三方 | ✅ P0 通过 |

## 勘误说明

- **F-001 日期口径**：博文按北京时间记 10-08 开放；微软官方博客按美西（太平洋）时间记 2026-10-07 generally available。属时区差异，非错误，正文以官方口径为准并注明博文口径。
- **F-004 / F-014 名单口径（F-027 勘误）**：博文"首批支持"名单（OpenAI Codex、GitHub Copilot、OpenClaw、OpenShell）不完整——官方"已支持"另含 Replit、LM Studio、Unsloth AI，且 OpenShell 官方单列为"已集成"（补充凭证管理+OCSF 审计）；"计划接入"官方名单另含 Box、Egnyte、Heidi Health、Hermes Agent、Raycast、Simular。正文以官方名单为准，标注博文口径不完整。
- **F-007 / F-026 归因**：博文将三关键词（隔离/身份/可管理性）归因为 Pavan Davuluri 概括；官方 MXC 博客（作者 Logan Iyer）以 Containment/Identity/Manageability 提出，Pavan Davuluri 的《Building Windows for hybrid intelligence》为并行发布。正文标注两篇官方博客分工，不把三能力框架单一归因于 Pavan。

## 单一信源 / 弱信源提示

- F-001/F-003/F-006/F-008/F-009（Willison 2025 提出年份）/F-011/F-012/F-017/F-018：博文表述为主，官方博客可支撑其中多数能力描述，但"Willison 2025 提出"与"Copilot+ PC 2 万亿次/月"未在本次核验中找到独立官方出处，标注"仅博文单源"或在验证后补充。
- F-013、F-015、F-016、F-019、F-020、F-022~F-025：均为作者观点/分析，正文保留"作者观点"标注，不作事实引用。