# Tasks

> 同步上游 `vendor/podman-compose` 增量（`e3df104` → `1f1cb09`，11 个非合并提交）至 `projects/xuanspace/libs/xuan-compose/`。
> 目录相对 `projects/xuanspace/libs/xuan-compose/`。全部改动在 xuanspace 子项目内（经用户指令授权）。

- [x] Task 1: C1-C4 `!override` 语义链（YAML 反序列化 → 插值 → 规范化 → 合并）同批落地
  - [x] SubTask 1.1: `src/xuan_compose/merge.py` — `OverrideTag.__init__` 支持直接传入 `dict`/`list`；`from_yaml` 按 `MappingNode`/`SequenceNode`/`ScalarNode` 分别 `construct_mapping`/`construct_sequence`/`construct_scalar`（其余取 `node.value`）；`to_yaml` 按 `value` 类型分别 `represent_mapping`/`represent_sequence`/`represent_scalar`（空值回退 `''`）（已与上游 `1f1cb09` 逐行对拍，L46-86 完全一致）
  - [x] SubTask 1.2: `src/xuan_compose/merge.py` — `rec_merge_one`：在「source 有、target 无」分支新增 `ResetTag`（`log.info` 后 `continue`）与 `OverrideTag`（`log.info` + `target[key] = clone(value.value)` + `done.add(key)` + `continue`）；「双方均为 `OverrideTag`」取值优先级改为 **source 优先**（已逐行对拍上游 L2267-2312，一致）
  - [x] SubTask 1.3: `src/xuan_compose/normalize.py` — `rec_subs` 新增第 4 个 `@overload`（`OverrideTag → OverrideTag`）与 `elif isinstance(value, OverrideTag)` 分支（dict 递归插值 / list 逐项插值后返回自身）；`environment` 为 `OverrideTag` 时以 `.value` 参与短格式环境变量解析（已逐行对拍上游 L531-575，一致）
  - [x] SubTask 1.4: `src/xuan_compose/normalize.py` — `normalize_service` 对 `environment`/`labels`：`ResetTag` → `continue`；`OverrideTag` → 对 `.value` 调 `norm_as_dict`；否则原逻辑（已逐行对拍上游 L2157-2166，一致）
  - [x] SubTask 1.5: 移植上游 `tests/unit/test_override_environment.py` → `tests/test_override_environment.py`（新增，11 个用例名与上游逐一对应，`setUp`/`tearDown` 增补 COMPOSE_* 环境快照隔离）；同步校对 `tests/test_merge_extra.py` 中受 from_yaml/优先级变更影响的 4 处断言
  - [x] SubTask 1.6: 运行 `pytest tests/test_override_environment.py tests/test_merge_extra.py` 通过（WSL 权威门禁合并 73 passed）

- [x] Task 2: C5 外部网络 dict 形态 `name:` 修复
  - [x] SubTask 2.1: `src/xuan_compose/translate/networks.py` — `get_net_args_from_networks` 第 2 处 `ext_desc` 判定由 `isinstance(is_ext, str)` 改为 `isinstance(is_ext, dict)`
  - [x] SubTask 2.2: 移植上游 `tests/unit/test_get_net_args.py` 的 +30 行增量到 `tests/test_get_net_args.py`
  - [x] SubTask 2.3: 运行 `pytest tests/test_get_net_args.py` 通过

- [x] Task 3: C6 `volumes: null` 显式报错
  - [x] SubTask 3.1: `src/xuan_compose/normalize.py` — `normalize_service` 在 `key == "volumes" and service[key] is None` 时 `raise PodmanComposeError("ERROR: volumes must be a list")`（已核验：`normalize.py:199-200`，与上游 L2148-2149 逐行一致；`PodmanComposeError` 已在 `errors.py`）
  - [x] SubTask 3.2: 移植上游 `tests/unit/test_normalize_service.py` 的 +5 行增量到 `tests/test_normalize_service.py`（`test_volumes_none_raises`，与上游 L148-151 逐字一致）
  - [x] SubTask 3.3: 运行 `pytest tests/test_normalize_service.py` 通过（WSL 权威门禁合并 73 passed）

