---
okf_version: "0.2"
type: spec
title: "Knocket「会聊天的个人名片」博文→OKF 知识包转化规划"
description: "将微信公众号博文《腾讯做了一个"会聊天的个人名片"》转化为 OKF 知识包，覆盖腾讯 Knocket 的产品事实（WebWidget/ContactPage/MobileWidget 三功能、Unified Inbox、AI Agent 知识库）、一人公司/个人业务总入口定位，以及"AI 从提效走向做生意"趋势分析，含官方产品页 P0 核验"
tags: [okf-bundle, blog-article, knocket, tencent-rtc, contact-page, ai-agent, ai-business-card, opc]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-10-10T11:50:00+08:00" }
---

# Knocket 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。
> 类目：**商业分析/产品观察**（观点+趋势文，非源码教程、非操作教程）。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/GstWn_PvN48fikFsvcsjNA |
| 公众号 / 作者 | 怪哥 / 怪哥（个人产品观察号） | 产品观察观点文，涉及腾讯新产品 Knocket |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式；`?from=industrynews` 为分享追踪参数，非访问控制 |
| 敏感度级别 | **公开内容** | 公开产品报道/观点文，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方综述（产品观察号）+ 腾讯官方产品页补充核验** | 非腾讯官方号；观点与产品事实交织，需分层；产品事实经 knocket.trtc.io 官方页与 TRTC 官方博客交叉核验 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否** | 博文为产品介绍与趋势观点，无安装、配置、代码、调用步骤；仅描述"可以把自己的 FAQ、网站内容、产品资料放进去让 AI 回答"，未给具体操作流程 |
| Q2：这些流程是否经作者实测、具备可复现性？ | **否** | 作者为"玩了一圈"的产品观察，未给出可复现的注册/配置步骤序列；Knocket 为闭源商业产品，无公开 API 文档根操作教程 |

