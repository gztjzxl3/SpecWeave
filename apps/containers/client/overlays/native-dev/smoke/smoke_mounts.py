"""native-dev 运行期冒烟：源码挂载可见性 + tvm/vta/xmnn 源码调试链路。

运行方式（栈在运行时）：
  podman-compose exec -T native /opt/conda/bin/python /opt/native-dev-smoke/smoke_mounts.py
  invoke native.smoke

语义：
  - 始终断言四个 bind 挂载点与关键子目录可访问；
  - /workspace/npu_tvm/build/libtvm.so 不存在（首次未编译）时跳过 import
    段并以退出码 0 通过——未编译是合法的首次状态，给出 build-tvm 提示；
  - libtvm.so 存在时导入 tvm/vta/xmnn，断言模块来自 /workspace 挂载源码
    （而非 site-packages），并跑 tvm.build('llvm') 固定向量加。
"""

import os
import sys
from pathlib import Path

TVM_ROOT = Path("/workspace/npu_tvm")
XMN_ROOT = Path("/workspace/npuusertools")
MODELS_ROOT = Path("/workspace/models")
PROJECTS_ROOT = Path("/workspace/projects")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


print("== 1. 挂载点与关键子目录 ==")
check("npu_tvm 根挂载", TVM_ROOT.is_dir())
check("npu_tvm/python/tvm 包", (TVM_ROOT / "python" / "tvm" / "__init__.py").is_file())
check("npu_tvm/vta/python/vta 包", (TVM_ROOT / "vta" / "python" / "vta" / "__init__.py").is_file())
check("npuusertools 根挂载", XMN_ROOT.is_dir())
check("npuusertools/xmnn 包", (XMN_ROOT / "xmnn" / "__init__.py").is_file())
check("models 挂载", MODELS_ROOT.is_dir())
check("projects 根挂载（第一方子项目）", PROJECTS_ROOT.is_dir())

# ---------------------------------------------------------------------------
# devuser 视角可达性探针（2026-10-12 C-I12）
#
# 本脚本经 compose exec 以容器 root 运行；rootless 下容器 root 对 owner=0 的
# 0700 文件仍可读（owner 位），**root 视角全部通过不等于 Jupyter/devuser 可用**。
# Jupyter 内核固定以 devuser(UID 1000) 运行，其访问 bind 宿主树只走 other 位。
# 故 root 时 fork 子进程 setuid(1000) 复现 devuser 身份做读/写探针；非 root
# 执行时直接探测。
# ---------------------------------------------------------------------------
DEVUSER_UID = 1000


def _first_regular_file(root: Path, cap: int = 200):
    """有界深度优先找第一个普通文件（避免大挂载树全扫）。"""
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in filenames:
            fp = Path(dirpath) / name
            seen += 1
            try:
                if fp.is_file():
                    return fp
            except OSError:
                continue
            if seen >= cap:
                return None
    return None


