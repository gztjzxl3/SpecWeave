# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 指标面板脚手架（能力④b）：
# 生成 M1–M5 指标的数据契约（JSON）与面板（Markdown），含 owner 占位。
# 对应模式检验标准⑤：指标闭环——有数据、有 owner、可周期复盘。

import json
from pathlib import Path

from .constants import METRICS_DEFINITIONS


def _build_records() -> list[dict[str, str]]:
    """构建带 owner 占位的指标记录。"""
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "definition": item["definition"],
            "collect": item["collect"],
            "unit": item["unit"],
            "owner": "TODO",
            "value": "",
        }
        for item in METRICS_DEFINITIONS
    ]


def _render_markdown(records: list[dict[str, str]]) -> str:
    """渲染指标面板 Markdown。"""
    lines = [
        "# 文档产品指标面板（M1–M5）",
        "",
        "> 由 docs-as-product metrics --scaffold 生成；请填写 owner 与周期数据。",
        "",
        "| 指标 | 名称 | 定义 | 采集方式 | 单位 | Owner | 当前值 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| {r['id']} | {r['name']} | {r['definition']} | "
            f"{r['collect']} | {r['unit']} | {r['owner']} | {r['value']} |"
        )
    lines += [
        "",
        "## 复盘要求",
        "",
        "- 连续 4 周有数据，各指标有明确 owner；",
        "- M3 零结果率应呈下降趋势；",
        "- 月度复盘并将结论回灌文档改进。",
        "",
    ]
    return "\n".join(lines)


def scaffold_metrics(
    root: str | Path, out_dir: str | Path
) -> list[Path]:
    """生成 M1–M5 面板脚手架。

    Args:
        root: 项目/docs 根（当前仅用于上下文校验，保留以备扩展）。
        out_dir: 脚手架输出目录。

    Returns:
        实际创建的文件路径列表；已存在的同名文件保持不变、不重复创建。
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    records = _build_records()
    files = {
        target / "metrics.json": json.dumps(records, ensure_ascii=False, indent=2),
        target / "metrics.md": _render_markdown(records),
    }

    created: list[Path] = []
    for path, content in files.items():
        if path.exists():
            continue
        path.write_text(content, encoding="utf-8")
        created.append(path)
    return created
