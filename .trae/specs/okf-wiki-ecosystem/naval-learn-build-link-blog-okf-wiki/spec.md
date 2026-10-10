# Spec：纳瓦尔"学造连"微信博文 → OKF Wiki 知识包

## 任务输入

- 用户指令：`/七概念 全面学习 https://mp.weixin.qq.com/s/PuC1WJL0rc98a3EbnZj37w ，生成 okf wiki 教程`
- 方法论链路：seven-concepts-cmd（场景 4 知识沉淀，R→I→E→V）→ blog-article-to-okf-wiki 七阶段工作流
- session：sc-20261008-wechat-okf-wiki

## 内容敏感度预检（阶段 0）

| 判据 | 结论 |
|------|------|
| URL 特征 | `mp.weixin.qq.com/s/...`，无 `share?code=`/`token=`/邀请码等访问控制参数 |
| 访问实测 | browser_use 一次打开成功，无验证码、无"继续访问"拦截、无付费墙 |
| 内容主题 | 公开发布的个人成长/财富思维自媒体文章，无个人隐私、无商业秘密 |
| **判定** | **公开内容（Public）** → 标准工作流：spec 在 `.trae/specs/okf-wiki-ecosystem/`，产出在 `projects/awesome-okf-xs/doc/bundles/` |

## 信源元信息

- 标题：《纳瓦尔：发财就是每天循环干这3件事，简单到没人信》
- 公众号 / 作者：洋洋读书成长记（页面未单独标注作者，作者位即公众号名）
- 发布时间：2026-10-02 11:15（位置标签：湖北）
- 正文字数：约 1088 字（不含空白），四个小标题，无代码块/表格/编号列表，2 张无图注配图
- 信源距离预判：**第三方自媒体转述**——公众号非 Naval 本人或官方渠道，属对 Naval 思想的二手中文转述/再创作

## 骨架判定（操作可复现性两问）

1. 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（只有"每天 30 分钟""带着问题学""动手做作品"等原则性倡议）
2. 这些流程是否经作者实测、具备可复现性（版本/输入输出/步骤顺序）？→ **否**（无作者实测、无任何可核验的个人案例数据，唯一案例"一部分人三年被动收入超工资"为匿名叙事）

**结论：两问皆否 → 不设 examples/**，采用 index + concepts/ + references/ + log 概念骨架，index 顶部声明"个人成长/财富思维观点类内容，非操作教程、非投资建议"。

## 归属位置分析（候选对照表）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `sheke/personal-growth/`（选定） | ✅ | ① 文章主线是普通人的**个人行动方法论循环**（学习积累→作品交付→对外链接），落点是自我提升而非理财操作；② 该分组已有公开文章转化先例（human-evolution-real-needs 笔记提纲，flagged/draft）与人物方法论先例（游本昌/胡歌/陶行知簇）；③ 同分组 how-to-live-better 已建立"循证/可信度分层"的内容传统，适合承载本类需勘误的自媒体内容 |
| `sheke/finance/` | ❌ | 该分组定位为投资实操通识（收益数学、资产配置、行为纪律、中国市场制度）与财富寓言书籍解读（pipeline-story），收录原则是"不荐产品、不预测市场、理论事实挂经典与官方"；本文无任何理财/投资实操内容，仅借"被动收入"叙事讲行动习惯，主题不符 |
| `zhexue/methodology/` | ❌ | 该分组收可迁移思维方法与理性实践工具（第一性原理、费曼学习法），本文是财富励志向自媒体文，非方法论工具 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（最小变更原则） |

**bundle 路径**：`projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/naval-learn-build-link/`

## P0 核验总结论（详见 facts.md F-019~F-027）

| # | 博文声明 | 结论 |
|---|---------|------|
| 1 | 纳瓦尔"投资孵化推特、优步等上百家企业" | ✅ 通过（口径修正：系早期**投资人**非"孵化"者；实际天使投资 200+ 家） |
| 2 | "学、造、连"是纳瓦尔给出的致富秘诀 | ❌ **核心失败**：三字诀无 Naval 原始出处；其 2018 原始框架为特定知识+担责+杠杆（Specific Knowledge + Accountability + Leverage），口号 Productize Yourself；原文为 "learn to build **and sell**"，"连（人脉）"并非独立支柱 |
| 3 | "特定知识无法标准化教学" | ✅ 通过（与 Naval 原文一致） |
| 4 | "每天 30 分钟就足够" | ❌ Naval 自述阅读每天 1-2 小时 |
| 5 | "三年被动收入超过固定工资" | ❌ 匿名故事无出处；Naval 称财富复利兑现"通常 10-20 年，有时 5 年"，时间尺度冲突 |
| 6 | 《纳瓦尔宝典》为其思想结集 | ✅ 通过（Eric Jorgenson 编，2020） |
| 7 | 被动收入/作品变现/长期主义方向 | ⚠️ 方向与 Naval 相通（睡后资产、code/media 杠杆、复利），但博文用"链接人脉"替代了原文的"杠杆+股权"核心 |

**状态判定**：第 2 项为文章标题级主推框架（核心声明），核验失败 → 整个 bundle `status: flagged`，verification.md 顶部明示，index 已知边界提示，stale_after 前安排复核。

## 知识地图（三层拆分）

| 层 | 篇目 | 内容 |
|----|------|------|
| 事实层（Who/What，出处何在） | concepts/00-naval-and-source-framework.md | Naval 身份时间线；2018 tweetstorm 与《纳瓦尔宝典》；原始三要素（特定知识/担责/杠杆）与 Productize Yourself；四类杠杆 |
| 分析层（博文框架对照） | concepts/01-learn-build-link-audit.md | "学/造/连"逐项与 Naval 原文对照核验表；30 分钟、三年质变等失实点；框架错位（漏掉杠杆/股权/担责） |
| 读者层（可信边界与用法） | concepts/02-reading-secondhand-wealth.md | 观点/事实/话术三层识别；励志叙事的时间尺度陷阱；二手财富内容的五条阅读纪律；与同库 pipeline-story 财富观念包互链 |

## ADDED Requirements（交付物）

bundle `naval-learn-build-link/` 共 9 个文件：

1. `index.md`（okf_version + flagged 警示 + 性质声明 + 结构 + 已知边界 + toctree）
2. `log.md`
3. `concepts/index.md` + `00`/`01`/`02` 共 4 个
4. `references/index.md` + `article-source.md`（F-001~F-027 双份登记）+ `verification.md`（7 项核验）共 3 个
5. 分组 `sheke/personal-growth/index.md` 接入（导航表 + 阅读路径 + toctree + 束数 9→10）
6. 总索引 `bundles/index.md` 计数同步（590→591、sheke 域 56→57、61 组不变）

## 质量门（V 阶段）

- G1：事实无因果推断词混入（作者观点显式标注 F-010/F-016/F-017）
- G2：核验四元组完整（声明 + 博文口径 + 权威口径 + 结论）
- G3：双份 F 编号集合一致（spec facts.md 与 article-source.md 均 F-001~F-027 连续）
- G4：子模块 `invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8` 三道门；依赖不可用时执行手动等效清单并在 log 注明
- 索引计数以现值为基准 +1（不凭记忆写数）
