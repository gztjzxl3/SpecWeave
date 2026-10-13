"""bind 挂载源树权限门禁单测（C-I12）。

覆盖 ``utils.ensure_bind_tree_accessible`` / ``ensure_world_writable_dir``：
宿主侧 0700 检出经 rootless 固定 UID 映射进容器后，devuser(UID1000) 只能走
other 位访问；门禁在 prepare_env 咽喉点幂等放宽到 777/666（可写树）或
755/644（只读树），仅改权限位、不 chown、不跟随符号链接。
另含 prepare_env 接线的端到端最小集成验证。
"""

import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from jpman_client.tasks import overlay_core as oc
from jpman_client.tasks import utils as u
from jpman_client.tasks import native as native_mod


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------


def _seal(root: Path) -> dict[Path, int]:
    """把目录树改成宿主 0700 检出形态（目录 2700 保留 setgid 以验证保留语义）。"""
    modes: dict[Path, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        d.chmod(0o2700)
        modes[d] = 0o2700
        for name in dirnames + filenames:
            p = d / name
            if p.is_symlink():
                continue
            p.chmod(0o700 if name.startswith("exe_") else 0o600)
            modes[p] = 0o700 if name.startswith("exe_") else 0o600
    return modes


def _build_sealed_tree(tmp_path: Path) -> Path:
    root = tmp_path / "src-tree"
    sub = root / "pkg"
    sub.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[build-system]\n")
    (sub / "__init__.py").write_text("")
    (sub / "exe_run").write_text("#!/bin/sh\n")
    return root


def _mode(p: Path) -> int:
    return stat.S_IMODE(p.lstat().st_mode)


# ---------------------------------------------------------------------------
# ensure_bind_tree_accessible
# ---------------------------------------------------------------------------


def test_writable_tree_opens_to_777_666_preserves_exec_and_setgid(tmp_path):
    root = _build_sealed_tree(tmp_path)
    _seal(root)

    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=True, label="测试源码树", namespace="test"
    )

    assert failed == 0
    # 文件数=3、目录数=2，全部需放宽
    assert fixed == 5
    assert _mode(root) == 0o2777  # setgid 保留
    assert _mode(root / "pkg") == 0o2777
    assert _mode(root / "pyproject.toml") == 0o666
    assert _mode(root / "pkg" / "__init__.py") == 0o666
    assert _mode(root / "pkg" / "exe_run") == 0o777  # owner x → 777


def test_readonly_tree_opens_to_755_644(tmp_path):
    root = _build_sealed_tree(tmp_path)
    _seal(root)

    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=False, label="模型目录", namespace="test"
    )

    assert failed == 0
    assert fixed == 5
    assert _mode(root) == 0o2755
    assert _mode(root / "pkg") == 0o2755
    assert _mode(root / "pyproject.toml") == 0o644
    assert _mode(root / "pkg" / "exe_run") == 0o755  # 只补执行，不给写位


def test_readonly_gate_never_downgrades_existing_write_bits(tmp_path, monkeypatch):
    """只读策略只加不减：已有 0777/0666 inode 不得被降级（对非属主会直接 EPERM）。"""
    root = tmp_path / "ro-tree"
    root.mkdir()
    (root / "open.py").write_text("")
    os.chmod(root, 0o777)
    os.chmod(root / "open.py", 0o666)
    calls: list[Path] = []
    real_chmod = Path.chmod
    monkeypatch_chmod = lambda self, mode, **kw: calls.append(self)  # noqa: E731
    monkeypatch.setattr(Path, "chmod", monkeypatch_chmod)

    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=False, label="ro", namespace="test"
    )

    assert (fixed, failed) == (0, 0)
    assert calls == []  # 既已满足只读契约，零 chmod、零降级
    monkeypatch.setattr(Path, "chmod", real_chmod)
    assert _mode(root) == 0o777 and _mode(root / "open.py") == 0o666


