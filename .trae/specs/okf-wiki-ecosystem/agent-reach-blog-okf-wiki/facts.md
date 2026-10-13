# 事实集：Agent Reach 博文 → OKF 知识包

- **主信源**：微信公众号「AI赋能干货铺」《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》
- **URL**：https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
- **发布时间**：2026-10-06 15:03（作者「学生小孙」原创，IP 辽宁）
- **采集日期**：2026-10-08
- **信源距离**：第三方公众号综述（非厂商自宣、非一手实测），以转述 README + 作者架构解读为主，已升级官方一手材料交叉核验
- **编号规则**：F-001~F-054 博文事实；F-055~F-072 为官方核验补充（含勘误）。本文件是唯一合法事实集。
- **类型标注**：O=客观事实，V=作者观点/评价，S=厂商（项目方）自述

---

## A. 博文元信息（F-001 ~ F-003）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-001 | 博文标题《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》，全文 6833 字，含 10 个编号小节 | 微信博文 O |
| F-002 | 公众号「AI赋能干货铺」，作者「学生小孙」（原创），2026-10-06 15:03 发布，IP 属地辽宁；文末有"抽一位送咖啡"等公众号常规互动引流 | 微信博文 O |
| F-003 | 推介项目 **Agent Reach**，项目地址 https://github.com/Panniantong/Agent-Reach（文中出现两次） | 微信博文 O |

## B. 项目身份与热度（博文口径，F-004 ~ F-007）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-004 | 博文头部信息卡：GitHub 92,000+ Star；语言 Python 3.10+；协议 MIT；Star 约 92,000、Fork 约 8,000；覆盖渠道 16 个（其中 6 个开箱即用）；首次发布 2026 年 2 月，至今不到 8 个月 | 微信博文 O（数字核验见 F-056，口径见 F-061） |
| F-005 | 一句话概括（博文）："它不是一个抓取工具，而是一个能力层——替你选型、安装、体检、路由，把'让 AI 读懂全网'这件反复折腾的事，变成一句命令" | 微信博文 O（定位转述） |
| F-006 | 技术栈口径：Python 3.10+、MIT 协议 | 微信博文 O（核验 F-055/F-059） |
| F-007 | 正文第 1 节称"这才是它 92k Star 的真正原因：它卖的不是功能，是'不用再操心'"；结尾段称"一个 92k Star 的项目，维护动力来自自用而非流量" | 微信博文 V（作者归因，非可核验因果） |

## C. 痛点与能力层定位（F-008 ~ F-014）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-008 | 博文列举六个平台门槛：YouTube 抽字幕要装 yt-dlp 且区分自动/手动字幕；Reddit 匿名接口被封、官方 API 审批制只剩登录态；B站通用下载工具被风控拦死返回 412；小红书不登录打不开、登录涉及凭据；GitHub 认证配置坑多；全网搜索好用的付费、免费的质量差 | 微信博文 O（其中 B站 412 核验见 F-064） |
| F-009 | 博文引用 README 原文："这些不难实现，但是需要自己折腾配置"；并归纳痛点为"别让我每次都重来一次"（平台策略变化后要重新踩坑） | 微信博文 O/S（README 引文） |
| F-010 | 定位对比（博文）："绝大多数同类项目"做"帮你抓 XX 平台"的工具，寿命等于依赖路径能活多久；Agent Reach"不做抓取，只负责选型、安装、体检、路由，抓取由 Agent 直接调用上游工具完成，中间没有包装层" | 微信博文 O（作者对项目设计的转述） |
| F-011 | 故障对比（博文）：传统做法 yt-dlp 被 B站封死→工具坏了→等作者修→Agent 瞎；能力层做法→调整 B站渠道后端列表顺序→用户零操作 | 微信博文 O（机制描述，事实核验 F-064） |
| F-012 | 博文引用 README 原文："当下最稳的接入方式，我们替你选好、装好、体检好。接入方式会换代，你不用操心。" | 微信博文 S（README 引文） |
| F-013 | 博文的架构语言翻译："它把'易变的接入方式'封装在了一层稳定接口后面。变的永远是实现，不变的是 agent-reach 这个入口和那 16 个渠道名" | 微信博文 V（作者解读） |
| F-014 | 博文小节标题《定位：它是能力层，不是第 17 个工具》，并称这是"整个项目最值得 AI 开发者学习的一点" | 微信博文 V |

