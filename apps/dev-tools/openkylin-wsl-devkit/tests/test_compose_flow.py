"""okw compose 流程级测试：fake WSL 注入，覆盖 preflight/install/verify
全分支与命令序列纪律（rootless 用户态、零 apt/sudo、--yes 闸门、幂等）。
"""

from types import SimpleNamespace

import pytest

from okw import cli, compose, distro

from conftest import make_result

# ---- 测试夹具常量 ---------------------------------------------------------
# 样本源路径使用中性虚拟位置（不引用本机真实 submodule 布局）；
# 发行版内形态直接由被测函数 to_distro_path 推导，不手写第二份字面量。
SRC_WIN = r"D:\sandbox\libs\xuan-compose"
SRC_MNT = compose.to_distro_path(SRC_WIN)

# HOME/用户名是伪装发行版（openKylin-3.0 实测默认用户 openkylin uid=1000）的夹具。
DISTRO = "openKylin-3.0"
DEFAULT_USER = "openkylin"
HOME = "/home/openkylin"

# 安装布局是 okw compose 的产品契约：相对路径与可执行名一律以 compose 常量为
# 唯一事实源，测试只拼 HOME（HOME 本身在运行时由发行版内 printenv 探测）。
UV = f"{HOME}/{compose.UV_REL}"
SHIM_MAIN = f"{HOME}/{compose.LOCAL_BIN}/{compose.XUAN_COMPOSE_EXE}"
SHIM_ALIAS = f"{HOME}/{compose.LOCAL_BIN}/{compose.XC_EXE}"

# xc 版本号样本（xuan-compose 0.1.0 元数据内 __version__ 同形态）
SAMPLE_VERSION = "1.6.0+xuan.1"

# 流程中任何路径都不得出现的写入/越权动作（compose 全程默认用户 rootless）
FORBIDDEN_ANY = ("apt", "sudo", "tee ", "-u root", "add-apt-repository", "wsl.conf")
# 只读命令不得出现的下载/安装动作
FORBIDDEN_READONLY = ("curl", "uv python install", "uv tool install", "chmod", "chown")


class FakeWsl:
    """按子串返回的假 run_wsl；sequences 支持同一命令按调用次序出队。"""

    def __init__(self, monkeypatch):
        self.calls: list[list[str]] = []
        self.script: dict[str, distro.CmdResult] = {}
        self.sequences: dict[str, list] = {}
        monkeypatch.setattr(distro, "run_wsl", self._run)

    def _run(self, args, timeout=60):
        self.calls.append(args)
        joined = " ".join(args)
        for key, queue in self.sequences.items():
            if key in joined and queue:
                return queue.pop(0)
        for key, result in self.script.items():
            if key in joined:
                return result
        return make_result(False, 1, "", "发行版不存在", "distro_missing")


@pytest.fixture
def fake_compose(monkeypatch):
    return FakeWsl(monkeypatch)


def joined(fr: FakeWsl) -> str:
    return "\n".join(" ".join(c) for c in fr.calls)


def has_call(fr: FakeWsl, tokens: list[str]) -> bool:
    return any(all(t in c for t in tokens) for c in fr.calls)


def distro_argv(fr: FakeWsl):
    """剥掉 wsl.exe -d <name> -- 前缀，逐次产出发行版内命令 argv。"""
    for c in fr.calls:
        if "--" in c:
            yield c[c.index("--") + 1:]


def tool_install_argv(fr: FakeWsl) -> list[str]:
    return next(a for a in distro_argv(fr) if a[1:3] == ["tool", "install"])


def call_index(fr: FakeWsl, key: str) -> int:
    for i, c in enumerate(fr.calls):
        if key in " ".join(c):
            return i
    return -1


