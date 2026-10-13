---
type: Reference
title: "LIFT 文章与官方材料事实登记"
source: "source-manifest.md 中登记的公开来源；采集时点 2026-10-10"
---

# 事实登记

事实按可核验来源记录。`author_claim` 仅表示文章作者的表述，不代表独立验证结论；官方材料事实以对应文档当前可见内容为准。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 文章标题为《Agent 会越用越聪明吗？这个开源项目开始量化「自我进化」！》。 | page_fact | blog | 页面标题 | verified |
| F-002 | 页面账号显示为「开源星探」。 | page_fact | blog | 账号署名区域 | verified |
| F-003 | 页面标记该文章为原创。 | page_fact | blog | 原创标记 | verified |
| F-004 | 页面显示发布时间为 2026-10-09 07:03，页面未注明时区。 | page_fact | blog | 页面发布时间 | verified |
| F-005 | 文章将 LIFT 介绍为量化 Agent 自我进化影响的一种评测框架，并以领域缺少统一衡量方式作为问题背景。 | author_claim | blog | 正文导语与项目介绍 | attributed; framing narrowed in bundle |
| F-006 | 文章指向的项目仓库为 `FeiZhuNiU-INFJA/LIFT`。 | page_fact | blog | 项目链接 | verified |
| F-007 | 官方仓库将项目描述为 “An Evaluation Framework for Self-Evolving-Agent (Loaded Impact on Holdout Final Task)”。 | official_fact | repo | GitHub repository description | verified |
| F-008 | 官方排行榜 JSON 的 `generated_at` 值为 `2026-08-23T15:14:31Z`。 | official_fact | leaderboard | `generated_at` | verified |
| F-009 | 官方排行榜声明 10 次 repeats 和 95% confidence interval。 | official_fact | leaderboard | leaderboard metadata | verified |
| F-010 | 官方排行榜 JSON 列出 11 个 runtime。 | official_fact | leaderboard | runtime entries | verified |
| F-011 | 官方论文页面报告 11 个 runtimes、14 个 scenes 和 84 个 tasks。 | official_fact | paper | evaluation summary | verified |
| F-012 | 官方论文将自身标记为 v1 preprint，并称结果来自 partial cross-runtime sweep，完整重复试验仍待后续更新。 | official_fact | paper | abstract / limitations | verified |
| F-013 | LIFT 文档区分 Warmup 与 Holdout 阶段，并将 Holdout 用作最终评估任务集。 | official_fact | benchmark | benchmark protocol | verified |
| F-014 | 评测将同一 Holdout 任务分别用于 Base 与加载演化产物后的 Loaded 条件。 | official_fact | benchmark | paired evaluation description | verified |
| F-015 | LIFT 使用 Docker 容器及 Delta 镜像/状态保存流程组织演化状态与 Holdout 评测环境。 | official_fact | eval-flow | evaluation flow | verified |
| F-016 | Suite 文档中的任务字段包括 query、requirements 和 trajectory requirements。 | official_fact | suite | task schema | verified |
| F-017 | 评测流程包含工作 Agent 与 Judge 的多轮交互。 | official_fact | eval-flow | agent/judge loop | verified |
| F-018 | 官方排行榜比较 turns、tools、tokens 和 latency 等效率指标。 | official_fact | leaderboard | metric fields | verified |
| F-019 | 排行榜构建脚本按 `(sum(evolved_X) - sum(baseline_X)) / sum(baseline_X) * 100` 计算 delta。 | official_fact | leaderboard-script | delta calculation | verified |
| F-020 | 按上述公式，负 delta 表示 Loaded 条件的对应资源/时延指标低于 Base 条件。 | official_fact | leaderboard-script | delta calculation; interpretation | verified |
| F-021 | 排行榜脚本先按每个 repeat 计算比例变化，以总体标准差（ddof=0）和正态近似计算 95% CI（均值 ± 1.96 × 标准差 / sqrt(n_repeats)）；CI 上界低于零时标记该指标显著下降。 | official_fact | leaderboard-script | per-repeat CI and significance logic | verified |
| F-022 | 官方论文讨论 Judge 偏差和评测环境保真度等局限。 | official_fact | paper | limitations | verified |
| F-023 | 官方论文提示不同 runtime 的绝对分数不宜直接作为跨 runtime 能力排名。 | official_fact | paper | comparison caveat | verified |
| F-024 | arXiv 在 2026 年 2 月已有题为 SE-Bench 的 Agent 自进化评测相关预印本记录。 | related_work | se-bench | arXiv:2602.04811v1 | verified |
| F-025 | arXiv 在 2026 年 7 月已有 EvoAgentBench 相关预印本记录。 | related_work | evoagentbench | arXiv:2607.05202 | verified |
| F-026 | GitHub API 对 LIFT 仓库返回 `license: null`，检查的仓库树中未发现 LICENSE 文件。 | official_fact | github-api | repository metadata and file tree | verified at collection time |
| F-027 | LIFT 仓库描述将缩写展开为 “Loaded Impact on Holdout Final Task”；论文标题则使用 “Loaded Impact on Final Task”，未包含 Holdout。 | official_fact | repo; paper | repository description; paper title | verified |
| F-028 | Suite 文档说明 Holdout requirements 与 Warmup requirements 约有 75% 重合，其余为变体或矛盾要求。 | official_fact | suite | requirement overlap description | verified |
| F-029 | 排行榜元数据声明 `n_repeats=10`；当前 11 个 runtime 条目的 `paired_task_repeats` 为 274 至 280。 | official_fact | leaderboard | repeat metadata and runtime entries | verified |
| F-030 | 运行时代码将排行榜 `turns` 字段映射到 `trials`，表示一个任务内 work Agent 与 Judge 的实际交互轮数，直到成功或达到上限。 | official_fact | runtime-task-loop; leaderboard-script | `src/lift/eval/run_task.py::run_task` 返回值；`scripts/build_leaderboard.py` 的 `trials` 映射 | verified |
| F-031 | 采集时 GitHub API 指向的 LIFT 仓库 `main` 提交为 `9d282e415c5e3b0f65b82c8758a013b269583d93`（提交时间 2026-09-11T05:33:00Z）。 | official_fact | repo-snapshot | GitHub API main commit | verified at collection time |

## G1 检查

- 编号连续：F-001 至 F-031，无跳号。
- 页面事实与作者主张分开；机制事实来自 LIFT 官方材料。
- F-020 为对官方公式的直接符号解释，未扩展为绝对能力结论；F-021 区分了总体聚合点估计与按 repeat 计算的区间。
- F-024、F-025 仅用于限制“领域无人衡量”的宽泛说法，不据此声称这些基准与 LIFT 设计相同。