## D. 核心机制一：有序后端列表（F-015 ~ F-018）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-015 | 博文给出 channels/ 目录树示意（9 个文件）：web.py→Jina Reader；twitter.py→twitter-cli ▸ OpenCLI ▸ bird；youtube.py→yt-dlp；github.py→gh CLI；bilibili.py→bili-cli ▸ OpenCLI ▸ 搜索 API；reddit.py→OpenCLI ▸ rdt-cli；xiaohongshu.py→OpenCLI ▸ xiaohongshu-mcp ▸ xhs-cli；rss.py→feedparser；exa_search.py→Exa via mcporter | 微信博文 O（树为示意，实际规模核验 F-063） |
| F-016 | 机制描述：每个渠道维护有序候选后端列表，第一个首选、依次备选；渠道通过 `active_backend` 字段上报当前实际在用的后端；"换接入方式=调整列表顺序，不是重写代码" | 微信博文 O（核验 F-065/F-067） |
| F-017 | 博文称可用环境变量单独覆盖某渠道后端（文中写作"`_backend`"，即对应渠道名后缀形式）；不信任某条路可改对应 channel 文件，其他渠道不受影响 | 微信博文 O |
| F-018 | 作者启示："面对'上游随时会变'的依赖，不要写 if upstream_a ... else 分支，写一个有序候选列表+探测选主。分支会随上游数量爆炸，列表不会" | 微信博文 V |

## E. 核心机制二：doctor 真体检（F-019 ~ F-022）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-019 | 博文批评常见健康检查只做 `which xxx`；列举真实失败形态：venv shebang 因系统 Python 升级失效、依赖在但网络超时、二进制存在但登录态过期 | 微信博文 V/O（现象描述） |
| F-020 | probe.py 真跑上游命令，三态分类：**missing**（没装→给安装命令）、**broken**（装了跑不通如 shebang 失效→给重装处方）、**timeout**（能跑但超时→提示网络或凭据问题）；"告诉你哪里坏了、怎么修" | 微信博文 O（核验 F-065） |
| F-021 | `agent-reach doctor --json` 支持 JSON 输出；JSON 中 `active_backend` 让 Agent 动手前知道该调哪套命令，无需先试错；博文称"这个设计是给 Agent 看的，不是给人看的" | 微信博文 O |
| F-022 | 作者产品判断："同一份诊断信息同时服务人和 Agent——文本报告给人读，JSON 给 Agent 读。做 Agent 基础设施的项目，几乎都会走到这一步" | 微信博文 V |

## F. 真实故障案例（F-023 ~ F-027）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-023 | 2026 年 6 月 B站风控升级，yt-dlp 拉 B站内容全面返回 412 | 微信博文 O（核验 F-064） |
| F-024 | 应对：channels/bilibili.py 后端列表本为 bili-cli ▸ OpenCLI ▸ 搜索 API，yt-dlp 退役、bili-cli 顶上，用户什么都不用做 | 微信博文 O |
| F-025 | 博文转述 README"当前选型"表：B站首选 bili-cli 备选 OpenCLI ▸ 搜索 API（退役原因"yt-dlp 被 B站风控 412 封死（2026-06 实测）"）；Twitter 首选 twitter-cli 备选 OpenCLI ▸ bird（OpenCLI 走登录态兜底）；Reddit 首选 OpenCLI（桌面）备选 rdt-cli；全网搜索 Exa via mcporter（MCP 接入免 Key） | 微信博文 O/S |
| F-026 | 博文称 2026 年 3 月有一批单平台 CLI 集体停更，项目换了一轮路由；"这种事在这个领域不是意外，是常态" | 微信博文 O（核验 F-064） |
| F-027 | 作者建议："判断一个 Agent 基建项目值不值得用，别看它现在支持多少平台，去看它的 CHANGELOG 里有没有'后端换了一轮但用户无感'这类记录" | 微信博文 V |

