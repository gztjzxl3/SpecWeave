#!/usr/bin/env python3
"""xmflow-cli 底座镜像守卫（构建期 root + xmnn 双跑 / 镜像内可复跑）。

底座 != 载荷（§9 承诺，与 xmnn-runtime 同构）：
  - 底座镜像（localhost/xmflow-cli:base-<形态>）只承载可重定位最小 CPython 3.14
    （/opt/conda，裸解释器、无载荷痕迹）+ 隔离 venv（/opt/xmflow：deps.txt 依赖面
    + torch 前端，形态可选 none|cpu）；
  - 底座**绝不**安装载荷 wheel：载荷（xmnn 分发包，内含 xmflow console_script）
    由交付侧派生时装入（release/payload/Dockerfile，`pip install --no-index
    --no-deps`），随即由随底座保留的载荷守卫 _runtime_smoke.py 验证；
  - 故本守卫的两条主线是：正向断言依赖面齐全（§2/§3）+ 反向断言载荷未混入（§6）。
    少了反向断言，"底座里混进 whl" 这类错版只会在交付侧派生时以「依赖被
    --no-deps 掩盖」的形式静默通过，故必须在此硬失败。

检查项（任一 FAIL 最终 exit 1，镜像构建失败；项数对齐 §11 骨架 6 项，与
Containerfile Layer 4 注释、release/README 清单逐字一致）：
  1. 可重定位解释器与 venv ABI：/opt/conda = cp314 GIL（relocated，prefix 正确、
     报告 GIL enabled）；/opt/xmflow = 由其派生的 venv（pyvenv.cfg 在、prefix
     正确）；venv 可导入 stdlib 关键扩展（FR-7 清单：ssl/ctypes/sqlite3/lzma/
     bz2/zlib/decimal/pyexpat/venv）——可重定位性破坏（lib-dynload 缺失、
     rpath 断裂）最先在这一项现形
  2. deps.txt 每条 Requirement 的发行版已在 venv 安装
  3. /opt/xmflow/bin/python -m pip check 无冲突（venv 依赖面全由 deps.txt 铺成，
     无基镜像元数据债务；若真机观测到系统元数据债务，须按 §11 补放行模式并
     同步三处，见 _ALLOWED_PREEXISTING_CONFLICTS）
  4. torch 形态与实物一致（marker ∈ none|cpu vs import 与 version.cuda；
     本产品无 CUDA 形态——交付 §4 P0 禁止 GPU 栈进客户镜像）
  5. 非 root（xmnn）身份可用：venv 可执行、deps.txt 可读、/workspace/temp 可写
     （root 轮以 su xmnn 子进程验证该维度；xmnn 轮自验——Layer 4 的整守卫 xmnn
     复跑已覆盖「同一清单双身份全绿」）
  6. 反断言：载荷未安装——两个解释器的 site-packages 无 xmnn* 残留、venv bin 无
     xmnn*/xmflow 脚本、`import xmnn` 必须失败且为 ModuleNotFoundError
"""

import json
import os
import re
import subprocess
import sys

PASS = 0
FAIL = 0

