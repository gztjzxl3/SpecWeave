"""xuan-compose（xc）子组命令：preflight / install / verify。

与 podman_cmds 同构：本模块只做参数解包、用法闸门与调用编排；
判定矩阵、报告类型与格式化函数都在领域模块 okw.compose。

用法闸门（安装源形态、--editable 适用范围）必须在任何 WSL 调用前完成，
保证非法输入零副作用。
"""

import argparse
import sys

from okw import compose


def cmd_preflight(args: argparse.Namespace) -> int:
    """CLI 入口：okw compose preflight <发行版> [--source 来源]。"""
    report = compose.preflight_check(args.name, source=getattr(args, "source", None))
    print(compose.format_preflight(report))
    return report.exit_code()


def cmd_install(args: argparse.Namespace) -> int:
    """CLI 入口：okw compose install <发行版> --source 来源 [--yes] [--editable]。"""
    source = args.source
    try:
        kind = compose.classify_source(source)
    except ValueError as exc:
        print(f"安装源无效：{exc}", file=sys.stderr)
        return 2
    if getattr(args, "editable", False) and kind != "local":
        print(
            "用法错误：--editable 仅支持本地目录源（--source 需为本地路径）；"
            "URL/包名源由 uv 自行管理构建形态",
            file=sys.stderr,
        )
        return 2

    if not getattr(args, "yes", False):
        report = compose.InstallReport(distro_name=args.name, missing_yes=True)
        print(compose.format_install(report))
        return report.exit_code()

    report = compose.install_run(args.name, source, editable=bool(args.editable))
    print(compose.format_install(report))
    return report.exit_code()


def cmd_verify(args: argparse.Namespace) -> int:
    """CLI 入口：okw compose verify <发行版> [--smoke]。"""
    report = compose.verify_run(args.name, smoke=bool(getattr(args, "smoke", False)))
    print(compose.format_verify(report))
    return report.exit_code()