## G. 16 渠道三档（F-028 ~ F-033）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-028 | 博文称项目支持 16 个渠道，分三档：开箱即用（零配置）、一句话解锁、需要登录态 | 微信博文 O（16 总数核验 F-060；档内计数口径 F-061） |
| F-029 | 博文"开箱即用"档列出 **7** 个：任意网页（Jina Reader）、YouTube（字幕+搜索）、GitHub（读公开仓库+搜索）、RSS/Atom、全网语义搜索（Exa）、V2EX、B站（搜索+详情，无需登录）——与头部信息卡"6 个开箱即用"不一致 | 微信博文 O（**博文内部口径矛盾，勘误 F-061**） |
| F-030 | "一句话解锁"档 5 个：Twitter/X（搜索、时间线）、雪球（行情、热门）、小宇宙播客（音频转文字）、LinkedIn、Boss直聘；方式为直接跟 Agent 说"帮我配 XXX"由其引导 | 微信博文 O |
| F-031 | "需要登录态"档 4 个：小红书、Reddit、Facebook、Instagram（涉及浏览器会话或 Cookie） | 微信博文 O |
| F-032 | 博文称小红书链路项目明确"不替用户登录、不读浏览器 Cookie——OpenCLI 只使用用户已有且明确控制的浏览器会话"，作者评价"这个克制在同类项目里很少见" | 微信博文 O + V |
| F-033 | 博文转述作者安全提醒：需要 Cookie 的平台务必使用专用小号；脚本调用有被平台检测限制的风险，Cookie 等同完整登录权限，小号可圈住影响范围 | 微信博文 O/S（核验 F-068） |

## H. 安全设计（F-034 ~ F-039）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-034 | 默认行为只读检查：`agent-reach install` 默认不装系统包、不写配置，只列出缺什么；真正动系统须显式加 `--system`；`--dry-run` 先列出全部计划动作、一个字节不改 | 微信博文 O（核验 F-065） |
| F-035 | 博文给出三条命令：`agent-reach install --env=auto`（只检查）、同命令加 `--dry-run`（预览）、加 `--system`（明确授权才真装） | 微信博文 O（逐字核验 F-066） |
| F-036 | 凭据本地存储：Cookie、Token 只存在 `~/.agent-reach/config.yaml`，文件权限 600（仅所有者可读写），不上传不外传 | 微信博文 O（核验 F-065） |
| F-037 | 卸载：`agent-reach uninstall` 清配置目录、各 Agent 的 skill 文件、MCP 配置；`--dry-run` 只预览；`--keep-config` 保留凭据方便重装 | 微信博文 O（核验 F-065） |
| F-038 | 可插拔：不信任某个组件就换掉对应 channel 文件，不影响其他渠道（与 F-017 同源设计） | 微信博文 O |
| F-039 | 作者判断："Agent 能执行 shell 命令就意味着能改系统；凡要交给 Agent 自动跑的安装器，'默认只读+显式授权+dry-run'应该成为标配，而不是加分项" | 微信博文 V |

## I. SKILL.md 与一句话安装（F-040 ~ F-044）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-040 | 博文称项目在仓库里放了一份 SKILL.md，"不是给人看的文档，是给 AI Agent 看的操作手册"，含路由表、常用命令、重试链、失败处理规则，及"动手前先跑 doctor --json 看 active_backend"的工作纪律（博文语境为仓库根目录） | 微信博文 O（**实际路径核验 F-062**） |
| F-041 | 一句话安装话术（博文逐字）："帮我安装 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md"；Agent 读文档后自行决定装什么、顺序、失败重试路径 | 微信博文 O（URL 核验 F-066） |
| F-042 | 使用体验：人不需记命令，只对 Agent 说"帮我看看这个链接""B站搜一下 XX"，Agent 自行决定调 `bili search` 还是 `curl r.jina.ai/URL`；博文归纳"人只说意图，Agent 自己查手册" | 微信博文 O |
| F-043 | SKILL.md 内规则："完成一次较大的调研任务后，顺手跑 agent-reach check-update，有新版就在收尾汇报里附一句"——版本更新提醒也交给 Agent | 微信博文 O |
| F-044 | 作者范式判断："开源项目交付的不只是代码，还有一份'教 Agent 怎么用我'的说明……你的项目如果也想被 Agent 用起来，缺的很可能不是 MCP server，而是这份 SKILL.md" | 微信博文 V |

