# 独立 Review — add-xmflow-cli-product

- **审查轮次**: R1（首轮）
- **审查日期**: 2026-10-10
- **审查人**: AI Agent（Task 13 独立 Review）
- **审查对象**: `spec.md`（status: approved）+ `tasks.md` Task 1–12 实施记录与取证
- **总体结论**: **通过**。8/8 AC 达成（6 条 rule 全 PASS、2 条 rubric 均 5/5 ≥ 阈值 4）；Task 1–12 的 29 条 TR 中 28 条全达成，TR-6.1 部分达成（故意污染验证未实跑，如实登记为发现 F-1，不冒充通过）；TR-13.1/13.2 由本 review 自身达成。建议关闭本 spec，F-1 列 NPU 真机补做项。

---

## 一、检查点（Checkpoints）

检查点编号规则：`CP-R*` 覆盖 `rule` 类 AC，`CP-U*` 覆盖 `rubric` 类 AC。每个检查点记录 R1 结果、覆盖的 TR 与证据落点（证据实体均已在 tasks.md 对应 Task 实施记录中归档，本 review 不重复粘贴输出原文）。

### rule 类

#### CP-R1 — AC-1 客户镜像定义唯一落点（`rule`）— **PASS**

- **覆盖 TR**: TR-12.2、TR-11.1、TR-2.1
- **R1 结果**:
  - TR-12.2：`git grep -l -E 'xmflow-release|Containerfile\.release|BUILDER_IMAGE=localhost/native-dev' -- 'apps'` 命中仅 `apps/containers/offline-delivery/.agents/CHANGELOG.md`（Task 11 新条目对 2026-10-09 收编来源的历史性陈述，属「历史条目除外」范畴）；client 侧零命中。全仓库口径（无 pathspec）命中 3 文件：本 spec 正文 `spec.md`/`tasks.md` + 该 CHANGELOG —— 命中集合只落在 `offline-delivery/`（历史条目与本 spec 正文除外）✓
  - Pass Condition：`apps/containers/client/overlays/native-dev/release/` 不存在（Task 12 经 `[System.IO.Directory]::Delete()` 清除空目录壳，`native-dev/` 仅保留 `builder/`、`docs/`、`scripts/`、`smoke/` 等无关内容）；`git status --porcelain` 干净（当前 main = origin/main = `cfc0c9150`）✓
  - TR-2.1：`bin/relpack -p xmflow-cli version` rc=0，四元组 `[info] 产品=xmflow-cli | 形态=none | 镜像=localhost/xmflow-cli:base-none | 版本=1.2.1.dev0` 打印无缺键报错 ✓
  - TR-11.1：产品登记落 docs 三处 + CHANGELOG（`docs/README.md` 16 处、`docs/00-overview.md` 4 处、`docs/01-quickstart.md` 7 处、CHANGELOG 新条目 L88–L108 与既有条目逐块同构），客户镜像定义唯一落点 `offline-delivery/` 成立 ✓

#### CP-R2 — AC-2 载荷阶段化（§9 红线不破）（`rule`）— **PASS**（附发现 F-1 部分达成登记）

