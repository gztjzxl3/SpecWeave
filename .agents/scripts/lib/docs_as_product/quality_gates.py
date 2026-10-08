# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 质量门集成（能力②）：
# G1 事实与文风（vale）、G2 结构（首段+标题层级）、G3 组件复用（autodoc 单一真值）、
# G4 原子性（一文件一单元）、V 门（sphinx-build -W + doctest + sphinx-lint）。
# 外部工具缺失时降级 WARN，绝不崩溃；对应模式检验标准③。

import re
import shutil
import subprocess
from pathlib import Path

from .constants import GATE_DEFINITIONS, VGATE_COMMANDS
from .discovery import scan_docs
from .models import (
    CheckResult,
    DocsProductConfig,
    Finding,
    Report,
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARN,
)

GATE = "gates"

# 单文件允许的 H2 单元数上限，超过建议拆分
MAX_UNITS_PER_FILE = 6

# Reference 页内 autodoc 指令特征
_AUTODOC_RE = re.compile(
    r"automodule|autoclass|autofunction|automethod|autodoc", re.IGNORECASE
)
# 手写函数签名特征（疑似与代码双轨真值）
_SIGNATURE_RE = re.compile(r"^\s*[a-zA-Z_]\w*\s*\([^)]*\)\s*$", re.MULTILINE)


def _tool_available(tool: str) -> bool:
    return shutil.which(tool) is not None


def _run_command(command: str, timeout: int) -> tuple[int, str]:
    """执行外部命令，返回 (返回码, 合并输出)；超时/异常按失败处置。"""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, f"命令超时（{timeout}s）: {command}"
    except OSError as exc:
        return 1, f"命令执行失败: {exc}"


def _builtin_g2(report: Report, tree) -> None:
    """G2：每页首段与标题层级。"""
    bad_lead: list[str] = []
    bad_heading: list[str] = []
    for node in tree.nodes:
        if node.is_index:
            continue
        if not node.has_lead:
            bad_lead.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate="G2",
                    severity=SEVERITY_ERROR,
                    code="DAP-G2-LEAD",
                    message="页面缺少首段摘要，读者无法在首屏判断页面用途",
                    file=node.rel_path,
                )
            )
        if not node.heading_ok:
            bad_heading.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate="G2",
                    severity=SEVERITY_ERROR,
                    code="DAP-G2-HEADING",
                    message="标题层级跳跃或存在多个 H1，结构不合规",
                    file=node.rel_path,
                )
            )
    report.add_check(
        CheckResult(
            gate="G2",
            name="每页有首段摘要",
            passed=not bad_lead,
            message=(
                f"{len(bad_lead)} 个页面缺首段" if bad_lead else "全部页面有首段摘要"
            ),
        )
    )
    report.add_check(
        CheckResult(
            gate="G2",
            name="标题层级合规",
            passed=not bad_heading,
            message=(
                f"{len(bad_heading)} 个页面标题异常"
                if bad_heading
                else "标题层级无跳跃、单一 H1"
            ),
        )
    )


def _builtin_g3(report: Report, tree) -> None:
    """G3：Reference 以 autodoc 为单一真值源，禁止手写签名双轨维护。"""
    handwritten: list[str] = []
    for node in tree.nodes:
        if node.doc_type != "reference":
            continue
        body = node.path.read_text(encoding="utf-8", errors="replace")
        if _SIGNATURE_RE.search(body) and not _AUTODOC_RE.search(body):
            handwritten.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate="G3",
                    severity=SEVERITY_WARN,
                    code="DAP-G3-HANDWRITTEN",
                    message="Reference 页面手写函数签名且未使用 autodoc，"
                    "代码与文档将双轨漂移，应以 autodoc 为单一真值源",
                    file=node.rel_path,
                )
            )
    report.add_check(
        CheckResult(
            gate="G3",
            name="Reference 使用 autodoc",
            passed=not handwritten,
            severity=SEVERITY_WARN,
            message=(
                f"{len(handwritten)} 个 reference 页疑似手写签名"
                if handwritten
                else "reference 页均通过 autodoc 复用代码真值"
            ),
        )
    )


def _builtin_g4(report: Report, tree) -> None:
    """G4：一文件一单元；H2 单元过多建议原子拆分。"""
    multi: list[str] = []
    for node in tree.nodes:
        if node.units > MAX_UNITS_PER_FILE:
            multi.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate="G4",
                    severity=SEVERITY_WARN,
                    code="DAP-G4-MULTIUNIT",
                    message=f"页面含 {node.units} 个 H2 单元（上限 {MAX_UNITS_PER_FILE}），"
                    "建议按单一职责原子拆分",
                    file=node.rel_path,
                )
            )
    report.add_check(
        CheckResult(
            gate="G4",
            name="一文件一单元",
            passed=not multi,
            severity=SEVERITY_WARN,
            message=(
                f"{len(multi)} 个文件疑似多单元"
                if multi
                else "全部文件保持单一原子单元"
            ),
        )
    )


