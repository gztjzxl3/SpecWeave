"""okw.cli 包：parser 装配（纯函数）与 main 分发（运行时）。

重导出 main/build_parser 以保持入口契约：
- console script ``okw = "okw.cli:main"``；
- 测试与历史调用方的 ``from okw import cli; cli.main(...)``。
"""

from okw.cli.main import main
from okw.cli.parser import build_parser

__all__ = ["main", "build_parser"]