- **覆盖 TR**: TR-3.1、TR-3.2、TR-3.3、TR-6.1、TR-6.2、TR-6.3、TR-4.2、TR-10.1
- **R1 结果**:
  - TR-3.1：对 `Containerfile.xmflow-cli` 精确 `grep -nE 'pip install [^|]*xmnn|xmnn==|xmnn\[|\.whl|COPY .*whl'` → rc=1 零命中；`COPY` 源仅 `deps.txt`/`scripts/`/`smoke/` 与 `--from=cpython`，无 wheel ✓
  - TR-3.2：`.dockerignore` 首条即 `**/*.whl`（另忽略 `wheels/`）；构建上下文 = 产品目录，`find . -type f` 实测无任何 `.whl`；Task 10 `build` rc=0（22 步全绿）补齐 `podman build` 上下文上传日志 ✓
  - TR-3.3（rubric，5/5）：Layer/LABEL/头注口径与 `Containerfile.xmnn-runtime` 同构（`org.specweave.*` 七个规范键、全部 RUN 显式 `/bin/bash -lc`、含引号逻辑固化为脚本）；两处有意偏离（Layer 顺序「deps.txt 先于 torch」、新增产品私有键 `org.specweave.cpython`）均在文件注释写明理由，符合 anchors-5「结构/LABEL/注释三者与本应用惯例同构」✓
  - TR-6.1（**部分达成，见 F-1**）：底座守卫两用户全绿已由 Task 10 `build` 22 步 rc=0 实跑覆盖（Containerfile Layer 4 root+xmnn 双跑命令，Task 6 已静态核实落盘路径）；但「误装 xmnn 故意污染验证」**未实跑**，不冒充通过 ✓（部分）
  - TR-6.2：三处同步闭环 —— Containerfile Layer 4 注释与守卫 docstring 逐字一致、骨架 README §8 清单（Task 7）与守卫测试断言项数（Task 9）均同源；项数刻意保持 6 / 10+pip check 与既有产品口径一致 ✓
  - TR-6.3（rubric，5/5）：断言对照表 12 项逐一映射 `_base_guards.py` 6 项与 `_runtime_smoke.py` 10 项，每项均有既有产品对应物，且新增 uid≠0 断言、`/workspace/temp` 写探针、deps 闭包模块导入三个 CLI 特有断言，满足 anchors-5 ✓
  - TR-4.2 / TR-10.1：客户侧派生（`payload/Dockerfile`）全程 `--no-index --no-deps`，Task 10 load 派生构建日志（STEP 1/8–8/8）无任何索引 URL；底座构建经 `PIP_MIRROR` 联网解析 `deps.txt` 属 NFR-3 修订后允许面 ✓
  - 反断言固化（Pass Condition）：`_base_guards.py` 第 6 项「载荷未安装」以代码固化（venv bin 无 `xmnn*`/`xmflow`、conda+venv 两 purelib 无 xmnn 前缀、`-I -P -c import xmnn` rc≠0 且 stderr 含 ModuleNotFoundError），非人工目视 ✓

#### CP-R3 — AC-3 离线交付链端到端（`rule`）— **PASS**

- **覆盖 TR**: TR-10.1、TR-10.2、TR-10.3、TR-4.1、TR-4.2、TR-4.3、TR-7.2、TR-2.1
- **R1 结果**:
  - TR-10.1：五步 `stage`→`deps`→`build`→`pack`→`smoke` 全部 rc=0（2026-10-10 Temp 工作副本实跑）；`release.json`（schema v2，块序 payload→image→archive）`payload.sha256`=`a3be2d895d3d…f20a4b45`、`archive.sha256`=`4654db7ec0e0…766521da` 按 §12 块定向读出，与 `sha256sum` 实测逐字一致，size_bytes 一致（payload wheel 177,617,215 B、归档 197,354,286 B）✓
  - TR-10.2：`guard_crlf_shebang` 位于 `cmd_pack` 第①位（`bin/relpack` L121），pack 链 rc=0 且归档产出即为守卫链上通过证据；新改 `payload/Dockerfile` 5,302 B 实测 CR=0；`gzip -t` 归档 rc=0（`GZIP_OK`）✓
  - TR-4.1：`bin/relpack -p xmflow-cli deps --write` → 20 项无条件依赖写入；`deps` 校验 rc=0「依赖集一致」；宿主 `unzip` 在位、`bsdtar` 缺失未触发 `[WARN]`，如实记录 ✓（Task 10 首跑 rc=0 实为「缺 unzip 跳过、不是通过」，`dnf install unzip` 后复跑 20 项一致——该纪律性更正已登记）
  - TR-4.2：客户侧派生构建以 `--no-index --no-deps` 装载荷成功（Task 10 load 日志），底座自身构建允许访问 `deps.txt` 所需索引（NFR-3 修订口径）✓
  - TR-4.3（rubric，5/5）：差异表逐条定位到 marker（`; extra == "..."` 被 §10 口径排除）、extras、平台轮子（`>=` 下界不 pin 与 aliyun 索引解析）原因并有处置结论；「双向闭合」逐名验证 `deps.txt` 闭包与原件 38 项闭包集合相等（除载荷 wheel）✓
  - TR-7.2：`./xmnnctl init → load → up → smoke → down` 全 rc=0 —— Task 7 记录时本机缺 podman-compose 如实登记 blocked；Task 10 Unblock 条件 3 解除（Fedora 43 仓库 `dnf install podman-compose` 1.5.0）后，smoke 第 3 轮全链绿：load 派生构建 STEP 1/8–8/8 COMMIT `localhost/xmflow-cli:1.2.1.dev0`、root 与 xmnn 双身份守卫各 `SUMMARY: 11 passed, 0 failed`、up 容器就绪、一次性容器 smoke 11/11 全绿、down 正常、日志无 `[ERR]` ✓（第 1 轮 `.env` 占位版本被 load 版本契约正确拦截、第 2 轮 site-packages 属主 Permission denied 根因定位并修复，均如实登记）
  - TR-2.1：四元组打印（见 CP-R1）✓

