---
type: spec
title: "斯惟云《普通人找对象，需要尽早认清这种关系》→ OKF Wiki 教程"
description: "单篇微信公众号个人观点文（择偶中的概率关系思维）转化为 OKF bundle 的方案：R→I→E→V→C 知识沉淀链路"
tags: [okf, wiki, wechat, relationships, probability, single-source]
status: draft
created: 2026-10-08
source_url: https://mp.weixin.qq.com/s/tdjmisd7S4BsU9sNKkKjrA
---

# 斯惟云概率关系文章 → OKF Wiki 教程 · Spec

## 0. 任务与内容敏感度预检

- **任务**：用户以 `/七概念` 触发，要求"全面学习"指定微信公众号文章并生成 OKF wiki 教程。
- **编排链路**：场景4 知识沉淀，R→I→E→V→C（standard depth，含强制 V）。
- **敏感度判定**：URL 为 `mp.weixin.qq.com/s/...`，无 `share?code=`/`token=`/邀请码参数；浏览器实际访问无登录/验证码门槛 → **公开内容（Public）** → 标准工作流：spec 在 `.trae/specs/okf-wiki-ecosystem/`，产出在 `projects/awesome-okf-xs/doc/bundles/`。

## 1. 信源画像（R 阶段结论）

| 项 | 值 |
|---|---|
| 标题 | 《普通人找对象，需要尽早认清这种关系》 |
| 公众号/作者 | 斯惟云的自留地 / 斯惟云（身份未独立核验） |
| 发布时间 | 2026-08-22 11:28（IP 属地安徽，时间戳 1787369316 一致） |
| 篇幅/形态 | 2425 字、5 节、原创、文末自标"个人观点，仅供参考" |
| 信源距离 | **个人原创观点文**（情感择偶领域，作者提供付费咨询）——非官方发布、非一手实测、非开源文档、非第三方综述、非厂商自宣 |
| 事实登记 | 31 条（F-001~F-031）：6 条页面事实 + 23 条作者观点 + 2 条匿名个案 |
| P0 核验 | **0 项**——无金额/版本/外部事件日期/官方表态/成效数字，勘误四张清单无适用对象；页面日期由浏览器快照直认 |
| 专项风险 | F-016 对"工程类男生"群体的刻板断言；F-025 "高攀/低娶/低嫁"等级化措辞；F-026/27 单方匿名个案 |

## 2. 骨架判定（操作可复现性两问）

1. 文中是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（择偶建议，无技术操作）。
2. 这些流程是否经作者实测、具备可复现性（版本/输入输出/步骤顺序）？→ **否**（建议为经验性叙述，关系结果无定义明确、可独立验证的输入输出）。

**结论：任一为"否" → 不设 `examples/`**。形态归入"观点/方法论类单篇文章"，与同分组两束先例（aidomain-wechat-relationship-practice、wechat-relationship-understanding）一致。

## 3. 归属判定（决策树 + 候选对照）

主线实体：文章主题是**择偶/亲密关系中的概率思维**，锚点为亲密关系领域。

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/relationships/`（选定） | ✅ | ① 主线为择偶与亲密关系认知，主题精确匹配"💕 亲密关系与两性情感"分组；② 该组已有**两束单篇微信公开文章转化先例**，证明可容纳博文转化产物；③ 可与组内学术实证层（米勒、戈特曼、依恋理论）形成"通俗观点 vs 实证证据"的对话 |
| `sheke/personal-growth/` | ❌ | 该组聚焦魅力/情商/个人方法论教程，本文核心是关系认知框架而非自我提升训练 |
| `guoxue/` | ❌ | "尽人事听天命"虽化用古典表述，但文章非国学经典研读 |
| 新建分组 | ❌ | 单篇博文新建分组违反最小变更原则 |

**bundle 名**：`wechat-probability-mindset-dating`（kebab-case，与 `wechat-relationship-understanding` 命名族一致）。
**完整路径**：`projects/awesome-okf-xs/doc/bundles/sheke/relationships/wechat-probability-mindset-dating/`。

## 4. 三层知识拆分（I 阶段知识地图）

文章为观点方法论类，按"命题层 → 应用层 → 收束/边界层"拆为 3 篇 concept + 1 篇 knowledge-map：

| 知识层 | 篇目 | 内容 | F 编号 |
|---|---|---|---|
| 概念命题层 | `concepts/00-causal-vs-probability.md` | 因果思维 vs 概率思维的界定、四个受挫场景、概率框架对自我归因的松动 | F-007~F-012 |
| 择偶应用层 | `concepts/01-probability-levers-in-dating.md` | 择偶中的概率判断（含高风险场景去刻板化改写）+ 提高遇合/识别/质量/正反馈四类概率的努力杠杆 | F-013~F-022 |
| 边界与收束层 | `concepts/02-uncertainty-boundaries-and-cooperation.md` | 概率框架的承诺边界、条件-要求-执行三变量、炒股男个案（标注单方匿名）、尽人事听天命、利他属性与"向内求" | F-023~F-031 |
| 知识地图 | `knowledge-map.md` | 事实层/观点层/迁移层分离、四元组洞察、与关系科学证据的对话索引 | 全部 |

## 5. 交付物清单（E 阶段）

```
wechat-probability-mindset-dating/
├── index.md                         # 根索引（单源观点文声明 + 内容边界 + toctree）
├── knowledge-map.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-causal-vs-probability.md
│   ├── 01-probability-levers-in-dating.md
│   └── 02-uncertainty-boundaries-and-cooperation.md
└── references/
    ├── index.md
    ├── source-manifest.md           # 信源登记（对齐先例）
    ├── facts.md                     # F-001~F-031 双份登记之二
    └── verification.md              # 零 P0 说明 + 单源边界 + 四视角对抗审查
```

共 10 个文件。frontmatter 遵循 OKF v0.2；`status: draft`（与两束先例一致，单源观点文）；`stale_after: 2027-12-31`（观点类弱时效）；sources 登记博文 URL 单源，不虚构权威信源。

## 6. V 阶段计划

- 四视角：魔鬼代言人（"概率"是否伪精确/不可证伪、幸存者偏差、付费咨询利益相关）、新人（概念是否解释得懂、第一步做什么）、老板/现实视角（建议的可操作性与伤害风险：刻板印象、等级化择偶话术）、未来视角（观点时效性、平台内容可能被删改）。
- 机械门禁：UTF-8 strict roundtrip、双份 F 编号集合比对（spec facts.md ↔ bundle references/facts.md，均 31 条连续）、三级 toctree 条目逐一 Test-Path、相对链接全可达、无 `file:///`、无家目录路径、frontmatter 完整。
- 索引接入：relationships 组 index 导航表 + toctree + 束数 8→9；sheke 域 index 计数 56→57（组计数 8→9）；bundles/index.md total_bundles 590→591、sheke 56→57、正文同步。
- 门禁：优先尝试 `invoke gates.toctrees` / `gates.bundles` / `gates.utf8`；依赖不可用时执行手动等效清单并在 log.md 注明，禁止谎报。

## 7. C 阶段

子模块内文件变更 + 三级索引计数。**按用户约定不主动 commit/push**；完成后汇报变更清单，由用户决定是否提交（提交须走 git-commit-utf8.py 显式文件列表，顺序：子模块→主仓库 spec→主仓库指针）。
