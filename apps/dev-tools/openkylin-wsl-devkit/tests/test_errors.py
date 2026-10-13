"""异常体系 L0 断言：基类层次、旧导入路径、消息逐字节不变。"""

import pytest

from okw.distro import WslError
from okw.errors import OkwError
from okw.scaffold import ScaffoldError


def test_wsl_error_is_okw_error_subclass():
    assert issubclass(WslError, OkwError)


def test_scaffold_error_is_okw_error_subclass():
    assert issubclass(ScaffoldError, OkwError)


def test_wsl_error_message_preserved():
    exc = WslError("找不到 wsl.exe")
    assert isinstance(exc, Exception)
    assert str(exc) == "找不到 wsl.exe"


def test_scaffold_error_message_preserved():
    exc = ScaffoldError("未知系列代号：foo。可选：yangtze(1.0) / nile(2.0) / huanghe(3.0)")
    assert str(exc) == "未知系列代号：foo。可选：yangtze(1.0) / nile(2.0) / huanghe(3.0)"


def test_can_raise_and_catch_as_okw_error():
    with pytest.raises(OkwError) as excinfo:
        raise WslError("boom")
    assert str(excinfo.value) == "boom"


def test_unrelated_exception_is_not_okw_error():
    assert not issubclass(ValueError, OkwError)
