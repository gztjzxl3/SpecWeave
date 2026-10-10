#!/usr/bin/env python3
"""xmflow-cli 交付镜像守卫（载荷安装后运行 / 镜像内可复跑）。

与 xmnn-runtime 交付守卫的验证差异（消费侧语义）：
  - 本脚本用 venv 解释器 /opt/xmflow/bin/python 导入 site-packages 中的载荷
    wheel（不是临时 venv、不是 --no-deps），等价于真实客户机 `pip install
    xmnn-*.whl` 后的首次启动；
  - 镜像内不存在 /workspace 源码树与 PYTHONPATH/TVM_LIBRARY_PATH，任何对
    /workspace 或 /opt/xmnn-builder 的路径命中都意味着 wheel 自包含性被破坏，
    必须失败；
  - tvm.build('llvm') 依赖的 libtvm.so / libLLVM 全部来自 wheel 的 _libs/
    （patchelf RPATH=$ORIGIN），镜像不安装 LLVM 工具链；
  - OQ-5 裁定：**不含** SIM_VTA2.0 模型编译冒烟（不引入真实模型进构建上下文），
    以 xmflow console script 的 `--help` + 六个子命令存在性（§9）与 deps.txt
    闭包模块可导入（§8）作为 CLI 侧替代断言；§5 的 tvm.build('llvm') 是 te
    合成计算的数值冒烟（零模型依赖），与 xmnn-runtime 对应项同源；真机模型组
    冒烟命令由 release/README 以可粘贴形式给出。

检查项（任一 FAIL 最终 exit 1，交付镜像构建失败；10 项 + pip check 对齐 §11
骨架，与 payload/Dockerfile 注释、release/README 清单逐字一致）：
  1. 解释器 ABI：/opt/xmflow/bin/python + cp314 GIL enabled
  2. import tvm / vta / xmnn，且 __file__ 落在 site-packages
  3. _libs 目录含 libtvm.so 与 libLLVM*
  4. 干净环境 ctypes RTLD_GLOBAL 加载 libtvm.so
  5. tvm.build('llvm') 向量乘 2 数值断言（合成计算，零模型依赖）
  6. relay/std/prelude.rly 数据存在
  7. 载荷数据文件：xmnn_bootstrap.pth 在 site-packages + xmnn 数据三目录
     （autolibs/tools_cpp/fonts）
  8. deps.txt 闭包关键模块逐一可导入（发行版名→导入名映射见
     _MODULE_BY_DISTRIBUTION）
  9. xmflow console script 存在、`--help` 退出码 0、输出含六个子命令名
     （compile/accuracy/infer/performance/excelreport/pipeline，OQ-5 替代断言）
 10. torch 形态与实物一致（marker vs import/version.cuda；none|cpu 双态，
     无 cu130——交付 §4 P0）
 + pip check：判据**收窄到载荷相关冲突**（^xmnn 开头的冲突行）；非载荷冲突行
   属底座层职责（_base_guards.py §3 已按全量阻断把关），此处仅 INFO 放行。
"""

import ctypes
import json
import os
import re
import subprocess
import sys
import sysconfig

PASS = 0
FAIL = 0

# 开发/构建路径黑名单：交付镜像中载荷模块绝不允许来自这些位置。
_FORBIDDEN_PREFIXES = ("/workspace/", "/opt/xmnn-builder")
_VENV_PYTHON = "/opt/xmflow/bin/python"
_XMFLOW_SCRIPT = "/opt/xmflow/bin/xmflow"
# OQ-5：以子命令存在性替代模型编译冒烟——这六个名字即客户契约的运行面。
_SUBCOMMANDS = ("compile", "accuracy", "infer", "performance", "excelreport", "pipeline")
# 与 Containerfile ARG TORCH_VERSION 对齐（仅校验主版本一致，补丁号以镜像实际为准）
_EXPECTED_TORCH_MAJOR = "2."
# 形态标记由 scripts/install-torch.sh 写入（底座层）；载荷层复验同一契约。
_TORCH_FLAVOR_MARKER = "/opt/xmflow-torch-flavor"
# 底座依赖清单（载荷守卫复用它做 §8 模块可用性抽测）。
_DEPS_FILE = os.environ.get("XMFLOW_DEPS_FILE", "/opt/xmflow-smoke/deps.txt")
# §11 收窄判据：只把**载荷相关**冲突行（owner 为 xmnn）当阻断。基镜像/依赖面
# 的其他冲突行在底座守卫已全量把关，派生层若再全量阻断，等于把底座债务的
# 修复压力错误地转嫁给每次交付派生。
_PAYLOAD_CONFLICT = re.compile(r"^xmnn\b")
# deps.txt 发行版名 → 导入模块名的例外映射（其余项两名一致）。
_MODULE_BY_DISTRIBUTION = {
    "Pillow": "PIL",
    "protobuf": "google.protobuf",
}

