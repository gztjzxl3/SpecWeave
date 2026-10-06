#!/usr/bin/env python3
"""幕布（mubu.com）OPML ↔ Markdown 互转 CLI。

纯 Python 标准库实现，零第三方依赖。
基于幕布客户端原生 OPML 导出格式，零 ToS 风险。

子命令：
  info          探查 OPML 文件结构（节点数、深度、根节点）
  parse         解析 OPML，输出 JSON / HTML
  to-markdown   OPML → Markdown
  to-opml       Markdown → OPML（反向导入幕布）
  list          遍历节点树，支持关键词与深度过滤

退出码：
  0=成功  2=文件不存在  3=格式错误  4=解析失败  5=输出不可写
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

# 跨平台 UTF-8 输出（Windows PowerShell 兼容）
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class MubuNode:
    """幕布大纲节点（对应 OPML 中的 <outline> 元素）。"""

    text: str = ""
    note: str = ""
    complete: Optional[str] = None  # _complete 属性（"true"/"false"/None）
    ts: Optional[str] = None  # _ts 时间戳
    node_id: Optional[str] = None  # _id
    children: list["MubuNode"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    @property
    def depth(self) -> int:
        """子树最大深度（根节点为 1）。"""
        if self.is_leaf:
            return 1
        return 1 + max(c.depth for c in self.children)

    def count(self) -> int:
        """子树全部节点数（含自身）。"""
        return 1 + sum(c.count() for c in self.children)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "note": self.note,
            "complete": self.complete,
            "ts": self.ts,
            "id": self.node_id,
            "children": [c.to_dict() for c in self.children],
        }


# ---------------------------------------------------------------------------
# OPML → MubuNode
# ---------------------------------------------------------------------------


def parse_opml(opml_path: Path) -> MubuNode:
    """解析幕布导出的 OPML 文件为节点树。

    幕布 OPML 结构示例：
      <opml version="2.0">
        <head><title>文档标题</title></head>
        <body>
          <outline text="根节点" _complete="false" _ts="..." _id="...">
            <outline text="子节点" .../>
          </outline>
        </body>
      </opml>

    幕布私有属性命名约定（带下划线前缀）：
      _complete: 任务完成状态 "true"/"false"
      _ts: 时间戳
      _id: 节点 ID
    """
    try:
        tree = ET.parse(opml_path)
    except ET.ParseError as exc:
        raise ValueError(f"OPML 解析失败：{exc}") from exc
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"文件不存在：{opml_path}") from exc

    root = tree.getroot()
    body = root.find("body")
    if body is None:
        raise ValueError("OPML 缺少 <body> 元素，不是有效幕布 OPML")

    top_outlines = body.findall("outline")
    if not top_outlines:
        raise ValueError("OPML <body> 内无 <outline> 节点")

    # 幕布文档通常只有一个顶层 outline 作为根节点
    if len(top_outlines) == 1:
        return _outline_to_node(top_outlines[0])

    # 多顶层 outline 时，包装一个虚拟根
    virtual_root = MubuNode(text=opml_path.stem)
    for outline in top_outlines:
        virtual_root.children.append(_outline_to_node(outline))
    return virtual_root


def _outline_to_node(elem: ET.Element) -> MubuNode:
    """递归把 <outline> 元素转为 MubuNode。"""
    text = elem.get("text", "") or ""
    note = elem.get("note", "") or ""
    complete = elem.get("_complete")
    ts = elem.get("_ts")
    node_id = elem.get("_id")

    node = MubuNode(
        text=text,
        note=note,
        complete=complete,
        ts=ts,
        node_id=node_id,
    )
    for child_elem in elem.findall("outline"):
        node.children.append(_outline_to_node(child_elem))
    return node


# ---------------------------------------------------------------------------
# MubuNode → Markdown
# ---------------------------------------------------------------------------


def node_to_markdown(
    node: MubuNode,
    indent_spaces: int = 2,
    _depth: int = 0,
    _lines: list[str] | None = None,
) -> list[str]:
    """节点树转 Markdown 嵌套列表。

    幕布层级 → Markdown 缩进列表：
      根节点
        子节点1
          孙节点
        子节点2

    任务节点（_complete）转 Markdown 任务列表：
      [x] 已完成
      [ ] 未完成
    """
    if _lines is None:
        _lines = []

    prefix = " " * (indent_spaces * _depth)
    text = node.text.strip() if node.text else ""

    # 统一使用 GFM 任务列表语法 "- [ ] 文本" / "- [x] 文本" / "- 文本"
    # 保证 to-markdown 输出能被 markdown_to_node 完整回转（双向闭环）
    if node.complete == "true":
        text = f"- [x] {text}" if text else "- [x]"
    elif node.complete == "false":
        text = f"- [ ] {text}" if text else "- [ ]"
    elif text:
        text = f"- {text}"
    else:
        text = "- "

    _lines.append(f"{prefix}{text}")

    # 备注作为引用块紧随其后
    if node.note:
        note_prefix = " " * (indent_spaces * (_depth + 1))
        for line in node.note.splitlines() or [""]:
            _lines.append(f"{note_prefix}> {line}")

    for child in node.children:
        node_to_markdown(child, indent_spaces, _depth + 1, _lines)
    return _lines


def to_markdown(node: MubuNode, indent_spaces: int = 2) -> str:
    lines = node_to_markdown(node, indent_spaces=indent_spaces)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Markdown → MubuNode → OPML
# ---------------------------------------------------------------------------

# Markdown 列表项正则：可选缩进 + 标记 + 文本
# 支持：- / * / + / 1. / [x] / [ ]
_MD_LIST_RE = re.compile(
    r"^(?P<indent>\s*)"
    r"(?P<marker>[-*+]|\d+\.)\s+"
    r"(?P<checkbox>\[[ xX]\]\s+)?"
    r"(?P<text>.*)$"
)


def markdown_to_node(md_text: str, title: str = "Markdown 导入") -> MubuNode:
    """Markdown 嵌套列表 → MubuNode 树。

    解析规则：
      - 缩进（空格）决定层级
      - `-` / `*` / `+` 与 `1.` 都视为无序节点（幕布只有无序层级）
      - `[x]` / `[ ]` 复选框 → _complete 属性
      - `>` 引用块 → note 属性（紧附于上一节点）
      - 缩进用空格，Tab 按 4 空格展开
    """
    # 统一 Tab → 4 空格
    md_text = md_text.replace("\t", "    ")
    lines = md_text.splitlines()

    root = MubuNode(text=title)
    # 用栈追踪当前层级的最后一个节点
    stack: list[tuple[int, MubuNode]] = [(-1, root)]
    last_node: Optional[MubuNode] = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue

        # 引用块 → 上一节点的 note
        if line.lstrip().startswith(">"):
            content = line.lstrip().lstrip(">").strip()
            if last_node is not None:
                last_node.note = (
                    last_node.note + "\n" + content if last_node.note else content
                )
            continue

        m = _MD_LIST_RE.match(line)
        if not m:
            # 非列表行作为上一节点 note
            if last_node is not None:
                content = line.strip()
                last_node.note = (
                    last_node.note + "\n" + content if last_node.note else content
                )
            continue

        indent = len(m.group("indent").expandtabs(4))
        checkbox = m.group("checkbox")
        text = m.group("text").strip()

        complete: Optional[str] = None
        if checkbox:
            cb = checkbox.strip().lower()
            complete = "true" if cb == "[x]" else "false"

        node = MubuNode(text=text, complete=complete)

        # 找到父节点：栈顶 indent < 当前 indent
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else root
        parent.children.append(node)

        stack.append((indent, node))
        last_node = node

    # 若仅一个顶层列表项，直接作为根返回，避免虚拟根造成双层嵌套
    # 保证 OPML → MD → OPML 双向幂等（节点数与层级一致）
    if len(root.children) == 1:
        return root.children[0]
    return root


def node_to_opml(node: MubuNode, title: str = "Markdown 导入") -> str:
    """MubuNode 树 → OPML 2.0 字符串（可导入幕布客户端）。

    注意：反向转换不保留幕布私有 _ts / _id（这些由幕布客户端重新生成）。
    """
    root = ET.Element("opml", {"version": "2.0"})
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = title
    body = ET.SubElement(root, "body")

    def _append(parent_elem: ET.Element, n: MubuNode) -> None:
        attrs: dict[str, str] = {}
        if n.text:
            attrs["text"] = n.text
        if n.note:
            attrs["note"] = n.note
        if n.complete is not None:
            attrs["_complete"] = n.complete
        elem = ET.SubElement(parent_elem, "outline", attrs)
        for child in n.children:
            _append(elem, child)

    # 顶层节点直接挂到 body
    _append(body, node)

    # 美化输出（缩进）
    _indent_xml(root)
    declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return declaration + ET.tostring(root, encoding="unicode")


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """简易 XML 缩进（Python 3.9+ 可用 ET.indent）。"""
    if sys.version_info >= (3, 9):
        ET.indent(elem, space="  ", level=level)
        return
    # 兼容 3.8 的手动缩进
    pad = "\n" + "  " * (level + 1)
    if len(elem):
        if not (elem.text and elem.text.strip()):
            elem.text = pad
        for child in elem:
            _indent_xml(child, level + 1)
        if not (child.tail and child.tail.strip()):
            child.tail = "\n" + "  " * level
    else:
        if level and not (elem.tail and elem.tail.strip()):
            elem.tail = "\n" + "  " * level


# ---------------------------------------------------------------------------
# MubuNode → HTML / JSON
# ---------------------------------------------------------------------------


def node_to_html(node: MubuNode) -> str:
    """节点树 → 嵌套 <ul><li> 结构。"""

    def _build(n: MubuNode) -> str:
        if not n.children:
            inner = _escape(n.text)
            if n.note:
                inner += f'<div class="note">{_escape(n.note)}</div>'
            return f"<li>{inner}</li>"

        inner = _escape(n.text) if n.text else ""
        if n.note:
            inner += f'<div class="note">{_escape(n.note)}</div>'
        children_html = "".join(f"<li>{_build(c)}</li>" for c in n.children)
        return f"{inner}<ul>{children_html}</ul>"

    children_html = "".join(f"<li>{_build(c)}</li>" for c in node.children)
    if node.text and not node.children:
        return f"<ul><li>{_escape(node.text)}</li></ul>"
    if node.text:
        head = f"<h1>{_escape(node.text)}</h1>"
        return f"{head}<ul>{children_html}</ul>"
    return f"<ul>{children_html}</ul>"


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# 节点遍历
# ---------------------------------------------------------------------------


def walk(
    node: MubuNode,
    max_depth: int = 0,
    keyword: str = "",
    _depth: int = 0,
) -> Iterator[tuple[int, MubuNode]]:
    """深度优先遍历，可选深度与关键词过滤。"""
    if max_depth and _depth >= max_depth:
        return
    if (not keyword) or (keyword.lower() in (node.text or "").lower()) or (
        keyword.lower() in (node.note or "").lower()
    ):
        yield _depth, node
    for child in node.children:
        yield from walk(child, max_depth, keyword, _depth + 1)


# ---------------------------------------------------------------------------
# 子命令实现
# ---------------------------------------------------------------------------


def cmd_info(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        return _fail(2, f"文件不存在：{path}")
    try:
        root = parse_opml(path)
    except ValueError as exc:
        return _fail(3, str(exc))

    info = {
        "file": str(path),
        "format": "opml",
        "root_text": root.text,
        "total_nodes": root.count(),
        "max_depth": root.depth,
        "leaf_count": sum(1 for _ in walk(root) if _[1].is_leaf),
        "complete_count": sum(
            1 for _, n in walk(root) if n.complete == "true"
        ),
        "incomplete_count": sum(
            1 for _, n in walk(root) if n.complete == "false"
        ),
    }
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"文件: {info['file']}")
        print(f"根节点: {info['root_text']}")
        print(f"总节点数: {info['total_nodes']}")
        print(f"最大深度: {info['max_depth']}")
        print(f"叶子节点: {info['leaf_count']}")
        print(f"已完成任务: {info['complete_count']}")
        print(f"未完成任务: {info['incomplete_count']}")
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        return _fail(2, f"文件不存在：{path}")
    try:
        root = parse_opml(path)
    except ValueError as exc:
        return _fail(3, str(exc))

    fmt = args.format
    if fmt == "auto":
        fmt = "json"

    if fmt == "json":
        out = json.dumps(root.to_dict(), ensure_ascii=False, indent=2)
    elif fmt == "html":
        out = node_to_html(root)
        out = f"<!DOCTYPE html>\n<html><body>{out}</body></html>"
    else:
        return _fail(3, f"不支持的格式：{fmt}（可选 json/html）")

    return _emit(out, args)


def cmd_to_markdown(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        return _fail(2, f"文件不存在：{path}")
    try:
        root = parse_opml(path)
    except ValueError as exc:
        return _fail(3, str(exc))

    out = to_markdown(root, indent_spaces=args.indent)
    return _emit(out, args)


def cmd_to_opml(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        return _fail(2, f"文件不存在：{path}")
    md_text = path.read_text(encoding="utf-8")
    root = markdown_to_node(md_text, title=path.stem)
    out = node_to_opml(root, title=path.stem)
    return _emit(out, args)


def cmd_list(args: argparse.Namespace) -> int:
    path = Path(args.input)
    if not path.exists():
        return _fail(2, f"文件不存在：{path}")
    try:
        root = parse_opml(path)
    except ValueError as exc:
        return _fail(3, str(exc))

    lines: list[str] = []
    for depth, node in walk(
        root, max_depth=args.max_depth, keyword=args.keyword
    ):
        prefix = "  " * depth
        marker = "-"
        if node.complete == "true":
            marker = "[x]"
        elif node.complete == "false":
            marker = "[ ]"
        text = node.text or "(空)"
        lines.append(f"{prefix}{marker} {text}")
        if node.note:
            for note_line in node.note.splitlines():
                lines.append(f"{prefix}    > {note_line}")

    if not lines:
        print("（无匹配节点）")
        return 0
    out = "\n".join(lines) + "\n"
    return _emit(out, args)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _emit(content: str, args: argparse.Namespace) -> int:
    """输出内容：dry-run 走 stdout，否则写 -o 指定文件。"""
    if args.dry_run or not args.output:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return 0
    out_path = Path(args.output)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return _fail(5, f"输出不可写：{exc}")
    print(f"已写入：{out_path}（{len(content)} 字节）")
    return 0


def _fail(code: int, msg: str) -> int:
    sys.stderr.write(f"[mubu] 错误：{msg}\n")
    return code


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mubu_cli.py",
        description="幕布 OPML ↔ Markdown 互转 CLI（纯标准库、零依赖）",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("input", help="输入文件路径")
    common.add_argument("-o", "--output", help="输出文件路径（默认 stdout）")
    common.add_argument(
        "--dry-run",
        action="store_true",
        help="预览不落盘（写操作强烈建议先开）",
    )

    p_info = sub.add_parser(
        "info", parents=[common], help="探查 OPML 结构（节点数、深度）"
    )
    p_info.add_argument("--json", action="store_true", help="JSON 输出")
    p_info.set_defaults(func=cmd_info)

    p_parse = sub.add_parser(
        "parse", parents=[common], help="解析 OPML，输出 JSON / HTML"
    )
    p_parse.add_argument(
        "-f", "--format", default="auto", help="auto/json/html"
    )
    p_parse.set_defaults(func=cmd_parse)

    p_md = sub.add_parser(
        "to-markdown", parents=[common], help="OPML → Markdown"
    )
    p_md.add_argument(
        "--indent", type=int, default=2, help="缩进空格数（默认 2）"
    )
    p_md.set_defaults(func=cmd_to_markdown)

    p_opml = sub.add_parser(
        "to-opml", parents=[common], help="Markdown → OPML"
    )
    p_opml.set_defaults(func=cmd_to_opml)

    p_list = sub.add_parser(
        "list", parents=[common], help="遍历节点树"
    )
    p_list.add_argument(
        "--max-depth", type=int, default=0, help="最大深度（0=不限）"
    )
    p_list.add_argument("--keyword", default="", help="关键词过滤")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help(sys.stderr)
        return 1
    try:
        return args.func(args)
    except (ValueError, ET.ParseError) as exc:
        return _fail(4, str(exc))


if __name__ == "__main__":
    sys.exit(main())
