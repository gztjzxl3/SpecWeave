---
title: "Spec：Agent Reach 博文 → OKF 知识包"
status: "draft"
---

# Spec：Agent Reach 博文 → OKF 知识包

## 目标

将微信公众号「AI赋能干货铺」博文《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》（作者学生小孙，2026-10-06）转化为 OKF v0.2 知识包，归属 `jishu/ai/products/` 分组，bundle 名 `agent-reach`。

## 内容敏感度预检（阶段 0）

- URL：`https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w`（无 `share?code=`/`token=`/邀请码等访问控制参数）
- 微信公众号公开文章 → **公开内容（Public）**，走标准工作流
- spec 位于 `.trae/specs/okf-wiki-ecosystem/agent-reach-blog-okf-wiki/`，产出位于子模块 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

**第三方公众号综述（非厂商自宣、非一手实测）**：公众号「AI赋能干货铺」为第三方开源项目推介号，作者「学生小孙」。博文以 README 转述 + 架构解读为主，大量直接引用项目 README 原文。核验路径升级为官方一手材料：GitHub REST API（不可伪造元数据）+ main 分支 README 全文 + docs/install.md + git tree，辅以第三方旁证（neodrop Trending 记录、lobehub 技能市场镜像、GitCode 同步镜像、deepwiki）。博文无"对比测试/benchmark"类厂商成效宣称；92k Star 属社区客观指标，仍按 P0 核验时点值。

## 骨架判定（操作可复现性两问）

1. 博文中有读者可照做的安装/配置/代码/调用流程吗？✅（pipx 安装、install 三档、doctor、uninstall、curl/gh/yt-dlp/bili 零配置命令、一句话安装 URL 均可照做）
2. 流程经官方材料确认且可复现吗？✅（命令逐字存在于官方 docs/install.md 与 README）