# 合并式 import 探测（单进程逐一导入，失败只记录不中断，由调用方汇总断言）；
# 以 `-I` 运行排除 PYTHONPATH 注入的假阳性，site 正常加载故 venv 内模块可见。
_IMPORTS_PROBE = "\n".join(
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
        print(f"  FAIL: {type(exc).__name__}: {exc}")
        FAIL += 1
    else:
        print("  PASS")
        PASS += 1
    print("")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _requirement_name(line: str) -> str:
    """取 Requirement 文本的发行版名（处理 >=/==/[extra] 等写法）。"""
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line.strip())
    _assert(match is not None, f"无法从清单行解析依赖名: {line!r}")
    return match.group(0)


def _read_deps() -> list:
    """读 deps.txt，返回去重后的发行版名清单（保持文件顺序）。"""
    _assert(os.path.isfile(_DEPS_FILE), f"依赖清单缺失: {_DEPS_FILE}")
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
    _assert(bool(names), f"依赖清单为空: {_DEPS_FILE}")
    return names


def test_interpreter_abi() -> None:
    print(f"  sys.executable = {sys.executable}")
    print(f"  sys.version    = {sys.version.split()[0]}")
    _assert(sys.executable == _VENV_PYTHON, f"解释器必须是 {_VENV_PYTHON}")
    gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
    print(f"  Py_GIL_DISABLED = {gil_disabled}")
    _assert(gil_disabled in (0, None), "wheel 是 cp314 GIL ABI，不能运行在 free-threaded 解释器")
    if hasattr(sys, "_is_gil_enabled"):
        _assert(sys._is_gil_enabled() is True, "cp314 GIL 解释器应报告 GIL enabled")


def test_imports_from_site_packages() -> None:
    import tvm
    import vta
    import xmnn

    for mod in (tvm, vta, xmnn):
        path = os.path.abspath(mod.__file__)
        print(f"  {mod.__name__} -> {path}")
        _assert("site-packages" in path, f"{mod.__name__} 不来自 site-packages: {path}")
        for bad in _FORBIDDEN_PREFIXES:
            _assert(not path.startswith(bad), f"{mod.__name__} 命中开发路径 {bad}: {path}")


def test_libs_directory() -> None:
    import tvm

    libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), "../_libs"))
    print(f"  _libs dir = {libs_dir}")
    _assert(os.path.isdir(libs_dir), "_libs 目录缺失")
    files = sorted(os.listdir(libs_dir))
    _assert(any(f == "libtvm.so" for f in files), "libtvm.so 缺失")
    llvm_libs = [f for f in files if "libLLVM" in f]
    _assert(bool(llvm_libs), f"libLLVM 缺失（实际条目：{files}）")
    print(f"  entries={len(files)}, libLLVM={llvm_libs}")


def test_ctypes_load_libtvm() -> None:
    import tvm

    libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), "../_libs"))
    libtvm = os.path.join(libs_dir, "libtvm.so")
    print(f"  loading {libtvm} (RTLD_GLOBAL, 无 LD_LIBRARY_PATH 依赖)")
    ctypes.CDLL(libtvm, mode=ctypes.RTLD_GLOBAL)


