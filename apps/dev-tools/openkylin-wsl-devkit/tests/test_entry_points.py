"""模块入口契约：python -m okw 与 python -m okw.cli 行为等价。

以 runpy 在进程内执行两个 __main__ 模块，验证 --version 正常退出（0）
与无参数打印帮助（2），并顺带覆盖入口桥接代码。
"""

import runpy

import pytest

from okw import __version__


@pytest.mark.parametrize("module_name", ["okw", "okw.cli"])
def test_dash_m_version(module_name, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", [module_name, "--version"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module(module_name, run_name="__main__", alter_sys=True)
    assert exc.value.code == 0
    assert f"okw {__version__}" in capsys.readouterr().out


@pytest.mark.parametrize("module_name", ["okw", "okw.cli"])
def test_dash_m_no_args_prints_help_exit_2(module_name, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", [module_name])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module(module_name, run_name="__main__", alter_sys=True)
    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().out.lower()
