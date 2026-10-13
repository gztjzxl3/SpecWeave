"""静态门禁：src/okw 全包不得访问 argparse 私有解析器属性。

锁定字符串 ``_subparsers`` / ``_group_actions`` / ``_name_parser_map``：
这些属性随 CPython 版本可能变动，子组帮助回打已改为装配期闭包。
"""

from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "okw"

# 带点号形态：只拦截私有属性访问（x._subparsers 等）。
# 注意裸 token "_subparsers" 是公有 API add_subparsers 的子串，不可直接匹配。
FORBIDDEN_TOKENS = ("._subparsers", "._group_actions", "._name_parser_map")


def test_no_private_argparse_api_tokens():
    offenders = []
    for path in SRC_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                offenders.append(f"{path.relative_to(SRC_ROOT)} 含 {token}")
    assert not offenders, "发现 argparse 私有 API 访问：\n" + "\n".join(offenders)