def test_tvm_build_llvm() -> None:
    import numpy as np
    import tvm
    from tvm import te

    n = 1024
    A = te.placeholder((n,), name="A", dtype="float32")
    B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
    s = te.create_schedule(B.op)
    f = tvm.build(s, [A, B], "llvm", name="vec_double")
    print(f"  tvm.build ok, entry={f.entry_name}")
    ctx = tvm.cpu(0)
    a = tvm.nd.array(np.random.uniform(size=n).astype("float32"), ctx)
    b = tvm.nd.array(np.zeros(n, dtype="float32"), ctx)
    f(a, b)
    np.testing.assert_allclose(b.asnumpy(), a.asnumpy() * 2.0, rtol=1e-5)
    print("  compute verified: A[i] * 2 == B[i]")


def test_relay_std_data() -> None:
    import tvm

    std_dir = os.path.join(os.path.dirname(tvm.__file__), "relay", "std")
    _assert(os.path.isdir(std_dir), f"relay/std 缺失: {std_dir}")
    files = os.listdir(std_dir)
    _assert("prelude.rly" in files, f"prelude.rly 缺失: {files}")
    print("  relay/std/prelude.rly present")


def test_payload_data_files() -> None:
    """§7 载荷数据面：bootstrap .pth + xmnn 三数据目录（合并骨架 7/8 两项）。"""
    import site

    candidates = [os.path.join(sp, "xmnn_bootstrap.pth") for sp in site.getsitepackages()]
    found = [p for p in candidates if os.path.exists(p)]
    _assert(found, f"xmnn_bootstrap.pth 未找到（候选：{candidates}）")
    print(f"  {found[0]}")

    import xmnn

    xmnn_dir = xmnn.__path__[0] if hasattr(xmnn, "__path__") else os.path.dirname(xmnn.__file__)
    required = ("autolibs", "tools_cpp", "fonts")
    for name in required:
        d = os.path.join(xmnn_dir, name)
        _assert(os.path.isdir(d), f"xmnn/{name} 缺失: {d}")
        print(f"  {name}/: {len(os.listdir(d))} entries")


def test_deps_modules_importable() -> None:
    """§8 deps.txt 闭包模块逐一可导入（发行版在≠模块可导入，此处补上运行面）。"""
    names = _read_deps()
    modules = []
    seen = set()
    for name in names:
        module = _MODULE_BY_DISTRIBUTION.get(name, name)
        if module not in seen:
            seen.add(module)
            modules.append(module)
    print(f"  manifest {_DEPS_FILE}: {len(names)} requirements -> {len(modules)} modules")
    out = subprocess.run(
        [sys.executable, "-I", "-c", _IMPORTS_PROBE],
        input=json.dumps(modules),
        capture_output=True,
        text=True,
        timeout=300,
    )
    _assert(out.returncode == 0, f"模块导入探测进程失败: {out.stderr.strip()}")
    results = json.loads(out.stdout.strip().splitlines()[-1])
    failed = {name: err for name, err in results.items() if err != "ok"}
    for module in modules:
        status = results.get(module)
        print(f"  {'[OK]  ' if status == 'ok' else '[FAIL]'} import {module}"
              f"{'' if status == 'ok' else ' -> ' + str(status)}")
    _assert(not failed, f"deps.txt 闭包存在不可导入的模块: {failed}")


