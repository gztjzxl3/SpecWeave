"""handler 层分支测试：不经 argparse，直接调用 commands 中的 handler。

覆盖 CLI 集成测试难以触达的分支（空列表、对象未找到、导出成败、
exec 的 -- 剥离与 stderr 回显、dput 写文件分支）。
"""

from types import SimpleNamespace

from okw import distro, scaffold
from okw.commands import distro_cmds, scaffold_cmds


def _result(ok=True, exit_code=0, stdout="", stderr=""):
    return SimpleNamespace(ok=ok, exit_code=exit_code, stdout=stdout, stderr=stderr)


class TestListHandler:
    def test_empty_list(self, monkeypatch, capsys):
        monkeypatch.setattr(distro, "list_distros", lambda: [])
        assert distro_cmds.cmd_list(SimpleNamespace()) == 0
        assert "未发现任何 WSL 发行版" in capsys.readouterr().out


class TestStatusHandler:
    def test_not_found(self, monkeypatch, capsys):
        monkeypatch.setattr(distro, "get_distro", lambda name: None)
        assert distro_cmds.cmd_status(SimpleNamespace(name="ghost")) == 1
        err = capsys.readouterr().err
        assert "ghost" in err and "不存在" in err


class TestExportHandler:
    def test_export_success(self, monkeypatch, capsys):
        monkeypatch.setattr(distro, "export_distro", lambda name, output: _result())
        args = SimpleNamespace(name="ok", output="ok.tar")
        assert distro_cmds.cmd_export(args) == 0
        assert "已导出：ok.tar" in capsys.readouterr().out

    def test_export_failure_keeps_exit_code(self, monkeypatch, capsys):
        monkeypatch.setattr(
            distro, "export_distro",
            lambda name, output: _result(False, 7, stderr="拒绝访问"),
        )
        args = SimpleNamespace(name="ok", output="ok.tar")
        assert distro_cmds.cmd_export(args) == 7
        assert "导出失败：拒绝访问" in capsys.readouterr().err


class TestExecHandler:
    def test_double_dash_stripped(self, monkeypatch):
        seen = {}

        def fake_exec(name, cmd):
            seen["cmd"] = cmd
            return _result(stdout="ok")

        monkeypatch.setattr(distro, "exec_distro", fake_exec)
        args = SimpleNamespace(name="ok", cmd=["--", "id"])
        assert distro_cmds.cmd_exec(args) == 0
        assert seen["cmd"] == ["id"]

    def test_exec_failure_exit_code_passthrough(self, monkeypatch, capsys):
        monkeypatch.setattr(
            distro, "exec_distro",
            lambda name, cmd: _result(False, 126, stderr="命令不存在"),
        )
        args = SimpleNamespace(name="ok", cmd=["badcmd"])
        assert distro_cmds.cmd_exec(args) == 126
        assert "执行失败：命令不存在" in capsys.readouterr().err

    def test_exec_success_echoes_stderr(self, monkeypatch, capsys):
        monkeypatch.setattr(
            distro, "exec_distro",
            lambda name, cmd: _result(stdout="out", stderr="warn"),
        )
        args = SimpleNamespace(name="ok", cmd=["sh"])
        assert distro_cmds.cmd_exec(args) == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == "out"
        assert captured.err.strip() == "warn"


class TestScaffoldHandler:
    def test_dput_written_to_file(self, monkeypatch, capsys):
        monkeypatch.setattr(
            scaffold, "scaffold_dput",
            lambda openkylin_id, output=None: ("片段文本", "/tmp/.dput.cf"),
        )
        args = SimpleNamespace(kind="dput", openkylin_id="u001", output=None)
        assert scaffold_cmds.cmd_scaffold(args) == 0
        assert "已写入：/tmp/.dput.cf" in capsys.readouterr().out

    def test_unknown_kind(self, capsys):
        # argparse choices 已在 CLI 层拦截；此处验证 handler 自身的防御分支。
        args = SimpleNamespace(kind="rpm", project=None, series=None, version=None,
                               output_dir=".", openkylin_id=None, output=None)
        assert scaffold_cmds.cmd_scaffold(args) == 2
        assert "未知 scaffold 类型：rpm" in capsys.readouterr().err
