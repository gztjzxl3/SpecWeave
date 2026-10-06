---
name: mubu
version: 0.1.0
description: >-
  幕布（mubu.com）大纲笔记与思维导图工具的本地集成 Skill。当用户提到"幕布"、"mubu"、"幕布文档"、"幕布大纲"、"幕布导出"、"OPML 转换"、"幕布转 Markdown"、"Markdown 转幕布"、"幕布整理"、"幕布思维导图"、"幕布待办"、"把幕布打通"、"幕布数据备份"、"幕布关停预防"时必须使用此技能。提供 OPML↔Markdown 互转、大纲结构解析、节点树遍历、AI 智能整理、数据导出兜底等能力。本 Skill 不调用幕布官方 API（不存在）、不逆向 Web 内部接口（ToS 风险），仅基于幕布客户端原生 OPML 导出能力构建零风险数据链路。
argument-hint: "<操作> [OPML/Markdown 文件路径] [选项]"
user-invocable: true
paths:
  - ".agents/skills/mubu/**"
---

# 幕布集成 Skill（mubu）

> 幕布（mubu.com）是极简大纲笔记 + 思维导图工具。本 Skill 在 SpecWeave 生态内提供"打通"幕布的零依赖、零 ToS 风险方案：以幕布客户端原生 OPML 导出为输入源，纯 Python 标准库实现解析与互转。

## 1. Skill ID
`mubu`

## 2. 功能描述

提供**三方案**支持，由技能根据场景自动选择：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **`parse`** | ⭐ 解析幕布 OPML，输出结构化 JSON / 节点树 | 零依赖、保留层级与文本、便于 AI 后处理 |
| **`to-markdown`** | ⭐ 幕布 → Markdown（纳入 docs/ 知识库） | 保留缩进层级、可双向回转 OPML |
| **`to-opml`** | ⭐ Markdown → OPML（导入回幕布客户端） | 让 AI 生成的 Markdown 大纲能回流幕布 |

核心能力：
- OPML → Markdown / JSON / HTML 互转
- Markdown 大纲 → OPML（可重新导入幕布）
- 节点树遍历与统计（节点数、深度、关键词检索）
- AI 智能整理（基于解析后的 Markdown 做归纳、转写、抽取待办）

> **为什么只走 OPML 链路，不调幕布 API？** 经多方调研（详见 §11 关键参考），幕布官网无"开放平台/开发者"入口，无官方 API、无 MCP server、无 Python wrapper。第三方仅有 xmind 团队开源的 Mubu Exporter/Dumper（仅支持 markdown+xmind）。直接逆向 Web 内部接口存在 ToS 违规与接口不稳定风险。OPML 是幕布客户端原生导出格式，零风险、稳定可依赖。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "幕布"、"mubu"、"幕布文档"、"幕布大纲"、"幕布笔记"
- "幕布导出"、"导出幕布"、"幕布转 Markdown"、"OPML 转 Markdown"
- "Markdown 转幕布"、"导入幕布"、"幕布导入"
- "幕布整理"、"整理幕布大纲"、"幕布待办"、"幕布思维导图"
- "把幕布打通"、"幕布备份"、"幕布关停预防"、"幕布数据迁移"

> **关于触发**：即使没有明确说"用 skill"，只要涉及幕布文档/大纲/思维导图与 Markdown/JSON/HTML 互转的操作就应该使用本技能，不要自己手写 OPML 解析——本 Skill 已封装层级保留、文本转义、双向回转、dry-run 预览等最佳实践。

## 4. 方案选择决策

```
需要执行幕布相关操作？
├─ 拿到 .opml 文件，想转成 Markdown / JSON？ → 方案 parse 或 to-markdown（§7.1）
├─ 有 Markdown 大纲，想导入回幕布？ → 方案 to-opml（§7.2）
├─ 想遍历节点树、统计、检索？ → 方案 list / info（§7.3）
├─ 想 AI 整理幕布内容（归纳/抽取待办/转写）？ → 先 to-markdown，再让 AI 基于 Markdown 处理
└─ 首次使用 / 不确定 OPML 格式？ → 先执行 mubu_cli.py info <file> 探查
```

