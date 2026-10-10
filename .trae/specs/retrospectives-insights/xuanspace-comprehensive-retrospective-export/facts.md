---
id: "xuanspace-comprehensive-retrospective-export-facts"
title: "xuanspace（玄境）全面复盘 R 阶段事实清单"
source: "git 记录与仓库文件实体（d:\\AI\\projects\\xuanspace 只读采集）"
methodology: "seven-concepts R 阶段"
content-sensitivity: public
---

# xuanspace（玄境）全面复盘 — R 阶段事实清单

> 采集对象：`d:\AI\projects\xuanspace`（第一方 git submodule，只读）
> 采集时间：2026-10-10
> 采集方式：全路径调用 `git.exe`（`D:\Program Files\Git\mingw64\bin\git.exe`）与文件系统读取
> 范围：本清单仅描述"是什么"，不含因果推断。

## A. 全量规模与节奏（2026-07-24 ~ 2026-10-10）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 仓库全量提交总数为 360 次 | 命令输出：`git rev-list --count HEAD` → `360` |
| F-002 | 提交日期范围为 2026-07-24 ~ 2026-10-10 | `git log --format=%ad --date=short` 首末项 |
| F-003 | 首提交为 `bb9ecce`，日期 2026-07-24，subject 为「feat: 初始化 Xuanspace（玄境）Python monorepo 项目」 | 命令输出：`git log --reverse --format="%h|%ad|%s" --date=short` 首行 |
| F-004 | 最新提交（HEAD）为 `587da1c`（完整 SHA `587da1cb283e5ffad9a326568287378ba74f27cd`），日期 2026-10-10 16:14:39 +0800，subject 为「test(xuan-compose): 加固 create_secrets 报错全文断言」 | 命令输出：`git log -1 --format="%H|%ad|%s" --date=iso` |
| F-005 | 当前分支为 `main` | 命令输出：`git rev-parse --abbrev-ref HEAD` → `main` |
| F-006 | 全量活跃日期数为 25 天 | 命令输出：`git log --format=%ad --date=short | Sort-Object -Unique` 计数 → `25` |
| F-007 | 峰值日期为 2026-07-31，当日 69 次提交 | 命令输出：`git log --format=%ad --date=short | Group-Object | Sort-Object Count -Descending` |
| F-008 | 次高峰日期依次为 2026-08-04（41 次）、2026-08-05（37 次）、2026-07-28（32 次）、2026-07-24（23 次）、2026-07-30（21 次）、2026-08-03（21 次）、2026-08-01（15 次） | 同上 |
| F-009 | 全量按月份分布：2026-07 = 168 次，2026-08 = 154 次，2026-09 = 33 次，2026-10 = 5 次 | 命令输出：`git log --format=%ad --date=format:"%Y-%m" | Group-Object` |
| F-010 | 2026-08-26 之后（增量口径）提交数为 38 次，占全量 360 次的 10.56%（38/360） | 命令输出：`git log --since=2026-08-26 --oneline` 计数 → `38`；占比为 38÷360 计算值 |
| F-011 | 截至 2026-08-19 提交数为 314 次；截至 2026-08-25 提交数为 322 次 | 命令输出：`git rev-list --count --until=2026-08-19T23:59:59 HEAD` → `314`；`--until=2026-08-25T23:59:59 HEAD` → `322` |
| F-012 | 全量作者分布：`Trae Agent` 253 次、`xinetzone` 107 次（合计 360） | 命令输出：`git log --format=%an | Group-Object` |

## B. 提交类型与 scope 分布

| 编号 | 事实 | 来源 |
|---|---|---|
| F-013 | 全量口径 type 分布：feat 93、test 63、fix 62、docs 58、chore 43、refactor 15、build 9、perf 9、ci 5、merge 1；另有 2 条 subject 不符合 `type(scope):` 前缀（1 条 `Merge branch ...`、1 条 `test+ci(caffe-ffi): ...`） | `git log --format=%s` 正则 `^(?<t>[a-z]+)(\(...\))?!?:` 分组统计 |
| F-014 | 增量口径（--since=2026-08-26，38 条）type 分布：docs 10、feat 9、build 7、chore 6、refactor 2、test 2、fix 1、merge 1 | `git log --since=2026-08-26 --format=%s` 正则分组统计 |
| F-015 | 增量口径 scope 分布：compose 13、xuan-compose 7、submodule 4、doctor 3、submodules 2、conf 1、doc 1、okf 1、readme 1、root 1、scripts 1、templates 1、xs 1、xuan-core 1 | `git log --since=2026-08-26 --format=%s` 提取 `type(scope)` 括号内容分组统计 |
| F-016 | 增量中 build 类型 7 条占增量 38 条的 18.4%（7/38）；全量中 build 类型 9 条占全量 360 条的 2.5%（9/360） | 由 F-013、F-014 数值计算 |

