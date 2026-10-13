---
id: "retro-20261009-caffe-pool-ceil-shape"
title: "Caffe 池化默认 ceil 取整误判为 floor 导致 shape 推导连锁错误复盘"
date: "2026-10-09"
scope: "problem"
type: "retrospective-report"
source: "2026-10-09 对外部交付区 lms.prototxt（VGG 式三段卷积池化网络）做静态 shape 推导时，误将 Caffe 池化默认 ceil 判为 floor 并错误警告网络无法前向，经用户一次质疑纠正后的知识沉淀"
tags: ["seven-concepts", "knowledge-retro", "caffe", "shape-inference", "pooling", "cross-framework", "falsification"]
related_patterns: ["cross-framework-default-semantics-verification", "import-path-priori-verification"]
---

# Caffe 池化默认 ceil 取整误判为 floor 导致 shape 推导连锁错误复盘报告

> **分析对象**：外部工作区文件 `notebook/release/examples/lms.prototxt`（XMNPU 工具链客户发布区示例网络，name: "vlmc"），该文件不在本仓库内，故以行内路径文本引用，不做超链接
> **错误主体**：AI 智能体在问答中的静态 shape 推导（非产品代码缺陷）
> **方法论**：七概念方法论编排（知识沉淀链路 `R→I→E`，本报告补齐 R/I 完整记录并回挂已入库模式）
> **报告日期**：2026-10-09
> **相关模式**：[cross-framework-default-semantics-verification](../patterns/process-patterns/cross-framework-default-semantics-verification.md)

***

## 一、概述

在回答客户发布区示例网络 `lms.prototxt` 中 `conv3_2` 层输入 shape 的问题时，智能体断言"Caffe 默认 floor 取整"，并据此推出该层输入为 `[1,40,2,2]`、在 `kernel_size:3, pad:0` 配置下输出尺寸为 0，进而给出"网络无法前向、需要修改网络"的错误警告。

用户以一句"Caffe 默认 floor 取整？你确定？"质疑后，核查确认：BVLC Caffe 的池化层实现默认使用 **ceil** 取整，与 PyTorch `MaxPool2d` 默认的 floor 方向相反。按正确规则连锁重算，`conv3_2` 输入实为 `[1,40,3,3]`、输出 `[1,80,1,1]`，网络完全自洽。

本次错误未流入代码或交付物，但暴露了"跨框架默认值直觉平移"与"只前向推导、不用下游约束反证"两类方法论缺陷，并已按 R→I→E 链路沉淀为流程模式。

---

## 二、复盘范围

本次复盘覆盖：

- 问答中两轮 shape 推导的事实经过与数值链
- 错误断言的来源（PyTorch 先验迁移）与放大机制（逐层累积、错误警告）
- 纠错过程中的证据核实动作与本地取证条件限制
- 知识沉淀产物（项目记忆条目、流程模式文件）及其二次 review 中发现的衍生错误

本次复盘不包含：

- `lms.prototxt` 网络本身的数值正确性评估（静态推导，无权重与运行期数据）
- Caffe 各 fork（Intel Caffe、NCNN 等）池化取整变体的全面普查
- XMNPU TVM Caffe 前端实际 shape inference 代码的审计（宿主工作区无该源码检出）

---

## 三、方法论说明

本次属于**知识沉淀**场景，主链路 `R→I→E`：先在会话内完成即时沉淀（项目记忆 Lessons Learned 条目），再按用户指令萃取为流程模式入库；本报告补齐可审计的 R/I 完整记录，并将模式的 `source` 回挂到本报告，闭合溯源链。

| 阶段 | 产出物 | 质量门 |
|------|--------|--------|
| R | 第四章 25 条编号事实 | G1：客观、可验证、无因果词 |
| I | 第五章 4 条四元组洞察 | G2：现象/根因/影响/建议 |
| E | 已入库流程模式 | G3：触发条件/步骤/反模式/迁移 |
| C | 第七章文档级原子行动项 | G4：单一职责、可独立验证 |

---

## 四、R（Retrospective 复盘）

### 4.1 事实回顾（G1）

**对象网络结构事实**

