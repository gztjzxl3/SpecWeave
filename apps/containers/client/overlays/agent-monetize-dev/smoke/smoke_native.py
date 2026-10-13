"""agent-monetize 源码挂载 + 原生 tvm-ffi 链路冒烟（栈运行路径）。

运行方式（栈在运行时，compose 已注入 PYTHONPATH=/workspace/agent-monetize/src）：
  /opt/conda/bin/python /opt/agent-monetize-dev-smoke/smoke_native.py

语义：
  - 始终断言挂载点与源码包关键路径可访问（独立于 .so 是否编译——首次未
    编译是合法态，挂载失败不得被 libtvm 缺席分支掩盖）。
  - score_opportunity.so 存在：FfiBridge 加载，断言 backend=native、
    tvm_ffi_available、固定输入原生结果 == 纯 Python 参考（容差 1e-9）。
  - .so 不存在：跳过原生段并提示先 build-native，整体仍 exit 0。
"""

import math
import os
import sys
from pathlib import Path

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


ROOT = Path("/workspace/agent-monetize")
SRC_PKG = ROOT / "src" / "agent_monetize"
NATIVE_SO = ROOT / "native" / "build" / "score_opportunity.so"

print("== 1. 挂载点与源码包 ==")
check("agent-monetize 根挂载", ROOT.is_dir())
check("pyproject.toml 可见", (ROOT / "pyproject.toml").is_file())
check("agent_monetize 包可见", (SRC_PKG / "__init__.py").is_file())
check("ffi_bridge.py 可见", (SRC_PKG / "core" / "ffi_bridge.py").is_file())
check("score_opportunity.cc 可见", (ROOT / "native" / "score_opportunity.cc").is_file())
print("  PYTHONPATH =", os.environ.get("PYTHONPATH"))
print("  LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH"))

# ---------------------------------------------------------------------------
# Jupyter kernelspec 用户脚本目录探针（2026-10-13）
#
# pip --user 的控制台脚本（xc/xs/pytest 等）落点 /home/devuser/.local/bin；
# notebook 单元格 ! 由内核经 dash 非登录 shell 执行（不读 ~/.profile），PATH
# 完全取自 kernelspec env。register-kernel.sh 漏写该目录时裸名命令在 notebook
# 中 100% not found，而 SSH 登录 shell 因 ~/.profile 正常形成排查盲区。
# 本探针只断言 kernelspec 配置（镜像构建期即可运行，不依赖事后 pip 安装），
# 并下沉 devuser(UID1000) 身份经 dash 复核——与 notebook ! 的解析路径同构。
# ---------------------------------------------------------------------------
KERNELSPEC = Path("/opt/conda/envs/main/share/jupyter/kernels/agent-monetize-dev/kernel.json")
USER_LOCAL_BIN = "/home/devuser/.local/bin"


def _kernel_path_probes() -> list[tuple[str, bool, str]]:
    import json
    import subprocess

    def run_body() -> list[tuple[str, bool, str]]:
        out: list[tuple[str, bool, str]] = []
        try:
            spec = json.loads(KERNELSPEC.read_text())
            path = spec.get("env", {}).get("PATH", "")
        except FileNotFoundError:
            return [("kernelspec 文件存在", False, f"missing {KERNELSPEC}")]
        except ValueError as exc:
            return [("kernelspec JSON 合法", False, f"{type(exc).__name__}: {exc}")]
        entries = path.split(":")
        out.append(("kernelspec 文件存在且 JSON 合法", True, str(KERNELSPEC)))
        out.append((
            "kernelspec PATH 前置 ~/.local/bin（pip --user 脚本可达）",
            entries[:1] == [USER_LOCAL_BIN],
            f"PATH[0]={entries[0] if entries else '<empty>'}",
        ))
        proc = subprocess.run(
            ["/usr/bin/sh", "-c",
             'case ":$PATH:" in *":$HOME/.local/bin:"*) exit 0;; *) exit 2;; esac'],
            env={"HOME": "/home/devuser", "PATH": path},
            capture_output=True, text=True,
        )
        out.append((
            "devuser/dash 非登录 shell 可见 ~/.local/bin（notebook ! 同构）",
            proc.returncode == 0,
            f"dash rc={proc.returncode}",
        ))
        return out

    if os.geteuid() != 0:
        return run_body()

    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r_fd)
        try:
            os.setuid(1000)
            import json as _json
            os.write(w_fd, _json.dumps(run_body()).encode())
        except BaseException as exc:  # noqa: BLE001 - 子进程任何异常都须回传
            os.write(w_fd, str(exc).encode())
        finally:
            os._exit(0)
    os.close(w_fd)
    import json as _json
    _, status = os.waitpid(pid, 0)
    raw = os.read(r_fd, 1 << 20).decode()
    os.close(r_fd)
    if status != 0:
        return [("kernelspec 探针子进程异常", False, f"wait status={status} {raw}")]
    try:
        return [(n, bool(ok), d) for n, ok, d in _json.loads(raw)]
    except ValueError:
        return [("kernelspec 探针下沉失败", False, raw)]


print("\n== 1c. Jupyter kernelspec 用户脚本目录（notebook ! 裸名命令可达性）==")
for _name, _ok, _detail in _kernel_path_probes():
    check(_name, _ok, _detail)