**写操作（创建/覆盖文件）原则**：所有写操作支持 `--dry-run`，先预览 stdout 再用 `--output` 落盘。

> **为什么 dry-run 是 OPML 互转的必要防线？** OPML 与 Markdown 互转可能丢失属性（如 `_complete`、`_ts`、`_id` 等幕布私有属性），先 dry-run 预览转换结果可避免不可逆覆盖原文件。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `action` | string | 是 | - | `parse` / `to-markdown` / `to-opml` / `list` / `info` |
| `input` | string | 是 | - | 输入文件路径（.opml 或 .md） |
| `--output` / `-o` | string | 否 | stdout | 输出文件路径 |
| `--format` / `-f` | string | 否 | auto | `auto` / `markdown` / `json` / `html` / `opml` |
| `--dry-run` | bool | 否 | false | 预览不落盘（**写操作强烈建议先开**） |
| `--indent` | int | 否 | 2 | Markdown 缩进空格数（to-markdown）/ OPML 缩进 |
| `--max-depth` | int | 否 | 0（不限） | 节点遍历最大深度（list/info） |
| `--keyword` | string | 否 | - | 节点关键词过滤（list） |
| `--json` | bool | 否 | false | 以 JSON 输出元信息（info） |

## 6. 依赖与前置准备

- **必读知识库**：暂无（OPML 是开放标准，自包含实现）
- **Python**：≥ 3.8（仅使用标准库 `xml.etree.ElementTree`、`json`、`argparse`、`pathlib`、`sys`、`re`）
- **幕布客户端**：用于原生导出 OPML（macOS/Windows/Linux 均支持"导出 → OPML"）
- **操作限制**：
  - 输入 OPML 必须是幕布客户端导出的标准 OPML 2.0 格式
  - `to-opml` 反向转换会丢失幕布私有属性（`_complete`/`_ts`/`_id` 等），仅保留文本与层级
  - 大文件（>10MB OPML）建议先用 `info` 探查节点数与深度

> **为什么限定幕布客户端导出？** 幕布 Web 端不提供 OPML 导出入口，必须用桌面/移动客户端"导出 → OPML"。这是幕布官方明确支持的导出格式，长期稳定。

## 7. 方案一：命令行（推荐所有操作使用）

### 7.1 常用命令速查

```bash
# 探查 OPML 文件结构（节点数、深度、根节点信息）—— 首次使用必先 info
python .agents/skills/mubu/scripts/mubu_cli.py info <file.opml>

# OPML → Markdown（先 dry-run 预览！）
python .agents/skills/mubu/scripts/mubu_cli.py to-markdown <file.opml> --dry-run
python .agents/skills/mubu/scripts/mubu_cli.py to-markdown <file.opml> -o <out.md>

# OPML → JSON（结构化，供 AI 后处理）
python .agents/skills/mubu/scripts/mubu_cli.py parse <file.opml> --format json

# Markdown → OPML（导入回幕布客户端）
python .agents/skills/mubu/scripts/mubu_cli.py to-opml <in.md> --dry-run
python .agents/skills/mubu/scripts/mubu_cli.py to-opml <in.md> -o <out.opml>

# 节点遍历 + 关键词过滤
python .agents/skills/mubu/scripts/mubu_cli.py list <file.opml> --keyword "TODO" --max-depth 3

# JSON 输出（便于管道处理）
python .agents/skills/mubu/scripts/mubu_cli.py info <file.opml> --json
```

### 7.2 内置安全机制

