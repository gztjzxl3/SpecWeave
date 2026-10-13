"""三验证信号：订阅登记 / 访问埋点 / 推荐位占位（SQLite 持久化）。

数据库路径由环境变量 ``GQLSITE_DB`` 指定；未设置时默认落到包内
``.data/gqlsite.db``（相对仓库根）。若路径不可写（如裸读测试环境），
回退到内存库 ``:memory:``，保证既有测试与只读场景仍可运行。

三张表均为幂等建表（``CREATE TABLE IF NOT EXISTS``）。
"""

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

__all__ = [
    "RECOMMENDED_SLOT",
    "get_connection",
    "init_db",
    "record_subscription",
    "record_visit",
    "recommended_slot",
]

_RECOMMENDED_SLOT = {"title": "推荐位", "note": "占位，后续接入真实商务"}
RECOMMENDED_SLOT = _RECOMMENDED_SLOT


@dataclass(frozen=True)
class RecommendedSlot:
    """推荐位占位：页面侧栏渲染的最小信息载体。"""

    title: str
    note: str


def recommended_slot() -> RecommendedSlot:
    return RecommendedSlot(**_RECOMMENDED_SLOT)


def _default_db_path() -> Path:
    return Path(__file__).resolve().parents[3] / ".data" / "gqlsite.db"


def get_connection() -> sqlite3.Connection:
    """建立 SQLite 连接；失败时回退内存库保证测试可跑。"""
    env_path = os.environ.get("GQLSITE_DB")
    explicit = bool(env_path)
    db_path = Path(env_path) if explicit else _default_db_path()
    if not explicit:
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        # 目标路径不可写 / 不可达（如只读或非法盘符）时回退内存库
        mem = sqlite3.connect(":memory:")
        mem.row_factory = sqlite3.Row
        return mem


def _schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            interests TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            referer TEXT NOT NULL DEFAULT '',
            ip TEXT NOT NULL DEFAULT '',
            visited_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def init_db() -> sqlite3.Connection:
    """建表（幂等）并返回连接。"""
    conn = get_connection()
    _schema(conn)
    return conn


def record_subscription(name: str, email: str, interests: str = "") -> int:
    """写入一条订阅/兴趣登记，返回新行的自增 id。"""
    conn = init_db()
    try:
        cur = conn.execute(
            "INSERT INTO subscriptions (name, email, interests, created_at) VALUES (?, ?, ?, ?)",
            (name, email, interests, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def record_visit(path: str, referer: str = "", ip: str = "") -> int:
    """写入一条访问埋点，返回新行的自增 id。"""
    conn = init_db()
    try:
        cur = conn.execute(
            "INSERT INTO visits (path, referer, ip, visited_at) VALUES (?, ?, ?, ?)",
            (path, referer, ip, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()