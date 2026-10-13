# xuan-compose 上游增量同步（e3df104 → 1f1cb09） - 产品需求文档

> 方法论编排：七概念场景 3「重构优化」轻量变体，链路 **R → I → A → V → C**
> （跳过 F：本次为纯对等移植，无本质重构需求，第一性原理无新增推导）
> Session：sc-20261010-sync-upstream-delta

## Overview

- **Summary**：`vendor/podman-compose`（第三方只读子模块）已由 pinned 基线 `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`（v1.6.0）推进到 `1f1cb09bfee4d79857ed23bfe2699febd7d20a53`，区间含 **11 个非合并提交**（代码面净 +143/−70，全部落在 `podman_compose.py`）。本次将其逐一对等移植进 `projects/xuanspace/libs/xuan-compose/`，并同步移植上游新增/变更的单元测试，保持「翻译式搬迁（translate-then-move）、行为逐行对等」不变。
- **Purpose**：维持 xuan-compose 作为 podman-compose 可 import 替代品的**对等性承诺**。上游在本区间修复了 4 个真实缺陷（外部网络 `name:` 被忽略、`volumes: null` 崩溃、`!override` 未类型化、`up --wait` 参数语义）并新增 2 项能力（`exec --detach`、stdin 仅对 run/exec 转发）。不跟进将使 fork 与上游行为分叉，对等证据（parity/ 分册）失效。
- **Target Users**：xuanspace 生态中以 import 方式复用 Compose 编排引擎的 Python 开发者；依赖 CLI 对等语义的运维场景。

## Goals

- **G1（对等）**：11 个非合并提交的**行为语义**逐条移植到对应分层模块，不引入上游未有的语义变更。
- **G2（可证）**：新增/变更的上游单元测试同名移植并全绿；`upstream-quirks.md` 中因上游修复而失效的怪癖条目按分级口径关闭或降级。
- **G3（可溯）**：上游基线单一事实源（`docs/README.md`、`parity/*`、`findings-ledger.md`）由 `e3df104` 更新为 `1f1cb09`，并登记本次同步的提交映射。
- **G4（门禁）**：ruff 零错误、mypy 零新增告警、全量测试通过、链接检查通过。

## Non-Goals

- **NG1**：不修改 `vendor/podman-compose/` 内任何文件（第三方只读子模块）。
- **NG2**：不移植上游 `tests/integration/**`（依赖真实 podman 守护进程，沿用 NG4 既有约定）。
- **NG3**：不更新根仓库 `vendor/podman-compose` 与 `projects/xuanspace` 的 gitlink 指针（另立 `chore` 提交，需用户明确指示）。
- **NG4**：不自动 `git commit`/`git push`；C 阶段仅产出提交建议，提交需用户明确批准。
- **NG5**：不顺手「修正」上游怪癖——上游未改的行为一律原样保留（本次仅裸体跟进上游自己的修复）。

## Background & Context

### R 阶段：客观事实清单（无因果判断词）

- **F-001**：上游区间起点 `e3df104`（v1.6.0 合并点），终点 `1f1cb09`（HEAD）；`git merge-base --is-ancestor` 确认起点为终点祖先，区间 **20 个提交**（含 9 个合并提交）、**11 个非合并提交**。
- **F-002**：区间代码面净变化 `podman_compose.py`：**+143/−70**（213 行），无新增/删除 Python 文件。
- **F-003**：xuan-compose 当前各目标文件仍为基线（旧）形态：`merge.py:40-84`（旧 OverrideTag/ResetTag）、`merge.py:91-127`（旧 rec_merge_one）、`normalize.py:45-69`（旧 rec_subs）、`normalize.py:178-182`（volumes 无 None 校验）、`translate/networks.py:233`（`isinstance(is_ext, str)`）、`translate/run_args.py:149,156`（`["--interactive"]`）、`translate/build.py:57,98,99`（`raise OSError`）、`runner.py:162-215`（无 `pass_stdin`/`stdin=`）、`cli/parser.py:834-858`（无 wait 校验）。
- **F-004**：根仓库记录的 `vendor/podman-compose` gitlink 仍为 `e3df104`，工作区检出为 `1f1cb09`（即根仓库 `M vendor/podman-compose` 的成因）；`docs/README.md:34-37,76` 记录的 pinned commit 亦为 `e3df104`。
- **F-005**：上游区间新增单元测试文件 `tests/unit/test_override_environment.py`（250 行，xuan-compose 尚无同名文件）；另有 5 个既有单元测试被扩写：`test_compose_up_args.py`(+51)、`test_compose_exec_args.py`(+10)、`test_get_net_args.py`(+30)、`test_normalize_service.py`(+5)、`test_container_to_build_args.py`(+3/−1)。
- **F-006**：`upstream-quirks.md` 现有 L0 条目「OverrideTag 的自定义 from_yaml 直接取 ScalarNode.value（无隐式类型解析，标量即字符串）」所描述的行为，在本区间被上游 `fd64dc2` 改写为按节点类型（Mapping/Sequence/Scalar）分别构造。