# ABI 契约（Containerfile 头注，不可互换）：/opt/conda = 可重定位裸 CPython
# （cp314 GIL，可执行名为 python3.14，Layer 1 即用它建 venv）；/opt/xmflow =
# 由其派生的隔离 venv = 依赖面 + torch + 载荷安装目标。
_CONDA_PYTHON = "/opt/conda/bin/python3.14"
_VENV_PYTHON = "/opt/xmflow/bin/python"
_VENV_PYVENV_CFG = "/opt/xmflow/pyvenv.cfg"
# 载荷 console_script 落点（由载荷 wheel 的 entry_points 提供；底座期不得存在）。
_CONSOLE_SCRIPT = "/opt/xmflow/bin/xmflow"
# 客户数据契约落点（Layer 1 chown xmnn；运行期 bind 挂载写权限以宿主目录属主
# 为准，见 release/README）。
_WORKSPACE_MODELS = "/workspace/models"
_WORKSPACE_TEMP = "/workspace/temp"
# 形态标记由 scripts/install-torch.sh 写入（printf '%s'，恒非空：none 或 cpu）；
# 守卫读 marker 而非 LABEL（镜像内运行时读不到 LABEL），据此断言「声明形态==实物」。
_TORCH_FLAVOR_MARKER = "/opt/xmflow-torch-flavor"
# 与 Containerfile ARG TORCH_VERSION 对齐（仅校验主版本一致，补丁号以实物为准）
_EXPECTED_TORCH_MAJOR = "2."
# 底座依赖清单：Layer 2 安装后留在镜像内（供本守卫核验与镜像内溯源）。
# 可用环境变量覆盖，便于对任意清单复跑。
_DEPS_FILE = os.environ.get("XMFLOW_DEPS_FILE", "/opt/xmflow-smoke/deps.txt")
# 载荷痕迹前缀：site-packages 内以此开头的条目都算残留
# （xmnn 包目录 / xmnn-*.dist-info / xmnn_bootstrap.pth）。
_PAYLOAD_PREFIX = "xmnn"

# FR-7 明列的可重定位性冒烟清单：venv 能导入这些 stdlib 扩展模块，即证明
# lib-dynload/共享库随前缀搬迁完好——可重定位 CPython 最典型的破坏形态就是
# 扩展模块加载失败，而非解释器本身起不来。
_STDLIB_EXTENSIONS = (
    "ssl",
    "ctypes",
    "sqlite3",
    "lzma",
    "bz2",
    "zlib",
    "decimal",
    "pyexpat",
    "venv",
)

# 已知债务放行族：**空**。venv 的依赖面全部由 deps.txt 铺成（Layer 2 全新
# `pip install`），不存在 xmnn-runtime 基镜像那种 conda 元数据既有冲突。
# 机制刻意保留（与 xmnn-runtime 底座守卫同构）：若真机观测到系统级元数据债务
# （例如 ubuntu 自带 pip 元数据报出的冲突行），必须在此补收窄的正则模式，并
# 按 §11 同步守卫测试、骨架 README、docs/ 三处——而不是放开整项检查。
_ALLOWED_PREEXISTING_CONFLICTS: tuple = ()

# 子进程 + `-S -c` 探测解释器事实：`-S` 跳过 site 导入，隔离 .pth 注入
# （载荷 bootstrap 会改 sys.path，必须在不加载它的前提下取 ABI 事实），
# `-c` 保证不落地临时文件——与 _runtime_smoke.py 的 ABI 断言手法一致。
_ABI_PROBE = (
    "import json, sys, sysconfig;"
    "print(json.dumps({"
    "'exe': sys.executable,"
    "'version': sys.version.split()[0],"
    "'gil_disabled': sysconfig.get_config_var('Py_GIL_DISABLED'),"
    "'gil_enabled': sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else None,"
    "'prefix': sys.prefix,"
    "'purelib': sysconfig.get_paths()['purelib']}))"
)

# `-I` 隔离（忽略 PYTHONPATH / 用户 site），仍正常导入 site，故能读到
# venv 的 dist-info——用于核验 deps.txt，与守卫自身运行身份无关。
_VERSIONS_PROBE = "\n".join(
    [
        "import importlib.metadata as md",
        "import json, sys",
        "out = {}",
        "for name in json.load(sys.stdin):",
        "    try:",
        "        out[name] = md.version(name)",
        "    except md.PackageNotFoundError:",
        "        out[name] = None",
        "print(json.dumps(out))",
    ]
)

# stdlib 扩展逐个 import 的合并探测（单进程跑完全部清单，失败只记录不中断，
# 由调用方汇总断言）；同样以 `-I` 运行，排除 PYTHONPATH 注入的假阳性。
_STDLIB_IMPORTS_PROBE = "\n".join(
    [
        "import importlib, json, sys",
        "out = {}",
        "for name in json.load(sys.stdin):",
        "    try:",
        "        importlib.import_module(name)",
        "        out[name] = 'ok'",
        "    except Exception as exc:",
        "        out[name] = f'{type(exc).__name__}: {exc}'",
        "print(json.dumps(out))",
    ]
)


