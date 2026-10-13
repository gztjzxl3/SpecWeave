"""CLI 表面确定性序列化器（重构安全网）。

口径说明（新旧 parser 同口径，任何一侧改变都会产生 diff）：
- 递归遍历 parser 树，覆盖二级 subparsers（podman/image）；
- 自动生成的 ``_HelpAction``（``-h/--help``）不纳入快照：它由 argparse
  统一注入，与业务命令面无关，纳入只会制造无意义噪声；
- ``_VersionAction`` 纳入并额外记录 ``version``，间接锁定 ``--version`` 输出；
- subparsers 的 ``add_parser(..., help=...)`` 文本经 ``_choices_actions``
  捕获（argparse 将其存为伪 action 而非子 parser 的 description）；
- default 用 ``repr`` 序列化以保证跨进程字节稳定。
"""

import argparse
from typing import Any, Dict, List, Optional

_SKIP_ACTION_KINDS = {"_HelpAction"}


def _repr_default(value: Any) -> str:
    return repr(value)


def _serialize_action(action: argparse.Action) -> Dict[str, Any]:
    kind = type(action).__name__
    data: Dict[str, Any] = {
        "kind": kind,
        "option_strings": list(action.option_strings),
        "dest": action.dest,
        "nargs": action.nargs,
        "required": bool(getattr(action, "required", False)),
        "metavar": action.metavar,
        "help": action.help,
        "default": _repr_default(action.default),
    }
    if isinstance(action, argparse._SubParsersAction):
        data["subparsers_dest"] = action.dest
        data["subparsers_metavar"] = action.metavar
        data["choice_helps"] = [
            {
                "option_strings": list(pseudo.option_strings),
                "dest": pseudo.dest,
                "metavar": pseudo.metavar,
                "help": pseudo.help,
            }
            for pseudo in action._choices_actions
        ]
        data["choices"] = [
            {"name": name, "parser": serialize_parser(child)}
            for name, child in action.choices.items()
        ]
    else:
        if action.choices is not None:
            data["choices"] = sorted(action.choices, key=str)
        if isinstance(action, argparse._VersionAction):
            data["version"] = action.version
    return data


def serialize_parser(parser: argparse.ArgumentParser) -> Dict[str, Any]:
    actions: List[Dict[str, Any]] = []
    for action in parser._actions:
        if type(action).__name__ in _SKIP_ACTION_KINDS:
            continue
        actions.append(_serialize_action(action))
    return {
        "prog": parser.prog,
        "description": parser.description,
        "epilog": parser.epilog,
        "actions": actions,
    }


def collect_leaf_commands(
    parser: argparse.ArgumentParser, prefix: Optional[List[str]] = None
) -> List[str]:
    """收集全部叶子命令的路径键（空格连接，如 ``podman preflight``）。"""
    prefix = prefix or []
    leaves: List[str] = []
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child in action.choices.items():
            path = prefix + [name]
            child_subs = [
                a
                for a in child._actions
                if isinstance(a, argparse._SubParsersAction)
            ]
            if child_subs:
                leaves.extend(collect_leaf_commands(child, path))
            else:
                leaves.append(" ".join(path))
    return leaves