#### CP-R4 — AC-4 对外契约修订面收敛（`rule`）— **PASS**

- **覆盖 TR**: TR-5.1、TR-5.2、TR-5.3、TR-9.1
- **R1 结果**:
  - TR-5.3：`git diff --stat -- bin tests docs .agents` = 5 文件 +30/−11（`bin/relpack` +4/−1 为 FR-6 形态白名单下移的同一契约修订两编辑点：`FLAVORS_DEFAULT` 重命名 + `FLAVORS="${FLAVORS:-$FLAVORS_DEFAULT}"` 固化行；`check_enum` 两处调用点与 fail-fast 打印逐字未动）；`git diff --stat -- products bin/lib` **空输出** —— `bin/lib/common.sh` 零改动、`products/xmnn-runtime/**` 零改动 ✓
  - TR-5.1：未声明 `FLAVORS` 的产品（`xmnn-runtime`）回退路径行为逐字不变（`形态=cpu`、`base-cpu`、`xmnn-runtime-base-cpu.tar.gz`）；`TORCH_FLAVOR=none` → `[ERR ] 非法形态：none（白名单 cpu|cu130）` fail-fast ✓
  - TR-5.2：`xmflow-cli` 形态集 `none|cpu` 通过校验，`BASE_REF`/`ARCHIVE_BASE` 按形态正确拼装（`base-none`/`base-cpu`）；`--torch cu130` → 非法形态 fail-fast（先于 `require_podman`，daemon-free 验证成立）✓
  - TR-9.1：`xmnn-runtime` 既有断言语义仅做「字面量→registry 取值」等价迁移，语义零改动；pytest 全绿（见 CP-R5）✓
  - Pass Condition 复核：全程无第二处 CLI 契约改动（`bin/relpack.ps1` L24 未参数化属已知局限 F-5，改动它即构成违例，故不动）✓

#### CP-R5 — AC-6 多产品测试可复用（`rule`）— **PASS**