## J. 上手流程与命令（F-045 ~ F-048）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-045 | 博文推荐 pipx 安装（避免污染系统 Python）：`pipx install https://github.com/Panniantong/agent-reach/archive/main.zip` 后 `agent-reach install --env=auto`；也可把一句话安装话术直接发给 Claude Code/Cursor/OpenClaw | 微信博文 O（逐字核验 F-066） |
| F-046 | 装完跑 `agent-reach doctor` 体检，查看哪些通、哪些要配；需要某平台能力就说"帮我配 XXX" | 微信博文 O |
| F-047 | 卸载两步：`agent-reach uninstall --dry-run`（先预览）→ `agent-reach uninstall`（再真删） | 微信博文 O |
| F-048 | 博文给出四条零配置命令示例：`curl -s "https://r.jina.ai/URL"`（读网页）、`gh search repos "query" --sort stars --limit 10`（搜 GitHub）、`yt-dlp --write-sub --skip-download "URL"`（抽 YouTube 字幕）、`bili search "AI 教程" --type video -n 5`（搜 B站）；Windows 提示：python3 打开 Microsoft Store 说明是 Store alias，改用 `py -3` | 微信博文 O（核验 F-067） |

## K. 五条设计启示与作者自我定位（F-049 ~ F-054）

| 编号 | 事实内容 | 信源/标注 |
|------|---------|----------|
| F-049 | 启示一（博文逐字）："做能力层，不做工具层。你的价值不应该是'我实现了某件事'，而是'我知道当下谁实现得最好'。前者会被上游变化打垮，后者不会。" | 微信博文 V |
| F-050 | 启示二："有序候选列表 > 单一实现。面对会变的上游，用一个列表+探测选主，比写分支健壮得多。换路线只是一次排序调整。" | 微信博文 V |
| F-051 | 启示三："健康检查要'真跑'，不要'看在不在'。missing/broken/timeout 是三种完全不同的故障，给的处方也完全不同。省这一步，用户就要自己 debug。" | 微信博文 V |
| F-052 | 启示四："同时给人给机器各一份输出。文本报告给人，JSON 给 Agent。做 Agent 基建，这几乎是必答题。" | 微信博文 V |
| F-053 | 启示五："交付一份 SKILL.md。让 Agent 知道怎么用你的项目，比让人知道更重要——因为现在真正读文档、敲命令的，越来越不是人了。" | 微信博文 V |
| F-054 | 博文引用作者自我定位："这个项目我自己每天在用，所以我会一直维护它。"；作者（学生小孙）评论"维护动力来自自用而非流量，这大概是它能持续追着平台变化跑的原因" | 微信博文 S（项目作者自述）+ V（推介作者归因） |

---

## L. 官方核验补充（F-055 ~ F-072，2026-10-07/08）

### 仓库元数据与热度时点