### 上游增量 → xuan-compose 模块映射（I 阶段产物）

| # | 上游提交 | 变更要点 | 目标模块 |
|---|---|---|---|
| C1 | `fd64dc2` | `OverrideTag.__init__` 支持直接传入 `dict`/`list`；`from_yaml` 按 MappingNode/SequenceNode/ScalarNode 分别 `construct_*`；`to_yaml` 按 `value` 类型分别 `represent_*` | `merge.py` |
| C2 | `fd64dc2` | `rec_subs` 新增 `OverrideTag` 分支（dict/list 递归插值后返回自身）；`environment` 为 `OverrideTag` 时取 `.value` 参与短格式解析；新增第 4 个 `@overload` | `normalize.py` |
| C3 | `fd64dc2` | `normalize_service` 对 `environment`/`labels`：`ResetTag` → 跳过；`OverrideTag` → 对 `.value` 做 `norm_as_dict` | `normalize.py` |
| C4 | `fd64dc2` | `rec_merge_one` 在「source 有、target 无」分支新增 `ResetTag`（记日志跳过）与 `OverrideTag`（记日志 + 取 `.value`）处理；修正双方均为 `OverrideTag` 时的取值优先级（**source 优先**） | `merge.py` |
| C5 | `816045e` | `get_net_args_from_networks` 第 2 处构造：`isinstance(is_ext, str)` → `isinstance(is_ext, dict)`（外部网络 dict 形态 `name:` 生效） | `translate/networks.py` |
| C6 | `f01d26d` | `normalize_service`：`volumes` 为 `None` 时 `raise PodmanComposeError("ERROR: volumes must be a list")`（替代下游 TypeError 崩溃） | `normalize.py` |
| C7 | `008ef4e`+`d1088b3`+`89a2033` | `Podman.run` 新增关键字参数 `pass_stdin: bool = False`；非 `pass_stdin` 时三条 `create_subprocess_exec` 分支均传 `stdin=asyncio.subprocess.PIPE`；`compose_run`/`compose_exec` 调用处传 `pass_stdin=True` | `runner.py`、`commands/runexec.py` |
| C8 | `03649a3` | `compose_exec_args`：`["--detach"] if args.detach else ["--interactive"]`；`--tty` 条件改为 `not args.detach and not args.T` | `translate/run_args.py` |
| C9 | `332cfdb` | `parse_args` 新增校验：`up`/`start` 的 `--wait-timeout` 为负 → `PodmanComposeError`；`up --wait` 与 `--abort-on-container-exit`/`--abort-on-container-failure`/`--exit-code-from` 互斥（多选时以 ` or ` 连接）；`up --wait` 强制 `detach=True` | `cli/parser.py` |
| C10 | `29760c4` | `container_to_build_args` 三处 `raise OSError(...)` → `raise PodmanComposeError(...)` | `translate/build.py` |
| C11 | `ee5ad43` | 注释文本清理：`# Add colored service prefix to output by piping output through sed` → `# Add colored service prefix to output` | `commands/updown.py`、`commands/logs.py` |
| C12 | `d8dea76` | README 补 DNS backend 说明（纯文档，仓库 README 非移植对象） | —（不适用） |

### I 阶段：核心洞察（G2）

- **I-1（陈述）** 本区间 11 个提交中，**5 个是真实行为修复**（C4 优先级、C5、C6、C8、C9），**3 个是新能力**（C1/C2/C3 的 `!override` 类型化、C7 的 stdin 转发），**2 个是错误类型规范化**（C10）与注释清理（C11）。**（证据）** F-001/F-002/F-003 与映射表逐条比对。**（反常识）** 「同步」不等于「复制粘贴」——`OverrideTag.from_yaml` 的改写会**翻转**一条已登记的 L0 怪癖，若只搬代码不改台账，对等证据会自相矛盾。**（行动）** 同步代码的同时必须回写 `upstream-quirks.md`/`findings-ledger.md`，把失效怪癖条目关闭并登记新的 L0 断言。
- **I-2（陈述）** C7（stdin）是唯一**跨层**变更：`runner.py` 接口 + `commands/runexec.py` 两处调用点，且语义为「默认不再继承 stdin，仅 run/exec 显式转发」。**（证据）** 映射表 C7；上游注释明确指出用 `DEVNULL` 会让 `stdin_open` 容器立刻退出。**（反常识）** 默认值选 `PIPE` 而非 `None`（继承）看似反直觉，实为对 `docker-compose` 行为的对齐。**（行动）** 参数默认值必须原样保留 `False`→`PIPE` 的映射，不得「顺手」改为继承。
- **I-3（陈述）** C1/C2/C3/C4 同属 `!override` 一条语义链（YAML 反序列化 → 插值 → 规范化 → 合并），必须**同批落地**。**（证据）** 映射表 C1-C4 分别落在 `merge.py`/`normalize.py`，但数据流串联。**（反常识）** 单独改 `merge.py` 而不改 `normalize.py` 会让 `!override` 的 environment 在插值阶段漏处理。**（行动）** 四项作为同一原子提交落地（或至少同一批验证）。