- **覆盖 TR**: TR-9.1、TR-9.2、TR-2.2
- **R1 结果**:
  - TR-9.1：通用不变量层 `--collect-only -q` 用例数与产品数成线性关系 —— 两真产品 `skeleton=102 = 2×50 + 2`，加假产品 `152 = 3×50 + 2`（+50/产品）；`test_relpack_cli.py=23` 不变，全量 `125→175`；实跑（本地盘副本含假产品）**159 passed, 16 skipped, 0 failed** ✓
  - TR-9.2：临时假产品 `products/fake-prod`（仅 `product.env` + 骨架清单，registry 无条目）—— 通用不变量层 37 项自动覆盖全部通过（无需改测试代码）、产品私有契约层 13 项显式 `pytest.skip`（不静默通过、不失败）；删除后 collect 复原 `125`、两真产品用例结果不变 ✓
  - TR-2.2：`load_product_env` 必需键校验（9 键齐全）在 TR-2.1 实跑中生效，Task 9 参数化后由通用不变量层按产品自动覆盖，归并裁定成立 ✓
  - skip 清单如实登记：`[13] fake-prod 无私有契约条目（显式 skip）` + `[3] xmflow-cli 无宿主端口面（port_preflight=False，显式 skip）` ✓

#### CP-R6 — AC-7 行尾与 shebang 守卫（`rule`）— **PASS**

- **覆盖 TR**: TR-10.2、TR-11.2、TR-7.1
- **R1 结果**:
  - TR-10.2：pack 链守卫通过、归档 `gzip -t` rc=0、全部新增文本 CR=0（见 CP-R3）✓
  - TR-11.2：`git check-attr -a` 对 `xmnnctl`/`xmnnctl.ps1`/`bin/relpack`/`bin/relpack.ps1` 四路径全部返回 `text: set` / `eol: lf`；依 NFR-5 控制脚本沿用 `xmnnctl` 名称，根 `.gitattributes` 未新增规则（实施中无新的无 `.sh` 后缀 CLI 出现）✓
  - TR-7.1：骨架不变量用例全绿 —— Task 7 静态取证（12 文件齐全、文本文件字节级 CR=0、零 `.py`、零 `../`、shebang `#!/usr/bin/env bash`、`pull_policy: never`、`.env.example` 恰两键含 `XMNN_VERSION`、两端命令面 8 命令同构）由 Task 9 pytest 实跑补齐（骨架不变量用例含 xmflow-cli 参数化实例在内全绿）✓

### rubric 类

#### CP-U1 — AC-5 客户契约文本无信息损失（`rubric`）— **PASS — 5/5**（阈值 ≥4）

- **覆盖 TR**: TR-8.1、TR-8.2、TR-12.1
- **R1 结果**:
  - TR-8.1（5/5）：逐节对照表（Task 8 实施记录 + Task 12 TR-12.1 扩展版）证原件 7 节全覆盖且可执行 —— ①镜像标签（旧名按 OQ-4 改写为 `base-none`/`base-cpu` 形态标签，`-torch` 选型判据保留）；②快速开始（双挂载点表逐字保留）；③模型组目录契约（近逐字保留，含 `config.toml` 六 target 枚举/`quantized_dtype`/`tune`/`device_ip`/`device_mount_dir`）；④常用命令（六子命令全覆盖）；⑤真机网络（逐字口径保留）；⑥镜像内容边界（齐全且回补「内置 LLVM 约 186 MB」「Nuitka 打包器」两处细节）；⑦FAQ（三条口径锚点全部在位：`--network host` 三处、temp uid 规避三方式齐备、`0x7F7F` 毒值判读保留且细化）✓
  - TR-8.2：`xmflow-release` 在 `offline-delivery/**` 全库检索 0 命中；README 命令示例镜像名/挂载路径与 `product.env`、`Containerfile.xmflow-cli` 实际骨架一致 ✓
  - TR-12.1：三文件内容去向对照表（Task 12 L293–L319）每处内容落到具体文件章节，无信息损失；SMB 缺失待定项经 git 三重证据（log/ls-files/stash 均空）核实为 FR-12 设计内删除非数据丢失，已关闭 ✓
  - 判定：满足 anchors-5「7 节全覆盖、命令可直接粘贴执行、标签与形态口径与最终实现一致」✓

#### CP-U2 — AC-8 提案质量（`rubric`）— **PASS — 5/5**（阈值 ≥4）

