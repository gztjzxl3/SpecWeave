# PineDrama 调研知识束 - 变更日志

## 2026-10-08：初始版本（v1.0）

基于截至 2026-10-08 的公开资料多源调研建束。PineDrama 为字节/TikTok 官方闭源商业产品（无源码、无官方财报），source-code-to-okf-wiki 工作流按"闭源项目外部文档分析模式"执行，保留五阶段质量门精神（信源先行、多源交叉、计数带口径、独立验证）。采用七概念方法论场景 4（R→I→E→V→C，depth=standard）。

### R 阶段（事实采集）

- 两轮 WebSearch 采集约 30 个信源，登记 S-01～S-26（P0–P3 分级，转引链显式标注）
- 形成 50 条编号事实 F-01～F-50，覆盖：产品身份、上线时间线、功能形态、增长数据、区域结构、商业模式与行业坐标、字节战略矩阵、红果对照、失败前科、行业环境
- 关键多源锚点：累计下载破 1 亿/DAU 约 700 万（Sensor Tower 口径，五家媒体独立转引一致）；印尼+巴西 82%（Sensor Tower，两家转引）；IAA 时长 15%→83%（Owl &Co.，两家转引）
- 单源事实（如 Q1 分账 2400 万美元、《10亿奈拉新娘》4000 万播放、Melolo 132 万下载）全部标注 `[SINGLE-SOURCE]`

### I 阶段（洞察）

- 提炼 5 条四元组洞察（陈述/证据/反常识/行动）：
  1. 免费 IAA 的落点由支付基础设施决定，而非人均收入（印尼 vs 巴西对比）
  2. 行业剪刀差：竞争从"卖集数"转向"卖时长"（+140% 下载 vs +20% 内购）
  3. 流量与算法优势不能替代本土内容生产（Melolo/PikoShow 对照）
  4. 主端 Minis + 独立 App 的双轨漏斗分工
  5. 红果模式出海的可复制边界：模式可复制，IP/内容供应链不可速成

### E 阶段（文档生成）

- `references/00-sources.md`：信源登记先行（26 条，含分组说明与引用纪律）
- `references/01-data-caliber.md`：数据口径与冲突说明（六套市场规模口径并列，禁止合并）
- `concepts/00-overview.md`～`08-risks-and-outlook.md`：9 篇概念文档，分两批生成
- 根 `index.md`、`concepts/index.md`、`references/index.md` 最后生成，均含 `{toctree}` 块
- 在 `docs/knowledge/tech/index.md` toctree 注册 `pinedrama/index`

### V 阶段（验证）

- 链接检查：`check-links.py --path docs/knowledge/tech/pinedrama`
- 数量陈述回验：所有数字与工作底稿 F 编号逐一对照；机构/月份/口径三要素检查
- 冲突口径：市场规模数字不合并、不取中值，单设 references/01 专页
- frontmatter 完整性：type/title/description/tags/generated/verified/status/stale_after/sources
- 调研工作底稿（50 条 F 事实 + 5 条洞察 + 知识地图）为会话内中间产物，任务完成后已清理，不落为仓库资产

### C 阶段（收尾）

- 本 log 首条版本记录；知识束在 tech 分组导航登记
- 未做 git 提交（用户未要求）
- 未沉淀新 Skill：闭源产品公开资料调研在本会话为首次完整执行，未达三次重复阈值

---

**状态**：draft
**规范**：OKF v0.2
**下次检查**：2027-04-08（stale_after；短剧行业数据季度性变化，建议 2027Q1 复核 Sensor Tower/DataEye 新榜与 PineDrama 收入披露）

---

## 2026-10-09：变现工作指南扩展（v1.1）

在既有知识束上扩展一篇「自动变现工作指南」（`concepts/09-monetization-playbook.md`），将调研从"知道"推进到"行动"。沿用七概念方法论场景 4（R→I→E→V→C，depth=standard，强制 V）。

### R 阶段（事实采集）

- 围绕"内容方如何接入 PineDrama/TikTok 短剧生态并获取分账"采集公开信源，在 `references/00-sources.md` 追加 **S-27～S-50** 登记（P0 官方源：Drama Center 官网 S-40、TikTok for Business S-41/S-49、TikTok for Developers S-50、浙江税务 S-44；媒体战报转引 S-42/S-45/S-46/S-48 等）
- 在 spec 区 `research-notes.md` 建立关键声明速查表 C-01～C-15（声明 → S 编号 → 核验状态）
- G1 自检：事实登记部分 grep 因果/推断词零命中

### I 阶段（洞察）

- 提炼 3 条四元组洞察（见 `path-design.md` §1.4）：
  1. 分成池在涨但个人到手不可预计算（官方不公开统一分成比例）
  2. 企业主体与三流一致是硬门槛，个人直接入驻不可行
  3. AI 短剧承制存在"以量换价"窗口

### E 阶段（文档生成）

- 设计稿 `path-design.md`（spec 区）：第一性原理推导、三角色矩阵、主路径五要素、16 条原子行动项、防画饼自检
- 正式产出 `concepts/09-monetization-playbook.md`：OKF v0.2 frontmatter 九字段，正文中文，含 1 个 mermaid 流程图（安全规范）
- 索引更新：`concepts/index.md`（toctree +1、导航表 +1）、根 `index.md`（导航表 +1；信源行描述同步为 S-01～S-50）
- 说明：根 `index.md` toctree 维持 `concepts/index` 聚合条目（束级约定），新篇由 `concepts/index` 的 toctree 承载，避免 Sphinx 侧边栏重复

### V 阶段（验证）

- 对抗审查（`review.md`，spec 区）：四视角（魔鬼代言人/新人/老板/未来）+ 魔鬼代言人证伪「画饼路径」，共 10 条具体发现（P0×1/P1×3/P2×4/P3×2）
- 采纳修复 4 条并回写 playbook：① 弱化「挂靠」建议、强调主体一致性合规风险；② 明确「月万分钟计划」个人产能不可达；③ 专项激励入口未公开 → 标「待验证」；④ 补充 Drama Center 官网入口
- 路径可达性评分 **2/2**：主路径七项画饼点全部证伪通过，无未修复发现
- G3 门补充：playbook 新增「可迁移模式」节（触发场景/核心步骤/反模式/迁移验证），满足 AC-9 质量门
- 机械验证：链接可达、零 `file:///`、frontmatter 九字段、toctree 目标存在、mermaid 禁用项清零、S 编号连续、收益声明抽查（详见 Task 7 记录）

### C 阶段（收尾）

- 交付汇总见最终回复；产物：`concepts/09-monetization-playbook.md` 新增、两处索引更新、`references/00-sources.md` 追加 S-27～S-50、`log.md` 本记录
- 未做 git 提交（用户未要求）
