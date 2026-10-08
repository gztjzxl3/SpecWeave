#!/usr/bin/env python3
"""lib/api_docs.py — .agents/scripts/lib/ API 文档生成工具

提供 lib/ 共享库的 API 参考文档生成能力，支持单文件输出和拆分文档模式。

## 使用方式

```python
from lib.api_docs import generate_api_docs, write_split_docs

# 单文件 Markdown
docs = generate_api_docs()

# 拆分文档到 lib/docs/
from pathlib import Path
written = write_split_docs(Path("lib/"))
```

CLI 模式：`python lib/api_docs.py --help`
"""


# 版本校验：相对导入共享库（depth=0）
from .python310_version_check import enforce_python310

enforce_python310()

import sys
import argparse
from pathlib import Path

if __package__ in (None, ""):
    SCRIPTS_DIR = Path(__file__).resolve().parents[1]
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

from lib._api_modules_data import get_module_definitions
from lib.atomic_write import atomic_write_text
from lib.markdown import update_marker_region

# README 自动生成区域标记：生成器仅替换两标记之间的内容，
# 标记之外的人工维护章节（如「Windows 平台陷阱」）原样保留。
API_DOCS_START = "<!-- API_DOCS_START -->"
API_DOCS_END = "<!-- API_DOCS_END -->"

_MODULES = None


def _get_modules():
    global _MODULES
    if _MODULES is not None:
        return _MODULES
    _MODULES = get_module_definitions()
    return _MODULES


_DEV_WORKFLOW = [
    "## 新增脚本开发流程\n",
    "新建 `.agents/scripts/` 下的脚本前，请遵循以下流程：\n",
    "1. **先查本文件**，确认 lib/ 是否已有可复用的函数",
    "2. **优先使用共享函数**，避免重复实现相同逻辑",
    "3. 如确需新功能，先考虑是否应提取到 lib/ 供其他脚本复用",
    "4. 脚本头部添加 sys.path 设置：",
    "```python",
    "import sys",
    "from pathlib import Path",
    "SCRIPTS_DIR = Path(__file__).resolve().parent",
    "if str(SCRIPTS_DIR) not in sys.path:",
    "    sys.path.insert(0, str(SCRIPTS_DIR))",
    "```",
    "5. 使用 `add_common_args(parser)` 注册通用参数（--path/--json）",
    "6. 使用 `print_pass/print_warn/print_error/print_summary` 输出检查结果",
    "7. 完成后运行 `python check-duplication.py` 检查是否引入新的重复代码\n",
]