def env_base(fr: FakeWsl, *, podman: bool = True) -> None:
    fr.script["-l -v"] = make_result(
        stdout="  NAME                   STATE           VERSION\n"
        f"* {DISTRO}           Running         2\n"
    )
    fr.script["cat /etc/os-release"] = make_result(
        stdout="ID=openkylin\nVERSION_ID=3.0\n"
    )
    fr.script["id -un"] = make_result(stdout=DEFAULT_USER + "\n")
    fr.script["id -u"] = make_result(stdout="1000\n")
    fr.script["printenv HOME"] = make_result(stdout=HOME + "\n")
    if podman:
        fr.script["podman --version"] = make_result(stdout="podman version 4.9.4\n")
        fr.script["podman info --format"] = make_result(stdout="true\n")


def env_uv(fr: FakeWsl, *, present: bool = True) -> None:
    if present:
        fr.script[f"{UV} --version"] = make_result(stdout="uv 0.9.5 (x86_64-unknown-linux-gnu)\n")
    else:
        fr.script[f"{UV} --version"] = make_result(
            ok=False, exit_code=127, stderr=f"bash: {UV}: 没有那个文件"
        )


def env_python314(fr: FakeWsl, state: str = "installed") -> None:
    if state == "installed":
        stdout = (
            "cpython-3.14.0-linux-x86_64-gnu    "
            f"{HOME}/.local/share/uv/python/cpython-3.14.0/bin/python3.14\n"
        )
        fr.script[f"{UV} python list"] = make_result(stdout=stdout)
    elif state == "available":
        fr.script[f"{UV} python list"] = make_result(
            stdout="cpython-3.14.0-linux-x86_64-gnu    <download available>\n"
        )
    else:
        fr.script[f"{UV} python list"] = make_result(
            stdout="cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3.12\n"
        )


def env_xc_shims(fr: FakeWsl, main_ver=SAMPLE_VERSION, alias_ver=SAMPLE_VERSION) -> None:
    fr.script[f"{SHIM_MAIN} version --short"] = make_result(stdout=main_ver + "\n")
    fr.script[f"{SHIM_ALIAS} version --short"] = make_result(stdout=alias_ver + "\n")


def env_xc_absent(fr: FakeWsl) -> None:
    fr.script[f"{SHIM_MAIN} version --short"] = make_result(
        ok=False, exit_code=127, stderr="bash: xuan-compose: 命令不存在"
    )
    fr.script[f"{SHIM_ALIAS} version --short"] = make_result(
        ok=False, exit_code=127, stderr="bash: xc: 命令不存在"
    )


def env_install_pass(fr: FakeWsl, *, listed: bool = False) -> None:
    fr.script[f"{UV} python install"] = make_result(stdout="Installed Python 3.14.0 in 2.3s\n")
    fr.script[f"{UV} tool list"] = make_result(
        stdout="xuan-compose v1.6.0+xuan.1\n" if listed else ""
    )
    fr.script[f"{UV} tool install"] = make_result(stdout="Installed 2 executables: xc, xuan-compose\n")


# ========================= preflight =========================