| 编号 | 事实内容 | 来源 |
|------|---------|------|
| F-055 | GitHub REST API：仓库真实存在（Panniantong/Agent-Reach，路径大小写不敏感），`created_at=2026-02-24T02:10:24Z`，默认分支 main，主语言 Python（617,420 字节），owner=User（显示名 **Pnant**，2020-11-04 注册，1,437 followers，38 个公开仓库）；最近 commit `94f06c1`（2026-10-07），活跃维护 | GitHub API + 仓库页 |
| F-056 | 时点快照 2026-10-07/08：Star **93,669→93,673**（页面显示 93.7k）、Fork **8,195**（8.2k）、open issues 88、open PR 112、325 watching、**36 位贡献者**。博文"92,000+/约 92,000""Fork 约 8,000"均属实且现值已更高 | GitHub API/仓库页 |
| F-057 | 官方 About："Give your AI agent eyes to see the entire internet..."；topics 含 agent-infrastructure、ai-agent、mcp、claude-code、cursor 等；Trendshift 徽章 **#24387**（GitHub Trending #1 Repository of the Day 类第三方榜单标识） | GitHub 仓库页 |
| F-058 | Releases 共 7 个；最新 **v1.5.0「能力层:多后端路由 + 真体检 + OpenCLI」，发布于 2026-06-11**（博文未提版本信息，补充） | GitHub releases |
| F-059 | 许可证 **MIT**（API license 字段与仓库 LICENSE 一致）；Python 3.10+ 要求与博文一致 | GitHub API/README |
| F-072 | 增长曲线旁证：neodrop.ai 收录记录显示 2026-06-22 当周项目登 GitHub Trending **#2**（36,854 stars，周增 +8,233）——与"2026-02 发布、6 月爆发、10 月达 93k"的时间线吻合；另有 GitCode 博客 2026-09-24/25 两篇、lobehub 技能市场、deepwiki 等第三方收录 | neodrop.ai、GitCode、lobehub、deepwiki |

### 口径补正与勘误

| 编号 | 事实内容 | 来源 |
|------|---------|------|
| F-060 | README 平台表确为 **16 个渠道**：网页、YouTube、RSS、全网搜索(Exa)、GitHub、Twitter-X、B站、Reddit、Facebook、Instagram、小红书、LinkedIn、Boss直聘、V2EX、雪球、小宇宙播客（xueqiu.py、v2ex.py 实际文件存在） | README + git tree |
| F-061 | **零配置口径补正**：官方激活口径为"默认只激活 **6** 个零配置渠道"；博文头部信息卡写 6，但正文零配置档列了 **7** 个（多出 B站）。README 平台表 B站行另注"装好即用：搜索+详情 bili-cli 无需登录"——即 B站无需登录但不属于默认激活的 6 个；博文 7 个名单扣除 B站恰为 6 个（网页/YouTube/GitHub/RSS/Exa/V2EX）。两套口径并存，本 bundle 以官方 6 激活口径为准 | README 原文核对 |
| F-062 | **SKILL.md 路径勘误**：仓库根目录**不存在** SKILL.md；实际路径为 `agent_reach/skill/SKILL.md`，同目录另有 `SKILL_en.md`（英文版）与 `references/` 下 7 个分类说明 md。博文"在仓库里放了一份 SKILL.md"的功能描述属实，位置表述需补正 | git tree + 仓库文件 |
| F-063 | **channels/ 规模勘误**：博文树图（9 文件）与 README 自带树图（13 个渠道）均为简化示意；git tree 实际 channels/ 下 **20 个文件、17 个渠道实现**（__init__.py、_opencli_site.py、base.py + bilibili/boss/exa_search/facebook/github/instagram/linkedin/mcporter/reddit/rss/twitter/v2ex/web/xiaohongshu/xiaoyuzhou/xueqiu/youtube 共 17 个渠道 py）；README 树图漏画 boss/v2ex/xueqiu/xiaoyuzhou 四个。渠道实现数（17）与对外宣称渠道数（16）存在 mcporter 作为 Exa 承载实现等内部映射差异 | GitHub git tree |
| F-064 | **故障史核验**：README 明确记载"yt-dlp 被 B站风控 412 封死（2026-06 实测）"，bilibili 渠道选型为 bili-cli▸OpenCLI▸搜索 API；README 设计理念段明确记载 2026-03 一批单平台 CLI 停更后项目更换路由——博文两个时间点案例均属实 | README 原文 |
| F-065 | 安全机制逐项核实于 README：install 默认只读检查、`--dry-run`、`--system`（另有 `--safe`、`--env=auto`）；凭据 `~/.agent-reach/config.yaml` 权限 600；uninstall 清配置目录/skill/MCP 配置，支持 `--dry-run`、`--keep-config`；doctor/probe 真实探测，`active_backend: null` 表示当前无可用后端 | README + GitCode 旁证文 |
| F-066 | **安装命令出处补正**：`pipx install https://github.com/Panniantong/agent-reach/archive/main.zip` 与 `agent-reach install --env=auto` 逐字存在于官方 **docs/install.md**；一句话安装 URL `raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md` 真实可访问；但 **README 正文无 pipx 字样**，主推"把一句话发给 Agent"的安装路径。博文 pipx 命令可照做，出处为 install.md 而非 README | docs/install.md + README |

