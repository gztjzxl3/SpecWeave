"""三验证信号持久化层测试：订阅、访问埋点、推荐位占位。"""

from gqlsite.signals.track import (
    get_connection,
    init_db,
    recommended_slot,
    record_subscription,
    record_visit,
)


def _query_scalar(sql: str):
    conn = get_connection()
    try:
        row = conn.execute(sql).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def test_init_db_idempotent():
    for _ in range(2):
        conn = init_db()
        conn.close()  # 二次建表不报错，且连接需释放


def test_record_subscription_and_retrieve():
    cid = record_subscription("小明", "xm@example.com", "健康,睡眠")
    assert isinstance(cid, int) and cid >= 1
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT name, email, interests FROM subscriptions WHERE id = ?", (cid,)
        ).fetchone()
        assert row is not None
        assert row["name"] == "小明"
        assert row["email"] == "xm@example.com"
        assert row["interests"] == "健康,睡眠"
    finally:
        conn.close()


def test_record_visit_and_count():
    record_visit("/domain/home", referer="http://localhost/", ip="127.0.0.1")
    record_visit("/search?q=睡眠", ip="127.0.0.1")
    count = _query_scalar("SELECT COUNT(*) FROM visits")
    assert count >= 1
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT path, referer FROM visits WHERE path = '/domain/home' ORDER BY id DESC"
        ).fetchone()
        assert row is not None
        assert row["path"] == "/domain/home"
        assert row["referer"] == "http://localhost/"
    finally:
        conn.close()


def test_recommended_slot_placeholder():
    slot = recommended_slot()
    assert slot.title == "推荐位"
    assert slot.note and "占位" in slot.note


def test_get_connection_default_path(monkeypatch):
    # 未配置 GQLSITE_DB → 走默认 .data 路径分支
    monkeypatch.delenv("GQLSITE_DB", raising=False)
    conn = get_connection()
    try:
        conn.execute("SELECT 1").fetchone()
    finally:
        conn.close()


def test_get_connection_falls_back_to_memory(monkeypatch, tmp_path):
    # 目标路径父级是一个普通文件 → sqlite3 连接失败 → 回退内存库
    blocker = tmp_path / "blocker"
    blocker.write_text("not a dir")
    monkeypatch.setenv("GQLSITE_DB", str(blocker / "sub" / "x.db"))
    conn = get_connection()
    try:
        assert conn.execute("SELECT 1").fetchone()[0] == 1
    finally:
        conn.close()