def check(name: str, fn) -> None:
    global PASS, FAIL
    print(f"─── Test: {name}")
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - 守卫需要逐项跑完并汇总
        print(f"  [FAIL] {type(exc).__name__}: {exc}")
        FAIL += 1
    else:
        print("  [OK]")
        PASS += 1
    print("")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _probe(python: str) -> dict:
    """子进程探测解释器事实（不导入 site，避免载荷 .pth 干扰）。"""
    out = subprocess.run(
        [python, "-S", "-c", _ABI_PROBE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    _assert(
        out.returncode == 0,
        f"解释器探测失败 {python}: {out.stderr.strip()}",
    )
    return json.loads(out.stdout.strip().splitlines()[-1])


def _whoami() -> str:
    try:
        import pwd

        return pwd.getpwuid(os.geteuid()).pw_name
    except Exception:  # noqa: BLE001 - 仅用于日志标签
        return str(os.geteuid())


def _requirement_name(line: str) -> str:
    """取 Requirement 文本的发行版名（处理 >=/==/[extra] 等写法）。

    名称必为行首连续匹配 `[A-Za-z0-9._-]` 的片段，其后紧跟版本区间、extras
    或 marker 分隔符；故 `numpy>=1.26` → `numpy`、`Pillow>=10.0` → `Pillow`、
    `typing_extensions>=4.8` → `typing_extensions`、`foo[extra]>=1.0` → `foo`、
    `foo == 1.0` → `foo`。
    """
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line.strip())
    _assert(match is not None, f"无法从清单行解析依赖名: {line!r}")
    return match.group(0)


def _read_deps() -> list:
    """读 deps.txt，返回去重后的发行版名清单（保持文件顺序）。"""
    _assert(os.path.isfile(_DEPS_FILE), f"底座依赖清单缺失: {_DEPS_FILE}")
    names = []
    seen = set()
    with open(_DEPS_FILE, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            name = _requirement_name(line)
            key = name.lower().replace("_", "-").replace(".", "-")
            if key in seen:
                continue
            seen.add(key)
            names.append(name)
    _assert(bool(names), f"底座依赖清单为空: {_DEPS_FILE}")
    return names


def _is_allowed_conflict(line: str) -> bool:
    return any(pattern.match(line) for pattern in _ALLOWED_PREEXISTING_CONFLICTS)


def test_relocated_interpreter() -> None:
    """§1 可重定位解释器 + venv ABI + stdlib 关键扩展（FR-7 清单）。"""
    conda = _probe(_CONDA_PYTHON)
    print(f"  conda: {conda['exe']} -> Python {conda['version']}, prefix={conda['prefix']}")
    print(
        f"  conda: Py_GIL_DISABLED={conda['gil_disabled']}, "
        f"_is_gil_enabled()={conda['gil_enabled']}"
    )
    _assert(conda["prefix"] == "/opt/conda", f"裸解释器前缀异常: {conda['prefix']}")
    _assert(
        conda["version"].startswith("3.14"),
        f"裸解释器必须是 Python 3.14（载荷 Requires-Python 下限）: {conda['version']}",
    )
    _assert(
        conda["gil_disabled"] in (0, None),
        "必须是 cp314 GIL ABI（载荷 wheel tag 为 cp314-cp314，venv 继承自它）",
    )
    _assert(conda["gil_enabled"] is True, "cp314 GIL 解释器应报告 GIL enabled")

    venv = _probe(_VENV_PYTHON)
    print(f"  venv : {venv['exe']} -> Python {venv['version']}, prefix={venv['prefix']}")
    _assert(venv["prefix"] == "/opt/xmflow", f"venv 前缀异常: {venv['prefix']}")
    _assert(
        venv["version"].startswith("3.14"),
        f"venv 必须是 Python 3.14: {venv['version']}",
    )
    _assert(
        os.path.isfile(_VENV_PYVENV_CFG),
        f"venv 结构不完整（缺 {_VENV_PYVENV_CFG}，前缀搬迁会静默指回宿主）",
    )

    out = subprocess.run(
        [_VENV_PYTHON, "-I", "-c", _STDLIB_IMPORTS_PROBE],
        input=json.dumps(list(_STDLIB_EXTENSIONS)),
        capture_output=True,
        text=True,
        timeout=120,
    )
    _assert(out.returncode == 0, f"stdlib 扩展探测进程失败: {out.stderr.strip()}")
    results = json.loads(out.stdout.strip().splitlines()[-1])
    failed = {name: err for name, err in results.items() if err != "ok"}
    for name in _STDLIB_EXTENSIONS:
        print(f"  {'[OK]  ' if results.get(name) == 'ok' else '[FAIL]'} import {name}"
              f"{'' if results.get(name) == 'ok' else ' -> ' + str(results.get(name))}")
    _assert(
        not failed,
        f"stdlib 关键扩展不可导入（可重定位性破坏，lib-dynload/rpath 异常）: {failed}",
    )


def test_deps_installed() -> None:
    """§2 deps.txt 逐条核验：wheel 声明的无条件运行时依赖必须全部已装进 venv。"""
    names = _read_deps()
    print(f"  manifest {_DEPS_FILE}: {len(names)} requirements")
    out = subprocess.run(
        [_VENV_PYTHON, "-I", "-c", _VERSIONS_PROBE],
        input=json.dumps(names),
        capture_output=True,
        text=True,
        timeout=120,
    )
    _assert(out.returncode == 0, f"依赖版本查询失败: {out.stderr.strip()}")
    versions = json.loads(out.stdout.strip().splitlines()[-1])

    missing = []
    for name in names:
        version = versions.get(name)
        print(f"  {'[OK]  ' if version else '[MISS]'} {name} -> {version or '<not installed>'}")
        if not version:
            missing.append(name)
    _assert(not missing, f"deps.txt 中未安装的发行版（底座依赖面不完整）: {missing}")


def test_pip_check() -> None:
    """§3 依赖区间自洽：venv 依赖面由 deps.txt 全量铺成，不得报告任何冲突。

    与 xmnn-runtime 底座守卫的**不对称点**在放行族为空（见常量注释）：本镜像
    基座是公共 ubuntu + 全新 venv，没有 conda 元数据既有债务，所以此处按
    「全部冲突行阻断」收口——venv 是干净的，就没有需要放行的东西。
    """
    out = subprocess.run(
        [_VENV_PYTHON, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    lines = [line.strip() for line in out.stdout.splitlines()
             if line.strip() and "No broken requirements found" not in line]
    allowed = [line for line in lines if _is_allowed_conflict(line)]
    blocking = [line for line in lines if not _is_allowed_conflict(line)]
    print(f"  pip check exit={out.returncode}, {len(lines)} line(s)")
    for line in allowed:
        print(f"  [INFO] 已知既有债务（放行）: {line}")
    for line in blocking:
        print(f"  [CONFLICT] {line}")
    if not lines:
        print("  no broken requirements found")
    _assert(
        out.returncode == 0 or bool(lines),
        f"pip check 非零退出且无诊断输出 ({out.returncode}): {out.stderr.strip()}",
    )
    _assert(
        not blocking,
        f"pip check 报告冲突（venv 依赖面不自洽，放行族为空即全量阻断）: {blocking}",
    )


def test_torch_flavor_build() -> None:
    """§4 形态契约：marker 声明什么形态，实物就必须是什么形态（none|cpu 双态）。

    判据是**声明 vs 实物**的一致性：marker（install-torch.sh 以 printf '%s' 落盘，
    恒非空）↔ 实际 import 与 version.cuda。本产品刻意**没有** cu130 分支——
    交付 §4 P0 禁止 GPU 栈进客户镜像，marker 出现任何其他取值即视为构建违规。
    """
    flavor = "<missing>"
    try:
        with open(_TORCH_FLAVOR_MARKER, encoding="utf-8") as fh:
            flavor = fh.read().strip()
    except OSError:
        pass
    print(f"  marker {_TORCH_FLAVOR_MARKER} = {flavor!r}")
    _assert(
        flavor in ("none", "cpu"),
        f"torch 形态标记异常（应存在且 ∈ none|cpu，由 install-torch.sh 落盘）: {flavor!r}",
    )

    if flavor == "none":
        try:
            import torch  # noqa: F401
        except ImportError:
            print("  形态 none（不装 torch）：venv 内无 torch")
            return
        raise AssertionError("形态声明为 none（不装 torch），但 venv 内可 import torch")

    import torch

    version = torch.__version__
    print(f"  torch.__version__ = {version}")
    print(f"  torch.version.cuda = {torch.version.cuda}")
    _assert(version.startswith(_EXPECTED_TORCH_MAJOR), f"torch 主版本异常: {version}")
    _assert(
        torch.version.cuda is None,
        f"cpu 形态必须是 CPU 构建（torch.version.cuda 应为 None），实际 {torch.version.cuda}",
    )
    _assert(torch.cuda.is_available() is False, "CPU 镜像不应报告 CUDA 可用")
    # pytorch 前端 compile_api 依赖 torch.jit.load；确认 TorchScript 子模块在
    _assert(hasattr(torch, "jit") and hasattr(torch.jit, "load"), "torch.jit.load 不可用")
    # 轻量功能探针：张量算子走 CPU 正常
    x = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    _assert(float(x.sum()) == 15.0, "torch CPU 张量算子异常")
    print("  CPU build OK（jit.load 可用、张量算子通过）")


def test_nonroot_identity() -> None:
    """§5 非 root（xmnn）身份可用：venv 可执行 / deps.txt 可读 / temp 可写。

    §11 骨架的「双可见」维度在本产品对应 CLI 身份面（无 Jupyter 内核）：底座
    镜像 USER xmnn、交付运行也以 xmnn 进行，故依赖面必须对非 root 完整可用。
    root 轮以 `su xmnn` 子进程验证该维度；xmnn 轮（Layer 4 的第二次整守卫复跑）
    走自验分支。bind 挂载后 /workspace/temp 写权限以宿主目录属主为准——构建期
    可写不代表运行期可写，运行期契约见 release/README 的挂载说明。
    """
    _assert(
        os.path.isdir(_WORKSPACE_MODELS) and os.path.isdir(_WORKSPACE_TEMP),
        f"客户数据契约目录缺失（{_WORKSPACE_MODELS} / {_WORKSPACE_TEMP}）",
    )
    if os.geteuid() == 0:
        script = (
            "set -e ; id -u ; "
            f"{_VENV_PYTHON} -I -c 'import ssl' ; "
            f"head -c 1 {_DEPS_FILE} > /dev/null ; "
            f"touch {_WORKSPACE_TEMP}/.xmflow-base-guard-probe ; "
            f"rm -f {_WORKSPACE_TEMP}/.xmflow-base-guard-probe"
        )
        out = subprocess.run(
            ["su", "-s", "/bin/bash", "xmnn", "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
        )
        _assert(
            out.returncode == 0,
            f"su xmnn 身份验证失败 rc={out.returncode}: {out.stderr.strip()}",
        )
        uid = out.stdout.strip().splitlines()[0]
        _assert(uid != "0", f"su xmnn 仍报告 uid=0（身份切换未生效）: {uid}")
        print(
            f"  su xmnn (uid={uid}): venv 可执行 / deps.txt 可读 / {_WORKSPACE_TEMP} 可写"
        )
        print("  [INFO] root 轮：整守卫的 xmnn 全量复跑由 Containerfile Layer 4 su 命令执行")
    else:
        me = _whoami()
        _assert(os.access(_VENV_PYTHON, os.X_OK), f"身份 {me} 无法执行 venv 解释器")
        _assert(os.access(_DEPS_FILE, os.R_OK), f"身份 {me} 无法读取依赖清单 {_DEPS_FILE}")
        probe = os.path.join(_WORKSPACE_TEMP, f".xmflow-guard-{os.getpid()}.probe")
        try:
            with open(probe, "w", encoding="utf-8"):
                pass
        finally:
            if os.path.exists(probe):
                os.remove(probe)
        print(
            f"  身份 {me} (uid={os.geteuid()}): venv 可执行 / deps.txt 可读 / "
            f"{_WORKSPACE_TEMP} 可写"
        )


def test_payload_absent() -> None:
    """§6 反断言（关键）：底座内不得有任何载荷（xmnn wheel）痕迹。

    venv 的 site-packages 无 xmnn* 条目、bin 目录无 xmnn* / xmflow 脚本、两个
    解释器 `import xmnn` 均以 ModuleNotFoundError 失败。载荷由交付侧派生安装
    （--no-index --no-deps）；底座若混入载荷，会绕过依赖解析并让「底座可复用」
    的定位失效。
    """
    venv_bin = os.path.dirname(_VENV_PYTHON)
    leftover_bin = sorted(
        entry
        for entry in os.listdir(venv_bin)
        if entry.lower().startswith(_PAYLOAD_PREFIX) or entry == "xmflow"
    )
    print(f"  {venv_bin} xmnn*/xmflow entries: {leftover_bin}")
    _assert(
        not leftover_bin,
        f"venv bin 残留载荷脚本（底座期不得安装载荷）: {leftover_bin}",
    )
    _assert(
        not os.path.exists(_CONSOLE_SCRIPT),
        f"载荷 console script 已出现在底座: {_CONSOLE_SCRIPT}",
    )

    for label, python in (("conda", _CONDA_PYTHON), ("venv", _VENV_PYTHON)):
        purelib = _probe(python)["purelib"]
        if os.path.isdir(purelib):
            leftover = sorted(
                entry for entry in os.listdir(purelib) if entry.lower().startswith(_PAYLOAD_PREFIX)
            )
        else:
            leftover = []
        print(f"  [{label}] {purelib} xmnn* entries: {leftover}")
        _assert(
            not leftover,
            f"[{label}] site-packages 残留载荷痕迹（应为纯底座）: {leftover}",
        )

        out = subprocess.run(
            [python, "-I", "-P", "-c", "import xmnn"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        detail = out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "<no stderr>"
        print(f"  [{label}] python -I -P -c 'import xmnn' -> exit {out.returncode}: {detail}")
        _assert(
            out.returncode != 0,
            f"[{label}] 载荷 xmnn 已混入底座镜像（import 成功，应为未安装状态）",
        )
        _assert(
            "ModuleNotFoundError" in out.stderr,
            f"[{label}] import xmnn 失败但非 ModuleNotFoundError: {out.stderr.strip()}",
        )


def main() -> int:
    print("==========================================")
    print("  XMFLOW-CLI BASE GUARDS (no payload)")
    print("==========================================")
    print(f"Python: {sys.version.split()[0]} @ {sys.executable}")
    print(f"USER  : {_whoami()} (euid={os.geteuid()})")
    print(f"deps  : {_DEPS_FILE}")
    print("")

    check("1. relocated CPython + venv ABI + stdlib extensions", test_relocated_interpreter)
    check("2. deps.txt requirements installed in venv", test_deps_installed)
    check("3. pip check (venv dependency surface self-consistent)", test_pip_check)
    check("4. torch flavor matches artifact (marker vs import, none|cpu)", test_torch_flavor_build)
    check("5. non-root (xmnn) identity can use interpreter/deps/temp", test_nonroot_identity)
    check("6. payload NOT installed (import xmnn / xmflow script absent)", test_payload_absent)

    print("==========================================")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed")
    print("==========================================")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