### A 阶段：拆分蓝图

按「上游提交 ↔ 模块」一一映射拆为 6 个可独立验证的实施单元（见 tasks.md），依赖关系：C1-C4 同链（须同批）；C5/C6/C8/C9/C10/C11 相互独立；C7 独立但改动 2 文件。

## What Changes

- **同步上游代码**（`src/xuan_compose/`，7 文件）：`merge.py`、`normalize.py`、`translate/networks.py`、`translate/run_args.py`、`translate/build.py`、`runner.py`、`commands/runexec.py`、`cli/parser.py`、`commands/updown.py`、`commands/logs.py`。
- **移植测试**（`tests/`）：新增 `test_override_environment.py`；扩写 `test_compose_up_args.py`、`test_compose_exec_args.py`、`test_get_net_args.py`、`test_normalize_service.py`、`test_container_to_build_args.py`；更新 `test_merge_extra.py` 中受影响断言。
- **回写对等证据**（`docs/`）：`README.md`（pinned commit）、`parity/symbol-map.md`、`parity/differences.md`、`parity/upstream-quirks.md`、`findings-ledger.md`。
- **不破坏**：既有 22 命令 CLI 表面、`tests/snapshots/cli_parity.json` 参数表（本次无 argparse 参数增删，仅 `parse_args` 校验增强——须实测确认快照不变）。

## Impact

- Affected specs：`.trae/specs/xuan-compose-refactor`（原始重构 spec，其 AC-3/AC-5/AC-10 对等承诺由本次同步延续）；`parity/README.md` 三册对等证据。
- Affected code：`src/xuan_compose/{merge,normalize,runner}.py`、`src/xuan_compose/cli/parser.py`、`src/xuan_compose/translate/{networks,run_args,build}.py`、`src/xuan_compose/commands/{runexec,updown,logs}.py`；`tests/**`；`docs/**`。

## ADDED Requirements

### Requirement: 上游基线推进为 1f1cb09

系统 SHALL 将 xuan-compose 记录的上游 pinned 基线由 `e3df10472e194ab6d547b5ad25542c5c79e1a5fb` 推进至 `1f1cb09bfee4d79857ed23bfe2699febd7d20a53`，并在对等证据分册登记。

#### Scenario: 基线可追溯

- **WHEN** 阅读 `docs/README.md` 的「上游基线（单一事实源）」小节
- **THEN** pinned commit 显示为 `1f1cb09`，且 `parity/README.md`、`parity/differences.md` 同步更新

### Requirement: `!override` 标签类型化构造（C1）

`merge.py` 的 `OverrideTag` SHALL 支持：`__init__` 直接接受 `dict`/`list`；`from_yaml` 按 `MappingNode`/`SequenceNode`/`ScalarNode` 分别 `construct_mapping`/`construct_sequence`/`construct_scalar`，其余取 `node.value`；`to_yaml` 按 `value` 类型分别 `represent_mapping`/`represent_sequence`/`represent_scalar`。

#### Scenario: `!override` 携带映射

- **WHEN** YAML 中 `environment: !override` 后接映射
- **THEN** `from_yaml` 返回的 `OverrideTag.value` 为等值 `dict`（非标量字符串）

### Requirement: `!override` 在插值/规范化/合并链中贯通（C2/C3/C4）

`normalize.py` 的 `rec_subs` SHALL 支持 `OverrideTag`（dict/list 递归插值）；`environment` 为 `OverrideTag` 时以其 `.value` 参与短格式环境变量解析。`normalize_service` SHALL 对 `environment`/`labels` 分别处理 `ResetTag`（跳过）与 `OverrideTag`（对 `.value` 调 `norm_as_dict`）。`merge.py::rec_merge_one` SHALL 在「source 有、target 无」分支对 `ResetTag` 记日志跳过、对 `OverrideTag` 取 `.value` 写入，并 SHALL 在双方均为 `OverrideTag` 时取 **source** 侧值。

