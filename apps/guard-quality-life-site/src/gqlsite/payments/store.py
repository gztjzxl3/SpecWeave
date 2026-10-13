"""支付订单持久化与状态机（SQLite，幂等建表）。

新增 ``pay_orders`` 表，承载「真实交易」的订单生命周期：
PENDING（待支付）→ PAID（已支付，权益已发放，幂等）。

复用 :func:`gqlsite.signals.track.get_connection` 的 SQLite 连接与
内存库回退逻辑，保证只读/测试环境不崩溃。

**幂等发放**（核心安全约束）：异步通知可能重复到达，发放权益必须幂等——
订单已是 PAID 时再次收到成功通知不重复发放，返回原状态即可。
"""

from datetime import datetime
from typing import Optional

from ..signals.track import get_connection

__all__ = [
    "PAY_STATUS_PENDING",
    "PAY_STATUS_PAID",
    "PAY_STATUS_CLOSED",
    "OrderRecord",
    "create_order",
    "get_order",
    "mark_order_paid",
    "close_order",
]

PAY_STATUS_PENDING = "PENDING"
PAY_STATUS_PAID = "PAID"
PAY_STATUS_CLOSED = "CLOSED"


def _schema(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pay_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            out_trade_no TEXT NOT NULL UNIQUE,
            product_code TEXT NOT NULL,
            amount TEXT NOT NULL,
            subject TEXT NOT NULL,
            status TEXT NOT NULL,
            buyer_email TEXT NOT NULL DEFAULT '',
            trade_no TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            paid_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.commit()


def init_orders() -> None:
    """幂等建表。"""
    _schema(get_connection())


class OrderRecord:
    """订单只读视图（普通类，非 dataclass 以贴近 sqlite3.Row 访问）。"""

    def __init__(self, row):
        self.id = row["id"]
        self.out_trade_no = row["out_trade_no"]
        self.product_code = row["product_code"]
        self.amount = row["amount"]
        self.subject = row["subject"]
        self.status = row["status"]
        self.buyer_email = row["buyer_email"]
        self.trade_no = row["trade_no"]
        self.created_at = row["created_at"]
        self.paid_at = row["paid_at"]

    @property
    def is_paid(self) -> bool:
        return self.status == PAY_STATUS_PAID


def create_order(
    out_trade_no: str,
    product_code: str,
    amount: str,
    subject: str,
    buyer_email: str = "",
) -> int:
    """新建一笔待支付订单，返回自增 id。调用方负责单号唯一。"""
    conn = get_connection()
    _schema(conn)
    try:
        cur = conn.execute(
            """
            INSERT INTO pay_orders
                (out_trade_no, product_code, amount, subject, status,
                 buyer_email, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                out_trade_no,
                product_code,
                amount,
                subject,
                PAY_STATUS_PENDING,
                buyer_email,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_order(out_trade_no: str) -> Optional[OrderRecord]:
    """按商户单号查订单；不存在返回 None。"""
    conn = get_connection()
    _schema(conn)
    try:
        row = conn.execute(
            "SELECT * FROM pay_orders WHERE out_trade_no = ?", (out_trade_no,)
        ).fetchone()
        return OrderRecord(row) if row is not None else None
    finally:
        conn.close()


def mark_order_paid(
    out_trade_no: str,
    trade_no: str,
    buyer_email: str,
) -> OrderRecord:
    """将订单标记为已支付（幂等）。重复调用返回同一 PAID 状态，不重复副作用。

    返回更新后的订单记录。若订单不存在返回 None 由调用方判定。
    """
    conn = get_connection()
    _schema(conn)
    try:
        now = datetime.now().isoformat(timespec="seconds")
        # 只有 PENDING 才升级为 PAID；CLOSED/已 PAID 保持原状（幂等）
        conn.execute(
            """
            UPDATE pay_orders
            SET status = ?, trade_no = COALESCE(?, trade_no),
                buyer_email = COALESCE(?, buyer_email),
                paid_at = CASE WHEN status = ? THEN ? ELSE paid_at END
            WHERE out_trade_no = ? AND status = ?
            """,
            (
                PAY_STATUS_PAID,
                trade_no,
                buyer_email,
                PAY_STATUS_PENDING,
                now,
                out_trade_no,
                PAY_STATUS_PENDING,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM pay_orders WHERE out_trade_no = ?", (out_trade_no,)
        ).fetchone()
        return OrderRecord(row) if row is not None else None
    finally:
        conn.close()


def close_order(out_trade_no: str) -> Optional[OrderRecord]:
    """关闭一笔待支付订单（用户取消/超时）。已支付订单不可关闭。"""
    conn = get_connection()
    _schema(conn)
    try:
        conn.execute(
            """
            UPDATE pay_orders SET status = ?
            WHERE out_trade_no = ? AND status = ?
            """,
            (PAY_STATUS_CLOSED, out_trade_no, PAY_STATUS_PENDING),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM pay_orders WHERE out_trade_no = ?", (out_trade_no,)
        ).fetchone()
        return OrderRecord(row) if row is not None else None
    finally:
        conn.close()