def test_xmflow_console_script() -> None:
    """§9 xmflow CLI 入口（OQ-5 替代断言）：存在 + --help rc=0 + 六子命令在列。"""
    _assert(os.path.isfile(_XMFLOW_SCRIPT), f"console script 缺失: {_XMFLOW_SCRIPT}")
    _assert(os.access(_XMFLOW_SCRIPT, os.X_OK), f"console script 不可执行: {_XMFLOW_SCRIPT}")
    out = subprocess.run(
        [_XMFLOW_SCRIPT, "--help"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    _assert(
        out.returncode == 0,
        f"xmflow --help 退出码 {out.returncode}: {out.stderr.strip()[:400]}",
    )
    missing = [name for name in _SUBCOMMANDS if name not in out.stdout]
    _assert(
        not missing,
        f"xmflow --help 输出缺少子命令（客户契约运行面不完整）: {missing}",
    )
    print(f"  --help rc=0, subcommands listed: {', '.join(_SUBCOMMANDS)}")


def test_torch_flavor_build() -> None:
    """§10 形态契约（C26）：marker 声明什么形态，实物就必须是什么形态。

    判据是**声明 vs 实物**的一致性：marker（install-torch.sh 写入）↔ import 与
    version.cuda。本产品形态白名单只有 none|cpu（交付 §4 P0 禁 GPU 栈进客户
    镜像），marker 出现其他取值即构建违规；派生层复验底座契约未被载荷安装
    动作破坏（--no-deps 不应动 torch，若动了就在这项现形）。
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
        f"torch 形态标记异常（应存在且 ∈ none|cpu）: {flavor!r}",
    )

    if flavor == "none":
        try:
            import torch  # noqa: F401
        except ImportError:
            print("  形态 none（不装 torch）：镜像内无 torch")
            return
        raise AssertionError("形态声明为 none（不装 torch），但镜像内可 import torch")

    import torch

    ver = torch.__version__
    print(f"  torch.__version__ = {ver}")
    print(f"  torch.version.cuda = {torch.version.cuda}")
    _assert(ver.startswith(_EXPECTED_TORCH_MAJOR), f"torch 主版本异常: {ver}")
    _assert(
        torch.version.cuda is None,
        f"cpu 形态必须是 CPU 构建（torch.version.cuda 应为 None），实际 {torch.version.cuda}",
    )
    _assert(torch.cuda.is_available() is False, "CPU 镜像不应报告 CUDA 可用")
    print("  CPU build OK")
    # pytorch 前端 compile_api 依赖 torch.jit.load；确认 TorchScript 子模块在
    _assert(hasattr(torch, "jit") and hasattr(torch.jit, "load"), "torch.jit.load 不可用")
    # 轻量功能探针：张量算子走 CPU 正常
    x = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    _assert(float(x.sum()) == 15.0, "torch CPU 张量算子异常")
    print("  tensor ops OK")


def test_pip_check_payload_scoped() -> None:
    """+ pip check：判据收窄到载荷相关冲突（§11 字面裁定）。

    阻断条件：冲突行以 `xmnn` 开头（owner 是载荷）——载荷 wheel 的
    Requires-Dist 与镜像内实物区间不符，正是 `--no-deps` 安装方式唯一可能
    引入的依赖病灶。其余冲突行（owner 是底座依赖面）在 _base_guards.py §3
    已按全量阻断把关，派生层只作 INFO 转录，不重复计罪。
    """
    out = subprocess.run(
        [_VENV_PYTHON, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    lines = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    blocking = [line for line in lines if _PAYLOAD_CONFLICT.match(line)]
    informational = [line for line in lines if not _PAYLOAD_CONFLICT.match(line)]
    print(f"  pip check exit={out.returncode}, {len(lines)} line(s)")
    for line in informational:
        print(f"  [INFO] 非载荷冲突（底座守卫已把关，此处放行）: {line}")
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
        f"pip check 报告载荷（xmnn）相关冲突（--no-deps 掩盖了依赖区间错配）: {blocking}",
    )


def main() -> int:
    print("==========================================")
    print("  XMFLOW-CLI Runtime Smoke (payload installed)")
    print("==========================================")
    print(f"Python: {sys.version.split()[0]} @ {sys.executable}")
    print(f"PYTHONPATH={os.environ.get('PYTHONPATH', '<unset>')}")
    print(f"TVM_LIBRARY_PATH={os.environ.get('TVM_LIBRARY_PATH', '<unset>')}")
    print("")

    check("1. cp314 GIL venv interpreter ABI", test_interpreter_abi)
    check("2. import tvm/vta/xmnn from site-packages", test_imports_from_site_packages)
    check("3. _libs directory (libtvm.so + libLLVM)", test_libs_directory)
    check("4. ctypes load libtvm.so (clean env)", test_ctypes_load_libtvm)
    check("5. tvm.build('llvm') vector compute", test_tvm_build_llvm)
    check("6. relay/std/prelude.rly data", test_relay_std_data)
    check("7. payload data files (bootstrap .pth + xmnn dirs)", test_payload_data_files)
    check("8. deps.txt closure modules importable", test_deps_modules_importable)
    check("9. xmflow console script --help lists six subcommands", test_xmflow_console_script)
    check("10. torch flavor matches artifact (marker vs version.cuda)", test_torch_flavor_build)
    check("+ pip check (payload-scoped: ^xmnn conflicts only)", test_pip_check_payload_scoped)

    print("==========================================")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed")
    print("==========================================")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