- **dry-run**：所有写操作（`to-markdown -o`、`to-opml -o`）支持 `--dry-run`，输出到 stdout 不落盘
- **格式校验**：输入必须是有效 OPML/Markdown，解析失败时返回非零退出码与错误码（见 §9）
- **属性保留**：`parse` 模式保留幕布私有属性（`_complete`/`_ts`/`_id`）到 JSON 输出；`to-markdown` 仅保留文本与层级
- **路径安全**：输出文件路径需显式指定 `-o`，禁止隐式覆盖原文件
- **错误码**：标准化退出码（0=成功，2=文件不存在，3=格式错误，4=解析失败）

> 完整参数表运行 `python .agents/skills/mubu/scripts/mubu_cli.py --help` 或 `<action> --help`。

## 8. AI 智能操作流程

让 AI 基于幕布内容做整理、归纳、待办抽取等智能操作的推荐流程：

```
1. 用户在幕布客户端导出 OPML → 得到 file.opml
2. 调用 to-markdown file.opml -o file.md（先 dry-run 预览）
3. AI 读取 file.md，按用户意图处理：
   - "整理幕布待办" → 抽取所有 [ ] / [x] 节点
   - "归纳幕布大纲" → 按主题聚类、生成摘要
   - "转写成文章" → 把层级大纲展开为段落
   - "提取关键词" → 遍历节点做词频统计
4. 如需回流幕布：AI 生成新 Markdown → to-opml 导入回客户端
```

> **为什么不让 AI 直接读 OPML？** OPML 是 XML 格式，文本与标签混杂，AI 直接读会浪费上下文且易遗漏层级。先转 Markdown 保留缩进层级，AI 读起来清晰、后处理精准。

## 9. 错误处理

| 退出码 | 场景 | 处理方式 |
|--------|------|---------|
| 0 | 成功 | 无需处理 |
| 2 | 输入文件不存在 | 检查路径，确认文件已从幕布客户端导出 |
| 3 | 文件格式错误（不是有效 OPML/Markdown） | 确认文件来源，幕布导出时选 OPML 格式而非 PDF/HTML |
| 4 | XML 解析失败（OPML 标签不闭合等） | 用 `xmllint` 等工具先修复，或重新从幕布客户端导出 |
| 5 | 输出路径不可写 | 检查目录权限与磁盘空间 |

## 10. 安全检查清单（写操作完成前逐项确认）

- [ ] 输入 OPML 来自幕布客户端原生导出（不是手写或第三方生成）
- [ ] **写操作已 dry-run 预览**（`--dry-run`）
- [ ] 输出路径 `-o` 显式指定，不与输入路径相同（避免覆盖原文件）
- [ ] 大文件（>5MB）已先 `info` 探查节点数与深度
- [ ] `to-opml` 反向转换已告知用户：幕布私有属性会丢失
- [ ] 操作完成后用 `info` 验证产出文件结构正常

## 11. Gotchas（陷阱与反直觉行为）

### 11.1 OPML 格式陷阱
- **幕布私有属性命名**：节点上的 `_complete`、`_ts`、`_id` 等下划线前缀属性是幕布私有，OPML 2.0 标准未定义，但其他工具（Workflowy、Dynalist）也有类似约定，互转时不要丢弃这些属性
- **空 outline 节点**：幕布允许空标题节点作为分组容器，转 Markdown 时应保留为空列表项，不要直接删除
- **HTML 转义**：OPML 文本可能含 `&lt;`、`&amp;` 等实体，ElementTree 解析后会自动还原，但输出 Markdown 时需注意 `<`、`>` 在 Markdown 中的特殊语义