def test_gate_is_idempotent(tmp_path, capsys):
    root = _build_sealed_tree(tmp_path)
    _seal(root)

    first, f1 = u.ensure_bind_tree_accessible(
        root, writable=True, label="x", namespace="test"
    )
    second, f2 = u.ensure_bind_tree_accessible(
        root, writable=True, label="x", namespace="test"
    )

    assert (first, f1) == (5, 0)
    assert (second, f2) == (0, 0)
    # 第二次零修正时不打印「已放宽」摘要
    out = capsys.readouterr().out
    assert out.count("已放宽挂载源") == 1


def test_symlink_is_skipped_and_target_untouched(tmp_path):
    root = _build_sealed_tree(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("secret")
    outside.chmod(0o600)
    (root / "link.py").symlink_to(outside)

    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=True, label="x", namespace="test"
    )

    assert failed == 0
    assert fixed == 5  # 链接不计入
    assert _mode(outside) == 0o600  # 未跟随链接改外部文件
    assert stat.S_ISLNK((root / "link.py").lstat().st_mode)


def test_chmod_noop_on_9p_emits_w19_style_warning(tmp_path, monkeypatch, capsys):
    """9p/drvfs 无 metadata：chmod rc=0 但位不变——必须点名 W-I19，不假装修好。"""
    root = _build_sealed_tree(tmp_path)
    _seal(root)

    real_chmod = Path.chmod

    def _noop_chmod(self, mode, *args, **kwargs):  # noqa: ANN001
        # 模拟空操作：不抛错但属性不变
        return None

    monkeypatch.setattr(Path, "chmod", _noop_chmod)
    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=True, label="x", namespace="test"
    )

    out = capsys.readouterr().out
    assert fixed == 5  # 调用都「成功」
    assert "chmod 未在宿主文件系统生效" in out
    assert "W-I19" in out
    assert _mode(root) == 0o2700
    monkeypatch.setattr(Path, "chmod", real_chmod)


def test_non_posix_host_is_skipped(tmp_path, monkeypatch):
    root = _build_sealed_tree(tmp_path)
    _seal(root)
    monkeypatch.setattr(u.os, "name", "nt")

    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=True, label="x", namespace="test"
    )

    assert (fixed, failed) == (0, 0)
    assert _mode(root / "pyproject.toml") == 0o600  # 原样未动


def test_missing_path_returns_zeros(tmp_path):
    assert u.ensure_bind_tree_accessible(
        tmp_path / "nope", writable=True, label="x", namespace="test"
    ) == (0, 0)


def test_foreign_owner_wall_aborts_early(tmp_path, monkeypatch, capsys):
    """属主非当前用户的子树 chmod 恒 EPERM：必须阈值早退（否则 up 被拖数十秒）。"""
    root = tmp_path / "foreign-tree"
    sub = root / "sealed"
    sub.mkdir(parents=True)
    for i in range(60):
        (sub / f"f{i}").write_text("x")
    _seal(root)

    def _deny_chmod(self, mode, *args, **kwargs):  # noqa: ANN001
        raise PermissionError(f"[Errno 13] Permission denied: {self}")

    monkeypatch.setattr(Path, "chmod", _deny_chmod)
    fixed, failed = u.ensure_bind_tree_accessible(
        root, writable=True, label="foreign", namespace="test"
    )

    out = capsys.readouterr().out
    assert fixed == 0
    assert failed <= 20  # 预算封顶，不逐文件硬撞 62 个 inode
    assert "已达阈值，停止遍历" in out
    assert "属主账户" in out


# ---------------------------------------------------------------------------
# ensure_world_writable_dir
# ---------------------------------------------------------------------------


def test_world_writable_dir_promotes_and_preserves_setgid(tmp_path):
    d = tmp_path / "temp"
    d.mkdir()
    os.chmod(d, 0o2755)

    assert u.ensure_world_writable_dir(d, label="临时目录", namespace="test") is True
    assert _mode(d) == 0o2777
    # 幂等：第二次不再打印/变更
    assert u.ensure_world_writable_dir(d, label="临时目录", namespace="test") is True
    assert _mode(d) == 0o2777