- **覆盖 TR**: TR-1.1、TR-1.2
- **R1 结果**:
  - TR-1.1：Open Questions 六条（OQ-1 至 OQ-6）全部「已裁定」且有裁定依据（人类批复记录 D3/D4 或条款引用），无未裁定残留 ✓
  - TR-1.2：定稿明确写出「底座不含 wheel、载荷只在 `payload/Dockerfile`」并与 §9 条款号对应（FR-3 ①② 与 FR-3b）✓
  - 冲突定位准确性：每项冲突给出条款级证据 —— `DIST_DIR` 三级上溯违反 §7 禁引用 `client/`（D2 取证）、双标签漂移（OQ-4）、wheelhouse 与底座-载荷分离红线冲突（OQ-3/FR-3b）✓
  - 替代方案比较：唯一契约修订面（FR-6 形态白名单下移）有替代方案与否决理由（OQ-2 否决 `base|torch` 命名、OQ-3 不引入 `python-build-standalone`）；形态集命名有判据（与 USAGE §1 两档客户实物一一对应）✓
  - 诚实度：不可验证项全部列入 Open Questions 并裁定；NFR-2 后半未达成、构建器最小等价替代、`relpack.ps1` 未参数化等局限均在实施记录如实登记，未见夸大 ✓
  - 批准门记录：spec.md status `approved`（人类批准门）+ 决策记录 D1–D5 ✓

---

## 二、TR-13.1 覆盖映射表（Evidence）

每条 AC 与 TR 均被至少一个检查点覆盖，无 Pending 证据残留（TR-6.1 部分达成项以发现 F-1 登记，非 Pending）。

| AC | 类型 | 覆盖检查点 | 结果 |
|----|------|-----------|------|
| AC-1 | rule | CP-R1 | PASS |
| AC-2 | rule | CP-R2 | PASS（附 F-1） |
| AC-3 | rule | CP-R3 | PASS |
| AC-4 | rule | CP-R4 | PASS |
| AC-5 | rubric ≥4 | CP-U1 | PASS 5/5 |
| AC-6 | rule | CP-R5 | PASS |
| AC-7 | rule | CP-R6 | PASS |
| AC-8 | rubric ≥4 | CP-U2 | PASS 5/5 |

| TR | 类型 | 覆盖检查点 | 结果 |
|----|------|-----------|------|
| TR-1.1 | rule | CP-U2 | 达成 |
| TR-1.2 | rule | CP-U2 | 达成 |
| TR-2.1 | rule | CP-R1、CP-R3 | 达成 |
| TR-2.2 | rule | CP-R5 | 达成（归并 Task 9 裁定） |
| TR-3.1 | rule | CP-R2 | 达成 |
| TR-3.2 | rule | CP-R2 | 达成（Task 10 补齐 build 上下文日志） |
| TR-3.3 | rubric | CP-R2 | 5/5 |
| TR-4.1 | rule | CP-R3 | 达成 |
| TR-4.2 | rule | CP-R2、CP-R3 | 达成（Task 10 派生构建补齐） |
| TR-4.3 | rubric | CP-R3 | 5/5 |
| TR-5.1 | rule | CP-R4 | 达成 |
| TR-5.2 | rule | CP-R4 | 达成 |
| TR-5.3 | rule | CP-R4 | 达成 |
| TR-6.1 | rule | CP-R2 | **部分达成**（双用户全绿已由 build 链覆盖；故意污染验证未实跑，见 F-1） |
| TR-6.2 | rule | CP-R2 | 达成 |
| TR-6.3 | rubric | CP-R2 | 5/5 |
| TR-7.1 | rule | CP-R6 | 达成（Task 9 补齐 pytest 实跑） |
| TR-7.2 | rule | CP-R3 | 达成（Task 10 Unblock 后 smoke 全链绿补齐） |
| TR-8.1 | rubric | CP-U1 | 5/5 |
| TR-8.2 | rule | CP-U1 | 达成 |
| TR-9.1 | rule | CP-R4、CP-R5 | 达成 |
| TR-9.2 | rule | CP-R5 | 达成 |
| TR-10.1 | rule | CP-R2、CP-R3 | 达成 |
| TR-10.2 | rule | CP-R3、CP-R6 | 达成 |
| TR-10.3 | rubric | CP-R3 | 5/5 |
| TR-11.1 | rule | CP-R1 | 达成 |
| TR-11.2 | rule | CP-R6 | 达成 |
| TR-12.1 | rule | CP-U1 | 达成 |
| TR-12.2 | rule | CP-R1 | 达成 |
| TR-13.1 | rule | 本映射表 | 达成（自证：上表全覆盖、无 Pending） |
| TR-13.2 | rubric | 结论段落 | 达成（见下节，5/5 ≥ 阈值 4） |

