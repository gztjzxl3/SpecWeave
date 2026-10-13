"""python -m okw.cli 入口（与 python -m okw、console script 等价）。"""

from okw.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