- [x] Task 4: C7 stdin 仅对 run/exec 转发
  - [x] SubTask 4.1: `src/xuan_compose/runner.py` — `Podman.run` 新增关键字参数 `pass_stdin: bool = False`；`stdin_arg = None if pass_stdin else asyncio.subprocess.PIPE`；三条 `create_subprocess_exec` 分支（log_formatter / suppress_output / 默认）均传 `stdin=stdin_arg`；保留上游解释性注释
  - [x] SubTask 4.2: `src/xuan_compose/commands/runexec.py` — `compose_run` 与 `compose_exec` 的 `compose.podman.run(...)` 调用追加 `pass_stdin=True`
  - [x] SubTask 4.3: 运行 `pytest tests/ -k "run or exec"` 通过（含 `test_runner_extra.py`、`test_compose_exec_args.py` 等）；`tests/test_commands_build_updown.py:505` 的 `assert_awaited_once_with` 已同步补 `pass_stdin=True`（不得删弱）

- [x] Task 5: C8 `exec --detach` 生效
  - [x] SubTask 5.1: 核对 `src/xuan_compose/cli/parser.py` 中 `compose_exec_parse` 确有 `--detach` 且落到 `args.detach`（基线已观察到 `--detach` 定义，须确认归属为 exec 而非 run/up）
  - [x] SubTask 5.2: `src/xuan_compose/translate/run_args.py` — `compose_exec_args` 首行改为 `podman_args = ["--detach"] if args.detach else ["--interactive"]`；`--tty` 条件改为 `if not args.detach and not args.T`
  - [x] SubTask 5.3: 移植上游 `tests/unit/test_compose_exec_args.py` 的 +10 行增量到 `tests/test_compose_exec_args.py`
  - [x] SubTask 5.4: 运行 `pytest tests/test_compose_exec_args.py` 通过
  - [x] SubTask 5.5: 回归修补——`tests/test_run_args_extra.py::TestComposeExecArgs` 两处 `_ns(...)` 调用点补齐 `detach=False`（该文件为 fork 本地测试，上游无同名文件；不得在通用 `_ns` helper 内注默认值），并确认全 `tests/` 无其它缺 `args.detach` 的 `compose_exec_args` 调用点

- [x] Task 6: C9 `up --wait` 参数校验与互斥
  - [x] SubTask 6.1: `src/xuan_compose/cli/parser.py` — `parse_args` 在 `parser.parse_args` 后新增：`command in ("up","start")` 且 `wait_timeout is not None and wait_timeout < 0` → `raise PodmanComposeError("--wait-timeout must be a non-negative integer")`
  - [x] SubTask 6.2: 同处新增：`command == "up" and wait` 时收集 `--abort-on-container-exit`/`--abort-on-container-failure`/`--exit-code-from` 冲突项，非空则 `raise PodmanComposeError(f"--wait cannot be combined with {incompatible_options}")`（多选以 `", ".join(...[:-1]) + " or " + last` 连接）；无冲突则 `global_args.detach = True`
  - [x] SubTask 6.3: 移植上游 `tests/unit/test_compose_up_args.py` 的 +51 行增量到 `tests/test_compose_up_args.py`
  - [x] SubTask 6.4: 运行 `pytest tests/test_compose_up_args.py` 通过

