# Spec：Agent Lightning v1.0 博文 → OKF bundle

## 1. 内容敏感度预检

- 信源：微信公众号公开博文（`mp.weixin.qq.com`，无访问控制参数）→ **公开内容（Public）**
- 工作流：标准流程，spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出位于 `projects/awesome-okf-xs/doc/bundles/`

## 2. 内容性质分流与骨架判定

- 内容性质：**产品发布资讯 + 技术综述**（Agent Lightning v1.0 发布 + 框架机制综述，含实验数据）。
- **操作可复现性两问**：
  1. 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（博文为概念与机制综述，未给出可照做的完整实操命令步骤）
  2. 这些流程是否经作者实测、可复现？→ **否**
- → **骨架：无 examples/**（index + concepts/ + references/ + log）
- frontmatter：type: bundle，description 标注"产品发布资讯/技术综述，非操作教程"

## 3. 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/models/agent-lightning/`（选定） | ✅ | ① 主线实体是 Microsoft Agent Lightning（Agent RL 强化学习训练框架/基础设施）；② `ai/models` 分组 description 明确含"强化学习基础设施"，且已有 **AReaL 自演进 Agent 强化学习基础设施**（areal）束，两者属同一"Agent RL 强化学习"主题簇，可直接互链（arXiv 确认 AReaL 2.0 采用了同范式）；③ 符合"主线实体优先 + 同主题先例聚集" |
| `jishu/ai/frameworks/` | ❌ | Agent Lightning 是训练框架/RL 基础设施，非 Agent 运行时框架；该组以源码教程集群为主（ai-agent/langchain/pocketflow），语义更偏 LLM 应用框架 |
| `jishu/ai/practice/` | ❌ | 该组偏"工程实践、方法论与行业洞察"，Agent Lightning 是具体训练框架，非实践方法论 |
| `jishu/ml/` | ❌ | 侧重模型交换格式与推理后端（ONNX/TVM），非 Agent RL 训练 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

**选定路径**：`jishu/ai/models/agent-lightning/`

## 4. 信源与核验结论

- 信源距离预判：**第三方综述**（AINLP/作者 NLPerNLPer 对微软官方开源的综述，非厂商自宣、非一手实测）
- P0 核验结论（共 10 项）：
  - F-001 v1.0 存在 ✅、F-008 特性 ✅、F-009 约 6,000 样本 ✅、F-010 41.8%→56.4% ✅、F-011 +14.6pp ✅、F-012 10/7 博客 ✅、F-013 8 月公开 ✅、F-014 Harnessed Agentic RL ✅、F-041 约 2 倍加速 ✅、F-044 约 3,500 行 ✅
  - F-046 硬件型号 ⚠️ 仅博文单源
- 勘误：**无源文硬错误**；约 6,000 样本/约 2 倍加速按官方实验口径标注
- 状态：stable（全部关键数字官方核验通过，无 flagged 触发）

## 5. 三层知识拆分（知识地图）

**技术综述/产品发布资讯类三层映射**（无 examples）：

| 博文内容层 | 映射篇目 | 引用 F 编号 |
|-----------|---------|-----------|
| 事件时间线层（What/When/Who） | `concepts/00-agent-lightning-v1.md`（Agent Lightning v1.0 概览：定义、harness 概念、发布、核心价值） | F-001, F-002, F-003, F-005, F-006, F-007, F-008, F-012, F-013, F-044, F-045 |
| 训练范式/机制层（Why/How） | `concepts/01-harnessed-agentic-rl.md`（Harnessed Agentic RL 范式：rollout、OpenAI 兼容代理、样本拆分、奖励统计、Collocated Async RL） | F-004, F-014, F-016~F-043, F-047, F-048 |
| 实验与格局层（成果/生态） | `concepts/02-training-results-ecosystem.md`（实验结果 + 数据筛选 + 奖励破解防护 + AReaL 等生态引用） | F-009~F-011, F-015, F-027, F-028, F-036, F-049~F-051 |

**references/**
- `references/article-source.md`：博文事实清单（F 编号双份登记之一，与 facts.md 对拍）
- `references/verification.md`：P0 核验报告 + 勘误 + 未核验项

## 6. ADDED Requirements

- 在 `concepts/` 建立 3 篇概念文档
- 在 `references/` 建立 2 篇信源文档（article-source + verification）
- 建立根 `index.md`（含 toctree）与 `log.md`
- 无 `examples/`
- references 与 concepts 的子目录 `index.md`（含 toctree）
- 归属 `ai/models/` 分组：更新 `models/index.md` 导航表 + toctree + 束数
- 全库 `bundles/index.md` 计数同步

## 7. 提交范围（C 阶段）

- 子模块 `projects/awesome-okf-xs`：bundle 文件集 + `ai/models/index.md` + `bundles/index.md`
- 主仓库：本 spec（`.trae/specs/okf-wiki-ecosystem/agent-lightning-blog-okf-wiki/`）+ 子模块指针更新
- 遵循 Conventional Commits，不 push