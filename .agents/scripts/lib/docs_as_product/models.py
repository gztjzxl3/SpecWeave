# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 数据模型：
# 定义检查过程中使用的全部 dataclass 与 JSON 序列化契约——
# Finding / CheckResult / DocNode / DocsTree / Report / DocsProductConfig。

from dataclasses import dataclass, field
from pathlib import Path

from .constants import (
    DEFAULT_BUILD_DIR,
    STABLE_METADATA_FIELDS,
    TYPE_UNCLASSIFIED,
)

# severity 取值
SEVERITY_ERROR = "error"
SEVERITY_WARN = "warn"
SEVERITY_INFO = "info"


@dataclass
class DocsProductConfig:
    """docs-as-product 校验配置。

    所有字段均有默认值，可由 TOML 配置文件覆盖。
    """

    docs_dir: str = "docs"
    build_dir: str = DEFAULT_BUILD_DIR
    canonical_base: str = ""
    stable_fields: frozenset[str] = STABLE_METADATA_FIELDS
    run_external: bool = True
    external_timeout: int = 300

    @classmethod
    def from_toml(cls, path: str | Path) -> "DocsProductConfig":
        """从 TOML 文件加载配置；缺失文件回退默认配置。"""
        import tomllib

        p = Path(path)
        if not p.exists():
            return cls()
        with p.open("rb") as f:
            data = tomllib.load(f)
        section = data.get("docs-as-product", data)
        kwargs: dict = {}
        for key in ("docs_dir", "build_dir", "canonical_base",
                    "run_external", "external_timeout"):
            if key in section:
                kwargs[key] = section[key]
        if "stable_fields" in section and isinstance(section["stable_fields"], list):
            kwargs["stable_fields"] = frozenset(section["stable_fields"])
        return cls(**kwargs)


@dataclass
class Finding:
    """单条检查发现。"""

    gate: str
    severity: str
    code: str
    message: str
    file: str | None = None

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
        }


@dataclass
class CheckResult:
    """单个检查点的二元结论。"""

    gate: str
    name: str
    passed: bool
    severity: str = SEVERITY_ERROR
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass
class DocNode:
    """单个文档页面的解析结果。"""

    path: Path
    rel_path: str
    title: str = ""
    doc_type: str = TYPE_UNCLASSIFIED
    metadata: dict[str, object] = field(default_factory=dict)
    head_meta: dict[str, str] = field(default_factory=dict)
    orphan: bool = False
    in_toctree: bool = False
    toctree_refs: list[str] = field(default_factory=list)
    has_lead: bool = False
    heading_ok: bool = True
    units: int = 1
    is_index: bool = False

    def to_dict(self) -> dict:
        return {
            "path": self.rel_path,
            "title": self.title,
            "doc_type": self.doc_type,
            "orphan": self.orphan,
            "in_toctree": self.in_toctree,
            "has_lead": self.has_lead,
            "heading_ok": self.heading_ok,
            "units": self.units,
            "is_index": self.is_index,
        }


@dataclass
class DocsTree:
    """扫描得到的文档树。"""

    root: Path
    nodes: list[DocNode] = field(default_factory=list)
    by_rel: dict[str, DocNode] = field(default_factory=dict)

    def add(self, node: DocNode) -> None:
        self.nodes.append(node)
        self.by_rel[node.rel_path] = node

    def get(self, rel_path: str) -> DocNode | None:
        return self.by_rel.get(rel_path)

    def __len__(self) -> int:
        return len(self.nodes)


@dataclass
class Report:
    """一次检查的完整报告。"""

    gate: str
    title: str
    root: Path | None = None
    findings: list[Finding] = field(default_factory=list)
    checks: list[CheckResult] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def add_check(self, check: CheckResult) -> CheckResult:
        self.checks.append(check)
        if not check.passed:
            self.findings.append(
                Finding(
                    gate=check.gate,
                    severity=check.severity,
                    code=check.name,
                    message=check.message,
                )
            )
        return check

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == SEVERITY_WARN]

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "title": self.title,
            "root": str(self.root) if self.root else None,
            "passed": self.passed,
            "per_gate": {
                self.gate: {
                    "passed": self.passed,
                    "errors": len(self.errors),
                    "warnings": len(self.warnings),
                }
            },
            "checks": [c.to_dict() for c in self.checks],
            "findings": [f.to_dict() for f in self.findings],
            "extra": self.extra,
        }