- F1：2026-10-09，用户在 IDE 中打开 `notebook/release/examples/lms.prototxt`，选中第 318–335 行 `conv3_2` 层定义，询问该层的输入 shape。
- F2：prototxt 头部声明 `name: "vlmc"`、`input: "data"`，四个 `input_dim` 依次为 1、3、120、120。
- F3：`conv_pre` 配置为 `num_output: 8, kernel_size: 5, stride: 2, pad: 0`。
- F4：`conv_pre` 后依次接 BatchNorm、Scale、ReLU（均 in-place，top 同名），再接 `pool_pre`：`pool: MAX, kernel_size: 2, stride: 2`。
- F5：`conv1_1`/`conv1_2` 均为 `num_output: 16, kernel_size: 3, stride: 1, pad: 0`，各配 BN/Scale/ReLU；其后 `pool1` 为 MAX、k2、s2。
- F6：`conv2_1`/`conv2_2` 均为 `num_output: 24, k3, s1, pad0`；其后 `pool2` 为 MAX、k2、s2。
- F7：`conv3_1` 为 `num_output: 40, k3, s1, pad0`，后接 BN/Scale/ReLU；`conv3_2` 为 `num_output: 80, k3, s1, pad0`，`bottom: "conv3_1"`。
- F8：`conv3_2` 后的 BatchNorm 带三组 `param { lr_mult: 0 decay_mult: 0 }`，Scale/ReLU 均 in-place。
- F9：`fc1`（InnerProduct，`num_output: 128`）与 `fc_qua0`（top `fcq0`，`num_output: 128`）的 bottom 均为 `conv3_2`；两分支末端分别为 `fc_para`（50 输出）与 `fc_qua2`（1 输出）。

**初轮错误推导事实**

- F10：智能体初轮回答的原文断言为"Caffe 默认 floor 取整"。
- F11：初轮逐层数值为：conv_pre 58×58、pool_pre 29×29、conv1_1 27×27、conv1_2 25×25、pool1 **12×12**、conv2_1 10×10、conv2_2 8×8、pool2 **4×4**、conv3_1 **2×2**。
- F12：初轮给出的结论为：`conv3_2` 输入 `[1,40,2,2]`；k3/pad0 作用于 2×2 的输出尺寸 (2−3)/1+1=0；并输出警告"该层无法得到合法输出，网络实际前向会在此报错"，同时建议修改网络（加 pad 或改 kernel）。

**纠错过程事实**

- F13：用户的反馈全文为"Caffe 默认 floor 取整？你确定？"。
- F14：纠错时尝试 Grep 宿主路径 `/media/pc/data/ai/server/libs/tvm/python/tvm/relay/frontend/caffe.py`，返回 IO error（No such file or directory）。
- F15：随后 Glob 搜索 `**/relay/frontend/caffe.py`（范围 `/media/pc/data/ai`）返回 No file found——TVM 源码位于开发容器挂载中，宿主工作区无此检出，无法在本地直接引用实现代码。
- F16：经知识核查确认 BVLC Caffe `pooling_layer.cpp` 的输出尺寸公式为 `pooled_height_ = static_cast<int>(ceil(static_cast<float>(height_ + 2*pad_h_ - kernel_h_) / stride_h_)) + 1`，即默认 ceil；仅当 pad>0 且末窗完全落在 padding 区时部分版本会减去该窗。
- F17：BVLC Caffe `base_conv_layer.cpp` 的卷积输出公式为 `(H + 2·pad − kernel) / stride + 1`，按 C++ 整数除法计算，正数输入下等价 floor。
- F18：按 ceil 规则连锁重算的数值为：pool1 **13×13**（⌈23/2⌉+1）、conv2_1 11×11、conv2_2 9×9、pool2 **5×5**（⌈7/2⌉+1）、conv3_1 **3×3**、conv3_2 输出 **1×80×1×1**。
- F19：更正后的结论为：`conv3_2` 输入 `[1,40,3,3]`、输出 `[1,80,1,1]`；明确撤回初轮"输出尺寸 0、网络无法前向"的警告与改网建议。
- F20：用户第三轮要求据修正 shape 推导 `fc1` 与 `fc_qua0` 的输入维度；答复为两者输入均 `[1,80,1,1]`，InnerProduct 展平维 `K = 80×1×1 = 80`，权重形状 `[128, 80]`，输出 `[1,128]`。

**沉淀与复审事实**

