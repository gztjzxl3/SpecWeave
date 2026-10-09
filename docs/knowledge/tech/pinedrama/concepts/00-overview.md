---
type: Concept
title: PineDrama 产品概览
description: PineDrama 是字节跳动旗下 TikTok 于 2025 年 12 月推出的官方独立竖屏微短剧 App，免费 IAA 模式，被称为海外版红果，2026 年 9 个月累计下载破 1 亿
tags: [pinedrama, tiktok, bytedance, short-drama, overview]
generated:
  by: agent-trae
  at: "2026-10-08T22:55:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-08T22:55:00+08:00"
status: draft
stale_after: "2027-04-08"
sources:
  - id: S-03
    resource: /references/00-sources.md
    title: TechCrunch 首报
  - id: S-05
    resource: /references/00-sources.md
    title: Digital Trends（引 Business Insider）
  - id: S-06
    resource: /references/00-sources.md
    title: 澎湃·短剧深水区
  - id: S-14
    resource: /references/00-sources.md
    title: MakeAppLike 产品页
  - id: S-19
    resource: /references/00-sources.md
    title: 第三方下载站三源互证
---

# PineDrama 产品概览

PineDrama 是字节跳动（ByteDance）旗下 TikTok 推出的官方独立**竖屏微短剧（micro-drama / short drama）App**，2025 年 12 月悄然上线，2026 年 1 月 16 日由 TechCrunch 首报时已在美国、巴西软启动。它复刻了国内红果短剧的"免费看剧 + 广告变现"（IAA）路径，与 ReelShort、DramaBox 等"前几集免费、后续按集付费"（IAP）的头部产品错位竞争，因此被中文媒体普遍称为"**海外版红果**"。

截至 2026 年 9 月的 Sensor Tower 口径，其上线不足 9 个月累计下载突破 1 亿、DAU 约 700 万、月下载超 1700 万，位列 Sensor Tower 2026 年第二季度中国非游戏应用出海下载榜第 7，是该榜单中唯一上线不足一年的新品。

## 身份信息

| 项目 | 信息 | 核实来源 |
|---|---|---|
| 产品定位 | TikTok 官方竖屏微短剧独立 App | TechCrunch、Digital Trends |
| 运营主体（App Store 卖家） | TIKTOK PTE. LTD. | MakeAppLike、下载站 |
| Android 包名 | `com.ss.android.ttmd.video` | 三家下载站与产品页互证 |
| 官方网站 | shortdrama.tiktok.com | MakeAppLike |
| 平台 | iOS + Android | TechCrunch |
| 美区 App Store 评分 | 4.8 | MakeAppLike |
| 账号体系 | TikTok 账号一键登录，观看数据互通 | Digital Trends、下载站 |

> ⚠️ **名称澄清**：`pinedrama.com` 是一个与字节无关的网文站点，并非该 App 官网；GitHub 上同名的 PineDrama/PinedramaAPK 等小仓库也与本产品无关。引用官方信息时只认 `shortdrama.tiktok.com` 与应用商店条目。

## 一句话产品模型

> 免费供给扩大用户时长 → 推荐系统提高连续消费密度 → 广告回收内容与分发成本。

这是行业媒体对其 IAA 机制的概括（澎湃·短剧深水区，2026-09）。该机制直接对应国内红果已经验证的路径，详见 [免费 IAA 商业模式](03-iaa-business-model.md) 与 [字节战略：红果复刻与双轨漏斗](06-bytedance-strategy.md)。

## 产品形态速览

- **内容**：单集 1–3 分钟竖屏剧集，题材以 romance、revenge、CEO、family、thriller 等女频强情绪类型为主；代表作 *Love at First Bite*、*The Officer Fell for Me*；第三方下载站称首批上架 51 部。
- **交互**：上下滑动切换、自动连播，刷剧体验与 TikTok 一致；Discover 标签页按 All/Trending/类型筛选；支持观看历史、收藏、评论、全屏、倍速。
- **本地化**：主打海外本土原创、拒绝译制剧；多语言字幕与配音（下载站称 52 种语言，另有媒体口径 40+ 语言，数字不一）。
- **免费策略**：上线初期无开屏/插播/贴片广告、不充会员；2026 年内逐步引入集间广告与信息流广告。

完整功能拆解见 [产品形态与功能](02-product-features.md)。

## 市场位置（三个数字先记住）

1. **82%**：印尼与巴西合计贡献其累计下载量的 82%（Sensor Tower，2026-09）——增长不来自付费能力最强的市场，详见 [区域市场：印尼与巴西](04-regional-markets.md)。
2. **15% → 83%**：免费广告短剧应用占用全球短剧用户总时长的比例，从 2025Q1 到 2026Q2（Owl &Co. 口径）——PineDrama 踩中的是全行业时长迁移，详见 [竞争格局与行业剪刀差](05-competitive-landscape.md)。
3. **两次失败前科**：字节此前在东南亚推出 Melolo（译制剧，3 个月约 132 万下载）、在日本试水 PikoShow（题材错投），均未跑通，详见 [失败前科：Melolo 与 PikoShow](07-failed-predecessors.md)。

## 适合谁读

- 出海内容/短剧从业者：想了解免费 IAA 模式在新兴市场如何成立。
- 产品经理：研究"超级 App 主端入口 + 独立 App"双轨漏斗的实际样本。
- 投资者/分析师：需要带机构口径的规模数据与市场规模多口径对照。

> 数据时效提醒：本束事实截至 2026-10-08。PineDrama 仍在快速迭代（2026-01 第三方记录版本 v42.3.2，2026-08 已到 v46.4.4），其广告负载、收入与区域结构可能已变化；商业化指标字节从未官方披露。

## 相关概念

- [上线与扩张时间线](01-timeline.md)
- [产品形态与功能](02-product-features.md)
- [免费 IAA 商业模式](03-iaa-business-model.md)
- [竞争格局与行业剪刀差](05-competitive-landscape.md)