→ **两问皆"是"：设 examples/**。内容性质为**技术教程/产品拆解（含可照做实操）**，骨架 index + concepts/ + examples/ + references/ + log。

## 归属位置分析（决策树）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/products/`（选定） | ✅ | Agent Reach 是 AI Agent 能力层 CLI 终端工具（Python/MIT/pipx 安装），products 类语义含"网页数据采集/Agent 工具"；同构先例 wigolo（本地 Web 情报层 CLI、博文转化、含安装实操）、browseract（浏览器自动化） |
| `jishu/ai/` 直挂 | ❌ | 单产品深度拆解束统一归 products/，组内已有 wigolo 等同构先例 |
| `jishu/ai/practice/` | ❌ | 方法论/行业洞察类；本文主体是具体产品机制与实操，五条设计启示虽可迁移但篇幅占比小，仅作为概念层一章节观点呈现 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（最小变更原则） |

## 事实与核验（R）

- F-001~F-054 来自博文（元信息 3 + 身份热度 4 + 痛点定位 7 + 双机制 8 + 故障 5 + 渠道 6 + 安全 6 + SKILL 5 + 上手 4 + 启示自述 6）
- F-055~F-072 为 18 条官方核验补充（含 5 项口径补正/勘误 + 商业化披露）
- 总事实 72 条（F-001~F-072 连续无跳号）
- P0 核验 15 项（数字/日期/许可/命令/目录结构/故障案例），P1 核验 6 项（能力声明/命令族/平台存在性）
- **勘误四张清单命中**：
  - ①日期/版本：首次发布博文"2026 年 2 月"✅（API `created_at=2026-02-24`）；最新 release v1.5.0（2026-06-11）博文未提，补充
  - ②成效数字溯源：Star 92,000+ ✅ 且现值更高（93,669→93,673，2026-10-07/08 时点）；Fork 8,000 ✅（8,195）；均为动态数字须带时点
  - ③口径对照：**博文头部"6 个开箱即用"与正文列出 7 个（含 B站）自相矛盾**；官方 README 激活口径为 6，平台表标注 B站"装好即用：搜索+详情 bili-cli 无需登录"——两套口径并存，本 bundle 以官方 6 激活口径为准并完整呈现差异
  - ④引文/命令逐字：pipx 安装命令仅出现在 docs/install.md（README 正文无 pipx，主推"一句话发给 Agent"）；**SKILL.md 不在仓库根目录**，实际在 `agent_reach/skill/SKILL.md`（另有 SKILL_en.md + references/ 7 个分类 md）；博文 channels/ 树图为 9 文件示意，git tree 实际 20 个文件、17 个渠道实现（README 自身树图也只画 13 个）
- **第三方镜像口径登记**：lobehub 技能市场镜像快照显示"13+ platforms"且含抖音/微博/微信文章渠道，系旧版快照，非官方现行口径，正文以官方 README 16 渠道为准
- **状态裁决**：无 ❌ 核心声明失败——仓库真实存在、活跃维护（最近 commit 2026-10-07）、全部核心机制（有序后端/active_backend/probe 三态/412 故障史/安全三档/config 600）均有官方材料支撑；5 项 ⚠️ 全为动态时点与口径细节 → `status: stable`

## 知识地图（I：三层拆分，技术教程类）

| 层 | 文件 | 内容 |
|----|------|------|
| references | article-source.md | F-001~F-065 双份事实登记（与 facts.md 集合一致） |
| references | verification.md | P0/P1 共 21 项核验报告（16✅/5⚠️/0❌）、勘误四清单、信源距离、权威 URL |
| concepts/00 | 00-what-is-agent-reach.md | 项目身份与发布事实：定位、作者、MIT、2026-02 发布、热度（带时点）、增长曲线旁证 |
| concepts/01 | 01-capability-layer-architecture.md | 能力层定位、channels 有序后端列表 + active_backend、_backend 覆盖、412 故障案例、16 渠道三档全景（含 Mermaid） |
| concepts/02 | 02-doctor-health-and-security-model.md | probe 真跑三态、doctor/--json 双输出、默认只读/--dry-run/--system、凭据 600、卸载、小号边界、商业化披露 |
| concepts/03 | 03-skill-md-agent-distribution-paradigm.md | SKILL.md 给 Agent 的说明书、一句话安装、check-update 规则、五条设计启示（观点分层） |
| examples/00 | 00-install-and-doctor.md | pipx/venv 安装、Windows py -3、OpenClaw exec 前置、install 三档、doctor/--json、卸载 |
| examples/01 | 01-zero-config-channels.md | 网页/GitHub/YouTube/B站/Exa/RSS/V2EX 零配置命令实操 |
| examples/02 | 02-login-channels-and-cookie-safety.md | Twitter/小红书/Reddit/LinkedIn/Boss/小宇宙配置路径、Cookie 小号纪律、服务器代理、PyPI 同名包警告 |

## 文件集（14 个，仿 wigolo）

```
jishu/ai/products/agent-reach/
├── index.md
├── log.md
├── concepts/{index.md, 00, 01, 02, 03}
├── examples/{index.md, 00, 01, 02}
└── references/{index.md, article-source.md, verification.md}
```

## 质量门

- G1：事实句无因果推断词，全部 F 编号可溯；作者观点（V）与厂商/作者自述（S）显式分层
- G2：机制描述"现象→结构→边界→信源"完整；五条设计启示标"作者观点"，不写成客观结论
- G3：信源先行（article-source/verification → concepts → examples → index 最后写）、F 编号双份集合一致
- G4：toctree 三级完整、相对链接可达、UTF-8 strict、三级计数同步（products/ai/bundles 总索引，现值以磁盘为准——子模块有并行会话改动）

## 门禁环境

`invoke gates.*` 依赖 optional-dependencies.doc（invocations）；若环境不可用，执行手动等效验证（UTF-8 strict 解码、双份 F 编号正则 `^\|\s*F-(\d{3})\s*\|` 集合比对、toctree 条目 Test-Path、相对链接全可达、三级计数同步、敏感路径零残留）并在 log.md 注明，禁止声称"gates 通过"。

## 并行会话冲突处置

子模块 `awesome-okf-xs` 工作区存在他人未提交改动（M 三个索引 + sheke 索引；未跟踪 pixelle-video/ 与 naval/wechat-* 三束），均与本次任务无关：**严禁纳入本次提交/暂存**。索引计数一律先 Read 磁盘现值再做本束增量；`git add` 只显式列本束文件与本束相关的索引计数行，提交前向用户说明混入风险。