- F21：用户指令"Use Skill: seven-concepts-cmd 请记住，避免再次犯错"；当轮按知识沉淀链路 R→I→E 执行，教训条目写入项目记忆 `project_memory.md` 的 Lessons Learned（含 Caffe/PyTorch/ONNX 池化取整对照与两条防错规则）。
- F22：用户随后指令"沉淀模式到 `notebook/dev/libs/AI/.agents`"；按磁盘 AGENTS.md「文档边界」条款（`.agents/` 禁写产出物、模式库唯一入口为 `docs/retrospective/patterns/`），模式文件实际落位于 `docs/retrospective/patterns/process-patterns/cross-framework-default-semantics-verification.md`，并注册该目录 `index.md` 的 toctree 与 `README.md` 索引表。
- F23：对模式文档做 review 时发现其第 4 步"展平维 K 与权重第一维一致"的表述与 Caffe InnerProduct 权重形状 `[num_output, K]` 不符（K 对应第二维/输入维）；该错误发生在一份教人"下游反证"的模式文档中。
- F24：同次 review 另修正三处：检验标准把四项反证误写为"三项"且漏 Reshape/Concat；对照表"ONNX MaxPool"行标签与"Convolution 输出"列不匹配；步骤 1 将 dilation（各框架默认均为 1，属易漏参数）误归入默认值分歧参数。
- F25：仓库 `check-links.py` 对模式目录（29 文件、81 个本地引用）与修改后单文件的两次校验均输出"校验通过：所有链接均有效"。

### 4.2 时间线

| 时刻（会话序） | 事件 |
|---|---|
| 第 1 轮 | 用户问 conv3_2 输入 shape；智能体给出 floor 推导 + "网络无法前向"警告 |
| 第 2 轮 | 用户质疑；本地取源码失败后经知识核查改为 ceil，连锁重算并撤回警告 |
| 第 3 轮 | 用户要求推导两 FC 输入维；答复 K=80 |
| 第 4 轮 | 用户要求用 seven-concepts-cmd 记住；写入项目记忆 |
| 第 5 轮 | 用户要求沉淀模式；模式入 docs/ 模式库并双注册 |
| 第 6 轮 | 用户要求 review 模式文档；发现并修正 1 个 P0 事实错误 + 3 处一致性问题 |
| 第 7 轮 | 用户要求补本复盘报告 |

### 4.3 错误数值与正确数值对照

| 层 | 初轮（错误 floor） | 正确（Caffe ceil） | 偏差 |
|----|--------------------|--------------------|------|
| pool1（入 25×25） | 12×12 | 13×13 | −1 |
| conv2_1 / conv2_2 | 10×10 / 8×8 | 11×11 / 9×9 | −1 / −1 |
| pool2 | 4×4 | 5×5 | −1 |
| conv3_1 | 2×2 | 3×3 | −1 |
| conv3_2 输出 | 0×0（非法） | 1×1 | 定性错误 |
| 末端 FC 判定 | "网络无法前向" | K=80，双分支自洽 | 警告方向反转 |

注：`pool_pre`（入 58×58，(58−2)/2=28 整除）两条链结果相同——整除层 floor/ceil 无差异，错误直到第一个非整除池化窗口才暴露。

***

## 五、I（Insight 洞察）

### 洞察 1：跨框架默认值直觉平移

- **现象**：在 Caffe 网络上直接断言"默认 floor 取整"（F10），而 Caffe 池化实为 ceil（F16）；PyTorch `MaxPool2d` 恰为 `ceil_mode=False`（floor）。
- **根因**：把高频使用框架（PyTorch）的默认参数当成跨框架普遍事实，断言前未执行任何针对目标框架的证据核实；"pooling 默认 floor"作为熟练直觉被无差别调用。
- **影响**：首个非整除池化层起每层空间尺寸静默偏小 1 并逐层传播（4.3 表），最终把一个自洽网络误判为不可运行，若用户采信将无谓修改交付区网络（且 release 目录按治理规范不允许手改）。
- **建议**：跨框架推导前枚举全部"默认值决策点"，逐个按"源码 > 官方文档 > 第三方教程 > 记忆"的证据等级核实目标框架，已固化为模式步骤 1–2。

### 洞察 2：异常推导结果未触发回查，反而升级为警告

- **现象**：初轮推出"2×2 特征图经 k3/pad0 卷积 → 0×0"这一明显异常（F12），反应不是回查前提，而是输出"网络无法前向"并建议改网。
- **根因**：推导过程只有前向计算，缺少用末端结构做反向约束的环节；末端两个 InnerProduct 对展平维的硬约束、空间尺寸必须为正这两条反证均缺席。
- **影响**：错误的严重度被放大——从"可能算错"升级为"交付物有缺陷"，直接误导用户对客户发布区文件的判断。
- **建议**：把"末端 FC 输入维一致、空间尺寸正性、多分支 shape 一致、Reshape/Concat 匹配"设为强制反证关卡，任一不满足必须回查而非下结论（模式步骤 4）。