def _devuser_probes() -> list[tuple[str, bool, str]]:
    """返回 (检查名, 是否成功, 详情)。"""
    probes: list[tuple[str, Path, str]] = [
        ("devuser 读 npu_tvm 包文件", TVM_ROOT / "python" / "tvm" / "__init__.py", "r"),
        ("devuser 读 vta 包文件", TVM_ROOT / "vta" / "python" / "vta" / "__init__.py", "r"),
        ("devuser 读 npuusertools 包文件", XMN_ROOT / "xmnn" / "__init__.py", "r"),
        ("devuser 遍历 models 挂载", MODELS_ROOT, "d"),
        ("devuser 遍历 projects 挂载", PROJECTS_ROOT, "d"),
        ("devuser 写 projects 根（源码编辑/editable 安装契约）", PROJECTS_ROOT, "w"),
    ]
    sample = _first_regular_file(MODELS_ROOT)
    if sample is not None:
        probes.append(("devuser 读 models 数据文件", sample, "r"))
    # projects 下每个第一方子项目独立探测入口（pip install -e . 的真实读取点）：
    # 优先 pyproject.toml，缺失时退化为子树首个普通文件。逐个子项目而不是全树
    # 取首个，避免其他可读文件造成假阴性（2026-10-12 实测单一哨兵漏报）。
    for child in sorted(PROJECTS_ROOT.iterdir()):
        if not child.is_dir() or child.is_symlink():
            continue
        entry = child / "pyproject.toml"
        if not entry.is_file():
            entry = _first_regular_file(child)
        if entry is not None:
            probes.append((f"devuser 读子项目 {child.name} 入口文件", entry, "r"))

    def run_body() -> list[tuple[str, bool, str]]:
        out: list[tuple[str, bool, str]] = []
        for name, target, kind in probes:
            try:
                if kind == "d":
                    os.listdir(target)
                elif kind == "r":
                    with open(target, "rb") as fh:
                        fh.read(1)
                elif kind == "w":
                    probe_file = target / ".__devuser_perm_probe"
                    fd = os.open(probe_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
                    os.close(fd)
                    os.unlink(probe_file)
                out.append((name, True, ""))
            except OSError as exc:
                out.append((name, False, f"{type(exc).__name__}: {exc}"))
        return out

    if os.geteuid() != 0:
        return run_body()

    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r_fd)
        try:
            os.setuid(DEVUSER_UID)
            import json
            os.write(w_fd, json.dumps(run_body()).encode())
        except BaseException as exc:  # noqa: BLE001 - 子进程内任何异常都要回传
            os.write(w_fd, str(exc).encode())
        finally:
            os._exit(0)
    os.close(w_fd)
    import json
    _, status = os.waitpid(pid, 0)
    raw = os.read(r_fd, 1 << 20).decode()
    os.close(r_fd)
    if status != 0:
        return [("devuser 探针子进程异常", False, f"wait status={status} {raw}")]
    try:
        return [(n, bool(ok), d) for n, ok, d in json.loads(raw)]
    except ValueError:
        return [("devuser 探针切换失败", False, raw)]


print("\n== 1b. devuser(UID1000) 视角挂载可达性 ==")
for _name, _ok, _detail in _devuser_probes():
    check(_name, _ok, _detail)

print("\n  PYTHONPATH =", os.environ.get("PYTHONPATH", "<unset>"))
print("  TVM_LIBRARY_PATH =", os.environ.get("TVM_LIBRARY_PATH", "<unset>"))

libtvm = TVM_ROOT / "build" / "libtvm.so"

if not libtvm.is_file():
    print("\n[SKIP] libtvm.so 尚未构建（", libtvm, "）")
    print("       首次环境的合法状态。编译 TVM：inv native.build-tvm")
    print("       随后打包 wheel：inv native.wheel")
    if failures:
        print(f"\n[FAIL] 挂载点断言 {len(failures)} 项未通过：{failures}")
        sys.exit(1)
    print("\n[OK] 挂载点全部可见；import/算例段因 libtvm.so 缺席跳过")
    sys.exit(0)

print("\n== 2. tvm/vta/xmnn 来自挂载源码（非 site-packages）==")
import tvm  # noqa: E402
import vta  # noqa: E402
import xmnn  # noqa: E402

print("  tvm :", tvm.__file__)
print("  vta :", vta.__file__)
print("  xmnn:", xmnn.__file__)
check("tvm 来自 /workspace/npu_tvm", str(tvm.__file__).startswith(str(TVM_ROOT / "python")), str(tvm.__file__))
check("vta 来自 /workspace/npu_tvm", str(vta.__file__).startswith(str(TVM_ROOT / "vta")), str(vta.__file__))
check("xmnn 来自 /workspace/npuusertools", str(xmnn.__file__).startswith(str(XMN_ROOT)), str(xmnn.__file__))

print("\n== 3. tvm.build('llvm') 固定向量加（n=4, A*2 == B）==")
import numpy as np  # noqa: E402
from tvm import te  # noqa: E402

n = 4
A = te.placeholder((n,), name="A", dtype="float32")
B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
s = te.create_schedule(B.op)
f = tvm.build(s, [A, B], "llvm", name="vec_double")
a_np = np.arange(n, dtype="float32") + 1.0
a = tvm.nd.array(a_np, tvm.cpu(0))
b = tvm.nd.array(np.zeros(n, dtype="float32"), tvm.cpu(0))
f(a, b)
got = b.asnumpy().tolist()
print("  A =", a_np.tolist(), " B =", got)
check("向量加结果 [2.0, 4.0, 6.0, 8.0]", got == [2.0, 4.0, 6.0, 8.0], str(got))

print("")
if failures:
    print(f"[FAIL] {len(failures)} 项未通过：{failures}")
    sys.exit(1)
print("[OK] native source mounts + imports + tvm.build smoke passed")