---

## 三、R1 结果汇总

| 检查点 | AC | 类型 | 结果 | 评分 |
|--------|----|------|------|------|
| CP-R1 | AC-1 | rule | PASS | — |
| CP-R2 | AC-2 | rule | PASS（附 F-1 部分达成登记） | — |
| CP-R3 | AC-3 | rule | PASS | — |
| CP-R4 | AC-4 | rule | PASS | — |
| CP-R5 | AC-6 | rule | PASS | — |
| CP-R6 | AC-7 | rule | PASS | — |
| CP-U1 | AC-5 | rubric | PASS | 5/5 |
| CP-U2 | AC-8 | rubric | PASS | 5/5 |

---

## 四、发现（Findings）

- **F-1（TR-6.1 部分达成）**：「误装 xmnn 故意污染验证」未实跑。底座守卫两用户全绿已由 Task 10 `build` 22 步 rc=0 实跑覆盖（Containerfile Layer 4 root+xmnn 双跑），但反断言在「误装 xmnn」时确实失败的故意污染验证依赖真机 podman 交互，本环境未执行。**建议**：NPU 真机补做一次故意污染验证（在底座 venv 内误装 xmnn 后跑 `_base_guards.py` 确认第 6 项按预期失败）。
- **F-2（spec 勘误，已登记）**：spec.md L44「三份原件均已入库跟踪」与 git 事实不符（assets/ 三文件从未入库，git log/ls-files/stash 三重证据为空）。spec 为已批准历史裁定文档，正文不回改，勘误事实已登记于 tasks.md Task 12「SMB 缺失处置核实」块。
- **F-3（NFR-2 后半未达成，如实登记）**：派生增量（经 bind-mount 改进后 ≈553 MB）与 §9 的 0.18 GB 量级不可比；归因已更新——可避免的架构残留已消除（`COPY` 层消减 ≈177 MB），剩余增量即 wheel 解包实体体量（`_libs` 内 libLLVM.so.22.1 200 MB 级），属载荷真实体量而非架构问题。改进方向（如进一步消减 wheel 实体）属交付契约变更，超出本 spec 范围，留待用户裁决。
- **F-4（构建器最小等价替代）**：Task 10 Stage 0 构建器为最小功能等价镜像（基底 `jupyter-podman-rootless`，含 Python 3.14.6 + `/opt/conda/ssl/cacert.pem`，即 `relocate-cpython.sh` 唯一输入），非完整 native-dev（无 LLVM/Nuitka 实体）。完整 native-dev 镜像与 CPU/GPU 形态验证仍须 NPU 真机执行。
- **F-5（已知局限）**：`bin/relpack.ps1` L24 `$Flavors = @('cpu','cu130')` 未参数化——改动它即构成第二处 CLI 契约改动（D3 禁止），故不动；Windows 侧 `xmflow-cli` 交付须用 WSL bash 版 `bin/relpack`。
- **F-6（blocked→解除的过程登记）**：TR-7.2 在 Task 7 记录时为 blocked（本机缺 podman-compose），经 Task 10 Unblock 条件 3 解除后由 smoke 全链绿补齐达成；过程如实登记，未以静态检查冒充端到端通过。
- **F-7（残留登记）**：`fake-prod/{release,scripts,smoke}` 与 `tests/__pycache__` 空目录壳因 IDE 文件监视器持有 SMB 目录句柄删除挂起（不含任何文件、git 不可见、不影响测试发现与结果，句柄释放后自动消失）。

