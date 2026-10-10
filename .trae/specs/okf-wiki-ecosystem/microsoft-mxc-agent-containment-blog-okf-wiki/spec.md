---
status: "draft"
version: "1.0"
---

# 微软 MXC / Agent 执行隔离博文 → OKF Wiki 教程 Spec

## Why

微信公众号"腾讯科技"文章《微软给Agent立规矩，Windows要管AI了》（作者晓静，编辑徐青阳，2026-10-08 发布）报道微软推出的面向 AI Agent 的执行隔离工具 **Microsoft Execution Containers（MXC）** 在 Windows 11 上正式开放，并分析了 Windows 作为 Agent 平台的角色变化与竞争格局。按 blog-article-to-okf-bundle 模式转化为 OKF 知识包，归入 `jishu/ai/practice/` 分组，作为 Agent 安全执行隔离产品发布 + 行业分析的资讯背景收录。

## 内容敏感度预检

- 信源是微信公众号公开文章（`mp.weixin.qq.com`，无 `share?code=`/`token=` 访问控制参数）→ **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 归属判定

**结论：`jishu/ai/practice/microsoft-mxc-agent-containment/`**

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/practice/`（选定，新增 bundle） | ✅ | ① 文章主线是微软 Windows 平台的 Agent 执行隔离产品（MXC）发布 + Agent 安全行业分析；② practice 分组明确承载"博文核验转化束 + 行业趋势研究"，已有 verbi/gpt6-intelligent-ui/answer-me-with-html 等博文转化先例；③ 非某厂商开源框架源码教程，不落 ecosystems/frameworks；④ 单篇博文新建顶级分组属过度工程，落既有分组 |
| `jishu/ai/practice/ai-security/` | ❌ | 该分组为 elder-plinius 三仓库红队**源码教程**，主题/溯源方式不符（本文非源码） |
| `jishu/ai/practice/agent-industry-research/` | ❌ | 该 bundle 为"2026-08 行业研究三篇"专题聚合，本文为单篇产品发布 + 竞争分析，主线不同 |
| `jishu/systems/` | ⚠️ | Windows 相关，但该分组仅 2 束（WSL 教程、PowerShell），无博文转化先例，且内容核心是 Agent 而非操作系统本体 |
| 新建顶级分组 | ❌ | 过度工程，违反最小变更原则 |

## 内容性质判定

**商业分析/战略资讯类**（产品发布资讯 + 竞争格局 + 作者观点）。操作可复现性两问：① 有无读者可照做的安装/配置/代码/实测流程？→ **无**（仅产品与安全机制描述，MXC 为商业产品非源码教程）；② 是否经作者实测、具备可复现性？→ **否**。

→ **不设 examples/**，骨架 = `index.md` + `concepts/` + `references/` + `log.md`；index 顶部声明"商业分析/战略资讯，非源码教程"。

## What Changes

- 新增 OKF bundle：`jishu/ai/practice/microsoft-mxc-agent-containment/`
  - index.md + log.md + concepts/（3 篇 + index）+ references/（2 篇 + index）
  - 不设 examples/（商业分析无可运行示例）
- 更新 `jishu/ai/practice/index.md`：新增导航条目 + toctree 追加 + 束数 16→17
- 更新 `bundles/index.md`：total_bundles、ai 域束数、practice 组束数同步 +1
- 不修改 external/ 任何内容

## 事实基础（博文 F-001 起）

完整事实集见 [facts.md](facts.md)。要点：

- F-001~F-003: MXC 发布与定义；F-004/F-014: 首批支持名单；F-005/F-031: Pavan Davuluri 身份；F-007: Containment/Identity/Manageability 三能力；F-009: Simon Willison 致命三要素；F-010~F-012: Anthropic 93% 批准与执行隔离经验；F-017~F-020: 混合智能与本地推理；F-021-F-024: 跨平台与苹果/Google 竞争；F-026~F-032: 核验补充（官方名单、隔离后端、运行模式、政策五领域等）

## ADDED Requirements

### Requirement: Bundle 根索引
index.md frontmatter 含 sources（博文 URL + 微软官方博客 URL），明确标注"商业分析/战略资讯，非源码教程"。已知边界声明：产品发布资讯时效性、名单口径差异、作者观点分层、核验依赖官方博客。

### Requirement: 概念文档（concepts/，3 篇）
- 00-mxc-what-is.md：MXC 是什么——发布信息、双向限权机制、四种隔离后端、三种运行模式、政策五领域、支持名单（含博文 vs 官方名单口径勘误）
- 01-agent-security-rationale.md：Agent 安全为何需要执行隔离——最小权限原则、提示注入/致命三要素、Anthropic 93% 批准与执行隔离转向、Containment/Identity/Manageability 三能力、Agent 不能自证安全
- 02-platform-competition.md：Windows 作为 Agent 平台的竞争格局——云 Agent vs 本地、混合智能、苹果/Google 对标、应用商店类比、作者观点分层

### Requirement: 信源登记簿（references/）
- article-source.md：F-001~F-032 事实完整登记（分"客观事实""作者观点""核验补充"三类）
- verification.md：P0/P1 核验逐项结论表，包含名单口径勘误（F-027）与日期口径说明（F-001）

### Requirement: 索引更新
`jishu/ai/practice/index.md` 导航表加行 + toctree 追加 + 束数 +1；`bundles/index.md` 计数同步。

## 约束
- 本文为商业分析/新闻资讯，非技术教程；不设 examples/；不编造未在博文或官方来源出现的数据
- 涉及名单、日期、成效数字一律引用官方博客核验；无法核验的标注"仅博文单源"或"作者观点"
- 交叉引用同分组 bundle 用相对路径；正文呈现正确值并标注源文口径（如 F-001 日期、F-004/F-027 名单）

<!-- changelog -->
<!--
- 2026-10-10 | initial | 按 blog-article-to-okf-bundle 模式转化微软 MXC 博文
-->