# ---------------------------------------------------------------------------
# 用户态安装/登录态持久化卷探针（2026-10-13，排障 C-I13）
#
# ~/.local（user-site + bin 控制台脚本）必须由 monetize-userlocal 卷承载；
# monetize-jupyter 以【嵌套子挂载】覆盖卷内 share/jupyter——父卷缺失或挂载
# 顺序颠倒都会让登录态卷失效，父子两条挂载关系一并断言。可写性下沉
# devuser(UID1000) 实测（root 视角恒可写，属假证据）。
# ---------------------------------------------------------------------------
USER_LOCAL = Path("/home/devuser/.local")


def _userlocal_volume_probes() -> list[tuple[str, bool, str]]:
    def parse_mounts() -> dict[str, tuple[str, str]]:
        mounts: dict[str, tuple[str, str]] = {}
        for line in Path("/proc/self/mountinfo").read_text().splitlines():
            left, _, right = line.partition(" - ")
            fields = left.split(" ")
            root, target = fields[3], fields[4]
            fstype = right.split(" ")[0] if right else "?"
            mounts[target] = (root, fstype)
        return mounts

    def run_body() -> list[tuple[str, bool, str]]:
        out: list[tuple[str, bool, str]] = []
        mounts = parse_mounts()
        parent = mounts.get(str(USER_LOCAL))
        out.append((
            "~/.local 由命名卷承载（非容器 overlay 临时层）",
            bool(parent) and parent[1] != "overlay" and "volumes/" in parent[0],
            f"fstype={parent[1] if parent else '<none>'}, root={parent[0] if parent else '<not mounted>'}",
        ))
        child = mounts.get(str(USER_LOCAL / "share" / "jupyter"))
        out.append((
            "share/jupyter 为嵌套子挂载（monetize-jupyter 登录态卷未被遮蔽）",
            bool(child) and "monetize-jupyter" in child[0] and (not parent or child[0] != parent[0]),
            f"root={child[0] if child else '<not mounted>'}",
        ))
        out.append((
            "devuser 对 ~/.local 可写（pip --user 安装契约）",
            os.access(USER_LOCAL, os.W_OK),
            "",
        ))
        return out

    if os.geteuid() != 0:
        return run_body()

    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r_fd)
        try:
            os.setuid(1000)
            import json as _json
            os.write(w_fd, _json.dumps(run_body()).encode())
        except BaseException as exc:  # noqa: BLE001
            os.write(w_fd, str(exc).encode())
        finally:
            os._exit(0)
    os.close(w_fd)
    import json as _json
    _, status = os.waitpid(pid, 0)
    raw = os.read(r_fd, 1 << 20).decode()
    os.close(r_fd)
    if status != 0:
        return [("userlocal 卷探针子进程异常", False, f"wait status={status} {raw}")]
    try:
        return [(n, bool(ok), d) for n, ok, d in _json.loads(raw)]
    except ValueError:
        return [("userlocal 卷探针下沉失败", False, raw)]


print("\n== 1d. 用户态 Python 安装持久化卷（pip --user / editable）==")
for _name, _ok, _detail in _userlocal_volume_probes():
    check(_name, _ok, _detail)

if not SRC_PKG.parent.is_dir():
    print(f"[FAIL] 源码 src 目录不可见，停止：{SRC_PKG.parent}")
    sys.exit(1)

print("\n== 2. 纯 Python 参考实现（不依赖 .so）==")
from agent_monetize.core.ffi_bridge import (  # noqa: E402
    FfiBridge,
    _reference_score_opportunity,
)

REF_INPUTS = (100.0, 0.8, 1.5, 20.0)
ref_value = _reference_score_opportunity(*REF_INPUTS)
print(f"  reference score{REF_INPUTS} = {ref_value:.6f}")
check("参考打分在 [0,100]", 0.0 <= ref_value <= 100.0, f"{ref_value}")

if not NATIVE_SO.is_file():
    print("\n[SKIP] score_opportunity.so 尚未编译（首次使用的合法态）")
    print("       编译后重跑本冒烟：invoke monetize.build-native && invoke monetize.smoke")
    print("       当前后端将是 reference（纯 Python 降级，功能正常）")
else:
    print(f"\n== 3. 原生 tvm-ffi backend（{NATIVE_SO}，{NATIVE_SO.stat().st_size} B）==")
    bridge = FfiBridge(fallback_to_reference=False)
    backend = bridge.initialize(native_lib_paths=[str(NATIVE_SO)])
    check("tvm_ffi_available", bridge.tvm_ffi_available)
    check("backend == native", backend == "native", f"backend={backend}, "
          f"load_error={bridge.load_error}")
    check("native_lib_path 指向挂载 .so",
          bool(bridge.native_lib_path) and Path(bridge.native_lib_path) == NATIVE_SO,
          bridge.native_lib_path or "")

    if backend == "native":
        native_value = float(bridge.score_opportunity(*REF_INPUTS))
        print(f"  native    score{REF_INPUTS} = {native_value:.9f}")
        print(f"  reference score{REF_INPUTS} = {ref_value:.9f}")
        check("原生结果在 [0,100]", 0.0 <= native_value <= 100.0, f"{native_value}")
        check("原生 == 参考（容差 1e-9）",
              math.isclose(native_value, ref_value, rel_tol=0.0, abs_tol=1e-9),
              f"diff={abs(native_value - ref_value):.3e}")

print("")
if failures:
    print(f"[FAIL] 原生/挂载冒烟未通过：{len(failures)} 项 — {failures}")
    sys.exit(1)
print("[OK] agent-monetize mounts + native smoke passed")
