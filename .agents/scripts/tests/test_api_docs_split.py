"""api_docs 拆分生成器单元测试。

回归防护：`write_split_docs()` 曾整体覆写 `lib/README.md`，静默删除人工维护
章节（如「Windows 平台陷阱」）；且注册表缺少手写分片条目，导致重新生成后
索引表丢行、计数失真。本套用例锁定修复后的三条不变式：

1. 标记区域：README 仅更新 `<!-- API_DOCS_START -->` 与 `<!-- API_DOCS_END -->`
   之间的内容，区域外的人工章节原样保留；
2. 手写分片：注册表中 `handwritten: True` 的分片不被覆写，但仍参与索引与导航；
3. 缺标记拒绝：README 无标记时抛 `ValueError`，绝不静默覆写。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import pytest

from lib import api_docs


# ── 夹具 ────────────────────────────────────────────────────

MODULES_FIXTURE = [
    {
        "num": 1,
        "slug": "alpha",
        "title": "lib.alpha — 甲模块",
        "filename": "01-alpha.md",
        "body": ["正文甲。\n"],
    },
    {
        "num": 2,
        "slug": "beta",
        "title": "lib.beta — 乙能量",
        "filename": "02-beta.md",
        "desc": "乙模块手写说明",
        "handwritten": True,
    },
]

MANUAL_SHARD = "# 手写分片\n\n人工维护内容，生成器不得覆写。\n"

MANUAL_SECTION = "## 人工章节\n\n请保留我。\n"


@pytest.fixture
def fake_modules(monkeypatch):
    """注入测试用注册表，避免依赖真实 lib/ 模块清单。"""
    monkeypatch.setattr(api_docs, "_MODULES", [dict(m) for m in MODULES_FIXTURE])


def _readme_with_markers() -> str:
    return (
        "# .agents/scripts/lib/ API 参考\n"
        "\n"
        f"{api_docs.API_DOCS_START}\n"
        "\n"
        "旧内容\n"
        "\n"
        f"{api_docs.API_DOCS_END}\n"
        "\n"
        + MANUAL_SECTION
    )


# ── 普通分片 ────────────────────────────────────────────────

class TestNormalShard:

    def test_shard_written_with_frontmatter_body_and_nav(self, tmp_path, fake_modules):
        api_docs.write_split_docs(tmp_path)
        text = (tmp_path / "docs" / "01-alpha.md").read_text(encoding="utf-8")
        assert 'id: "lib-api-alpha"' in text
        assert "# lib.alpha — 甲模块" in text
        assert "正文甲。" in text
        assert "**[返回索引](../README.md)**" in text

    def test_nav_chain_reaches_handwritten_shard(self, tmp_path, fake_modules):
        api_docs.write_split_docs(tmp_path)
        text = (tmp_path / "docs" / "01-alpha.md").read_text(encoding="utf-8")
        assert "下一章 → [乙能量 →](02-beta.md)" in text


# ── 手写分片保护 ────────────────────────────────────────────

class TestHandwrittenShard:

    def test_handwritten_shard_not_overwritten(self, tmp_path, fake_modules):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        target = docs_dir / "02-beta.md"
        target.write_text(MANUAL_SHARD, encoding="utf-8")

        api_docs.write_split_docs(tmp_path)

        assert target.read_text(encoding="utf-8") == MANUAL_SHARD

    def test_handwritten_shard_still_indexed(self, tmp_path, fake_modules):
        api_docs.write_split_docs(tmp_path)
        readme = (tmp_path / "README.md").read_text(encoding="utf-8")
        assert "| [docs/02-beta.md](docs/02-beta.md) | `lib.beta` | 乙模块手写说明 |" in readme


# ── README 标记区域 ─────────────────────────────────────────

class TestReadmeMarkerRegion:

    def test_marker_region_updated_and_manual_section_kept(self, tmp_path, fake_modules):
        (tmp_path / "docs").mkdir()
        readme = tmp_path / "README.md"
        readme.write_text(_readme_with_markers(), encoding="utf-8")

        api_docs.write_split_docs(tmp_path)

        text = readme.read_text(encoding="utf-8")
        assert "旧内容" not in text
        assert "| [docs/01-alpha.md](docs/01-alpha.md) | `lib.alpha` | 甲模块 |" in text
        assert MANUAL_SECTION in text
        assert text.index(api_docs.API_DOCS_END) < text.index("## 人工章节")

    def test_readme_created_with_markers_when_absent(self, tmp_path, fake_modules):
        api_docs.write_split_docs(tmp_path)
        text = (tmp_path / "README.md").read_text(encoding="utf-8")
        assert api_docs.API_DOCS_START in text
        assert api_docs.API_DOCS_END in text

    def test_missing_markers_raises_and_file_untouched(self, tmp_path, fake_modules):
        (tmp_path / "docs").mkdir()
        readme = tmp_path / "README.md"
        original = "# 索引\n\n无标记的人工内容。\n"
        readme.write_text(original, encoding="utf-8")

        with pytest.raises(ValueError):
            api_docs.write_split_docs(tmp_path)

        assert readme.read_text(encoding="utf-8") == original


# ── 幂等性 ──────────────────────────────────────────────────

class TestIdempotence:

    def test_second_run_produces_identical_output(self, tmp_path, fake_modules):
        (tmp_path / "docs").mkdir()
        readme = tmp_path / "README.md"
        readme.write_text(_readme_with_markers(), encoding="utf-8")

        def snapshot():
            shards = {
                p.name: p.read_text(encoding="utf-8")
                for p in sorted((tmp_path / "docs").glob("*.md"))
            }
            return shards, readme.read_text(encoding="utf-8")

        api_docs.write_split_docs(tmp_path)
        first_shards, first_readme = snapshot()

        api_docs.write_split_docs(tmp_path)
        second_shards, second_readme = snapshot()

        assert first_shards == second_shards
        assert first_readme == second_readme