### 命令族与配置补充

| 编号 | 事实内容 | 来源 |
|------|---------|------|
| F-067 | 零配置底层命令核实：网页 `curl https://r.jina.ai/URL`、GitHub `gh search`/`gh repo view`、YouTube 字幕 `yt-dlp`、B站 `bili`（bili-cli）、Exa 经 mcporter（MCP 免 Key）、RSS feedparser；deepwiki 佐证存在 search-* 子命令族（如 search-twitter 默认 `-n 10`、search-bilibili 走 bili-cli），与博文四条示例同构 | README + deepwiki |
| F-068 | 登录态渠道配置补充：Twitter 需环境变量 `TWITTER_AUTH_TOKEN`/`TWITTER_CT0`；OpenClaw 宿主需先 `openclaw config set tools.profile "coding"` 开启 exec 权限；官方建议服务器代理方案（约 $1/月）；Cookie 封号风险下官方同样建议专用小号 | README/SKILL references |
| F-069 | **PyPI 同名包警告**：官方明确不要从 PyPI 安装同名包（仿冒/占位风险），安装以 GitHub archive 或一句话安装文档为准 | README |
| F-070 | **第三方镜像口径登记**：lobehub 技能市场镜像版 SKILL.md 快照显示"13+ platforms"且含抖音/微博/微信文章渠道，系**旧版快照**，与官方现行 16 渠道名单不一致，不采信；项目存在 GitCode 同步镜像（gitcode.com/Panniantong/Agent-Reach）与 README 友情链接 AtomGit 镜像 | lobehub + GitCode |
| F-071 | **商业化元素披露**：README 含赞助商区块（BrowserAct、腾讯云 OpenClaw、CoreClaw、UCloud）；作者另在 README/公众号承接 Agent 落地业务合作（微信联系方式）。博文为第三方推介且文末有公众号互动引流——读者应知悉项目存在商业合作与作者获客渠道，热度数字本身为 GitHub 客观指标不受影响 | README + 博文 |

---

## 事实分类统计

| 分类 | 编号 | 数量 |
|------|------|------|
| A 元信息 | F-001~F-003 | 3 |
| B 项目身份与热度（博文） | F-004~F-007 | 4 |
| C 痛点与定位 | F-008~F-014 | 7 |
| D 机制一：有序后端 | F-015~F-018 | 4 |
| E 机制二：doctor | F-019~F-022 | 4 |
| F 故障案例 | F-023~F-027 | 5 |
| G 16 渠道三档 | F-028~F-033 | 6 |
| H 安全设计 | F-034~F-039 | 6 |
| I SKILL.md | F-040~F-044 | 5 |
| J 上手命令 | F-045~F-048 | 4 |
| K 五条启示与自述 | F-049~F-054 | 6 |
| L 官方核验补充 | F-055~F-072 | 18 |
| **合计** | F-001 ~ F-072（连续无跳号） | **72** |

## P0 核验结论汇总

- P0（15 项：Star/Fork/发布日期/许可/渠道总数/零配置数/安装命令/安装 URL/SKILL.md 位置/channels 树/412 案例/2026-03 案例/install 三档/config 600/uninstall）：**11✅ / 4⚠️ / 0❌**
- P1（6 项：probe 三态/active_backend/雪球 V2EX 存在/选型表后端/零配置命令族/lobehub 镜像口径）：**5✅ / 1⚠️**
- 合计 21 项：**16✅ / 5⚠️ / 0❌**；无核心声明失败 → status: stable
- 5 项 ⚠️：F-056（Star 动态时点）、F-061（6 vs 7 零配置口径矛盾）、F-062（SKILL.md 实际路径）、F-063（channels 示意树 vs 20 文件/17 实现）、F-070（lobehub 旧快照 13+ 口径；另 F-066 pipx 出处仅 install.md 已在正文注明）