---

## 五、TR-13.2 审查结论（Evidence = 本段落）

**结论：第二产品接入充分验证了当初抽应用的多产品假设，评级 5/5（阈值 ≥4，anchor 5 = 以改动面数据回答并给出第三产品接入建议）。**

**判断依据（改动面数据）**：

1. **假设的直接实验验证**：TR-9.2 假产品实验证明 FR-10 两层拆分成立 —— 通用不变量层对零登记的 `fake-prod` 自动覆盖 37 项且无需改测试代码，私有契约层显式 skip 不静默通过，删除后结果复原。这是「新增产品不必改测试」假设的可证伪实验，结论为成立。
2. **契约改动面收敛到最小**：`bin/relpack` 仅 +4/−1（FR-6 形态白名单下移的同一契约修订两编辑点），`bin/lib/common.sh` 零改动，`products/xmnn-runtime/**` 零改动，`tests/` 改动严格限定为 FR-6 三处形态字面量 + FR-10 参数化改造（`conftest.py` 55→111 行、`test_release_skeleton.py` 748→944 行两层重构，xmnn-runtime 断言仅字面量→registry 取值等价迁移）。AC-4 的 Pass Condition（出现任何第二处 CLI 契约改动即判不通过）复核通过。
3. **线性可扩展性**：collect 计数 `102 = 2×50 + 2` → `152 = 3×50 + 2`，通用不变量层用例数随产品目录数线性变化（+50/产品），符合 AC-6 的可观察判据。
4. **第二产品实际接入成本**：总改动面 = 6 文件（Task 5 契约修订）+ 2 tests 文件（Task 9 参数化）+ 新建产品目录（`products/xmflow-cli/` 12+ 文件）+ docs/CHANGELOG 登记；其中真正触及共享代码的仅 `bin/relpack` 两处编辑点。

**第三产品接入建议**（按本 spec 已验证的模式）：

1. 新建 `products/<name>/`：`product.env`（必需键 `PRODUCT`/`IMAGE_NAME`/`BASE_IMAGE`/`WHEEL_DIST` 等 9 键 + 可选键 `FLAVORS`）+ `Containerfile.<name>`（沿用底座/载荷两段定位与 `org.specweave.*` LABEL 惯例）+ `release/` 骨架（控制脚本沿用 `xmnnctl` 名称）+ `smoke/` 守卫（按模板 6/10 项）。
2. `bin/relpack` **零改动**（`FLAVORS` 可选键驱动，缺省回退 `cpu|cu130` 全局常量）。
3. `tests/` 仅需在 `PRODUCT_CONTRACTS` per-product registry 追加一条私有契约条目；通用不变量层自动覆盖，无需改测试代码。
4. `deps.txt` 经 `bin/relpack -p <name> deps --write` 生成；交付链五步与 smoke 按 Task 10 已验证口径执行。
5. 登记 docs 三处 + CHANGELOG 条目（Task 11 格式）。
6. 预计改动面：0 处 CLI 契约 + 1 处 registry 条目 + 产品目录新建 + 治理文档登记。

**剩余风险**（诚实登记）：第三产品若含网络端口面或凭证面，需在 registry 中显式声明 `port_preflight` 等私有契约键；若控制逻辑出现第三次复制（现为两份骨架并存），须先抽公共再取第三产品（Task 7 Notes 已预警）。

---

*R1 审查完成。审查证据实体（命令输出、release.json、归档 sha256、pytest 输出、对照表）均归档于 tasks.md Task 1–12 实施记录，本 review 以指针引用，不重复粘贴。*