def generate_api_docs() -> str:
    """生成单文件 API 参考文档 Markdown 内容（向后兼容）。"""
    modules = _get_modules()
    sections = []

    sections.append("# .agents/scripts/lib/ API 参考\n")
    sections.append("> 本文档由 `lib/api_docs.py` 中的 `generate_api_docs()` 自动生成，描述共享库所有公开模块和函数。\n")
    sections.append("## 目录\n")
    for m in modules:
        anchor = m["title"].lower().replace(" — ", "-").replace(" ", "-").replace(".", "").replace("/", "")
        sections.append(f"- [{m['title']}](#{anchor})")
    sections.append("")
    sections.append("## README 生成建议\n")
    sections.append("- **预览输出**：可直接运行 `python .agents/scripts/lib/api_docs.py` 查看生成内容。")
    sections.append("- **拆分模式（推荐）**：运行 `python .agents/scripts/lib/api_docs.py --split` 自动生成分片文档到 `lib/docs/` 目录。")
    sections.append("- **禁止整体覆写 README**：`README.md` 含人工维护章节，直接写回本函数输出会静默丢失它们；请统一使用 `--split`，它只更新 `<!-- API_DOCS_START -->` 与 `<!-- API_DOCS_END -->` 标记之间的自动生成区域。")
    sections.append("- **不推荐**：`python .agents/scripts/lib/api_docs.py | Set-Content ...`。在 Windows PowerShell 文本管道场景下，中文内容可能被错误转码。\n")

    for m in modules:
        sections.append("---\n")
        sections.append(f"## {m['title']}\n")
        if m.get("handwritten"):
            sections.append(f"> 本模块为手写分片，内容见 [`docs/{m['filename']}`](docs/{m['filename']})。\n")
        sections.extend(m.get("body", []))

    sections.append("\n---\n")
    sections.extend(_DEV_WORKFLOW)

    sections.append("## 相关模式\n")
    sections.append("- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
    sections.append("- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")

    return "\n".join(sections)


def _module_frontmatter(module_id, title, source_file, toml_ref):
    return (
        "---\n"
        f'id: "{module_id}"\n'
        f'title: "{title}"\n'
        f'source: "{source_file}"\n'
        f'x-toml-ref: "{toml_ref}"\n'
        "---\n"
    )


def _nav_prev(modules, idx):
    if idx == 0:
        return None
    prev = modules[idx - 1]
    return f"[← {prev['title'].split(' — ')[1] if ' — ' in prev['title'] else prev['title']}]({prev['filename']})"


def _nav_next(modules, idx):
    if idx >= len(modules) - 1:
        return None
    nxt = modules[idx + 1]
    return f"[{nxt['title'].split(' — ')[1] if ' — ' in nxt['title'] else nxt['title']} →]({nxt['filename']})"


def _split_docs_block(modules) -> str:
    """构造 README 自动生成区域（导航表 + 文档生成说明 + 开发流程 + 相关模式）。"""
    index_lines = []
    index_lines.append("## 文档导航\n")
    index_lines.append("| 文档 | 模块 | 说明 |")
    index_lines.append("|------|------|------|")
    for m in modules:
        desc = m.get("desc") or (
            m["title"].split(" — ")[1] if " — " in m["title"] else m["title"]
        )
        mod_name = m["title"].split(" — ")[0]
        index_lines.append(f"| [docs/{m['filename']}](docs/{m['filename']}) | `{mod_name}` | {desc} |")
    index_lines.append("")
    index_lines.append("## 文档生成\n")
    index_lines.append(f"- **拆分模式（当前使用）**：索引页 + {len(modules)}个模块分片文档，位于 `lib/docs/` 目录")
    index_lines.append("- **重新生成**：运行 `python .agents/scripts/lib/api_docs.py --split`（仅更新自动生成区域，人工章节保留）")
    index_lines.append("- **单文件预览**：运行 `python .agents/scripts/lib/api_docs.py` 输出到 stdout\n")
    index_lines.append("---\n")
    index_lines.extend(_DEV_WORKFLOW)
    index_lines.append("## 相关模式\n")
    index_lines.append("- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
    index_lines.append("- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")
    return "\n".join(index_lines)


def write_split_docs(lib_dir: Path) -> list[Path]:
    """将 API 文档拆分为索引页 + 各模块独立文档，写入 lib/docs/ 目录。

    安全设计（修复 --split 覆写丢人工内容的缺陷）：
      1. 标记区域：README.md 仅更新 ``<!-- API_DOCS_START -->`` 与
         ``<!-- API_DOCS_END -->`` 之间的自动生成区域；区域外的人工维护章节
         （如「Windows 平台陷阱」）原样保留。
      2. 手写分片：注册表中 ``handwritten: True`` 的条目（如 15-testing、
         16-sphinx-config）仅参与索引/导航，其分片文件由人工维护，不覆写。

    Returns:
        写入的文件路径列表。
    """
    modules = _get_modules()
    docs_dir = lib_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    written = []

    for idx, m in enumerate(modules):
        if m.get("handwritten"):
            continue
        doc_id = f"lib-api-{m['slug']}"
        toml_ref = f"../../../../.meta/toml/.agents/scripts/lib/docs/{m['filename'].replace('.md', '.toml')}"
        source_ref = f"lib/api_docs.py#{m['slug']}"

        lines = []
        lines.append(_module_frontmatter(doc_id, m["title"], source_ref, toml_ref))
        lines.append(f"# {m['title']}\n")
        lines.extend(m["body"])

        lines.append("---\n")
        lines.append("## 相关模式\n")
        lines.append("- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)")
        lines.append("- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)")
        lines.append("")
        lines.append("---\n")

        nav_parts = []
        prev_link = _nav_prev(modules, idx)
        next_link = _nav_next(modules, idx)
        if prev_link:
            nav_parts.append(f"← 上一章: {prev_link}")
        nav_parts.append("**[返回索引](../README.md)**")
        if next_link:
            nav_parts.append(f"下一章 → {next_link}")
        lines.append(" | ".join(nav_parts) + "\n")

        content = "\n".join(lines)
        out_path = docs_dir / m["filename"]
        atomic_write_text(out_path, content, encoding="utf-8")
        written.append(out_path)

    readme_path = lib_dir / "README.md"
    readme_toml_ref = "../../../.meta/toml/.agents/scripts/lib/README.toml"
    index_block = _split_docs_block(modules)

    if not readme_path.exists():
        # 首次生成：不存在人工内容，写入带标记的完整骨架
        atomic_write_text(
            readme_path,
            "\n".join(
                [
                    _module_frontmatter("lib-api", ".agents/scripts/lib/ API 参考", "lib/api_docs.py", readme_toml_ref),
                    "# .agents/scripts/lib/ API 参考",
                    "",
                    "> 本文档由 `lib/api_docs.py` 自动生成，描述共享库所有公开模块和函数。",
                    "",
                    API_DOCS_START,
                    "",
                    index_block,
                    "",
                    API_DOCS_END,
                    "",
                ]
            ),
            encoding="utf-8",
        )
    else:
        existing = readme_path.read_text(encoding="utf-8")
        if API_DOCS_START not in existing or API_DOCS_END not in existing:
            raise ValueError(
                f"{readme_path} 缺少 {API_DOCS_START} / {API_DOCS_END} 标记，"
                "已拒绝覆写以免丢失人工维护内容；请先手工补入标记再运行 --split"
            )
        update_marker_region(readme_path, API_DOCS_START, API_DOCS_END, index_block)

    written.insert(0, readme_path)

    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 lib/ API 参考文档")
    parser.add_argument("--split", action="store_true", help="拆分模式：生成分片文档到 lib/docs/ 并更新 README.md")
    args = parser.parse_args()

    lib_dir = Path(__file__).resolve().parent
    if args.split:
        written = write_split_docs(lib_dir)
        project_root = lib_dir.parent.parent.parent
        for p in written:
            print(f"  写入: {p.relative_to(project_root)}")
        print(f"\n共写入 {len(written)} 个文件（1个索引页 + {len(written)-1}个模块文档）")
    else:
        print(generate_api_docs())