## C. 增量提交逐条清单（2026-08-26 之后，共 38 条）

来源：`git log --since=2026-08-26 --format="%h|%ad|%s" --date=short --reverse`

| 编号 | hash | 日期 | subject |
|---|---|---|---|
| F-017 | 89eedf5 | 2026-09-03 | chore(submodule): 新增 libs/mystx 子模块统筹 MystX Sphinx 主题与扩展共享库 |
| F-018 | e893b25 | 2026-09-03 | docs(conf): Xuanspace 文档新增 setup() 声明 parallel_read_safe=True + Fail-Fast 并行守卫钩子，配合 mystx submodule 更新落地 Sphinx 并行构建 P0 三项 [prevent: fail-fast-assertion] |
| F-019 | 4d4a6cd | 2026-09-03 | refactor(doc): 统一Sphinx文档目录名为doc/，规避与第三方工具的docs/路径约定冲突 |
| F-020 | 31c28b5 | 2026-09-04 | chore(submodule): 子模块 URL 协议从 HTTPS 切换为 SSH |
| F-021 | 9e39435 | 2026-09-04 | docs(readme): 修正 Python 版本徽章为 3.14+ |
| F-022 | 35e8b58 | 2026-09-04 | chore(submodule): 更新 libs/mystx 指针至 P1-A 审计落地提交 |
| F-023 | 98dcaa6 | 2026-09-04 | chore(submodule): 更新 libs/mystx 指针至并行构建环境分流提交 |
| F-024 | 7edfda0 | 2026-09-15 | feat(compose): 新增 xuan-compose 包脚手架，确立 GPL-2.0 对等重构基线 |
| F-025 | d2f9992 | 2026-09-15 | feat(compose): 迁入基础层 compat/types/interpolation 等六模块 |
| F-026 | aca51fa | 2026-09-15 | feat(compose): 迁入规范层 normalize/merge/discovery 三模块 |
| F-027 | cc6a49e | 2026-09-15 | feat(compose): 迁入执行层 runner/model/dependencies 及镜像拉取 |
| F-028 | 7ce078a | 2026-09-15 | feat(compose): 迁入翻译层 translate 子包完成服务描述到 podman 参数的对等翻译 |
| F-029 | 39c2538 | 2026-09-15 | feat(compose): 迁入引擎层 ComposeEngine 完成 compose 文件解析与引擎状态装配 |
| F-030 | 245f9ad | 2026-09-15 | feat(compose): 迁入命令层 24 个 handler 与显式注册表 |
| F-031 | 9d91a3e | 2026-09-15 | feat(compose): 迁入 CLI 层 parser/main 与 python -m 入口 |
| F-032 | 43f7812 | 2026-09-16 | test(compose): T9 全量对等门禁——argparse 快照零差异与覆盖率补齐 |
| F-033 | 1c40e44 | 2026-09-16 | docs(compose): T10 对等审计与文档收尾并去除重复依赖检查 |
| F-034 | 5f73292 | 2026-09-16 | refactor(compose): T11 对抗审查修复——下沉 resolve_extends 消除规范层环 |
| F-035 | 9a39ddf | 2026-09-16 | docs(compose): T11 独立对抗审查报告与 README 架构图校正 |
| F-036 | 8868a6d | 2026-09-16 | docs(compose): T1-T12 分层重构交付总结报告 |
| F-037 | 4b4c082 | 2026-09-16 | build(scripts): 纯 Python 包构建门禁双轨化并同步构建规范文档 |
| F-038 | 448d729 | 2026-09-16 | build(xuan-compose): 纯 Python 打包改用 wheel.cmake=false 产出通用 wheel |
| F-039 | dc3d365 | 2026-09-16 | docs(xuan-compose): 新增功能完整性七概念独立验证报告 |
| F-040 | 46b1601 | 2026-09-16 | build(templates): python 脚手架改用 wheel.cmake=false 纯 Python 模式 |
| F-041 | 0a64553 | 2026-09-16 | build(xuan-core): 纯 Python 打包改用 wheel.cmake=false 产出通用 wheel |
| F-042 | 20f2a33 | 2026-09-16 | build(xs): 纯 Python 打包改用 wheel.cmake=false 并清理 sdist 清单 |
| F-043 | e1213bf | 2026-09-16 | build(okf): 纯 Python 打包改用 wheel.cmake=false 并清理 sdist 清单 |
| F-044 | f293ed6 | 2026-09-16 | build(root): 枢纽包改用 wheel.cmake=false 去除根 CMake 占位 |
| F-045 | 94c565d | 2026-09-16 | chore(submodules): 前进 mystx 指针至 ninja/cmake 无效依赖清理提交 |
| F-046 | 401d51d | 2026-09-21 | chore(submodules): 同步tvm-ffi结构遍历与策略支持 |
| F-047 | ef18da7 | 2026-09-22 | feat(doctor): 新增子模块指针一致性检查 |
| F-048 | fc45aef | 2026-09-23 | fix(doctor): 修正 Sphinx 检查硬编码 docs/ 导致恒为跳过 |
| F-049 | 294772f | 2026-09-23 | merge(doctor): 合入 fix/doctor-sphinx-doc-path 分支 |
| F-050 | e4b2a74 | 2026-10-10 | docs(xuan-compose): 对等文档原子化为索引、台账与快照十文件 |
| F-051 | 8289395 | 2026-10-10 | docs(xuan-compose): 库内引用改指原子化文档新路径 |
| F-052 | dea3e6b | 2026-10-10 | docs(xuan-compose): 移除原子化前的四份长文档 |
| F-053 | 88e3ea7 | 2026-10-10 | docs(xuan-compose): 建立上游怪癖固化级别分级口径 |
| F-054 | 587da1c | 2026-10-10 | test(xuan-compose): 加固 create_secrets 报错全文断言 |

