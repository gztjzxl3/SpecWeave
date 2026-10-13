# Checklist

> 逐项核验「xuan-compose 上游增量同步（e3df104 → 1f1cb09）」的落地质量。
> 每项均对应 spec.md 的 Requirement 与 tasks.md 的实施单元。

## A. 代码对等（逐提交）

- [x] `merge.py::OverrideTag` 的 `__init__`/`from_yaml`/`to_yaml` 与上游 `fd64dc2` 逐行等价（含 Mapping/Sequence/Scalar 三分支与空值回退）——`merge.py:51-86`：`__init__` 首分支 `isinstance(value, (dict, list))`、`from_yaml` 四分支（Mapping/Sequence/Scalar/兜底 `node.value`）、`to_yaml` 三分支（`represent_mapping`/`represent_sequence`/`represent_scalar(… or "")`）
- [x] `merge.py::rec_merge_one` 的「source 有、target 无」分支含 ResetTag/OverrideTag 处理，且双方均为 OverrideTag 时 source 优先——`merge.py:121-130`（ResetTag `log.info`+`continue`；OverrideTag 解包 `clone(value.value)`+`done.add`+`continue`）、`merge.py:151-155`（`clone(value2.value) if isinstance(value2, OverrideTag) else clone(value.value)`）
- [x] `normalize.py::rec_subs` 含 OverrideTag 分支与第 4 个 overload；`environment` 为 OverrideTag 时取 `.value` 参与短格式解析——`normalize.py:43/45/47/49` 四个 `@overload`、`normalize.py:78` `elif isinstance(value, OverrideTag)`
- [x] `normalize.py::normalize_service` 对 environment/labels 正确处理 ResetTag（跳过）与 OverrideTag（对 `.value` 规范化）——`normalize.py:208-216`
- [x] `normalize.py::normalize_service` 对 `volumes: null` 抛 `PodmanComposeError("ERROR: volumes must be a list")`——`normalize.py:196-200`
- [x] `translate/networks.py::get_net_args_from_networks` 第 2 处使用 `isinstance(is_ext, dict)`——`networks.py:233`
- [x] `runner.py::Podman.run` 含 `pass_stdin: bool = False`，三条子进程分支均传 `stdin=stdin_arg`（非 pass_stdin → PIPE）——`runner.py:170`（签名）、`:186`（`stdin_arg = None if pass_stdin else asyncio.subprocess.PIPE`，置于 `dry_run` 早返之后）、`:191`/`:217`/`:224`（三分支均传 `stdin=stdin_arg`）
- [x] `commands/runexec.py` 的 `compose_run`/`compose_exec` 均以 `pass_stdin=True` 调用——`runexec.py:65`、`runexec.py:91`
- [x] `translate/run_args.py::compose_exec_args` 按 `args.detach` 输出 `--detach`，且 `--tty` 条件为 `not args.detach and not args.T`——`run_args.py:151`、`run_args.py:158`
- [x] `cli/parser.py::parse_args` 含 `--wait-timeout` 非负校验、`up --wait` 互斥校验（` or ` 连接）与 `detach=True` 强制——`parser.py:847-866`（`:850` 非负校验、`:853-865` 互斥收集与 `", ".join(…) + " or " + last`、`:866` `global_args.detach = True`）
- [x] `translate/build.py::container_to_build_args` 三处构建校验改抛 `PodmanComposeError`——`build.py:58`、`:101`、`:102`（`:19` 已导入）
- [x] C11 注释清理（`by piping output through sed` 已移除，若原文件存在该注释）——实际落点 `logs.py:32` 与 `commands/updown.py:361`（非 spec 原写的 `commands/logs.py`），全仓已无该串残留

## B. 测试移植

