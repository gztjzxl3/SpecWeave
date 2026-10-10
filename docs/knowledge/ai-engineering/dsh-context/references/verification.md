# dsh-context P0 核验（Verification）

> 采集协议：wechat-public-okf 的 P0 核验。对日期/数量/兼容/官方声明等"可被证伪"的声明逐一核验，尽量给出独立权威 URL；无法独立核验者标 `single-source` 或 `single-source/flagged`。绝不把作者观点升级为研究事实。

## 核验方法

- 主信源：公众号文章（defuddle 提取，采集日 2026-10-10）。
- 交叉信源：GitHub 仓库 `bowenliang123/dsh-context`（2026-10-10 只读核验，含 README 与文件提交记录）。
- 声明类型：`page_fact`（可核验页面事实）/ `author_claim`（作者/发布者观点）。

## 核验表

| # | 声明（关联 F） | 声明类型 | 核验结果 | 独立依据 | 判断 |
|----|---------------|---------|---------|---------|------|
| V-01 | 安装 CLI 命令 `dsh plugin --profile web add dsh-context`（F-022） | page_fact | 与 GitHub README 完全一致 | github-repo README "Install with dsh cli" | ✅ 通过 |
| V-02 | 更新命令 `dsh plugin --profile web update dsh-context@latest`（F-023） | page_fact | 与 GitHub README 一致 | github-repo README | ✅ 通过 |
| V-03 | 装后用 `dsh web` 启动，无需构建、无需重启（F-024） | page_fact | 与 GitHub README 一致 | github-repo README | ✅ 通过 |
| V-04 | 兼容矩阵覆盖 dsh 0.1.5-rc.1 / 0.1.7-rc.2 / 0.2.0-rc.2（F-025） | page_fact | **存在时效漂移** | github-repo 提交记录（2026-10-07："drop dsh 0.1.5-rc.1, floor the support matrix at 0.1.7-..."） | ⚠️ 部分通过 / 需双口径呈现 |
| V-05 | 包要求 Node `^22.19.0` 或 `>=24.0.0`（F-026） | page_fact | 文章引 README，本核验未抓包 manifest 明细 | npm 包未单独核验 | ⚠️ single-source（待补 npm 核验） |
| V-06 | 开源地址 github.com/bowenliang123/dsh-context（F-032） | page_fact | 仓库存在且与 README 一致 | github-repo | ✅ 通过 |
| V-07 | 仓库 Apache-2.0、约 2.0k star、59 forks（F-033） | page_fact | 与仓库页一致 | github-repo | ✅ 通过 |
| V-08 | 四入口（Context Insights page / Context tab / Context panel / `/context` 命令）（F-004/F-035） | page_fact | 与 README 一致 | github-repo README | ✅ 通过 |
| V-09 | 占用率采用 DSH 官方 token-meter 投影（contextPressure/contextBreakdown）（F-009/F-039） | page_fact | 与 README 一致 | github-repo README | ✅ 通过 |
| V-10 | Context Browser 含 Skill Injections 独立类目（F-040） | page_fact | 与 README 一致 | github-repo README | ✅ 通过 |
| V-11 | "被 DSH 团队成员 @tianyicui/@turtle1999 推荐并 star"（F-036） | page_fact | 来自 README 作者自述；附 X 帖链接；**属第三方推荐观察，非官方保证** | github-repo README | ⚠️ 单源 + 观察性，正文须降权标注 |
| V-12 | "不会主动删上下文、不替你决定何时压缩"（F-028） | author_claim | 单一来源（文章作者判断） | wechat-article | ⚠️ single-source，正文标观点 |
| V-13 | "工具定义与工具结果常占上下文大头"（F-011） | author_claim | 单一来源，经验判断 | wechat-article | ⚠️ single-source，正文标观点 |

## 核验结论

- 硬性 P0（安装命令、仓库地址、许可证、高热度）全部通过 ✅。
- **兼容矩阵存在版本漂移**：文章所述"覆盖 0.1.5-rc.1"在验证时点已被上游丢弃（2026-10-07 起 matrix 下限为 0.1.7-...）。正文按"文章时点 / 验证时点"双口径呈现，引用请勿退回旧口径。
- Node 版本要求（F-026）为单源，未取 npm manifest 独立复核，标 `single-source`，建议在 stale_after 前补核。
- 作者观点（F-007/F-011/F-027/F-028/F-029/F-030/F-031）一律在正文显式标注为观点，不作为事实引用。

## 未覆盖边界

- 未在本机实际安装运行 dsh-context；以上为信源层核验，非真机验证。
- 未对 GitHub README 全部功能截图逐张比对；仅核验与文章相关的声明维度。
- npm 包版本明细、Node 引擎声明未单独抓取核验。