### 11.2 Markdown → OPML 反向陷阱
- **缩进识别**：Markdown 列表缩进必须用空格（建议 2 或 4），Tab 缩进会被识别为同一层级
- **有序/无序列表混用**：幕布只支持无序层级，有序列表 `1.` `2.` 会被统一转为无序 `outline` 节点，丢失编号
- **代码块与引用**：Markdown 代码块（```）与引用（`>`）会被作为纯文本节点，丢失格式语义

### 11.3 编码与环境陷阱
- **OPML 编码声明**：幕布导出的 OPML 头部声明 `<?xml version="1.0" encoding="UTF-8"?>`，Python ElementTree 默认按 UTF-8 解析，无需特殊处理
- **Windows 终端 GBK 输出**：在 Windows PowerShell 直接运行可能乱码，设环境变量 `PYTHONIOENCODING=utf-8` 或脚本内 `sys.stdout.reconfigure(encoding='utf-8')`（脚本已内置）
- **路径分隔符**：跨平台脚本统一用 `pathlib.Path`，不要手拼 `\` 或 `/`

### 11.4 数据迁移兜底陷阱
- **幕布关停预防**：建议每月用 `to-markdown` 全量导出一次到 `docs/knowledge/mubu-backup/`，文件名带日期后缀
- **属性丢失不可逆**：`to-opml` 反向导入幕布后，幕布会重新生成 `_id`/`_ts`，原节点 ID 丢失，无法追溯历史编辑记录

## 12. 关键参考速查表

| 目标 | 命令 | 注意事项 |
|------|------|---------|
| 探查 OPML 结构 | `info <file.opml>` | 大文件必先执行 |
| 转 Markdown | `to-markdown <file.opml> -o <out.md>` | 先 `--dry-run` |
| 转 JSON | `parse <file.opml> -f json` | 保留全部属性 |
| 转 HTML | `parse <file.opml> -f html` | 输出嵌套 ul/li |
| Markdown 转 OPML | `to-opml <in.md> -o <out.opml>` | 私有属性会丢失 |
| 关键词检索节点 | `list <file.opml> --keyword X` | 仅匹配节点文本 |
| 限制深度遍历 | `list <file.opml> --max-depth 3` | 0=不限 |

## 13. 调研依据（为什么本 Skill 走 OPML 链路）

本 Skill 设计基于 2026-10-06 的网络调研，结论：

| 维度 | 调研发现 |
|---|---|
| 幕布官方开放 API | mubu.com 首页无"开放平台/开发者"入口 |
| 幕布 MCP server | 不存在（搜 `mubu mcp`、`幕布 MCP` 全部无匹配） |
| GitHub Python wrapper / cli | 不存在 |
| SpecWeave 生态内幕布 skill | 不存在（Grep `/workspace` 无匹配） |
| 第三方导出工具 | 仅 xmind 团队的 Mubu Exporter/Dumper（仅 markdown+xmind） |
| 浏览器插件 | 「幕布MD」（手动加载） |
| 命令行转换链 | `opml-to-markdown` npm 包可用，但本 Skill 用纯 Python 标准库零依赖实现 |

> **为什么不用 opml-to-markdown npm 包？** 引入 npm 依赖会增加环境负担（需 Node.js），且 npm 包仅做单向 OPML→Markdown，不支持反向。本 Skill 用 Python 标准库 `xml.etree.ElementTree` 自包含实现双向互转，零新依赖、跨平台、可纳入 SpecWeave 主权区直接维护。

## 14. 长期方案与演进方向

- **v0.1（当前）**：纯 OPML 链路、零依赖、零 ToS 风险
- **v0.2（规划）**：增加 HTML 与思维导图（FreeMind .mm）格式互转
- **v0.3（评估中）**：调研幕布 Web 端内部 API（需用户授权抓包），评估是否值得冒 ToS 风险做读写能力
- **v1.0（远期）**：若幕布官方发布开放 API 或 MCP server，迁移到官方方案

## 15. Changelog

- **v0.1.0** (2026-10-06): 初始版本。基于网络调研结论"幕布无官方开放 API、无现成 MCP/skill"，走 OPML 链路实现零依赖、零 ToS 风险的本地集成。提供 `parse` / `to-markdown` / `to-opml` / `list` / `info` 五个子命令，纯 Python 标准库实现。
