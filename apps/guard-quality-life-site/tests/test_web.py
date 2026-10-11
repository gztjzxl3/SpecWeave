"""Web 层端到端测试：路由返回 200、关键内容、订阅写入。"""

from fastapi.testclient import TestClient

from gqlsite.main import app

client = TestClient(app)


def test_homepage():
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    assert "守护品质生活" in body
    assert "知识树" in body
    # 推荐位占位应被渲染
    assert "推荐位" in body


def test_domain_page():
    r = client.get("/domain/health")
    assert r.status_code == 200
    assert "健康" in r.text
    assert "evidence" in r.text or "证据" in r.text


def test_domain_unknown_returns_404():
    r = client.get("/domain/does-not-exist")
    assert r.status_code == 404


def test_entry_page():
    r = client.get("/entry/sleep/sleep-fixed-wakeup")
    assert r.status_code == 200
    body = r.text
    assert "固定起床时间" in body
    for factor in ("目的", "可执行步骤", "成本收益", "证据等级", "禁忌"):
        assert factor in body


def test_entry_unknown_returns_404():
    r = client.get("/entry/home/nope")
    assert r.status_code == 404


def test_search():
    r = client.get("/search", params={"q": "餐盘"})
    assert r.status_code == 200
    assert "餐盘法" in r.text


def test_search_no_result():
    r = client.get("/search", params={"q": "绝不存在xyzq"})
    assert r.status_code == 200
    assert "没有找到" in r.text


def test_subscribe_form_get():
    r = client.get("/subscribe")
    assert r.status_code == 200
    assert "订阅" in r.text


def test_subscribe_post_records():
    r = client.post(
        "/subscribe",
        data={
            "name": "测试用户",
            "email": "t@example.com",
            "interests": ["健康", "饮食"],
        },
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "已成功登记" in r.text
    assert "记录编号" in r.text


def test_ping():
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_static_css():
    r = client.get("/static/styles.css")
    assert r.status_code == 200
    assert "--bg" in r.text