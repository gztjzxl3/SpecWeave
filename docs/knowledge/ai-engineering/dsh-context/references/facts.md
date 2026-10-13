# dsh-context 事实清单（Facts）

> 采集协议：wechat-public-okf 的 R 阶段。连续 F-001 编号；区分 `page_fact`（页面事实）与 `author_claim`（作者观点）；执行者解读不入本表，见 [knowledge-map.md](knowledge-map.md)。

| F | claim | type | source_id | locator | status |
|----|-------|------|-----------|---------|--------|
| F-001 | dsh-context 是 DeepSeek Harness（DSH）的开源插件，用于把 AI Agent 上下文生命周期可视化 | author_claim | wechat-article | 文首宣介 | registered |
| F-002 | 文章来自微信公众号「AI开源无界」，标题关于 dsh-context 上下文"全部可视化" | page_fact | wechat-article | 标题与文末名片 | verified |
| F-003 | 文中称"装上它，一次会话的上下文由什么组成、后来怎么变、什么时候压缩或剪枝，都能直接看" | author_claim | wechat-article | 文首 | registered |
| F-004 | 文章给出四种查看入口：跨会话 Context Insights 页面、单个会话 Context 标签页、右侧栏 Context 面板、聊天内 `/context` 命令 | page_fact | wechat-article | 《它能看什么》 | registered |
| F-005 | Context Insights 面向一段时间内所有会话：列出会话数、计费 token、估算费用、缓存命中率、近 7 天用量柱状图、近几周活动热力图 | page_fact | wechat-article | 《跨会话用量》 | registered |
| F-006 | Context Insights 下方每个会话都有上下文组成环、token 数、轮次、估算费用，可按时间/token/上下文大小排序、按工作区分组 | page_fact | wechat-article | 《跨会话用量》 | registered |
| F-007 | 文称费用估算按 models.dev 目录价，并把 DeepSeek 峰谷价算入，"也就是看个大方向" | author_claim | wechat-article | 《跨会话用量》 | registered |
| F-008 | 单个会话 Context 标签页含轮次、步数、工具调用、缓存命中率、token 去向与时间分配，往下还有当前窗口、趋势、浏览器、事件、文件活动、Agent 网络 | page_fact | wechat-article | 《单个会话的 Context 页面》 | registered |
| F-009 | 面板头部占用率与组成使用与 DSH 官方 token meter 同一组投影数据 | page_fact | wechat-article | 《单个会话的 Context 页面》 | registered |
| F-010 | Current Context 用多色堆叠条展示当前上下文窗口分类占用：系统提示、工具 schema、用户消息、注入内容、助手回复、工具结果，剩余用斜纹 | page_fact | wechat-article | 《当前窗口的组成》 | registered |
| F-011 | 文称上下文不够用时工具定义与工具结果常占大头，非用户输入本身；插件会标出占用最高的工具 schema | author_claim | wechat-article | 《当前窗口的组成》 | registered |
| F-012 | 文称分类数字为估算值，用 DSH 固定密度启发式；钉住某步后 provider 上报的实际 prompt/output/cache 数字才会出现在估算值旁 | page_fact | wechat-article | 《当前窗口的组成》 | registered |
| F-013 | Context Trend 把每次模型请求画成一根堆叠条，可切 Step/Turn 粒度、总量/增量；压缩与剪枝会标在对应柱子上 | page_fact | wechat-article | 《上下文变化趋势》 | registered |
| F-014 | 趋势图下有 step 摘要，写出用户发了什么、新进入上下文的内容、模型回复或调用的工具；Delta 模式下增长堆在基线上方、压缩往下掉 | page_fact | wechat-article | 《上下文变化趋势》 | registered |
| F-015 | Context Browser 可打开保留下来的请求，查看该次请求实际组成；各分类可展开（系统提示原文、工具 JSON schema、消息正文、工具结果参数/状态/返回值） | page_fact | wechat-article | 《Context Browser》 | registered |
| F-016 | 助手回复可按 Thinking / Tools / Answer 筛选；图片以卡片展示（缩略图、尺寸、存储大小、DeepSeek 图像 token 估算） | page_fact | wechat-article | 《Context Browser》 | registered |
| F-017 | 工具 schema 会尽量标出来源：官方 `tool-*` 包、`dsh-*` 能力包、某 MCP server、或插件注册的工具 | page_fact | wechat-article | 《Context Browser》 | registered |
| F-018 | Context Browser 可与上一轮 diff，类目增减条数与 token 用徽标标出；压缩前步骤从被移除消息归档重建并标"近似" | page_fact | wechat-article | 《Context Browser》 | registered |
| F-019 | File Activity 按文件列出 Agent 操作（读/写/搜/图），写操作估算新增删除行数，可跳回 Context Browser 对应工具结果 | page_fact | wechat-article | 《文件活动和 Agent 网络》 | registered |
| F-020 | Agent Network 展示主 Agent、父级 Agent 与所有子 Agent；环大小按窗口占用缩放，悬停看 token/请求数/费用/活跃时间，点进对应会话 | page_fact | wechat-article | 《文件活动和 Agent 网络》 | registered |
| F-021 | 安装方式一：DSH Web/桌面端打开 Add plugin，搜索 `dsh-context`，点击 Install | page_fact | wechat-article | 《安装方式》 | verified（与 github-repo README 一致） |
| F-022 | 安装方式二（CLI）：`dsh plugin --profile web add dsh-context` | page_fact | wechat-article | 《安装方式》 | verified（与 github-repo README 一致） |
| F-023 | 更新命令：`dsh plugin --profile web update dsh-context@latest` | page_fact | wechat-article | 《安装方式》 | verified（与 github-repo README 一致） |
| F-024 | 装完用 `dsh web` 启动 Web UI；README 称无需手动构建、无需额外重启 | page_fact | wechat-article | 《安装方式》 | verified（与 github-repo README 一致） |
| F-025 | 文称兼容矩阵覆盖 `@deepseek-ai/dsh` 0.1.5-rc.1、0.1.7-rc.2、0.2.0-rc.2 三条版本线 | page_fact | wechat-article | 《安装方式》引 README | **flagged**（与验证时点 README 存在漂移，见 verification） |
| F-026 | 包要求 Node `^22.19.0` 或 `>=24.0.0` | page_fact | wechat-article | 《安装方式》引 README | flagged（待 crosscheck） |
| F-027 | 文提醒插件是本机跑的第三方代码，装前应翻源码、依赖、看仓库是否活跃；此提醒对 DSH 插件通用 | author_claim | wechat-article | 《安装方式》 | registered |
| F-028 | 文称 README 用了 management 字样，但公开文档看 dsh-context 主要能力是观测、定位、回看；不会主动删上下文、不替你决定何时压缩 | author_claim | wechat-article | 《容易误读的地方》 | registered |
| F-029 | 文称真想省上下文，应从工具数量、提示词、注入内容、任务拆分下手 | author_claim | wechat-article | 《容易误读的地方》 | registered |
| F-030 | 文称偶尔用 DSH 聊几句装不装差别不大；长会话、多工具、多插件、多 Agent 场景信息更多 | author_claim | wechat-article | 《适合哪些情况》 | registered |
| F-031 | 文称更愿意把它当排查工具用；不改模型、不负责省 token，只把上下文组成/变化/文件操作/Agent 关系摊开 | author_claim | wechat-article | 《适合哪些情况》 | registered |
| F-032 | 开源地址：https://github.com/bowenliang123/dsh-context | page_fact | wechat-article | 《开源地址》 | verified（github-repo 存在） |
| F-033 | GitHub 仓库 `bowenliang123/dsh-context`：Apache-2.0 许可证、约 2.0k star、59 forks、902 commits、1 分支、133 标签 | page_fact | github-repo | 仓库页 | verified |
| F-034 | 仓库 README 定位为 "The best DeepSeek Harness plugin for Agent's context insights and management" | page_fact | github-repo | README 标题 | verified |
| F-035 | README 四入口：Context Insights page、Context tab、Context panel（右侧栏）、`/context` 命令 | page_fact | github-repo | README Install/Use it | verified |
| F-036 | README 称被 DeepSeek Harness 团队成员 @tianyicui、@turtle1999 推荐并 star，附 X 帖链接 | page_fact | github-repo | README 引言 | registered（第三方推荐观察） |
| F-037 | Context Insights 页含 KPI band（7d/30d/all）、7 天用量图、活动热力图、设置入口、Context Composition 汇总环、可筛选会话卡片 | page_fact | github-repo | README Context Insights page | verified |
| F-038 | Context 标签页含 Context Stats / Token Stats / Timing Stats / Current Context / Context Trend / Context Browser / Context Events / File Activity / Agent Network | page_fact | github-repo | README Context tab | verified |
| F-039 | 占用率与组成读取 `contextPressure` / `contextBreakdown`（官方 token-meter 投影），与聊天区上下文环一致 | page_fact | github-repo | README Context tab | verified |
| F-040 | Context Browser 含 Skill Injections 独立类目，避免技能上下文占用混入注入/工具结果桶 | page_fact | github-repo | README Context Browser | verified |
| F-041 | 工具 schema 来源标记：tool-* 一包、dsh-* 能力包、mcp:<server> 代理、或 plugins 注册工具 | page_fact | github-repo | README Context Browser | verified |
| F-042 | 由 DSH 多模态管线图像 token 估算（如 read_image 结果与图像附件） | page_fact | github-repo | README Context Browser | verified |
| F-043 | 验证时点（2026-10-10）仓库最近提交称"drop dsh 0.1.5-rc.1，floor the support matrix at 0.1.7-..."（2026-10-07 提交） | page_fact | github-repo | 仓库文件提交记录 | verified |