#!/usr/bin/env python3
"""Markdown 相对链接与锚点门禁（GitHub slug 规则）。

submodule-atomization-finalize-cmd 技能 S3 步骤的底层脚本。主仓 check-links.py
不覆盖 git 子模块，本子模块等价检查器递归校验给定文档根下全部 Markdown：

- 行内链接 [text](url) 与引用式定义 [id]: url 均纳入检查；
- http(s)/mailto 外链跳过；file:/// 绝对路径单独计数告警（不致失败）；
- 相对目标文件不存在 -> broken；
- URL fragment 仅对 .md 目标校验：标题锚点按 GitHub slug 规则生成
  （小写、去除 `*~ 等标点、空白转连字符、保留中日韩文字），
  并兼容显式 <a id="..."> / <a name="..."> 锚点；
- 指向 .py 等源码文件的 #L85-L90 是 GitHub 行号锚点，不按 Markdown 锚点校验。

用法：
    python3 check_doc_links.py <docs-root> [<docs-root> ...]

退出码：存在 broken 链接/锚点时为 1，否则为 0。
"""

import argparse
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, List, Set, Tuple

INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
REF_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s+(\S+)", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
ANCHOR_RE = re.compile(r"<a\s+(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def github_slug(title: str) -> str:
    """复刻 GitHub 锚点生成规则的可判定子集（经中文标题锚点实测）。"""
    text = title.strip().lower()
    text = re.sub(r"[`*~]", "", text)
    chars: List[str] = []
    for ch in text:
        if ch.isalnum() or ch in "-_":
            chars.append(ch)
        elif ch.isspace():
            chars.append("-")
    return "".join(chars)


def collect_anchors(markdown_file: Path, cache: Dict[Path, Set[str]]) -> Set[str]:
    if markdown_file in cache:
        return cache[markdown_file]
    anchors: Set[str] = set()
    text = markdown_file.read_text(encoding="utf-8")
    anchors.update(github_slug(m.group(1)) for m in HEADING_RE.finditer(text))
    anchors.update(m.group(1) for m in ANCHOR_RE.finditer(text))
    cache[markdown_file] = anchors
    return anchors


def split_target(url: str) -> Tuple[str, str]:
    if "#" in url:
        path_part, fragment = url.split("#", 1)
        return path_part, urllib.parse.unquote(fragment)
    return url, ""


def check_file(md_file: Path, anchor_cache: Dict[Path, Set[str]]) -> Tuple[List[str], int, int]:
    broken: List[str] = []
    links = 0
    file_uri_warnings = 0
    text = md_file.read_text(encoding="utf-8")
    for match in INLINE_LINK_RE.finditer(text):
        url = match.group(1)
        if url.startswith(EXTERNAL_PREFIXES):
            continue
        if url.startswith("file:///"):
            file_uri_warnings += 1
            continue
        links += 1
        path_part, fragment = split_target(url)
        target = (md_file.parent / path_part).resolve() if path_part else md_file.resolve()
        if path_part and not target.exists():
            broken.append(f"{url}  [文件不存在]")
            continue
        if fragment and target.suffix == ".md":
            if fragment not in collect_anchors(target, anchor_cache):
                broken.append(f"{url}  [Markdown 锚点缺失]")
    # 引用式链接定义：仅校验定义行本身的 URL（引用使用点不重复计数）。
    for match in REF_DEF_RE.finditer(text):
        url = match.group(1).strip("<>")
        if url.startswith(EXTERNAL_PREFIXES) or url.startswith("file:///"):
            continue
        links += 1
        path_part, fragment = split_target(url)
        if not path_part:
            continue
        target = (md_file.parent / path_part).resolve()
        if not target.exists():
            broken.append(f"{url}  [引用式定义目标不存在]")
        elif fragment and target.suffix == ".md":
            if fragment not in collect_anchors(target, anchor_cache):
                broken.append(f"{url}  [引用式定义锚点缺失]")
    return broken, links, file_uri_warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown 相对链接与锚点门禁（GitHub slug）")
    parser.add_argument("roots", nargs="+", type=Path, help="待扫描的文档根目录（可多个）")
    args = parser.parse_args()

    anchor_cache: Dict[Path, Set[str]] = {}
    md_files: List[Path] = []
    for root in args.roots:
        root = root.resolve()
        if not root.exists():
            print(f"ERROR: 文档根不存在: {root}", file=sys.stderr)
            return 2
        md_files.extend(sorted(root.rglob("*.md")))

    total_links = 0
    total_file_uri = 0
    all_broken: List[str] = []
    for md_file in md_files:
        broken, links, file_uri_count = check_file(md_file, anchor_cache)
        total_links += links
        total_file_uri += file_uri_count
        for item in broken:
            all_broken.append(f"{md_file}: {item}")

    print(f"checked_files={len(md_files)} links={total_links} broken={len(all_broken)}")
    if total_file_uri:
        print(f"warning: file:/// 绝对链接 {total_file_uri} 处（主仓规范禁止，子模块按自身约定处置）")
    for item in all_broken:
        print("BROKEN:", item)
    return 1 if all_broken else 0


if __name__ == "__main__":
    sys.exit(main())
