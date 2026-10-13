---
name: docs-as-product-cmd
version: 1.0.0
description: "当用户提到'文档即产品'、'docs-as-product'、'文档产品化'、'Diátaxis'、'四型分区'、'文档质量门'、'G1-G4'、'V门'、'sphinx-build -W'、'元数据漂移'、'F-021'、'读者契约'、'文档指标'、'M1-M5'、'检查文档结构'、'orphan 逃逸'时，必须使用此技能。把《文档即产品经营法》模式固化为可执行校验：结构校验（Diátaxis 四型分区 + toctree/orphan 一致性）、质量门（G1-G4 + V门集成 vale/sphinx-build/doctest/sphinx-lint）、元数据漂移检查（canonical/稳定字段，F-021）、读者契约校验与 M1-M5 指标面板脚手架。本 Skill 严格只读，不修改任何文档内容；仅 metrics 子命令生成面板脚手架。"
argument-hint: "<structure|gates|metadata|contract|metrics|all> [--path <dir>] [--json]"
user-invocable: true
paths:
  - ".agents/scripts/docs-as-product.py"
  - "docs/"
  - "docs/conf.py"
title: "Docs-as-Product 文档即产品校验 Skill"
---
# Docs-as-Product 文档即产品校验 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [docs-as-product.py](../../scripts/docs-as-product.py) 与库 [lib/docs_as_product/cli.py](../../scripts/lib/docs_as_product/cli.py)

## 1. Skill ID
`docs-as-product-cmd`

## 2. 功能描述

把方法论模式《文档即产品经营法》（[docs-as-product.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/docs-as-product.md)）固化为六个子命令的可执行校验工具：

| 子命令 | 功能 | 对应模式步骤/标准 |
|--------|------|------------------|
| **structure** | Diátaxis 四型分区 + toctree/orphan 一致性；报告逃逸页、未挂载页、四型错位 | 步骤3；检验标准② |
| **gates** | G1 事实文风(vale)、G2 首段与标题、G3 autodoc 复用、G4 原子性、V 门(sphinx-build -W + doctest + sphinx-lint) | 步骤4；检验标准③⑥ |
| **metadata** | head 元数据仅含跨版本稳定字段；canonical 与基准核对 | 反模式 F-021；检验标准④ |
| **contract** | 四类读者各有可执行验收任务；Tutorial <15 分钟、Reference docstring ≥90% 声明 | 步骤1；检验标准① |
| **metrics** | 生成 M1–M5 指标面板脚手架（JSON 数据 + Markdown 面板，含 owner 占位） | 步骤6；检验标准⑤ |
| **all** | 依次执行 structure → gates → metadata → contract（只读，不生成指标） | 发布前全量自检 |

> **为什么用本Skill而非凭印象核对？** "文档即产品"包含四型分区、五个质量门、稳定字段白名单、读者契约与五项指标，凭印象核对必然漏项；工具把每条标准变成可重复执行、可被 CI 调用的检查，且结论与退出码可审计。这与单元测试同理——主张需要可执行的验证才能成为工程事实。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "文档即产品"、"docs-as-product"、"文档产品化"、"把文档当产品"
- "Diátaxis"、"四型分区"、"tutorial/how-to/reference/explanation"
- "文档质量门"、"G1"、"G2"、"G3"、"G4"、"V 门"、"sphinx-build -W"
- "元数据漂移"、"F-021"、"canonical 核对"、"稳定字段"
- "读者契约"、"验收任务"、"文档指标"、"M1–M5"、"指标面板"
- 发布前需要对文档做全量只读自检
- 新增文档后检查是否挂载 toctree、是否有首段摘要

> **关于触发边界**：本 Skill 不修复内容，只报告问题。修复文档结构/字段/链接时，应按报告逐项人工修改，链接类问题配合 `link-check-cmd`/`link-fixer`，拆分类问题配合原子化相关 Skill。

## 4. 方案选择决策树

```
需要对文档做"产品化"校验？
├─ 检查页面归属与导航可达性？ → structure（第5.1节）
├─ 跑质量门（首段/标题/autodoc/原子性/vale/sphinx）？ → gates（第5.2节）
├─ 核对 head 字段是否漂移、canonical 是否一致？ → metadata（第5.3节）
├─ 校验读者契约与可执行验收任务？ → contract（第5.4节）
├─ 初始化 M1–M5 指标面板？ → metrics（第5.5节，唯一写文件操作）
└─ 发布前全量只读自检？ → all（第5.6节）
```

### 外部工具策略

- `gates` 默认允许调用外部工具（vale / sphinx-build / sphinx-lint）；
- 离线或无工具环境加 `--no-external`，仅执行内置检查；
- **工具缺失自动降级为 WARN，不报错、不阻断**；CI 环境应安装工具使门禁真实生效。

> **为什么工具缺失是 WARN 而不是 FAIL？** 工具缺失属于环境问题而非文档缺陷，直接 FAIL 会让本地检查无法运行、迫使调用方伪装结果；WARN 明确指出缺失工具与安装方式，既保持本地可用性，又保证 CI 装好工具后门禁真实生效。

**与其他Skill的关系**：
- 发布前自检：先 `docs-as-product-cmd all` 定位问题，再按类型修复；
- 链接修复交由 `link-check-cmd`；导航/看板生成交由 `docgen-cmd`；
- 本 Skill 不替代 Sphinx 构建，不接管 conf.py。

## 5. 核心命令（快速开始）

脚本路径：[docs-as-product.py](../../scripts/docs-as-product.py)

### 5.1 结构校验（structure）

