"""三验证信号的持久化层：订阅登记 / 访问埋点 / 推荐位占位。

使用标准库 sqlite3，无需外部数据库服务。
"""

from .track import (
    RECOMMENDED_SLOT,
    get_connection,
    init_db,
    recommended_slot,
    record_subscription,
    record_visit,
)

__all__ = [
    "RECOMMENDED_SLOT",
    "get_connection",
    "init_db",
    "record_subscription",
    "record_visit",
    "recommended_slot",
]