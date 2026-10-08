"""守护门禁：白名单文件禁止 ``from __future__ import annotations``（PEP 563 样板）。

红线依据：``.agents/rules/ai-coding-guidelines.md`` 技术红线——Python 3.14 起
PEP 649 已默认惰性注解，PEP 563 future import 冗余且语义有别；仅当代码确实
依赖延迟求值（递归类型别名、模块级前置引用且无法前移）且 ``requires-python``
明确时方可豁免。

范围说明：``.agents/scripts`` 树内仍有存量文件使用该 import（约 96 处，含
``mdi/generators`` 代码生成模板的语料惯性，属另案批量治理），故本守护采用
**白名单制**——仅守护已完成整改的文件；新增/整改文件须同步加入
``_GUARDED_FILES``。检测基于 AST（只认真实 ``ImportFrom`` 节点），注释、
文档字符串与本守护自身的字符串常量均不误报。

特殊守护：``lib/python310_version_check.py`` 的职责是在 Python 3.8/3.9 下
也能导入并显示友好错误，删除 PEP 563 后其注解会在定义期被真实求值，因此
该文件的注解语法必须保持 3.8 可求值（禁止 PEP 585 内置泛型下标与 PEP 604
``X | Y`` 联合语法），由 ``test_py38_compatible_annotations`` 守护。
"""

import ast
import sys
from pathlib import Path

import pytest

_SCRIPTS_ROOT = Path(__file__).resolve().parents[1]

# 已完成 PEP 563 整改、任何时候都不得加回 future import 的文件（相对 .agents/scripts）
_GUARDED_FILES = [
    _SCRIPTS_ROOT / "lib" / "python310_version_check.py",
]

# 防止路径写错导致守护空转（收集期即失败）
for _guarded in _GUARDED_FILES:
    assert _guarded.is_file(), "守护目标不存在: {}".format(_guarded)

# PEP 585：内置容器泛型下标（dict[str, ...] 等）仅 Python 3.9+ 可在注解外求值，
# 无 PEP 563 时 3.8 定义期即抛 TypeError
_PEP585_BUILTIN_GENERICS = frozenset(
    {"dict", "list", "tuple", "set", "frozenset", "type"}
)


def _has_future_annotations(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.module != "__future__":
            continue
        if any(alias.name == "annotations" for alias in node.names):
            return True
    return False


@pytest.mark.parametrize(
    "path",
    _GUARDED_FILES,
    ids=lambda p: p.relative_to(_SCRIPTS_ROOT).as_posix(),
)
def test_no_future_annotations(path: Path) -> None:
    assert not _has_future_annotations(path), (
        "{} 含冗余的 PEP 563 future import；该文件不依赖注解延迟求值，"
        "直接删除该行（红线见 .agents/rules/ai-coding-guidelines.md）".format(
            path.relative_to(_SCRIPTS_ROOT).as_posix()
        )
    )


def _iter_annotation_nodes(tree: ast.AST):
    """收集函数签名、返回值与变量注解的全部注解表达式节点。"""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            candidates = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
            for arg in candidates:
                if arg.annotation is not None:
                    yield arg.annotation
            if args.vararg is not None and args.vararg.annotation is not None:
                yield args.vararg.annotation
            if args.kwarg is not None and args.kwarg.annotation is not None:
                yield args.kwarg.annotation
            if node.returns is not None:
                yield node.returns
        elif isinstance(node, ast.AnnAssign) and node.annotation is not None:
            yield node.annotation


@pytest.mark.parametrize(
    "path",
    _GUARDED_FILES,
    ids=lambda p: p.relative_to(_SCRIPTS_ROOT).as_posix(),
)
def test_py38_compatible_annotations(path: Path) -> None:
    """守护文件注解必须可在 Python 3.8 运行时（无 PEP 563）求值。

    禁止：PEP 585 内置泛型下标（3.9+）、PEP 604 ``X | Y`` 联合（3.10+）。
    ``typing.Dict`` 等 typing 模块泛型在 3.8 即支持下标，不受限制。
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations = []
    for annotation in _iter_annotation_nodes(tree):
        for sub in ast.walk(annotation):
            if (
                isinstance(sub, ast.Subscript)
                and isinstance(sub.value, ast.Name)
                and sub.value.id in _PEP585_BUILTIN_GENERICS
            ):
                violations.append(
                    "PEP 585 内置泛型下标 {}[...] 需 Python 3.9+（行 {}）".format(
                        sub.value.id, sub.lineno
                    )
                )
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.BitOr):
                violations.append(
                    "PEP 604 X | Y 联合注解需 Python 3.10+（行 {}）".format(
                        sub.lineno
                    )
                )
    assert not violations, "{} 注解破坏 Python 3.8 兼容承诺：\n  {}".format(
        path.relative_to(_SCRIPTS_ROOT).as_posix(), "\n  ".join(violations)
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
