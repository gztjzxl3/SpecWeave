# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 元数据漂移检查（能力③，反模式 F-021）：
# 页面 head 仅允许跨版本稳定字段；环境/构建期字段（version/deployment-id/
# published-at 等）写入页面会造成无限回归。
# 对应模式检验标准④：元数据无漂移，canonical 与基准一致。

from .constants import DRIFT_FIELD_HINTS, DRIFT_META_NAMES
from .models import (
    CheckResult,
    DocsProductConfig,
    DocsTree,
    Finding,
    Report,
    SEVERITY_ERROR,
    SEVERITY_WARN,
)

GATE = "metadata"

CODE_DRIFT = "DAP-META-DRIFT"
CODE_NONSTANDARD = "DAP-META-NONSTANDARD"
CODE_CANONICAL = "DAP-META-CANONICAL"


def _is_drift_field(key: str) -> bool:
    """判断字段是否为已知的漂移字段。"""
    normalized = key.lower()
    if normalized in DRIFT_FIELD_HINTS or normalized in DRIFT_META_NAMES:
        return True
    # qw-pages:version 等带冒号名 + 常见环境标识子串
    if ":" in normalized and "version" in normalized:
        return True
    return any(hint in normalized for hint in ("deployment", "published", "build-id"))


def _check_canonical(value: str, config: DocsProductConfig) -> bool:
    """canonical 值须与配置基准前缀一致。"""
    if not config.canonical_base:
        return True
    return value.startswith(config.canonical_base)


def check_metadata_drift(
    tree: DocsTree, config: DocsProductConfig | None = None
) -> Report:
    """检查页面 head 元数据是否仅含跨版本稳定字段。

    判定规则：
      1. 已知漂移字段（version/deployment-id/published-at 等）→ error；
      2. 不在稳定字段白名单的其他字段 → warn；
      3. 配置了 ``canonical_base`` 时，canonical 须以其为前缀 → error。
    """
    config = config or DocsProductConfig()
    report = Report(
        gate=GATE,
        title="元数据漂移检查：head 仅含跨版本稳定字段（F-021）",
        root=tree.root,
    )

    drift_pages: set[str] = set()
    nonstandard_pages: set[str] = set()
    canonical_bad: list[str] = []

    for node in tree.nodes:
        for key, value in node.head_meta.items():
            if _is_drift_field(key):
                drift_pages.add(node.rel_path)
                report.add_finding(
                    Finding(
                        gate=GATE,
                        severity=SEVERITY_ERROR,
                        code=CODE_DRIFT,
                        message=(
                            f"漂移字段 '{key}' 写入页面 head；"
                            "环境/构建期信息应保留在 CI 侧，禁止写入页面（F-021）"
                        ),
                        file=node.rel_path,
                    )
                )
            elif key not in config.stable_fields:
                nonstandard_pages.add(node.rel_path)
                report.add_finding(
                    Finding(
                        gate=GATE,
                        severity=SEVERITY_WARN,
                        code=CODE_NONSTANDARD,
                        message=(
                            f"字段 '{key}' 不在跨版本稳定字段白名单中，"
                            "请确认其跨版本稳定性或加入配置白名单"
                        ),
                        file=node.rel_path,
                    )
                )

            if key == "canonical" and not _check_canonical(value, config):
                canonical_bad.append(node.rel_path)
                report.add_finding(
                    Finding(
                        gate=GATE,
                        severity=SEVERITY_ERROR,
                        code=CODE_CANONICAL,
                        message=(
                            f"canonical '{value}' 与配置基准 "
                            f"'{config.canonical_base}' 不一致"
                        ),
                        file=node.rel_path,
                    )
                )

    report.add_check(
        CheckResult(
            gate=GATE,
            name="无漂移字段",
            passed=not drift_pages,
            message=(
                f"{len(drift_pages)} 个页面含漂移字段"
                if drift_pages
                else "全部页面无环境/构建期漂移字段"
            ),
        )
    )
    report.add_check(
        CheckResult(
            gate=GATE,
            name="canonical 与基准一致",
            passed=not canonical_bad,
            message=(
                f"{len(canonical_bad)} 个页面 canonical 不一致"
                if canonical_bad
                else "canonical 均符合基准（或未配置基准）"
            ),
            severity=SEVERITY_WARN,
        )
    )

    report.extra["nonstandard_page_count"] = len(nonstandard_pages)
    return report