def _external_g1(report: Report, docs: Path, config: DocsProductConfig) -> None:
    """G1：vale 事实与文风。"""
    if not _tool_available("vale"):
        report.add_finding(
            Finding(
                gate="G1",
                severity=SEVERITY_WARN,
                code="DAP-G1-NO-TOOL",
                message="未检测到 vale，G1 事实与文风门降级未执行；"
                "安装：https://vale.sh 并配置 .vale.ini",
            )
        )
        report.add_check(
            CheckResult(
                gate="G1",
                name="vale 事实与文风",
                passed=True,
                severity=SEVERITY_WARN,
                message="工具缺失，降级跳过",
            )
        )
        return

    code, output = _run_command(
        f"vale --output=line {docs}", config.external_timeout
    )
    lines = [ln for ln in output.splitlines() if ln.strip()]
    report.add_check(
        CheckResult(
            gate="G1",
            name="vale 事实与文风",
            passed=code == 0,
            message="vale 无告警" if code == 0 else f"vale 报告 {len(lines)} 条问题",
        )
    )
    if code != 0:
        detail = " | ".join(lines[:5])
        report.add_finding(
            Finding(
                gate="G1",
                severity=SEVERITY_ERROR,
                code="DAP-G1-VALE",
                message=f"vale 检查未通过：{detail}",
            )
        )


def _external_vgate(report: Report, docs: Path, config: DocsProductConfig) -> None:
    """V 门：sphinx-build -W + doctest + sphinx-lint。"""
    out_dir = docs.parent / Path(config.build_dir).name
    for item in VGATE_COMMANDS:
        tool = item["tool"]
        if not _tool_available(tool):
            report.add_finding(
                Finding(
                    gate="V",
                    severity=SEVERITY_WARN,
                    code=f"DAP-V-NO-TOOL-{tool}",
                    message=f"未检测到 {tool}，V 门子项 {item['id']} 降级未执行；"
                    "安装：pip install sphinx sphinx-lint",
                )
            )
            report.add_check(
                CheckResult(
                    gate="V",
                    name=item["id"],
                    passed=True,
                    severity=SEVERITY_WARN,
                    message=f"{tool} 缺失，降级跳过",
                )
            )
            continue

        command = item["command"].format(docs=docs, out=out_dir)
        code, output = _run_command(command, config.external_timeout)
        report.add_check(
            CheckResult(
                gate="V",
                name=item["id"],
                passed=code == 0,
                message="通过" if code == 0 else f"{item['id']} 未通过（返回码 {code}）",
            )
        )
        if code != 0:
            tail = " | ".join(output.splitlines()[-5:]) if output else "无输出"
            report.add_finding(
                Finding(
                    gate="V",
                    severity=SEVERITY_ERROR,
                    code=f"DAP-V-{item['id'].upper()}",
                    message=f"V 门 {item['id']} 失败：{tail}",
                )
            )


def check_quality_gates(
    root: str | Path,
    *,
    run_external: bool = True,
    config: DocsProductConfig | None = None,
) -> Report:
    """执行 G1–G4 与 V 门检查。

    Args:
        root: docs 目录路径。
        run_external: 是否调用外部工具；False 时仅执行内置检查且不报工具缺失。
        config: 可选配置。

    Returns:
        汇总各门结论的 Report。
    """
    config = config or DocsProductConfig()
    docs = Path(root).resolve()
    tree = scan_docs(docs, config)

    report = Report(
        gate=GATE,
        title="质量门：G1–G4 与 V 门集成",
        root=docs,
    )

    _builtin_g2(report, tree)
    _builtin_g3(report, tree)
    _builtin_g4(report, tree)

    if run_external and config.run_external:
        _external_g1(report, docs, config)
        _external_vgate(report, docs, config)
    else:
        report.add_finding(
            Finding(
                gate=GATE,
                severity=SEVERITY_INFO,
                code="DAP-EXTERNAL-SKIPPED",
                message="已按 --no-external 跳过外部工具检查",
            )
        )

    report.extra["gate_definitions"] = [
        {"id": g["id"], "name": g["name"], "kind": g["kind"]}
        for g in GATE_DEFINITIONS
    ]
    return report
