"""从当前 ``okw.cli.build_parser()`` 生成 CLI 表面快照。

用法（在项目根 apps/dev-tools/openkylin-wsl-devkit 下）：

    python tests/generate_cli_snapshot.py

仅允许在基线建立或经审批的命令面变更时运行；生成结果人工零编辑。
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cli_surface_lib import serialize_parser  # noqa: E402

from okw.cli import build_parser  # noqa: E402

SNAPSHOT_PATH = Path(__file__).resolve().parent / "snapshots" / "cli_surface.json"


def build_snapshot() -> dict:
    return serialize_parser(build_parser())


def main() -> int:
    snapshot = build_snapshot()
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"已写入 {SNAPSHOT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
