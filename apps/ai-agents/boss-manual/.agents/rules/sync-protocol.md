---
id: boss-manual-sync-protocol
version: 1.0
source: 2026-10-14 boss-manual 应用初始化实践萃取
---

# 增量同步协议：私域知识库 → boss-manual

本协议是私域知识库 `1-老板说明书` 库内容更新到本应用的**唯一通道**。任何内容写入 `persona/` 前必须走本协议。

## 1. 触发方式

用户对话中说出以下任一句即启动本协议：

- 「更新老板说明书到 apps」
- 「同步 boss-manual」
- 「老板说明书加了新内容，同步一下」

## 2. 定位知识库根目录（KB_ROOT）

按顺序尝试，每步用 `Test-Path -LiteralPath` 显式验证，禁止沿用旧值：

1. 用户本次给定路径
2. 环境变量 `PERSONAL_KB_ROOT`
3. 向用户询问

验证锚点：`<KB_ROOT>\AGENTS.md` 与 `<KB_ROOT>\1-老板说明书\` 同时存在。

## 3. 文件映射表

同步以本表为唯一映射依据。私域库新增文件不在表内时，按 §5 流程处理。

| 私域源文件（相对 `1-老板说明书\`） | 应用内目标 |
|---|---|
| `00-总入口\老板说明书.md` + `00-总入口\写作前人格校准清单.md` | `persona\identity.md`（合并）+ `persona\README.md`（索引） |
| `04-判断边界\AI可以辅助整理，但不能替我体验和判断.md` | `persona\boundaries\ai-assists-not-replaces-judgment.md` |
| `04-判断边界\梦想库记录可能性，不等于现实承诺.md` | `persona\boundaries\dream-list-is-not-commitment.md` |
| `04-判断边界\个人健康记录不等于医疗建议.md` | `persona\boundaries\health-records-not-medical-advice.md` |
| `02-个人故事\01-主轴线\我为什么一直追求两种自由.md` | `persona\stories\main-line\why-i-pursue-two-freedoms.md` |
| `02-个人故事\02-时间管理与自律\我为什么花半年写任务管理知识体系.md` | `persona\stories\time-management\why-i-spent-half-year-on-task-system.md` |
| `02-个人故事\04-自媒体与知识付费\从学技术转入销售，再一路学到写作.md` | `persona\stories\content-creation\from-tech-to-sales-to-writing.md` |
| `02-个人故事\04-自媒体与知识付费\从放弃素材库到主动复用旧文.md` | `persona\stories\content-creation\from-abandoning-to-reusing-materials.md` |
| `02-个人故事\04-自媒体与知识付费\从放弃素材库到重新找回旧文-故事版.md` | `persona\stories\content-creation\from-abandoning-to-rediscovering-old-articles-story.md` |
| `02-个人故事\04-自媒体与知识付费\从日更100天几乎全删到两个月发文近60篇.md` | `persona\stories\content-creation\from-100-days-daily-to-60-posts-in-2-months.md` |
| `02-个人故事\04-自媒体与知识付费\大四那年我读了接近100本书.md` | `persona\stories\content-creation\reading-100-books-senior-year.md` |
| `02-个人故事\04-自媒体与知识付费\停更以后旧文章还在继续工作.md` | `persona\stories\content-creation\old-articles-still-working-after-pause.md` |
| `02-个人故事\05-职业选择与裸辞\2021年5月24日我休学了.md` | `persona\stories\career-choice\i-took-leave-on-2021-05-24.md` |
| `02-个人故事\05-职业选择与裸辞\毕业典礼还没结束我就飞去了深圳.md` | `persona\stories\career-choice\flew-to-shenzhen-before-graduation-ended.md` |

## 4. 增量同步流程

```
读取私域库映射表内全部源文件
  → 与对应应用内目标逐一比对（忽略 frontmatter 的 source/sanitized 字段）
  → 生成差异清单（新增 / 内容变化 / 无变化）
  → 对「新增 + 内容变化」逐项过脱敏检查清单（§6）
  → 向用户展示预览（改动位置 + 脱敏处理点）
  → 用户明确确认后写入
  → 写后验证：重新读取目标文件，确认内容落在预期位置
  → 若是新增故事：同步更新 persona/README.md 索引与本映射表
```

- **禁止**：未经预览确认直接写入；把私域库删除操作同步到应用（应用内删除必须用户单独确认）。
- **单向流动**：只从私域库 → 应用；应用不回写私域库。

## 5. 新增源文件处理

私域库出现映射表之外的文件时：

1. 判断类型：方法论（校准/边界类）还是个人故事。
2. 方法论 → 检查零隐私后可进 `boundaries/` 或并入 `identity.md`。
3. 个人故事 → 必须过完整脱敏检查清单后进 `stories/` 对应主题目录；新主题目录需用户确认。
4. 英文文件名遵循 `kebab-case`，语义对应中文标题。
5. 写入后更新 `persona/README.md` 索引与本协议 §3 映射表。

## 6. 脱敏检查清单（逐项，缺一不可）

写入 `persona/` 前逐项确认：

- [ ] **真实姓名**：全文检索真实姓名（含来源字段），一律替换为「宪令」或泛化描述
- [ ] **来源字段泛化**：含真实姓名/客户名/隐私信息的来源文件名 → 泛化为描述性名称（如「自我介绍与简历类原文」）
- [ ] **客户与他人信息**：客户、朋友、家庭成员的可识别信息一律移除或征得用户单独确认
- [ ] **收入与商业细节**：具体收入数字、未公开的商业策略、合作条款不进入应用
- [ ] **旧资料标注**：旧价格/旧权益/旧发售节奏标注历史资料风险
- [ ] **事实边界保留**：原文件的「事实边界」小节必须完整保留，不得删除——这是防夸大护栏
- [ ] **归属标签**：文件末尾保留 🧭 归属 / 📌 来源（泛化后）/ 🎯 应用 三行标签
- [ ] **frontmatter 溯源**：顶部 frontmatter 携带 `source`（私域源路径 + 脱敏说明）与 `sanitized: true`（故事类）

### 默认放行项（不算隐私）

- 「宪令 / xl / zxl」称呼（库内统一称呼，AI 校准必需）
- 用户自写叙事中的第三方品牌名（微淼、顺丰、十倍好等公开叙事组成部分）
- 时间、地点（城市级）、学校名等用户已用于公开自我介绍的经历事实
- 数字类事实（阅读量、篇数、字数）——但必须连同「事实边界」中的口径说明一起保留

## 7. 写后验证

- [ ] 重新读取每个写入的目标文件，确认内容完整落位
- [ ] `persona/README.md` 索引链接指向实际存在的文件（无断链）
- [ ] 新增文件未触发 `.gitignore` 规则（`git check-ignore` 验证）
- [ ] 全文检索确认无真实姓名残留

## 8. Changelog

- **v1.0.0**（2026-10-14）：初始版本。随 boss-manual 应用初始化建立，含 15 个源文件映射、增量流程、8 项脱敏检查。
