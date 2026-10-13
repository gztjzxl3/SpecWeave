---
id: boss-manual-agents-manifest
version: 1.0
source: SpecWeave apps 区域新增应用流程
---

# boss-manual 应用智能体契约 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：读取 .agents/rules/sync-protocol.md（任何内容同步/更新前必读）
> 步骤 3：执行任务后退出 apps/ 目录，恢复 SpecWeave 主权区路由
> ```

## 应用性质

boss-manual 是 **AI 人格上下文应用**：把知识库所有者「我是谁、我怎么表达、我的判断边界」从私域知识库提炼为 **AI 可调用的人格资产**，供任何 AI 智能体在代写、改写、整理公开内容前进行人格校准。

- **不是什么**：不是个人博客、不是完整自传、不是隐私仓库。
- **内容来源**：私域知识库 `1-老板说明书` 库的脱敏提炼版；隐私原文永远留在私域，本应用只保存可公开的人格上下文。
- **敏感级别**：公共区资产（纳入版本控制），**禁止写入任何未脱敏的隐私内容**（真实姓名、客户信息、收入细节、未公开策略）。

## 目录结构

```
apps/ai-agents/boss-manual/
├─ AGENTS.md              ← 本文件（应用入口）
├─ README.md              ← 人类可读说明
├─ persona/               ← 人格上下文资产（AI 校准取材区）
│  ├─ README.md           ← 人格资产总索引（取材第一入口）
│  ├─ identity.md         ← 身份称呼规则 + 写作前人格校准清单
│  ├─ boundaries/         ← 判断边界（3 篇：AI 协作/梦想库/健康记录）
│  └─ stories/            ← 脱敏个人故事（9 篇，按主题分目录）
└─ .agents/
   └─ rules/
      └─ sync-protocol.md ← 增量同步协议（私域库 → 本应用）
```

## 核心规则

1. **取材入口**：AI 需要人格校准素材时，从 `persona/README.md` 开始，按索引定位。
2. **同步唯一通道**：私域知识库 → 本应用的内容更新，必须走 [.agents/rules/sync-protocol.md](.agents/rules/sync-protocol.md)，禁止手工直接搬运。
3. **脱敏前置**：任何内容写入 `persona/` 前必须通过同步协议中的脱敏检查清单。
4. **单向流动**：只从私域库向本应用同步；本应用不回写私域库。
5. **称呼统一**：应用内统一使用「宪令」，禁止出现真实姓名。

## 参考链接

- [SpecWeave 根 AGENTS.md](../../../AGENTS.md) — 主权区入口
- [apps/AGENTS.md](../../AGENTS.md) — apps 区域入口路由
- [同步协议](.agents/rules/sync-protocol.md) — 增量同步与脱敏检查