### 增量主题聚类

来源：对 F-017 ~ F-054 逐条按 subject 归类计数

| 编号 | 主题 | 提交数 | 代表 commit |
|---|---|---|---|
| F-055 | xuan-compose 分层重构交付（脚手架 + 七层迁入 + T9/T10/T11 + 验收/总结报告） | 14（7edfda0、d2f9992、aca51fa、cc6a49e、7ce078a、39c2538、245f9ad、9d91a3e、43f7812、1c40e44、5f73292、9a39ddf、8868a6d、dc3d365） | 7edfda0（脚手架/GPL 基线）、9d91a3e（CLI 层）、43f7812（T9 全量对等门禁） |
| F-056 | 纯 Python 打包门禁双轨化（wheel.cmake=false） | 7（4b4c082、448d729、46b1601、0a64553、20f2a33、e1213bf、f293ed6） | 4b4c082（双轨化）、f293ed6（枢纽包） |
| F-057 | 子模块指针与上游同步 | 6（89eedf5、31c28b5、35e8b58、98dcaa6、94c565d、401d51d） | 89eedf5（新增 libs/mystx）、401d51d（tvm-ffi） |
| F-058 | 2026-10-10 xuan-compose 对等文档原子化与上游怪癖分级 | 5（e4b2a74、8289395、dea3e6b、88e3ea7、587da1c） | e4b2a74（原子化十文件）、88e3ea7（怪癖分级口径） |
| F-059 | 文档与配置治理（doc/ 目录改名、conf 并行守卫、README 徽章） | 3（e893b25、4d4a6cd、9e39435） | 4d4a6cd（docs/→doc/）、e893b25（fail-fast 守卫） |
| F-060 | doctor 子系统（子模块指针检查 + Sphinx 路径修复） | 3（ef18da7、fc45aef、294772f） | ef18da7（子模块指针检查） |
| F-061 | 增量聚类合计核对：14 + 7 + 6 + 5 + 3 + 3 = 38 | 38 | 与 F-010 一致 |

### 增量每日分布

| 编号 | 事实 | 来源 |
|---|---|---|
| F-062 | 增量 38 条集中于 8 个活跃日期：2026-09-03（3）、09-04（4）、09-15（8）、09-16（14）、09-21（1）、09-22（1）、09-23（2）、10-10（5） | `git log --since=2026-08-26 --format=%ad --date=short | Group-Object` |
| F-063 | 增量区间内单日峰值日期为 2026-09-16（14 次）；次高为 2026-09-15（8 次） | 同 F-062 |
| F-064 | 增量覆盖区间中，2026-08-26 ~ 2026-09-02、09-05 ~ 09-14、09-17 ~ 09-20、09-24 ~ 2026-10-09 各时段无提交 | 由 F-062 活跃日期集合与区间对照 |

### 关键里程碑提交

