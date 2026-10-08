# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 统一输出层：
# 文本（带分节标题的可读报告）与 JSON（稳定 schema）双输出，
# 单报告或多报告（all 子命令合并）共用同一契约。

from lib.cli import (
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
)

from .models import Report, SEVERITY_ERROR, SEVERITY_INFO, SEVERITY_WARN


def _print_finding(finding) -> None:
    location = f" [{finding.file}]" if finding.file else ""
    text = f"({finding.code}){location} {finding.message}"
    if finding.severity == SEVERITY_ERROR:
        print_error(text)
    elif finding.severity == SEVERITY_WARN:
        print_warn(text)
    else:
        print(f"  · {text}")


def print_report_text(report: Report) -> None:
    """打印单个报告的文本形式。"""
    print_header(report.title)
    for check in report.checks:
        if check.passed:
            print_pass(f"{check.gate} · {check.name}: {check.message}")
        else:
            printer = print_warn if check.severity == SEVERITY_WARN else print_error
            printer(f"{check.gate} · {check.name}: {check.message}")
    print()
    for finding in report.findings:
        _print_finding(finding)


def print_reports_text(reports: list[Report]) -> None:
    """打印多报告并输出合并摘要。"""
    for report in reports:
        print_report_text(report)
        print()

    total_errors = sum(len(r.errors) for r in reports)
    total_warnings = sum(len(r.warnings) for r in reports)
    total_checks = sum(len(r.checks) for r in reports)
    passed_checks = sum(
        1 for r in reports for c in r.checks if c.passed
    )
    print_summary(
        pass_count=passed_checks,
        warn_count=total_warnings,
        error_count=total_errors,
    )
    print(f"  检查点: {passed_checks}/{total_checks} 通过")


def reports_to_json(reports: list[Report]) -> dict:
    """构建合并 JSON：顶层含 per_gate 与 findings。"""
    per_gate: dict[str, dict[str, object]] = {}
    for report in reports:
        per_gate[report.gate] = {
            "passed": report.passed,
            "errors": len(report.errors),
            "warnings": len(report.warnings),
        }
    return {
        "passed": all(r.passed for r in reports),
        "per_gate": per_gate,
        "findings": [f.to_dict() for r in reports for f in r.findings],
        "reports": [r.to_dict() for r in reports],
    }