**判定：两问任一为"否" → 商业分析/产品观察类骨架，不设 examples/**

**骨架**：
```
jishu/ai/products/knocket/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-what-is-knocket.md                      # 产品是什么：三功能/归属腾讯 RTC/发布时间线（What·When·Who）
│   ├── 01-mechanisms-contact-page-inbox.md        # 机制原理：Contact Page + Unified Inbox + AI Agent 知识库
│   └── 02-business-card-trend.md                  # 趋势定位：一人公司总入口 & "AI 从提效走向做生意"
└── references/
    ├── index.md
    ├── article-source.md                          # 博文事实清单（F 编号双份登记之一）
    └── verification.md                            # P0 核验报告（含勘误）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/products/knocket/`（选定） | ✅ | ① 主线实体 Knocket 是腾讯 AI 接待/个人名片产品，归 ai 产品生态；② 该组承载众多异形产品束（octop、todesk-ai、ok-platform 等腾讯系产品先例）；③ 名称独特无同名冲突 |
| `sheke/industry/`（行业分析） | ❌ | 该组为行业/产业综述；本篇主线是具体产品 Knocket，而非某行业的系统分析 |
| `sheke/personal-growth/` | ❌ | 该组定位个人成长方法论；本篇不是自我提升指南，是产品观察 |
| 新建顶级分组 | ❌ | 单篇博文新建分组属过度工程 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/products/knocket/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-10（采集时点 2026-10-10，未显示具体日期） |
| 官方核验时间 | 2026-10-10（knocket.trtc.io 官方产品页 + templates/html-live-chat + TRTC 官方博客） |
| `stale_after` | **2026-12-31**（产品处于早期且免费吸引增长，年末复核价格/功能/归属） |
| 高时效字段 | 免费口径、功能集、产品归属/域名、是否扩展向量 | 
| 已知边界声明 | ① Knocket 为闭源商业产品，本束核心产品事实以官方页 knocket.trtc.io 为准，博文作第三方观察视角；② 博文"AI 模型可以自己接""AI 生成页面"等细节为作者观点/转述，官方页未逐字确认处标"仅博文单源"；③ 产品发布时间媒体口径不一（"近期上线"vs"上线2年"），本束不采信修饰性时间声明 |

## 5. P0 必核验清单与结论摘要

| 核验对象（F 编号） | 类型 | 权威信源 | 结论 |
|--------------------|------|----------|------|
| Knocket 产品存在、归属腾讯 RTC（F-003/F-004） | 产品身份 | knocket.trtc.io 官网页 + trtc.tencentcloud.com 官方博客 | ✅ 域名 knocket.trtc.io 真实存在，TRTC 官方博客确认"网页占用行为知识库应用" |
| 三功能 WebWidget/ContactPage/MobileWidget（F-005~F-017） | 能力事实 | 官方产品页 + templates 页 | ✅ Contact Page 官方确认"发行单链接"；Mobile Widget 官方确认"iOS 应用内嵌"；HTML 聊天脚本官方确认 |
| Contact Page 生成独立专属链接（F-006/F-007） | 能力事实 | 官方产品页 | ✅ 官方"发布一个可分享链接"确认；`knocket.ai` 子域名为三方报道口径，官方页使用 trtc.io 域名 |
| Unified Inbox 多渠道统一收件箱（F-015） | 能力事实 | 官方产品页 + templates FAQ | ✅ 官方确认聚合 Live Chat/Telegram/Email（页图含 WhatsApp/Instagram）；templates 页明确"Unified inbox (Live Chat, Telegram, and Email)" |
| AI Agent + 知识库自动回答 + 转人工（F-008~F-011） | 能力事实 | 官方产品页 "Upload docs and FAQs" | ✅ 官方确认 AI 回答常规问题、需要时转人工 |
| 核心功能免费（F-012） | 商业事实 | templates 页 "100% free forever，无广告" | ✅ 官方确认 free-forever 无广告；与 Intercom/Tawk.to 对比表佐证 |
| AI 模型可自接（F-013） | 作者转述 | 官方页未逐字确认 | ⚠️ 官方对比表未明示自定义模型接入，标"仅博文单源/厂商自述待核" |
| AI 生成页面（F-014） | 作者转述 | 官方页未逐字确认 | ⚠️ 官方页未直接呈现"自然语言生成页面"入口，标单源 |
| 腾讯 RTC"底层能力→产品壳"战略判断（F-018~F-021） | 作者观点 | 官方博客（"楚门的我想"视角） | ⚠️ 官方博客确认 Tencent RTC 提供底层实时音视频能力，但"产品壳/引流"为作者分析，非官方声明，归观点层 |

**汇总**：P0/P1 核验约 12 项 —— ✅ 8、⚠️ 4（2 项单源待核 + 2 项归观点层）、❌ 0。无核心产品声明失败 → `status: stable`；4 项 ⚠️ 在 verification.md 完整勘误并在正文标注口径。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 产品事实层（Knocket 是什么/三功能/归属腾讯 RTC/发布时间线） | concepts/00-what-is-knocket.md | F-001~F-003、F-015~F-016、F-030~F-033、F-043 |
| 机制原理层（Contact Page / Unified Inbox / AI Agent 知识库 / 多端承接） | concepts/01-mechanisms-contact-page-inbox.md | F-004~F-008、F-011~F-014、F-033~F-039 |
| 趋势定位层（一人公司总入口 & AI 从提效走向做生意 & 腾讯产品壳战略） | concepts/02-business-card-trend.md | F-007、F-009~F-010、F-017~F-029 |

## 7. ADDED Requirements（验收标准）

- bundle 9 个文件齐备（3 concepts + 2 references + 2 目录 index + 根 index + log，无 examples），每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（产品名/功能/域名/信源）携带 F 编号，无 facts.md 之外编造；作者观点显式标"作者观点"
- 4 项 ⚠️ 勘误在正文呈现正确口径并标注；"AI 模型自接""AI 生成页面"标"仅博文单源"
- frontmatter 双信源（博文 URL + 官方产品页）标注，stale_after=2026-12-31
- 双份 F 编号一致（facts.md ↔ article-source.md 连续无跳号，F-001~F-045）
- products 组 index 导航表 + toctree 接入本束；计数 sync：products 25 / ai 228（并行会话在途束 inkos/vidbee/image-blaster/opencreator，由对应会话收尾，本束仅接入不改他人）
- V 阶段执行四视角审查与 8 项机械门禁；invoke gates 不可用时执行手动等效清单并在 log.md 注明