- [x] `tests/test_override_environment.py` 已新增且覆盖 `!override` 环境变量合并——新增 267 行，11 个用例名与上游逐一对应（`setUp`/`tearDown` 增补 COMPOSE_* 快照隔离），实测 11 passed
- [x] `test_get_net_args.py` / `test_normalize_service.py` / `test_compose_exec_args.py` / `test_compose_up_args.py` / `test_container_to_build_args.py` 已移植上游增量——分别 +2 / +1（`test_volumes_none_raises`，与上游 L148-151 逐字一致）/ +`test_detach` / +6 wait 用例 / `assertRaises(OSError)` → `PodmanComposeError`；连带修正 `test_build_args_extra.py`、`test_run_args_extra.py`、`test_commands_build_updown.py`
- [x] `test_merge_extra.py` 中受 from_yaml/优先级变更影响的断言已同步——修正 4 处失效断言 + 新增 4 用例（`test_new_source_override_key_unwrapped`、`test_new_source_reset_key_skipped`、`test_both_override_source_wins`、`test_to_yaml_emits_tagged_mapping_and_sequence`）
- [x] 全量 `pytest tests/ -q` 全绿，无回归——WSL 权威门禁 965 passed / 79 subtests / 0 failed，覆盖率 92%（对照 2026-09-16 基线 940，差值 +25 恰为本次新增用例数）

## C. 对等证据

- [x] `docs/README.md` 的 pinned commit 为 `1f1cb09bfee4d79857ed23bfe2699febd7d20a53`——`docs/README.md:37`；`vendor 洁净` 行 HEAD 同步为 `1f1cb09`（`:76`）
- [x] `docs/parity/README.md`、`symbol-map.md`、`differences.md` 的锚定 commit 已同步——`symbol-map.md:3` 头部声明行号锚定 `1f1cb09`（全表重锚）、`parity/README.md:25/28/29/33`、`differences.md:8` 维护说明（M3/M4/M5 登记时点行号不重锚）与 `:32` D2 快照锚点说明
- [x] `docs/parity/upstream-quirks.md` 中「from_yaml 直接取 ScalarNode.value」条目已关闭/改写，新增条目（若有）带固化级别标注——`:35` 划删除线并注关闭理由；`:36-39` 新增 `fd64dc2` 三条语义变更登记，标注 `【L0】`
- [x] `docs/findings-ledger.md` 含本次同步记录（区间/提交映射/怪癖变更/遗留）——新增 `<a id="g-upstream-sync"></a>## G.`（区间 11 提交、提交→模块映射表、符号面、怪癖裁决、测试面、遗留项与环境事实）
- [x] `tests/snapshots/cli_parity.json` 与 `test_cli_parity.py`/`test_command_surface.py` 一致（无参数表变更，或已再生并登记）——快照锚点刻意停在 `e3df104`（本次增量无 argparse 参数增删，防篡改守卫 `test_cli_parity.py:38` 未动），实测 9 passed / 50 subtests

## D. 门禁与边界

- [x] `ruff check src tests` 零错误——`All checks passed!`（修复 `tests/test_override_environment.py` 末尾缺换行的 `W292` 后归零）
- [x] `mypy` 零新增告警——`Success: no issues found in 39 source files`
- [x] 链接检查与文件名规范校验通过——`check-links.py --path .`（cwd=docs）10 个 md / 125 个本地引用全绿、0 断链；`check-filename-convention.py --directory` 覆盖 docs 与子模块根均 0 违规
- [x] `vendor/podman-compose/` 零改动（`git status --porcelain` 为空）——实测 porcelain 输出为空，`HEAD=1f1cb09bfee4d79857ed23bfe2699febd7d20a53`
- [x] 未自动执行 `git commit`/`git push`；C 阶段提交建议已呈交用户待批——全程无任何 git 写操作
- [x] 未更新根仓库 `vendor/podman-compose`、`projects/xuanspace` gitlink 指针（留待用户指示）——根仓库 `git status --porcelain` 中二者虽显示 ` M`（源于上游 vendor 更新与本子项目未提交改动），但全程未执行 `git add`/`git commit`，指针未被提交更新