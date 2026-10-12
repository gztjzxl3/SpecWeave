"""导入时 Python 版本守卫的 L0 精确断言。

不依赖真实低版本解释器：current 元组可注入；另对守卫源码做 AST 检查，
保证它在低版本上可解析（无 PEP 604 联合注解）且调用位置先于一切其他导入。
"""

import ast
import sys
from pathlib import Path

import pytest

import okw
from okw import MINIMUM_PYTHON_VERSION, require_python_version

INIT_SOURCE = (
    Path(okw.__file__).resolve().read_text(encoding="utf-8")
)


def test_minimum_version_constant():
    assert MINIMUM_PYTHON_VERSION == (3, 10)


def test_lower_major_minor_rejects():
    with pytest.raises(RuntimeError) as excinfo:
        require_python_version(current=(3, 9, 18))
    message = str(excinfo.value)
    assert "3.10" in message
    assert "3.9.18" in message


def test_boundary_three_ten_zero_passes():
    assert require_python_version(current=(3, 10, 0)) is None


def test_patch_release_does_not_change_gate():
    assert require_python_version(current=(3, 10, 99)) is None


def test_newer_minor_passes():
    assert require_python_version(current=(3, 14, 7)) is None


def test_two_element_tuple_supported():
    assert require_python_version(current=(3, 10)) is None
    with pytest.raises(RuntimeError):
        require_python_version(current=(3, 9))


def test_default_current_matches_running_interpreter():
    # 当前测试解释器满足 >=3.10，默认参数必须静默放行。
    assert sys.version_info[:2] >= (3, 10)
    assert require_python_version() is None


def test_high_threshold_default_branch_reports_running_version():
    with pytest.raises(RuntimeError) as excinfo:
        require_python_version(minimum=(99, 0))
    actual = ".".join(str(part) for part in sys.version_info[:3])
    assert actual in str(excinfo.value)
    assert "99.0" in str(excinfo.value)


def test_guard_source_has_no_pep604_union():
    tree = ast.parse(INIT_SOURCE)
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            pytest.fail(f"守卫源码存在 PEP 604 联合表达式，低版本无法解析：{ast.dump(node)}")


def test_guard_call_precedes_other_imports():
    tree = ast.parse(INIT_SOURCE)
    first_import_line = None
    guard_call_line = None
    for node in tree.body:
        if first_import_line is None and isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            if names != ["sys"]:
                first_import_line = node.lineno
        if (
            guard_call_line is None
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "require_python_version"
        ):
            guard_call_line = node.lineno
    assert guard_call_line is not None
    # 仅允许标准库 sys 出现在守卫调用之前；任何业务/第三方导入必须在守卫之后。
    assert first_import_line is None or first_import_line > guard_call_line
