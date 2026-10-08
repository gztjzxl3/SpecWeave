# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 结构校验（能力①）：
# Diátaxis 四型分区归属 + toctree/orphan 一致性。
# 对应模式检验标准②：结构无逃逸——全站无 :orphan:，未挂载页面视为不存在。

from pathlib import Path

from .constants import DIATAXIS_TYPES, TYPE_UNCLASSIFIED
from .discovery import _infer_type_from_metadata, _infer_type_from_path
from .models import (
    CheckResult,
    DocsTree,
    Finding,
    Report,
    SEVERITY_ERROR,
    SEVERITY_WARN,
)

GATE = "structure"

CODE_ORPHAN = "DAP-STRUCT-ORPHAN"
CODE_UNMOUNTED = "DAP-STRUCT-UNMOUNTED"
CODE_UNCLASSIFIED = "DAP-STRUCT-UNCLASSIFIED"
CODE_TYPE_CONFLICT = "DAP-STRUCT-TYPE-CONFLICT"


def check_structure(tree: DocsTree) -> Report:
    """校验文档树的四型分区与 toctree/orphan 一致性。

    检查项：
      1. 显式 ``:orphan:`` 逃逸页 → error；
      2. 非索引页未被任何 toctree 挂载 → error；
      3. 无法识别四型归属 → warn；
      4. frontmatter 显式类型与路径推断冲突 → warn。
    """
    report = Report(
        gate=GATE,
        title="结构校验：Diátaxis 四型分区与 toctree/orphan 一致性",
        root=tree.root,
    )

    type_counts = {t: 0 for t in DIATAXIS_TYPES}
    type_counts[TYPE_UNCLASSIFIED] = 0
    orphan_pages: list[str] = []
    unmounted_pages: list[str] = []

    for node in tree.nodes:
        type_counts[node.doc_type] = type_counts.get(node.doc_type, 0) + 1

        if node.orphan:
            orphan_pages.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_ERROR,
                    code=CODE_ORPHAN,
                    message="页面以 :orphan: 逃逸 toctree 挂载，违反结构无逃逸约束",
                    file=node.rel_path,
                )
            )

        if not node.is_index and not node.in_toctree:
            unmounted_pages.append(node.rel_path)
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_ERROR,
                    code=CODE_UNMOUNTED,
                    message="页面未被任何 toctree 挂载，读者无法导航到达",
                    file=node.rel_path,
                )
            )

        if node.doc_type == TYPE_UNCLASSIFIED and not node.is_index:
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_WARN,
                    code=CODE_UNCLASSIFIED,
                    message="无法识别 Diátaxis 类型，建议归入四型目录或在 frontmatter 声明",
                    file=node.rel_path,
                )
            )

        # 显式声明与路径推断交叉核对
        explicit = _infer_type_from_metadata(node.metadata)
        inferred = _infer_type_from_path(tuple(Path(node.rel_path).parts))
        if (
            explicit is not None
            and inferred != TYPE_UNCLASSIFIED
            and explicit != inferred
        ):
            report.add_finding(
                Finding(
                    gate=GATE,
                    severity=SEVERITY_WARN,
                    code=CODE_TYPE_CONFLICT,
                    message=f"frontmatter 声明类型 {explicit} 与路径推断 {inferred} 冲突",
                    file=node.rel_path,
                )
            )

    report.add_check(
        CheckResult(
            gate=GATE,
            name="无 :orphan: 逃逸页",
            passed=not orphan_pages,
            message=(
                f"发现 {len(orphan_pages)} 个逃逸页"
                if orphan_pages
                else "全站无 :orphan: 逃逸"
            ),
        )
    )
    report.add_check(
        CheckResult(
            gate=GATE,
            name="无未挂载页面",
            passed=not unmounted_pages,
            message=(
                f"发现 {len(unmounted_pages)} 个未挂载页面"
                if unmounted_pages
                else "全部非索引页均已挂载 toctree"
            ),
        )
    )

    report.extra["type_counts"] = type_counts
    report.extra["total_pages"] = len(tree.nodes)
    return report