- [x] Task 7: C10 构建校验错误类型规范化 + C11 注释清理
  - [x] SubTask 7.1: `src/xuan_compose/translate/build.py` — `container_to_build_args` 三处 `raise OSError(...)` → `raise PodmanComposeError(...)`（已核验：L19 已导入，L58/L101/L102 三处改写）
  - [x] SubTask 7.2: 注释清理——实际落点是 `src/xuan_compose/logs.py:32` 与 `src/xuan_compose/commands/updown.py:361`（**非 spec 原写的 `commands/logs.py`**；`commands/logs.py` 无该注释，全仓已无 `by piping output through sed` 残留）
  - [x] SubTask 7.3: 移植上游 `tests/unit/test_container_to_build_args.py` 的 +3/−1 增量到 `tests/test_container_to_build_args.py`（`assertRaises(OSError)` → `PodmanComposeError`）；连带修正 `tests/test_build_args_extra.py` 两处 `pytest.raises(OSError)`
  - [x] SubTask 7.4: 运行 `pytest tests/test_build_args_extra.py tests/test_logs.py tests/test_commands_build_updown.py -q` 通过（41 passed）；`tests/test_container_to_build_args.py` 6 个失败均为**既有的、已登记的**原生 Windows `/` vs `\` 平台差异（见 `docs/findings-ledger.md:94-95`），非本次引入

- [x] Task 8: 对等证据回写（上游基线推进 + 怪癖条目裁决）
  - [x] SubTask 8.1: `docs/README.md` — 「上游基线（单一事实源）」pinned commit 改为 `1f1cb09bfee4d79857ed23bfe2699febd7d20a53`（已核验 L37）；`vendor 洁净` 行 HEAD 引用同步为 `1f1cb09`（L76）；测试计数补注「2026-10-10 同步后 965 例」（L15/L70）、覆盖率补注 92%（L71）
  - [x] SubTask 8.2: `docs/parity/README.md`、`docs/parity/symbol-map.md`、`docs/parity/differences.md` — 已更新锚定 commit（symbol-map 头部声明行号锚定 `1f1cb09`；README L25 快照锚点说明、L29 测试数 +25、L33 覆盖率 92%）；symbol-map 全表行号按 1f1cb09 重锚，`rec_subs` 表后追加 `@overload` 脚注，总账 142/138/4/139/1/2 不变；differences L8 补「M3/M4/M5 行号为登记时点证据、不重锚」维护说明、L32 D2 补快照锚点说明
  - [x] SubTask 8.3: `docs/parity/upstream-quirks.md` — L35 关闭「OverrideTag 的 from_yaml 直接取 ScalarNode.value」条目（注 2026-10-10 上游 `fd64dc2` 修复理由）；「合并」小节新增 `fd64dc2` 三条语义变更登记（双 override source 优先 / `!override {}` 得 `{}` / 标量按标记解析，定级 L0）；T7 段 pinned 改 `1f1cb09`
  - [x] SubTask 8.4: `docs/findings-ledger.md` — 追加 §G「上游增量同步 e3df104 → 1f1cb09（2026-10-10）」（区间 11 提交、提交→模块映射、符号面、怪癖裁决、测试面、遗留项与环境事实）
  - [x] SubTask 8.5: 确认 `tests/snapshots/cli_parity.json` 无需再生（本次无 argparse 参数增删）；`pytest tests/test_cli_parity.py tests/test_command_surface.py -q` 实测 9 passed / 50 subtests（快照守卫绿）

- [x] Task 9: 全量门禁验证
  - [x] SubTask 9.1: WSL 权威全量测试（`PYTHONPATH=src /home/user/.venvs/xuan-gate/bin/pytest -q`）实测 **965 passed / 79 subtests / 0 failed**，`--cov=src/xuan_compose` 总覆盖率 **92%**（与 2026-09-16 交付基线一致；注：权威门禁为 WSL POSIX，原生 Windows 侧的 POSIX 路径差异失败为已登记项 §E.2）
  - [x] SubTask 9.2: `ruff check src tests` 零错误（`All checks passed!`）；`mypy src` 零新增告警（`Success: no issues found in 39 source files`）（权威环境 Windows py314；本轮已安装 `ruff 0.16.10` / `mypy 2.4.0` 于 `d:\AI\.venv`）
  - [x] SubTask 9.3: 链接检查（`check-links.py --path .`，cwd=docs）**10 个 md / 125 个本地引用全绿、0 断链**；文件名规范校验（`check-filename-convention.py --directory`，覆盖 docs 与子模块根）**0 违规**
  - [x] SubTask 9.4（本轮新增·修复）：`tests/test_override_environment.py` 文件末尾缺换行触发 ruff `W292`，已补尾行换行（+1 LF，未 reformat/未增删行）；复跑 `ruff check src tests` → `All checks passed!`、`mypy src` → 39 文件无问题、该测试文件 11 passed

# Task Dependencies

- Task 1 的 SubTask 1.1-1.4 为同一语义链，须同批落地后再跑 SubTask 1.6。
- Task 9 依赖 Task 1-8 全部完成。
- Task 8 依赖 Task 1-7 的最终代码形态。
- Task 2、3、4、5、6、7 相互独立，可与 Task 1 并行。
- 全部任务完成后由用户明确批准再执行 C 阶段（`atomic-commit-cmd` 原子提交，建议按 Task 分组拆提交）。