#### Scenario: override 环境变量合并

- **WHEN** 基础文件声明 `environment` 映射，覆盖文件以 `environment: !override` 提供新映射
- **THEN** 合并结果为覆盖侧映射（非两侧并集），且插值/短格式解析均正确应用

### Requirement: 外部网络 dict 形态 `name:` 生效（C5）

`translate/networks.py::get_net_args_from_networks` 第 2 处 `ext_desc` 构造 SHALL 使用 `isinstance(is_ext, dict)` 判定，使 `external: {name: ...}` 生效。

#### Scenario: external 网络带 name

- **WHEN** compose 文件声明 `networks: {n1: {external: true, name: real-net}}`
- **THEN** 生成的 podman 网络参数使用 `real-net` 而非默认名

### Requirement: `volumes: null` 显式报错（C6）

`normalize_service` SHALL 在 `service["volumes"] is None` 时抛出 `PodmanComposeError("ERROR: volumes must be a list")`。

#### Scenario: 空 volumes 段

- **WHEN** 服务声明 `volumes:`（值为 null）
- **THEN** 抛出 `PodmanComposeError` 且消息为 `ERROR: volumes must be a list`（而非 `TypeError`）

### Requirement: stdin 仅对 run/exec 转发（C7）

`runner.py::Podman.run` SHALL 新增关键字参数 `pass_stdin: bool = False`；三条子进程创建分支 SHALL 在非 `pass_stdin` 时传 `stdin=asyncio.subprocess.PIPE`，`pass_stdin` 时传 `stdin=None`。`compose_run` 与 `compose_exec` SHALL 以 `pass_stdin=True` 调用。

#### Scenario: up 不继承 stdin

- **WHEN** 执行 `up`（非 run/exec）
- **THEN** 子进程 stdin 为 `PIPE`（不继承父进程 stdin）

### Requirement: `exec --detach` 生效（C8）

`translate/run_args.py::compose_exec_args` SHALL 在 `args.detach` 为真时输出 `["--detach"]`（否则 `["--interactive"]`），且 SHALL 仅在 `not args.detach and not args.T` 时追加 `--tty`。

#### Scenario: exec -d

- **WHEN** 执行 `exec -d svc cmd`
- **THEN** podman 参数含 `--detach` 且不含 `--tty`

### Requirement: `up --wait` 参数校验与互斥（C9）

`cli/parser.py::parse_args` SHALL 在命令为 `up`/`start` 且 `--wait-timeout` 为负时抛出 `PodmanComposeError`；SHALL 在 `up --wait` 与 `--abort-on-container-exit`/`--abort-on-container-failure`/`--exit-code-from` 之一共用时抛出 `PodmanComposeError`（多选以 ` or ` 连接）；SHALL 在 `up --wait` 时强制 `global_args.detach = True`。

#### Scenario: up --wait 与 abort 互斥

- **WHEN** 执行 `up --wait --abort-on-container-exit`
- **THEN** 抛出 `PodmanComposeError`，消息含 `--wait cannot be combined with --abort-on-container-exit`

### Requirement: 构建校验错误类型规范化（C10）

`translate/build.py::container_to_build_args` 的三处构建校验失败 SHALL 抛出 `PodmanComposeError`（替代 `OSError`）。

#### Scenario: dockerfile_inline 与 dockerfile 并存

- **WHEN** 同时声明 `dockerfile_inline` 与 `dockerfile`
- **THEN** 抛出 `PodmanComposeError`，消息为 `dockerfile_inline and dockerfile can't be used simultaneously`

### Requirement: 上游单元测试同步移植（G2）

系统 SHALL 新增 `tests/test_override_environment.py` 并扩写 5 个既有测试文件，覆盖 C1-C10 的新行为；`override_environment` 契约 SHALL 有独立测试文件。

#### Scenario: 新增测试文件

- **WHEN** 阅读 `tests/test_override_environment.py`
- **THEN** 存在且覆盖 `!override` 环境变量合并场景

## MODIFIED Requirements

### Requirement: 上游怪癖固化清单（`upstream-quirks.md`）

条目「OverrideTag 的自定义 from_yaml 直接取 ScalarNode.value（无隐式类型解析，标量即字符串）」，因上游 `fd64dc2` 改写 from_yaml 而 SHALL 被关闭或改写为「上游已修复」；若合并优先级（C4）等新行为构成新的对等风险点，SHALL 按 L0-L3 分级口径登记。

#### Scenario: 怪癖条目与上游对齐

- **WHEN** 阅读 `parity/upstream-quirks.md` 合并段
- **THEN** 不含已失效的 from_yaml 描述，且新增条目（若有）逐点标注固化级别

## REMOVED Requirements

无。