class TestPreflight:
    def test_distro_missing_aborts_early(self, fake_compose, capsys):
        ret = cli.main(["compose", "preflight", "ghost"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "未注册" in out
        # 发行版不存在：仅一次 -l -v 枚举，绝不触达 -d <name> 内任何命令
        assert not any("-d" in " ".join(c) for c in fake_compose.calls)

    def test_podman_missing_is_fail_with_hint(self, fake_compose, capsys):
        env_base(fake_compose, podman=False)
        env_uv(fake_compose, present=False)
        env_xc_absent(fake_compose)
        ret = cli.main(["compose", "preflight", DISTRO])
        assert ret == 1
        out = capsys.readouterr().out
        assert "rootless Podman" in out and "[FAIL" in out
        assert "okw podman install" in out

    def test_fresh_env_only_unknown_is_exit_2(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose, present=False)
        env_xc_absent(fake_compose)
        ret = cli.main(["compose", "preflight", DISTRO])
        assert ret == 2
        out = capsys.readouterr().out
        assert "uv 引导器" in out and "UNKNOWN" in out
        assert "xuan-compose shim" in out
        assert "结论" in out

    def test_python314_download_available_is_unknown(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose, "available")
        env_xc_absent(fake_compose)
        ret = cli.main(["compose", "preflight", DISTRO])
        assert ret == 2
        out = capsys.readouterr().out
        assert "托管 Python 3.14" in out
        assert "install" in out  # UNKNOWN 明细说明 install 阶段将自动获取

    def test_all_ready_exit_0(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_xc_shims(fake_compose)
        ret = cli.main(["compose", "preflight", DISTRO])
        assert ret == 0
        assert "全部通过" in capsys.readouterr().out

    def test_readonly_sentinel(self, fake_compose):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_xc_shims(fake_compose)
        assert cli.main(["compose", "preflight", DISTRO]) == 0
        calls = joined(fake_compose)
        for forb in FORBIDDEN_ANY + FORBIDDEN_READONLY:
            assert forb not in calls, f"preflight 出现写入/安装动作：{forb}\n{calls}"

    def test_local_source_pyproject_pass(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result()
        ret = cli.main(["compose", "preflight", DISTRO, "--source", SRC_WIN])
        assert ret == 0
        out = capsys.readouterr().out
        assert "安装源" in out and "[PASS" in out
        assert SRC_MNT in out
        assert has_call(fake_compose, ["test", "-f", f"{SRC_MNT}/pyproject.toml"])

    def test_local_source_pyproject_missing_fail(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result(
            ok=False, exit_code=1
        )
        ret = cli.main(["compose", "preflight", DISTRO, "--source", SRC_WIN])
        assert ret == 1
        assert "pyproject.toml" in capsys.readouterr().out

    def test_url_source_probed_without_network(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose, present=False)
        env_xc_absent(fake_compose)
        url = "git+https://github.com/xuanspace/xuan-compose.git"
        ret = cli.main(["compose", "preflight", DISTRO, "--source", url])
        # podman PASS，uv/xc UNKNOWN，源 UNKNOWN（不触网）→ exit 2
        assert ret == 2
        out = capsys.readouterr().out
        assert "安装源" in out and "UNKNOWN" in out
        calls = joined(fake_compose)
        assert "curl" not in calls and "git " not in calls and "wget" not in calls


# ========================= install：--yes 闸门 =========================

class TestInstallYesGate:
    def test_missing_yes_zero_writes_and_lists_side_effects(self, fake_compose, capsys):
        ret = cli.main(["compose", "install", DISTRO, "--source", SRC_WIN])
        assert ret == 2
        out = capsys.readouterr().out
        for line in compose.YES_SIDEEFFECTS_LINES:
            assert line.strip() in out
        # GPL 边界：副作用清单场景必须显著声明
        assert "GPL-2.0-only" in out
        assert fake_compose.calls == []


# ========================= install：全绿路径与序列纪律 =========================

class TestInstallHappyPath:
    def test_full_pass_downloads_uv_then_python_then_tool(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose, present=False)
        # uv 首次探测失败（script 固定失败），安装后复验成功：序列里先放一次失败，
        # 出队后落回 script——script 是失败，故复验用 sequences 第二次给成功。
        fake_compose.sequences[f"{UV} --version"] = [
            make_result(ok=False, exit_code=127, stderr="缺失"),
            make_result(stdout="uv 0.9.5\n"),
        ]
        fake_compose.script[f"{UV} --version"] = make_result(stdout="uv 0.9.5\n")
        # uv installer 为单行 curl ... | sh（bash -c 单 token 透传，无 base64）
        fake_compose.script["curl -LsSf"] = make_result()
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result()

        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 0, capsys.readouterr().out
        out = capsys.readouterr().out
        assert "安装成功" in out

        calls = joined(fake_compose)
        # rootless 纪律：无 apt/sudo/root
        for forb in FORBIDDEN_ANY:
            assert forb not in calls, f"出现越权动作：{forb}\n{calls}"

        # installer 恰好一次，且位于 uv 探测之后、python install 之前
        assert calls.count("curl -LsSf") == 1
        i_installer = call_index(fake_compose, "curl -LsSf")
        i_py = call_index(fake_compose, f"{UV} python install")
        i_tool = call_index(fake_compose, f"{UV} tool install")
        assert 0 < i_installer < i_py < i_tool

        # uv python install 3.14 精确参数
        assert has_call(fake_compose, [UV, "python", "install", compose.MIN_PYTHON])

        # tool install：--python 3.14 + /mnt/d 本地源；默认非 editable、非 --force
        cmd = tool_install_argv(fake_compose)
        assert "--python" in cmd and compose.MIN_PYTHON in cmd
        assert SRC_MNT in cmd
        assert "--editable" not in cmd
        assert "--force" not in cmd

        # 双 shim 全路径验收
        assert has_call(fake_compose, [SHIM_MAIN, "version", "--short"])
        assert has_call(fake_compose, [SHIM_ALIAS, "version", "--short"])

    def test_uv_present_skips_installer(self, fake_compose):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result()
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 0
        assert "curl -LsSf" not in joined(fake_compose)

    def test_editable_flag_passed_only_when_requested(self, fake_compose):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result()
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes",
             "--source", SRC_WIN, "--editable"]
        )
        assert ret == 0
        assert "--editable" in tool_install_argv(fake_compose)

    def test_already_installed_tool_uses_force(self, fake_compose):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose, listed=True)
        env_xc_shims(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result()
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 0
        assert "--force" in tool_install_argv(fake_compose)

    def test_url_source_passed_verbatim(self, fake_compose):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        env_xc_shims(fake_compose)
        url = "git+https://github.com/xuanspace/xuan-compose.git"
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", url]
        )
        assert ret == 0
        cmd = tool_install_argv(fake_compose)
        assert url in cmd
        assert "/mnt/" not in " ".join(cmd)
        # URL 源不做本地 pyproject 校验
        assert not any(a[:2] == ["test", "-f"] for a in distro_argv(fake_compose))

    def test_local_source_missing_pyproject_aborts_before_downloads(
        self, fake_compose, capsys
    ):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        fake_compose.script[f"test -f {SRC_MNT}/pyproject.toml"] = make_result(
            ok=False, exit_code=1
        )
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        assert "pyproject.toml" in capsys.readouterr().out
        calls = joined(fake_compose)
        assert "uv python install" not in calls and "uv tool install" not in calls
        assert "curl -LsSf" not in calls

    def test_rootless_gate_failure_aborts_everything(self, fake_compose, capsys):
        env_base(fake_compose, podman=False)
        env_uv(fake_compose)
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        assert "rootless Podman" in capsys.readouterr().out
        calls = joined(fake_compose)
        assert "uv python install" not in calls and "uv tool install" not in calls
        assert "curl -LsSf" not in calls


# ========================= install：失败分类 =========================

class TestInstallFailures:
    def test_uv_installer_network_error_hint(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose, present=False)
        fake_compose.script["curl -LsSf"] = make_result(
            ok=False, exit_code=6, stderr="curl: (6) Could not resolve host: astral.sh"
        )
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        out = capsys.readouterr().out
        assert "uv 引导器" in out and "[FAIL" in out
        calls = joined(fake_compose)
        assert f"{UV} python install" not in calls

    def test_python_download_failure_mirror_hint(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        fr = fake_compose
        fr.script[f"{UV} python list"] = make_result(stdout="cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3\n")
        fr.script[f"{UV} python install"] = make_result(
            ok=False, exit_code=1, stderr="error: failed to download cpython-3.14.0"
        )
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        out = capsys.readouterr().out
        assert "托管 Python 3.14" in out
        assert "UV_PYTHON_INSTALL_MIRROR" in out
        assert f"{UV} tool install" not in joined(fake_compose)

    def test_tool_install_index_failure_hint(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        fake_compose.script[f"{UV} tool list"] = make_result(stdout="")
        fake_compose.script[f"{UV} tool install"] = make_result(
            ok=False, exit_code=1,
            stderr="error sending request for url (https://pypi.org/simple/pyyaml/)",
        )
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        assert "UV_DEFAULT_INDEX" in capsys.readouterr().out

    def test_shim_acceptance_failure(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        fake_compose.script[f"{SHIM_MAIN} version --short"] = make_result(
            ok=False, exit_code=1, stderr="RuntimeError: Python 3.14 required"
        )
        fake_compose.script[f"{SHIM_ALIAS} version --short"] = make_result(
            ok=False, exit_code=1, stderr="RuntimeError: Python 3.14 required"
        )
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        out = capsys.readouterr().out
        assert "shim" in out and "安装成功" not in out

    def test_shim_version_mismatch_is_fail(self, fake_compose, capsys):
        env_base(fake_compose)
        env_uv(fake_compose)
        env_python314(fake_compose)
        env_install_pass(fake_compose)
        env_xc_shims(fake_compose, main_ver=SAMPLE_VERSION, alias_ver="1.5.0")
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", SRC_WIN]
        )
        assert ret == 1
        assert "不一致" in capsys.readouterr().out


# ========================= verify =========================

class TestVerify:
    def test_all_pass_no_smoke(self, fake_compose, capsys):
        env_base(fake_compose)
        env_xc_shims(fake_compose)
        ret = cli.main(["compose", "verify", DISTRO])
        assert ret == 0
        out = capsys.readouterr().out
        assert "验收通过" in out
        assert "base64 -d" not in joined(fake_compose)

    def test_shim_missing_fail(self, fake_compose, capsys):
        env_base(fake_compose)
        env_xc_absent(fake_compose)
        ret = cli.main(["compose", "verify", DISTRO])
        assert ret == 1
        assert "compose install" in capsys.readouterr().out

    def test_version_mismatch_fail(self, fake_compose):
        env_base(fake_compose)
        env_xc_shims(fake_compose, main_ver=SAMPLE_VERSION, alias_ver="1.6.0+xuan.2")
        assert cli.main(["compose", "verify", DISTRO]) == 1

    def test_smoke_pass_end_to_end(self, fake_compose, capsys):
        env_base(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script["base64 -d"] = make_result()
        ret = cli.main(["compose", "verify", DISTRO, "--smoke"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "compose 冒烟" in out and "[PASS" in out
        assert joined(fake_compose).count("base64 -d") == 1

    def test_smoke_skipped_when_gate_fails(self, fake_compose, capsys):
        env_base(fake_compose, podman=False)
        ret = cli.main(["compose", "verify", DISTRO, "--smoke"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "前置检查存在 FAIL" in out
        assert "base64 -d" not in joined(fake_compose)

    def test_smoke_failure_reported(self, fake_compose, capsys):
        env_base(fake_compose)
        env_xc_shims(fake_compose)
        fake_compose.script["base64 -d"] = make_result(
            ok=False, exit_code=1, stderr="Error: cannot connect to podman"
        )
        ret = cli.main(["compose", "verify", DISTRO, "--smoke"])
        assert ret == 1
        assert "compose 冒烟" in capsys.readouterr().out

    def test_readonly_sentinel(self, fake_compose):
        env_base(fake_compose)
        env_xc_shims(fake_compose)
        assert cli.main(["compose", "verify", DISTRO]) == 0
        calls = joined(fake_compose)
        for forb in FORBIDDEN_ANY + ("uv tool install", "uv python install", "curl"):
            assert forb not in calls


# ========================= CLI 装配与用法错误 =========================

class TestComposeCliPlumbing:
    def test_group_without_subcommand_help_has_gpl_notice(self, capsys):
        assert cli.main(["compose"]) == 2
        out = capsys.readouterr().out
        assert "preflight" in out and "install" in out and "verify" in out
        assert "GPL-2.0-only" in out

    def test_malformed_source_is_usage_error_zero_wsl(self, fake_compose, capsys):
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes", "--source", "bad name!"]
        )
        assert ret == 2
        err = capsys.readouterr().err
        assert "安装源" in err
        assert fake_compose.calls == []

    def test_editable_with_url_source_is_usage_error(self, fake_compose, capsys):
        ret = cli.main(
            ["compose", "install", DISTRO, "--yes",
             "--source", "git+https://github.com/o/r.git", "--editable"]
        )
        assert ret == 2
        assert "editable" in capsys.readouterr().err.lower()
        assert fake_compose.calls == []
