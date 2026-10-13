#!/usr/bin/env python3

# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product CLI 装配：
# structure | gates | metadata | contract | metrics | all
# 只读原则：仅 metrics 子命令写脚手架文件；all 不触发任何写入。

import argparse
import json
import sys
from pathlib import Path

from lib.cli import add_common_args, print_header, setup_safe_output
from lib.project import resolve_project_root

from .discovery import scan_docs
from .metadata_drift import check_metadata_drift
from .metrics import scaffold_metrics
from .quality_gates import check_quality_gates
from .reader_contract import check_reader_contract
from .reporter import print_reports_text, print_report_text, reports_to_json
from .structure import check_structure

from .models import DocsProductConfig

COMMANDS = ("structure", "gates", "metadata", "contract", "metrics", "all")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docs-as-product",
        description="文档即产品：结构 / 质量门 / 元数据 / 读者契约 / 指标 校验工具",
    )
    parser.add_argument("command", choices=COMMANDS, help="执行的检查项")
    add_common_args(parser)
    parser.add_argument("--config", type=Path, default=None, help="TOML 配置文件路径")
    parser.add_argument(
        "--run-external",
        dest="run_external",
        action="store_true",
        default=True,
        help="允许调用 vale/sphinx 等外部工具（默认）",
    )
    parser.add_argument(
        "--no-external",
        dest="run_external",
        action="store_false",
        help="仅执行内置检查，不调用外部工具",
    )
    parser.add_argument(
        "--scaffold",
        type=Path,
        default=None,
        help="metrics 子命令的脚手架输出目录（默认 docs/metrics）",
    )
    return parser


def _load_config(args: argparse.Namespace) -> DocsProductConfig:
    if args.config:
        return DocsProductConfig.from_toml(args.config)
    return DocsProductConfig()


def main() -> None:
    setup_safe_output()
    parser = _build_parser()
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    docs = args.path if args.path is not None else project_root / "docs"
    config = _load_config(args)

    # metrics：唯一写文件路径，单独处理
    if args.command == "metrics":
        out_dir = args.scaffold if args.scaffold is not None else docs / "metrics"
        created = scaffold_metrics(project_root, out_dir)
        if args.json:
            print(json.dumps(
                {"created": [str(p) for p in created], "out_dir": str(out_dir)},
                ensure_ascii=False,
                indent=2,
            ))
        else:
            print_header("M1–M5 指标面板脚手架")
            if created:
                for path in created:
                    print(f"  已创建: {path}")
            else:
                print(f"  目标目录已存在同名文件，未覆盖: {out_dir}")
        sys.exit(0)

    if args.command == "structure":
        tree = scan_docs(docs, config)
        reports = [check_structure(tree)]
    elif args.command == "metadata":
        tree = scan_docs(docs, config)
        reports = [check_metadata_drift(tree, config)]
    elif args.command == "gates":
        reports = [
            check_quality_gates(
                docs, run_external=args.run_external, config=config
            )
        ]
    elif args.command == "contract":
        reports = [check_reader_contract(docs)]
    else:  # all：只读四项
        tree = scan_docs(docs, config)
        reports = [
            check_structure(tree),
            check_quality_gates(
                docs, run_external=args.run_external, config=config
            ),
            check_metadata_drift(tree, config),
            check_reader_contract(docs),
        ]

    if args.json:
        payload = (
            reports_to_json(reports)
            if len(reports) > 1
            else reports[0].to_dict()
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif len(reports) > 1:
        print_reports_text(reports)
    else:
        print_report_text(reports[0])

    sys.exit(1 if any(not r.passed for r in reports) else 0)
