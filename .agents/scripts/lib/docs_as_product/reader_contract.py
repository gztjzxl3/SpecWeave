# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 读者契约校验（能力④a）：
# 四类读者（tutorial/how-to/reference/explanation）各须有一条可执行验收任务；
# Tutorial 时长 <15 分钟、Reference docstring 覆盖率 ≥90% 须有可核对声明。
# 对应模式检验标准①：读者契约可验收。

import re
from pathlib import Path

from .constants import (
    CONTRACT_FILE_CANDIDATES,
    READER_TYPES,
    REFERENCE_DOCSTRING_MIN,
    TUTORIAL_MAX_MINUTES,
)
from .models import (
    CheckResult,
    Finding,
    Report,
    SEVERITY_ERROR,
    SEVERITY_WARN,
)

GATE = "contract"

# 标题与读者类型的匹配词
_TYPE_TOKENS: dict[str, tuple[str, ...]] = {
    "tutorial": ("tutorial", "教程"),
    "how-to": ("how-to", "howto", "操作指南", "指南"),
    "reference": ("reference", "参考"),
    "explanation": ("explanation", "解释", "概念"),
}

# 可执行验收任务特征：复选框 / 编号步骤 / “验收”引导句
_TASK_RE = re.compile(
    r"(?:^[ \t]*[-*][ \t]+\[[ xX]\])"
    r"|(?:^[ \t]*\d+\.[ \t]+)"
    r"|验收",
    re.MULTILINE,
)

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+)$", re.MULTILINE)


def find_contract_file(docs_root: str | Path) -> Path | None:
    """在候选位置定位读者契约文件。"""
    root = Path(docs_root)
    for candidate in CONTRACT_FILE_CANDIDATES:
        path = root / candidate
        if path.exists():
            return path
    return None


def _split_sections(text: str) -> dict[str, str]:
    """按标题切分正文，返回 类型 → 该标题下内容（未匹配类型不收录）。"""
    headings = list(_HEADING_RE.finditer(text))
    sections: dict[str, str] = {}
    for i, match in enumerate(headings):
        heading = match.group(2).lower()
        start = match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        for reader_type, tokens in _TYPE_TOKENS.items():
            if any(token in heading for token in tokens):
                sections[reader_type] = text[start:end]
    return sections


def _has_table_row(text: str, reader_type: str) -> bool:
    """表格首列含读者类型标识。"""
    tokens = _TYPE_TOKENS[reader_type]
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if cells and any(token in cells[0] for token in tokens):
            return True
    return False


def check_reader_contract(docs_root: str | Path) -> Report:
    """校验读者契约文件是否为四类读者各提供可执行验收任务。"""
    root = Path(docs_root).resolve()
    report = Report(
        gate=GATE,
        title="读者契约校验：四类读者的可执行验收任务",
        root=root,
    )

    contract = find_contract_file(root)
    if contract is None:
        report.add_finding(
            Finding(
                gate=GATE,
                severity=SEVERITY_ERROR,
                code="DAP-CONTRACT-MISSING",
                message="未找到读者契约文件（候选："
                + "、".join(CONTRACT_FILE_CANDIDATES)
                + "）",
            )
        )
        report.add_check(
            CheckResult(
                gate=GATE,
                name="读者契约存在",
                passed=False,
                message="契约文件缺失",
            )
        )
        return report

    text = contract.read_text(encoding="utf-8", errors="replace")
    sections = _split_sections(text)

    for reader_type in READER_TYPES:
        body = sections.get(reader_type, "")
        present = bool(body) or _has_table_row(text, reader_type)
        if not present:
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_ERROR,
                    code="DAP-CONTRACT-READER",
                    message=f"契约缺少 {reader_type} 类读者的约定章节或表格行",
                    file=str(contract.relative_to(root.parent))
                    if _is_relative(contract, root.parent)
                    else str(contract),
                )
            )
            continue

        if body and not _TASK_RE.search(body):
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_ERROR,
                    code="DAP-CONTRACT-TASK",
                    message=f"{reader_type} 类读者缺少可执行验收任务（复选框/步骤/验收标准）",
                    file=contract.name,
                )
            )

    # Tutorial 时长声明
    tutorial_body = sections.get("tutorial", "")
    if tutorial_body and not re.search(
        rf"(?:<|＜|不超过|小于)\s*{TUTORIAL_MAX_MINUTES}\s*分钟|{TUTORIAL_MAX_MINUTES}\s*minutes",
        tutorial_body,
    ):
        report.add_finding(
            Finding(
                gate=GATE,
                severity=SEVERITY_WARN,
                code="DAP-CONTRACT-TIME",
                message=f"tutorial 章节未声明 <{TUTORIAL_MAX_MINUTES} 分钟完成承诺",
                file=contract.name,
            )
        )

    # Reference docstring 覆盖率声明
    reference_body = sections.get("reference", "")
    if reference_body and not re.search(
        rf"(?:≥|>=|不低于)\s*{REFERENCE_DOCSTRING_MIN}\s*%|{REFERENCE_DOCSTRING_MIN}\s*%",
        reference_body,
    ):
        report.add_finding(
            Finding(
                gate=GATE,
                severity=SEVERITY_WARN,
                code="DAP-CONTRACT-DOCSTRING",
                message=f"reference 章节未声明 docstring 覆盖率 ≥{REFERENCE_DOCSTRING_MIN}%",
                file=contract.name,
            )
        )

    report.add_check(
        CheckResult(
            gate=GATE,
            name="四类读者约定齐全",
            passed=all(
                (t in sections) or _has_table_row(text, t) for t in READER_TYPES
            ),
            message="四类读者均有约定" if report.passed else "存在缺失的读者类型约定",
        )
    )
    report.extra["contract_file"] = str(contract)
    return report


def _is_relative(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
