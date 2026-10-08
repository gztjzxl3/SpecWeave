# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 公共 API——
# 把《文档即产品经营法》固化为可执行能力：
#   scan_docs 扫描文档树；check_structure 校验 Diátaxis 四型与 toctree/orphan；
#   check_quality_gates 执行 G1–G4 + V 门；check_metadata_drift 检查漂移（F-021）；
#   check_reader_contract 校验读者契约；scaffold_metrics 生成 M1–M5 面板脚手架。

from .cli import main
from .discovery import scan_docs
from .metadata_drift import check_metadata_drift
from .metrics import scaffold_metrics
from .models import (
    CheckResult,
    DocNode,
    DocsProductConfig,
    DocsTree,
    Finding,
    Report,
)
from .quality_gates import check_quality_gates
from .reader_contract import check_reader_contract
from .structure import check_structure

__all__ = [
    "main",
    "scan_docs",
    "check_structure",
    "check_quality_gates",
    "check_metadata_drift",
    "check_reader_contract",
    "scaffold_metrics",
    "DocsProductConfig",
    "DocsTree",
    "DocNode",
    "Report",
    "Finding",
    "CheckResult",
]