def test_world_writable_dir_noop_fs_warns(tmp_path, monkeypatch, capsys):
    d = tmp_path / "temp"
    d.mkdir()
    os.chmod(d, 0o2755)
    monkeypatch.setattr(Path, "chmod", lambda self, mode: None)

    assert u.ensure_world_writable_dir(d, label="临时目录", namespace="test") is False
    assert "chmod 是空操作" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 声明式规格：写权限策略
# ---------------------------------------------------------------------------


def test_native_spec_mount_writability_policy():
    by_env = {m.env: m for m in native_mod.NATIVE_SPEC.source_mounts}
    assert by_env["MODELS_PATH"].writable is False  # 纯数据树只读
    assert by_env["NPU_TVM_PATH"].writable is True  # build/ 写产物
    assert by_env["NPUUSERTOOLS_PATH"].writable is True
    assert by_env["NATIVE_PROJECTS_PATH"].writable is True  # 源码编辑 + pip -e
    assert by_env["NATIVE_TEMP_PATH"].must_exist is False


# ---------------------------------------------------------------------------
# prepare_env 端到端接线（hermetic：临时布局 + 接触面打桩）
# ---------------------------------------------------------------------------


def _minimal_harness(tmp_path: Path, monkeypatch) -> SimpleNamespace:
    repo = tmp_path / "repo"
    root = repo / "apps" / "containers" / "client"
    for rel in (
        "external/chaos/npu_tvm",
        "external/containers/workspace/dev/npuusertools",
        "external/chaos/models",
        "projects/xuanspace",
    ):
        (repo / rel).mkdir(parents=True, exist_ok=True)
    (root / "overlays/native-dev").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(oc, "_project_root", lambda: root)
    monkeypatch.setattr(oc, "_load_env_overrides", lambda r: {})
    monkeypatch.setattr(oc, "ensure_workspace_checkpoint_writable", lambda p: None)
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Linux"))
    for key in (
        "NATIVE_WORKSPACE", "NPU_TVM_PATH", "NPUUSERTOOLS_PATH",
        "MODELS_PATH", "NATIVE_PROJECTS_PATH",
        "NATIVE_IMAGE_TAG", "NATIVE_CONTAINER_NAME", "NATIVE_SSH_PORT",
        "NATIVE_JUPYTER_PORT", "NATIVE_OFFLINE",
    ):
        monkeypatch.delenv(key, raising=False)
    # 缺省 .temp 在 tmp 布局下会上溯到文件系统根触发越界守卫，钉到 tmp 内
    monkeypatch.setenv("NATIVE_TEMP_PATH", str(tmp_path / "temp"))
    return SimpleNamespace(root=root, repo=repo)


def test_prepare_env_heals_sealed_projects_tree(tmp_path, monkeypatch):
    h = _minimal_harness(tmp_path, monkeypatch)
    proj = h.repo / "projects"
    sealed = proj / "xuanspace" / "pyproject.toml"
    sealed.write_text("[build-system]\n")
    os.chmod(sealed, 0o600)
    os.chmod(proj / "xuanspace", 0o700)
    models_file = h.repo / "external/chaos/models/a.bin"
    models_file.write_bytes(b"\0")
    os.chmod(models_file, 0o600)

    oc.prepare_env(native_mod.NATIVE_SPEC)

    # 可写树：文件补 other 读写位
    assert stat.S_IMODE(sealed.lstat().st_mode) == 0o666
    # 只读树（models）：补读位但不补写位
    assert stat.S_IMODE(models_file.lstat().st_mode) == 0o644
    # temp 根非递归放宽为可写（0777，容器内 devuser 可自建子项）
    temp_root = Path(os.environ["NATIVE_TEMP_PATH"])
    assert temp_root.is_dir()
    assert stat.S_IMODE(temp_root.lstat().st_mode) == 0o777