| 编号 | 事实 | 来源 |
|---|---|---|
| F-065 | 里程碑提交 1：`7edfda0`（2026-09-15，「新增 xuan-compose 包脚手架，确立 GPL-2.0 对等重构基线」） | F-024 |
| F-066 | 里程碑提交 2：`9d91a3e`（2026-09-15，「迁入 CLI 层 parser/main 与 python -m 入口」，为分层迁入链末环） | F-031 |
| F-067 | 里程碑提交 3：`43f7812`（2026-09-16，「T9 全量对等门禁——argparse 快照零差异与覆盖率补齐」） | F-032 |
| F-068 | 里程碑提交 4：`88e3ea7`（2026-10-10，「建立上游怪癖固化级别分级口径」） | F-053 |
| F-069 | 里程碑提交 5：`587da1c`（2026-10-10，HEAD，「加固 create_secrets 报错全文断言」） | F-004 |

## D. 当前仓库状态

| 编号 | 事实 | 来源 |
|---|---|---|
| F-070 | 工作区非干净：`git status --porcelain` 输出 13 行，全部为 ` M`（已修改未暂存）状态 | 命令输出：`git status --porcelain` |
| F-071 | 13 个已修改文件全部位于 `libs/xuan-compose/`，含 8 个 src 文件（cli/parser.py、commands/runexec.py、commands/updown.py、logs.py、runner.py、translate/build.py、translate/networks.py、translate/run_args.py）与 5 个 tests 文件（test_commands_build_updown.py、test_compose_exec_args.py、test_compose_up_args.py、test_container_to_build_args.py、test_get_net_args.py） | 命令输出：`git status --porcelain` |
| F-072 | 未提交改动规模为 13 files changed，145 insertions(+)，14 deletions(-) | 命令输出：`git diff --stat` |
| F-073 | 暂存区为空（`git diff --cached --stat` 无输出）；无 stash 记录（`git stash list` 为空） | 命令输出：`git diff --cached --stat`、`git stash list` |
| F-128 | 复核时点（2026-10-10，Task 1 完成后立即复核）`git status --porcelain` 输出 20 行：19 行 ` M`（已修改未暂存）+ 1 行 `?? libs/xuan-compose/tests/test_override_environment.py`（未跟踪）；与 F-070 的 13 行不一致，表明该工作区处于并行会话持续写入状态，规模随时间变动 | 命令输出：`git status --porcelain`（复核） |
| F-129 | 本复盘任务对 `projects/xuanspace` 全程只读，未在该仓库写入任何文件；F-070 与 F-128 所列改动均归因于并行会话（`.trae/specs/sync-upstream-delta/`）的在途工作 | 本任务写入路径清单（仅 `.trae/specs/` 与本主仓库 `docs/`） |
| F-074 | `.gitmodules` 声明 4 个子模块：`vendor/tvm-ffi`（git@github.com:apache/tvm-ffi.git）、`libs/tvm-book`（git@github.com:xinetzone/tvm-book.git）、`vendor/caffe`（git@github.com:daoflows/caffe.git）、`libs/mystx`（git@github.com:xinetzone/mystx.git） | 文件 `projects/xuanspace/.gitmodules` |
| F-075 | `git submodule status` 显示 4 个子模块均已初始化（无 `-` 前缀）且指针无漂移（无 `+` 前缀）：libs/mystx @ ba6f0b1（v0.3.7-7）、libs/tvm-book @ 3ddcefe（v0.1.4-8）、vendor/caffe @ f938d88（heads/main）、vendor/tvm-ffi @ aef2d00（v0.1.14-26） | 命令输出：`git submodule status` |
| F-076 | 根 `pyproject.toml`：`version = "0.1.0"`、`requires-python = ">=3.14.6"`、build-backend = `scikit_build_core.build`（requires `scikit-build-core>=0.10`） | 文件 `projects/xuanspace/pyproject.toml` 第 2-11 行 |
| F-077 | 根 `pyproject.toml` 声明 `[tool.scikit-build.wheel] cmake = false` 与 `minimum-version = "0.10"` | 文件 `projects/xuanspace/pyproject.toml` 第 140-144 行 |
| F-078 | 根 `CHANGELOG.md` 最新条目为 `## [0.1.0] - 2026-07-23`（日期早于首提交 2026-07-24），含 Added 段 10 条 | 文件 `projects/xuanspace/CHANGELOG.md` 第 8-19 行 |
| F-079 | 根 `README.md` frontmatter 声明 `id: "xuanspace-readme"`、`version: "0.1.0"`、`x-toml-ref: ".meta/toml/README.toml"` | 文件 `projects/xuanspace/README.md` 第 1-5 行 |
| F-080 | 根 `README.md` 徽章声明 Python 3.14+、Build: CMake+Ninja、Docs: Sphinx+MyST | 文件 `projects/xuanspace/README.md` 第 11-13 行 |
| F-081 | `libs/xuan-core/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 文件 `projects/xuanspace/libs/xuan-core/pyproject.toml` 第 7、9 行 |
| F-082 | `libs/xuan-compose/pyproject.toml`：version 0.1.0、requires-python >=3.14（与其他 libs 的 >=3.14.6 不同） | 文件 `projects/xuanspace/libs/xuan-compose/pyproject.toml` 第 9、13 行 |
| F-083 | `libs/caffe-ffi/pyproject.toml`：version 1.2.0、requires-python >=3.14.6 | 文件 `projects/xuanspace/libs/caffe-ffi/pyproject.toml` 第 7、23 行 |
| F-084 | `libs/demo-ffi/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`libs/npu-ffi/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`libs/xuan-ext-demo/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 各 `pyproject.toml` 文件对应行 |
| F-085 | 子模块 `libs/tvm-book/pyproject.toml`：requires-python >=3.14；子模块 `libs/mystx/pyproject.toml`：requires-python >=3.14 | 文件 `projects/xuanspace/libs/tvm-book/pyproject.toml` 第 34 行、`projects/xuanspace/libs/mystx/pyproject.toml` 第 11 行 |
| F-086 | `tools/xs/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`tools/okf/pyproject.toml`：version 0.1.0（另含第 45 行 version 0.1.0）、requires-python >=3.14.6 | 文件 `projects/xuanspace/tools/xs/pyproject.toml` 第 7、10 行；`tools/okf/pyproject.toml` 第 7、10、45 行 |
| F-087 | `tools/templates/python/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`tools/templates/native/pyproject.toml`：version 0.1.0、requires-python >=3.14.6；`tools/templates/native-ffi/pyproject.toml`：version 0.1.0、requires-python >=3.14.6 | 各模板 `pyproject.toml` 文件对应行 |
| F-088 | 顶层目录（排除 `.git`）为：`.agents`、`.github`、`.meta`、`.mypy_cache`、`.pytest_cache`、`.ruff_cache`、`.trae`、`apps`、`attic`、`doc`、`libs`、`scripts`、`tests`、`tools`、`vendor` | 命令输出：`Get-ChildItem -Directory` |
| F-089 | `apps/` 内容仅为 `.gitkeep` 与 `README.md`（无实际应用子项目） | 命令输出：`Get-ChildItem apps` |
| F-090 | `libs/` 内容为 8 个条目：caffe-ffi、demo-ffi、mystx、npu-ffi、tvm-book、xuan-compose、xuan-core、xuan-ext-demo，另有 `.gitkeep`、`README.md`（其中 mystx、tvm-book 为子模块；其余 6 个为第一方库） | 命令输出：`Get-ChildItem libs` |
| F-091 | `tools/` 内容为 okf、templates、xs，另有 `.gitkeep`、`README.md` | 命令输出：`Get-ChildItem tools` |
| F-092 | `scripts/` 内容为 `.gitkeep`、`check_pyproject_style.py`、`README.md` | 命令输出：`Get-ChildItem scripts` |
| F-093 | `attic/` 内容仅为 `.gitkeep` 与 `README.md` | 命令输出：`Get-ChildItem attic` |
| F-094 | `tests/`（顶层）内容为 `__pycache__`、`__init__.py` 与 5 个测试文件：test_affected.py、test_config.py、test_discovery.py、test_doctor_sphinx.py、test_doctor_submodules.py | 命令输出：`Get-ChildItem tests` |
| F-095 | `doc/` 内容为 `_static`、`adr`、`cli`、`okf`、`user-guide` 目录，以及 conf.py、index.md、intro.md、architecture.md、build-system.md、contributing.md、dependency-report.md、quickstart.md、README.md、Makefile、make.bat、`.gitkeep` | 命令输出：`Get-ChildItem doc` |
| F-096 | 全仓 `pyproject.toml` 共 20 个（含 vendor 子系统与子模块内）：根、libs/{caffe-ffi,demo-ffi,mystx,npu-ffi,tvm-book,xuan-compose,xuan-core,xuan-ext-demo}、tools/{xs,okf}、tools/templates/{python,native,native-ffi}、vendor/tvm-ffi 及其中 3 个、vendor/caffe 及其中 2 个 | `Glob **/pyproject.toml` |
| F-097 | 仓库根存在文件：pyproject.toml、README.md、CONTRIBUTING.md、AGENTS.md、.gitmodules、.gitignore、CHANGELOG.md、LICENSE、CMakePresets.json、.gitattributes | `Glob projects/xuanspace/*` |