### 洞察 3：证据核实时序倒置，且未声明不确定性

- **现象**：源码核查发生在用户质疑之后（F13–F17）；首次断言时以确定语气交付；纠错时本地无 TVM/Caffe 源码可查（F14–F15），这一取证条件限制在初轮未被识别和说明。
- **根因**：回答流程中"断言"与"取证"的先后没有约束；缺乏"查不到实现源码时显式标注结论可信度"的机制。
- **影响**：无证据断言以与已验证结论相同的确定度呈现，用户必须自行承担证伪成本（本次由用户一句质疑拦截）。
- **建议**：无法取得目标框架源码/文档时，结论必须附带不确定性标注与待验证项；条件允许时用最小 shape spike 代替口头争论（模式步骤 2、5）。

### 洞察 4：纠错沉淀的产物发生二次事实污染

- **现象**：按教训萃取的模式文档，其"下游反证"条目自身写错了 FC 权重维度（"第一维"，实为第二维）（F23），另有三处一致性/精确性问题（F24）。
- **根因**：沉淀动作复用了同一会话上下文中未经验证的表述；"我正在总结的是别人（自己）刚犯的错"产生了虚假的审查豁免感，模式文档成稿后未经独立事实核对即入库。
- **影响**：若未做 review，错误的权重维指引会随模式复用扩散，使"反证模式"自身成为新错误源；也说明 L1-draft 模式的 review 环节不是可选项。
- **建议**：模式入库前过一遍与正文等强度的事实审查（公式、维度、框架版本），并将成熟度标为 L1-draft 直至第二个独立案例验证；本次 review 修正即该关卡的首次执行。

***

## 六、E（Extraction 萃取）

已萃取流程模式：**跨框架默认语义先验核实与下游自洽反证模式**

- 模式文件：[cross-framework-default-semantics-verification.md](../patterns/process-patterns/cross-framework-default-semantics-verification.md)
- 分类：process-patterns，成熟度 L1-draft（单案例）
- 核心步骤：①枚举默认值决策点 → ②断言前按证据等级核实目标框架 → ③逐层标注公式与取整方向 → ④下游自洽性反证（FC 输入维/尺寸正性/多分支/Reshape·Concat）→ ⑤最小 shape spike → ⑥修正后连锁重算
- 反模式 6 条、检验标准 5 条、跨域迁移示例 5 个（量化默认值、resize 坐标对齐、ONNX 前端、数据库、序列化）

模式的 `source` 字段已由会话 ID 回挂为本报告 ID，溯源链闭合。

***

## 七、C（原子行动项 / 闭环）

| # | 行动项 | 状态 | 验收标准 |
|---|--------|------|----------|
| 1 | 教训写入项目记忆 Lessons Learned（跨框架取整对照 + 两条防错规则） | ✅ 已完成 | `project_memory.md` 含 2026-10-09 条目 |
| 2 | 萃取流程模式入库并双注册（toctree + README） | ✅ 已完成 | 模式文件存在且被两个索引引用 |
| 3 | 模式文档事实 review，修正 P0 权重维度等 4 处 | ✅ 已完成 | 见 F23–F24；check-links 通过 |
| 4 | 补本复盘报告并注册 reports toctree，回挂模式 source | ✅ 本次完成 | 本文件入 index.md；模式 frontmatter `source` 指向本报告 |
| 5 | （建议，待第二个独立案例）模式升级 L2 | ⏳ 待验证 | 在 ONNX ceil_mode 或 resize 坐标对齐场景再成功应用一次 |
| 6 | （建议，不自动执行）后续同类问答优先跑最小 shape spike | ⏳ 建议 | 回答中附运行期 shape 证据而非纯静态推导 |

所有文档变更均未提交 git，按项目约定等待用户明确指令后再提交。

***

## 八、结论

本次错误的本质是 **把 PyTorch 的池化 floor 默认值无证据平移到 Caffe（实为 ceil），并用纯前向推导把逐层 −1 的尺寸偏差累积成"网络无法前向"的虚假定性**；整除层结果相同掩盖了规则分歧，零尺寸异常本应触发回查却被直接升级为结论。

纠错后沿知识沉淀链路形成三层防线：项目记忆条目（个人侧防再犯）、流程模式（可复用的核实+反证步骤）、本复盘报告（可审计的事实与洞察记录）；模式 review 中又捕获一处沉淀产物自身的维度错误，验证了"L1 模式入库前必须独立事实审查"。该模式当前为 L1-draft，待跨框架场景的第二次独立验证后升级。