```bash
# 校验四型分区与 toctree/orphan 一致性
python .agents/scripts/docs-as-product.py structure

# JSON 输出（稳定 schema：per_gate / findings[] / severity）
python .agents/scripts/docs-as-product.py structure --json
```

### 5.2 质量门（gates）

```bash
# 内置检查 + 外部工具（vale / sphinx-build -W / doctest / sphinx-lint）
python .agents/scripts/docs-as-product.py gates

# 离线环境：仅内置检查（G2/G3/G4）
python .agents/scripts/docs-as-product.py gates --no-external
```

### 5.3 元数据漂移（metadata）

```bash
python .agents/scripts/docs-as-product.py metadata
```

配置 canonical 基准时使用 TOML 配置（见 §6）。

### 5.4 读者契约（contract）

```bash
python .agents/scripts/docs-as-product.py contract
```

### 5.5 指标面板脚手架（metrics）

```bash
# 默认输出到 docs/metrics/（metrics.json + metrics.md）
python .agents/scripts/docs-as-product.py metrics

# 指定输出目录
python .agents/scripts/docs-as-product.py metrics --scaffold docs/ops/metrics
```

> 同名文件已存在时**不覆盖**，仅创建缺失文件，避免冲掉已填写数据。

### 5.6 全量自检（all）

```bash
# 发布前只读全量检查（外部工具可用时）
python .agents/scripts/docs-as-product.py all

# 离线快速自检
python .agents/scripts/docs-as-product.py all --no-external
```

> 完整参数见 `--help`；所有检查类子命令支持 `--path <dir>` 指定 docs 目录、`--json` 机器可读输出。

## 6. 配置文件（可选）

通过 `--config <file.toml>` 覆盖默认行为：

```toml
[docs-as-product]
docs_dir = "docs"
build_dir = "docs/_build"
canonical_base = "https://your-domain.io"
run_external = true
external_timeout = 300
stable_fields = ["title", "url", "canonical"]
```

## 7. 退出码与输出契约

| 退出码 | 含义 |
|--------|------|
| 0 | 全部检查通过（允许有 WARN） |
| 1 | 至少存在一条 error 级发现 |

JSON 顶层字段：`passed`、`per_gate`（各门的 passed/errors/warnings）、`findings[]`（含 `gate`/`severity`/`code`/`message`/`file`）、`reports[]`。

## 8. 安全检查清单（执行前确认）

- [ ] 明确要执行的子命令，避免无意义的全量运行
- [ ] **理解只读契约**：检查类子命令绝不写文件；仅有 `metrics` 且显式 `--scaffold` 时写脚手架
- [ ] 检查路径指向目标项目的 `docs/` 目录，避免扫描到 `vendor/`/归档副本
- [ ] CI 中需要真实门禁时确认已安装 vale / sphinx / sphinx-lint，否则门禁只降级不生效
- [ ] 解读结果时区分 error（文档缺陷）与 warn（环境缺失/建议改进）
- [ ] 修复后重新运行对应子命令确认 error 清零

## 9. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| 大量"未挂载页面" | 页面未被任何 toctree 引用 | 将页面加入对应索引页 toctree；确认非逃逸草稿 |
| "缺首段摘要" | 页面首个标题后未紧接说明段落 | 在标题下补一段页面用途说明 |
| "标题层级跳跃" | 出现 H1 直接到 H3 或多个 H1 | 补齐中间层级，保留单一 H1 |
| reference 页报"手写签名" | 未用 autodoc 而手写函数签名 | 改用 automodule/autoclass，以代码 docstring 为单一真值 |
| gates 全是 WARN | 外部工具未安装 | 按需安装 vale、sphinx、sphinx-lint；或使用 --no-external |
| metrics 未生成文件 | 目标目录已有同名文件 | 属正常保护；如需重建先手动移走旧文件 |

## 10. Gotchas（陷阱与反直觉行为）

- **WARN 不阻断、error 才阻断**：工具缺失等环境问题是 WARN，CI 若依赖门禁必须主动安装工具，否则门禁"看起来通过"实则未执行。
- **行内 `` `:orphan:` `` 不算逃逸**：仅页面中真实的 `:orphan:` 指令会被判定；模式文档里作为示例文字的行内代码不会误报。
- **all 不生成指标面板**：all 严格只读；指标脚手架需单独执行 metrics。
- **四型识别优先看 frontmatter 再看目录**：`diataxis`/`doc_type` 显式声明优先；二者冲突会报 WARN，需人工裁决。
- **canonical 核对需要显式基准**：离线无法访问线上，未配置 `canonical_base` 时只做字段白名单检查，不做值核对。
- **中文目录名受支持**：教程/指南/参考/解释等目录可正确映射，但非索引页仍须挂载 toctree。

## 11. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 模式原文（功能来源） | L1 | [docs-as-product.md](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/docs-as-product.md) | 理解六步做法与边界 |
| 脚本源码 | L2 | [docs-as-product.py](../../scripts/docs-as-product.py) | CLI 装配与参数细节 |
| 库实现 | L2 | [lib/docs_as_product/cli.py](../../scripts/lib/docs_as_product/cli.py) | 各检查器/模型/发现层 |
| 链接检查 Skill | L1 | [link-check-cmd](../link-check-cmd/SKILL.md) | 断链类问题的检查与修复 |
| 导航生成 Skill | L1 | [docgen-cmd](../docgen-cmd/SKILL.md) | 导航表与看板生成 |

## 12. Changelog

- **v1.0.0** (2026-10-08): 初始版本。基于七概念编排（场景5 创新突破，session sc-20261008-docs-as-product-api）实现六项能力并封装为命令门面，含只读契约、外部工具降级与稳定 JSON schema。