## E. 与既有复盘基线的对照事实

| 编号 | 事实 | 来源 |
|---|---|---|
| F-098 | 既有复盘报告 1（阶段一里程碑）：`d:\AI\docs\retrospective\reports\2026-08-25-xuanspace-milestone-retro.md`，存在；frontmatter 声明覆盖「第一阶段 2026-07-24 ~ 2026-08-19」、提交总数 314；该报告正文列「提交作者：Trae Agent 219 次、xinetzone 95 次」 | 文件 `docs/retrospective/reports/2026-08-25-xuanspace-milestone-retro.md` 第 1-27 行 |
| F-099 | 既有复盘报告 2（初始化阶段）：`d:\AI\docs\retrospective\reports\project-reports\retrospective-xuanspace-mono-repo-20260724\`（含 index.md、README.md、insight-extraction.md），存在；README 声明复盘日期 2026-07-24、项目周期 2026-07-20 ~ 2026-07-24、任务 20/20 | 文件 `.../retrospective-xuanspace-mono-repo-20260724/README.md` 第 1-12 行 |
| F-100 | 既有复盘报告 3（首次全量）：`d:\AI\docs\retrospective\reports\project-reports\retrospective-xuanspace-comprehensive-20260826\`（含 index.md、README.md、insight-extraction.md、pattern-verification-plan-dual-track-progressive.md），存在；README 声明 2026-07-24 ~ 2026-08-25、提交总数 322、活跃日期 17 天、峰值 07-31（69 次） | 文件 `.../retrospective-xuanspace-comprehensive-20260826/README.md` 第 1-26 行 |
| F-101 | 基线报告 3 所列全量 type 分布为 feat 84、test 62、fix 61、docs 48、chore 37、refactor 13、perf 9、ci 5、build 2、merge 1（合计 322） | 文件 `.../retrospective-xuanspace-comprehensive-20260826/README.md` 第 30-39 行 |
| F-102 | 本次增量区间为 2026-08-26 ~ 2026-10-10，增量 38 条；与基线报告 3（截至 2026-08-25 的 322 条）拼接后为全量 360 条 | 由 F-010、F-011 数值计算 |
| F-103 | 基线报告 1 所述一阶段提交数 314 经复核一致（`--until=2026-08-19T23:59:59` → 314）；基线报告 3 所述 322 经复核一致（`--until=2026-08-25T23:59:59` → 322） | 命令输出：`git rev-list --count --until=... HEAD` |

## F. 治理与规范资产事实

| 编号 | 事实 | 来源 |
|---|---|---|
| F-104 | `d:\AI\docs\retrospective\patterns\methodology-patterns\governance-strategy\` 下无任何 `.toml` 伴生文件 | `Glob` 该目录 `*.toml` → 无匹配 |
| F-105 | 该 governance-strategy 目录 `index.md` 第 17、136、146 行分别登记条目 `behavior-characterization-freeze`、`snapshot-parity-migration`、`submodule-directory-convention` | `Grep index.md` |
| F-106 | governance-strategy 目录存在文件 `snapshot-parity-migration.md`、`submodule-directory-convention.md`、`behavior-characterization-freeze.md`（另有 docs-as-product.md、three-tier-governance.md 等模式文档） | `Glob` 该目录 `*` |
| F-107 | `.trae/specs/xuan-compose-refactor/` 存在，含 spec.md 与 tasks.md；spec 标题为「xuan-compose：podman-compose 单体重构进 xuanspace/libs - 产品需求文档」，声明「七概念场景 3『重构优化』链路 I → F → A → V → C」、Session `sc-20260915-podman-compose-refactor` | 文件 `.trae/specs/xuan-compose-refactor/spec.md` 第 1-5 行 |
| F-108 | `.trae/specs/workspace-governance/xuanspace-mono-repo/` 存在，含 spec.md（frontmatter status: "draft"、id: "xuanspace-mono-repo-spec"、version: "1.4"）与 tasks.md、review.md | 文件 `.trae/specs/workspace-governance/xuanspace-mono-repo/spec.md` 第 1-7 行 |
| F-109 | `.trae/specs/workspace-governance/consolidate-xuanspace-governance/` 存在，含 spec.md（frontmatter status: "draft"、id: "consolidate-xuanspace-governance-spec"）、tasks.md、review.md；spec 标题为「xuanspace 治理加固 Spec」，其 `source` 字段为 `"../../.agents/docs/retrospective/2026-08-25-xuanspace-milestone-retro.md"` | 文件 `.trae/specs/workspace-governance/consolidate-xuanspace-governance/spec.md` 第 1-7 行 |
| F-110 | `.trae/specs/sync-upstream-delta/` 存在，含 spec.md、tasks.md、checklist.md；spec 标题为「xuan-compose 上游增量同步（e3df104 → 1f1cb09） - 产品需求文档」，声明「七概念场景 3『重构优化』轻量变体，链路 R → I → A → V → C」、Session `sc-20261010-sync-upstream-delta`，基线 `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`（v1.6.0）→ `1f1cb09bfee4d79857ed23bfe2699febd7d20a53`，区间含 11 个非合并提交 | 文件 `.trae/specs/sync-upstream-delta/spec.md` 第 1-10 行 |
| F-111 | `libs/xuan-compose/docs/` 在 HEAD 状态含 10 个文件：README.md、findings-ledger.md、parity/{README.md,differences.md,symbol-map.md,upstream-quirks.md}、delivery/2026-09-16-delivery-summary.md、verification/2026-09-16-full-parity-verification.md、review/2026-09-16-t11-adversarial-review.md、patterns/2026-09-16-refactor-patterns.md | `Glob libs/xuan-compose/docs/**/*`；`git show --stat e4b2a74`（列 10 files changed, 1063 insertions） |
| F-112 | `libs/xuan-compose/CHANGELOG.md` 声明本项目版本号独立于上游，重构切片 T1-T12 保持对 containers/podman-compose v1.6.0（commit `e3df10472e194ab6d547b5ad25542c5c79e1a5fb`）的行为对等；最新版本段为「0.1.0 — 初始分层重构（T1-T10）」 | 文件 `libs/xuan-compose/CHANGELOG.md` 第 1-8 行 |
| F-113 | `libs/xuan-compose/CHANGELOG.md` 记录 `__version__="1.6.0+xuan.1"`、容器标签 `1.6.0+xuan.1`、T9 门禁「上游 26 个单元测试文件全量移植（484 ≥ 478，skip=0）、覆盖率整体 91%」、T10「142 个上游公开符号 100% 映射」 | 文件 `libs/xuan-compose/CHANGELOG.md` 第 15-34 行 |
| F-114 | `libs/xuan-compose/docs/parity/upstream-quirks.md` 声明上游怪癖固化级别为 L0（精确断言）、L1（弱断言）、L2（注释固化）、L3（清单固化）四级，并逐条标注级别；文末含「T7 清单固化段（L2/L3）」 | 文件 `libs/xuan-compose/docs/parity/upstream-quirks.md` 第 1-63 行 |
| F-115 | `upstream-quirks.md` 文末登记条目「create_secrets 报错串第二个片段漏 f 前缀（2026-10-10 由 L1 补全文断言升级）【L0】」 | 文件 `libs/xuan-compose/docs/parity/upstream-quirks.md` 第 47 行 |
| F-116 | `upstream-quirks.md` 开篇声明「本项目有 10+ 次此类纠正」（指新写测试与上游行为冲突时按上游真实输出断言） | 文件 `libs/xuan-compose/docs/parity/upstream-quirks.md` 第 5 行 |

## G. 质量与工程实践事实

| 编号 | 事实 | 来源 |
|---|---|---|
| F-117 | 顶层 `tests/` 含 5 个 `test_*.py` 文件 | 命令输出：`Get-ChildItem tests -Filter test_*.py` 计数 → 5 |
| F-118 | 各 libs 子项目 `tests/` 下 `test_*.py` 文件数：caffe-ffi 104、demo-ffi 2、mystx 6、npu-ffi 7、tvm-book 0、xuan-compose 53 | 命令输出：逐目录 `Get-ChildItem -Recurse -Filter test_*.py` 计数 |
| F-119 | `tools/okf/` 含 19 个 `test_*.py`；`tools/xs/` 无 tests 目录 | 命令输出：`Get-ChildItem tools\okf\tests`、`tools\xs` 检查 |
| F-120 | 全仓（含 vendor）`test_*.py` 文件总数为 277；排除 `\vendor\` 后为 199 | 命令输出：`Get-ChildItem -Recurse -Filter test_*.py` 计数（含/排除 vendor） |
| F-121 | `.github/workflows/` 含 2 个文件：ci.yml、release.yml | 命令输出：`Get-ChildItem .github\workflows` |
| F-122 | `.agents/` 含子目录 checklists、prompts、protocols、rules、templates，以及 context-routing.md、global-core-rules.md、ONBOARDING.md、README.md、`.gitkeep` | 命令输出：`Get-ChildItem .agents` |
| F-123 | `.meta/toml/` 含 `AGENTS.toml`、`CONTRIBUTING.toml`、`README.toml`、`doc/dependency-report.toml` 与 `.gitkeep` | 命令输出：`Get-ChildItem .meta\toml -Recurse` |
| F-124 | 仓库根 `AGENTS.md` 声明「Xuanspace（玄境）是一个 Python 3.14.6+ monorepo 项目」，其「AI Agent 提交质量验收基线」表列：测试覆盖率核心模块 ≥90%/一般模块 ≥80%、每个 Bug 修复 ≥1 个防回归用例、每个新功能 ≥1 个测试、mypy 零新增告警、ruff check 零错误 | 文件 `projects/xuanspace/AGENTS.md` |
| F-125 | 仓库根存在 `.trae/` 目录（顶层目录清单中列出） | 命令输出：F-088 |
| F-126 | 根 `pyproject.toml` 的 pytest 配置 `testpaths = ["tests"]`；ruff 配置 `line-length = 120`、`target-version = "py314"`，exclude 含 vendor、libs/tvm-book、attic、.agents、tools/templates；mypy `python_version = "3.14"` | 文件 `projects/xuanspace/pyproject.toml` 第 146-194 行 |
| F-127 | 根 `pyproject.toml` 声明 `[tool.pdm.workspace]` packages 为 apps、libs、tools 三个来源 | 文件 `projects/xuanspace/pyproject.toml` 第 128-133 行 |

---

## 采集自检

- 采集命令均通过全路径 `D:\Program Files\Git\mingw64\bin\git.exe` 对 `d:\AI\projects\xuanspace` 以只读方式执行。
- 本文件为 R 阶段唯一写入文件（写入位置在主仓库 `.trae/specs/` 内，未触达 `projects/xuanspace`）。

## 附：AC-2 抽查取证表（2026-10-10 复核，命中率 12/12 = 100%）

| F 编号 | 事实要点 | 复核命令 / 文件 | 复核结果 | 结论 |
|---|---|---|---|---|
| F-001 | 全量 360 次 | `git rev-list --count HEAD` | `360` | 命中 |
| F-003 | 首提交 `bb9ecce` 2026-07-24 | `git log --reverse --format="%h\|%ad\|%s"` | `bb9ecce\|2026-07-24\|feat: 初始化 Xuanspace（玄境）Python monorepo 项目` | 命中 |
| F-004 | HEAD `587da1c` | `git log -1 --format="%H\|%ad\|%s"` | `587da1cb283e5ffad9a326568287378ba74f27cd\|2026-10-10 16:14:39 +0800\|test(xuan-compose): 加固 create_secrets 报错全文断言` | 命中 |
| F-006 | 活跃日期 25 天 | `git log --format=%ad --date=short` 去重计数 | `25` | 命中 |
| F-007 | 峰值 2026-07-31 = 69 次 | `Group-Object \| Sort-Object Count -Descending` | `2026-07-31\|69` | 命中 |
| F-008 | 次高峰 08-04=41、08-05=37 | 同上 | `2026-08-04\|41`、`2026-08-05\|37` | 命中 |
| F-010 | 增量 38 次 | `git log --since=2026-08-26 --oneline` 计数 | `38` | 命中 |
| F-012 | 作者 Trae Agent 253 / xinetzone 107 | `git log --format=%an \| Group-Object` | `Trae Agent\|253`、`xinetzone\|107` | 命中 |
| F-075 | 4 子模块已初始化且指针无漂移 | `git submodule status` | 4 行均无 `-`/`+` 前缀，指针与清单一致 | 命中 |
| F-078 | CHANGELOG 最新 `## [0.1.0] - 2026-07-23` | `Select-String CHANGELOG.md "^## \["` | 首条 `## [0.1.0] - 2026-07-23` | 命中 |
| F-082 | xuan-compose `requires-python >=3.14` | `Select-String libs/xuan-compose/pyproject.toml` | 第 13 行 `requires-python = ">=3.14"` | 命中 |
| F-104 | governance-strategy 无 `.toml` 伴生 | `Glob *.toml` | 计数 `0` | 命中 |