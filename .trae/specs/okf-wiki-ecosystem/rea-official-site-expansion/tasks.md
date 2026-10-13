# REA 中文官网第四轮增量更新任务

## Task 1: 全站采集与逐页覆盖登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 批量读取 sitemap 中的 17 个中文页面并机械盘点各页内部链接，扩展到全部发现的中文内容页。
  - 正文提取不足时读取 HTML/相关页面源码；保存访问结果、章节和必要证据，临时缓存位于工作区外。
  - 检查子模块 merge/rebase 状态，批准后先落本轮 references 官网信源登记与覆盖表。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1：中文 sitemap 集合与发现链接集合的未处理差集为空；失败页单独记录且不计入已学习。
  - `rule` TR-1.2：每页均有 URL、访问日期、章节概要、知识归属与覆盖状态；折叠内容/交互实验的证据不足单独说明。
- **Completion Evidence**:
  - 官网台账 official-site-source.md 登记 W01~W17；17 个 HTML/Markdown 快照均已读，折叠正文及八份 website/evidence 文档已回验。
  - 2026-10-12 集合复核：HTML=17、Internal=17、Sitemap=17，双向差集为空；图片未 OCR、页面交互未本机实跑已声明。

## Task 2: 事实续编号与洞察设计
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 对照 F-001~F-135，新增 F-136 起事实；数字与历史案例版本逐项回验。
  - 区分官方自述、源码印证和推断，补充独立的新洞察及页面到教程映射。
  - 对既有疑似错误形成勘误清单，保留历史来源与修正理由。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-2.1：事实定义编号唯一、连续；新增声明全部具有已读页面 URL/章节指向，旧编号未重排。
  - `rule` TR-2.2：数量陈述有来源与统计/验证口径；官网快照、固定源码和历史案例版本分开登记。
  - `rubric` TR-2.3：知识地图与洞察质量，1-5，1=重复摘要、3=有分层但证据或行动不清、5=洞察四元组完整且覆盖新手与进阶路径；阈值>=4；证据为 insights 与页面映射。
- **Completion Evidence**:
  - 事实定义脚本结果 Facts=180 Unique=180，顺序等于 1~180；F-136~F-180 保留 W 编号及已读章节来源。
  - 固定 blob 客户端 name=18、unique=18、unsupported=1；docs=48；版本、CI、schema 及历史案例数字分开回验，见 official-site-verification.md。
  - TR-2.3 自评 4/5：10 项洞察均含陈述、证据、反常识和行动，第四轮地图映射新手与进阶路径；未运行原目标的限制已保留。

## Task 3: 教程与示例增量更新
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 每批不超过 7 文件，续接主题文档；补安装/首次调查、三类指南、完整案例证据和实验验证。
  - 对新增与修改命令核对完整调用形态，修正既有示例错误并留勘误。
  - 内容完成后统一更新各级 index/toctree 与 log，不修改无关父级计数或创建重复知识包。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-3.1：所有本轮命令的必填参数/选项均有对应官方文档或源码依据；示意输入与未实跑说明明确。
  - `rule` TR-3.2：所有新增文件被索引和 toctree 收录，sources 使用 resource，子页面不含 okf_version，链接使用标准相对路径。
  - `rubric` TR-3.3：教学可用性，1-5，1=摘要集合、3=主要路径完整但验证判据不清、5=前置/输入/步骤/证据/验收/限制完整；阈值>=4；证据为 concepts/examples。
- **Completion Evidence**:
  - 13 篇概念、8 篇示例、5 篇参考与四级索引及 log 共31 Markdown；官方 toctree run_scan(bundle) 无错误。
  - sources/YAML/UTF-8/okf_version 自验通过；新增命令形态与接口示意限制见验证表；binary_session 和 tools/list 职责已分开。
  - TR-3.3 自评 4/5：Notes 与公开算法有输入、步骤、结果判据；五案例区分编译、函数与整程序验证。Apple/Electron 仍为明确标注的接口示意，非完整重建。

## Task 4: 验证与独立审查
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 独立手段复核页面覆盖、事实计数、数字与命令；跑链接、frontmatter、UTF-8、toctree 和定向构建。
  - 队列清空后创建 review.md，向全新上下文委托只读独立审查。
  - 审查失败时建立修复 issue、修补并重新审查；通过后提供文件入口与验证结果，不自行提交 Git。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1：机械覆盖复核无未处理中文内容页，引用与命令回验无未解释差异。
  - `rule` TR-4.2：本轮链接、frontmatter、UTF-8、toctree 与定向构建检查通过；全库问题按归属隔离并如实报告。
  - `rubric` TR-4.3：实施者按 AC-4 量表自评>=4并提供证据；独立 Review 队列清空后再复核评分及全部 rule，无遗留可行动发现才结束。
- **Notes**:
  - 阶段解释：独立 Review 是队列清空后的最终门，不作为实施任务的循环前置条件；AC-4/AC-5 的最终验收不变。
- **Completion Evidence**:
  - ✅ 独立审查 Review R1 已执行并回填 review.md：CP-R1~R4 均 PASS、CP-U1=4/5（≥4 达标），**总结果 PASS**，AC-1~AC-5 全部达标，无遗留可行动缺陷。下述为独立复核与实施者自验证据。
  - HTMLParser 复核 HTML=17、Internal=17、差集为空；Invoke-WebRequest 实时 sitemap=17，与缓存差集为空。
  - UTF8/YAML/Source/Toctree PASS，Markdown=31 Facts=180 Unique=180；有效链接扫描31文件/155本地引用全部存在。
  - Sphinx9.1.0 原配置限定本束 dummy -E -W 构建31文档成功、零警告；git diff --check通过。未声称全库或HTML视觉验收。
  - 公开教学算法：CTF26方程、数值算术、133组Python/WebCrypto、恐龙5输入及4教学JS代码块均通过；未运行原目标或REA。
  - TR-4.3实施者自评4/5；经独立 Review R1 复核评分一致并裁决通过（详见 review.md）。

## 批准门

本规格与计划已在前序会话通过用户批准门，恢复时沿用该批准，进入实施。批准范围不包含安装 REA/逆向引擎、运行目标程序或 Git 提交。2026-10-12 恢复检查：子模块工作树干净，rebase-merge/rebase-apply/MERGE_HEAD 均不存在。
