"""支付子包测试：RSA2 签名验签、表单构建、异步通知入账、Web 路由降级。"""

import base64

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from gqlsite.main import app
from gqlsite.payments import (
    PaymentConfig,
    PaymentNotConfigured,
    build_page_pay_form,
    create_order,
    get_order,
    handle_notify,
    load_payment_config,
    mark_order_paid,
)
from gqlsite.payments.sign import (
    build_signed_query,
    parse_notify_params,
    sign_params,
    verify_signature,
)
from gqlsite.payments.store import PAY_STATUS_PAID, PAY_STATUS_PENDING
from gqlsite.signals.track import init_db

from fastapi.testclient import TestClient


# ---------------- 夹具：一对真实 RSA 密钥 ----------------

@pytest.fixture(scope="module")
def rsa_keys():
    """生成一对 RSA-2048 密钥，用于真实的加解密/验签断言。"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        serialization.NoEncryption(),
    ).decode("utf-8")
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


@pytest.fixture()
def config(rsa_keys, monkeypatch):
    """构造已就绪的 PaymentConfig，并把环境变量也灌入以便 Web 层用。"""
    private_pem, public_pem = rsa_keys
    monkeypatch.setenv("GQLSITE_PAY_APP_ID", "2088100000000011")
    monkeypatch.setenv("GQLSITE_PAY_APP_PRIVATE_KEY", private_pem)
    monkeypatch.setenv("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", public_pem)
    monkeypatch.setenv("GQLSITE_PAY_NOTIFY_URL", "https://example.com/pay/notify")
    monkeypatch.setenv("GQLSITE_PAY_RETURN_URL", "https://example.com/return")
    return PaymentConfig(
        app_id="2088100000000011",
        app_private_key=private_pem,
        alipay_public_key=public_pem,
        server_url="https://openapi-sandbox.dl.alipaydev.com/gateway.do",
        notify_url="https://example.com/pay/notify",
        return_url="https://example.com/return",
    )


# ---------------- 配置加载 ----------------

def test_load_payment_config_placeholder_by_default(monkeypatch):
    monkeypatch.delenv("GQLSITE_PAY_APP_ID", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", raising=False)
    cfg = load_payment_config()
    assert cfg.is_ready() is False


def test_is_ready_true_with_keys(config):
    assert config.is_ready() is True


def test_build_form_raises_when_not_ready(rsa_keys):
    _, public_pem = rsa_keys
    cfg = PaymentConfig(
        app_id="", app_private_key="", alipay_public_key=public_pem, server_url="x"
    )
    with pytest.raises(PaymentNotConfigured):
        build_page_pay_form(cfg, "no-1", "1.00", "x")


# ---------------- RSA2 签名 / 验签（真实密钥往返） ----------------

def test_sign_and_verify_roundtrip(rsa_keys):
    private_pem, public_pem = rsa_keys
    params = {
        "method": "alipay.trade.page.pay",
        "app_id": "2088100000000011",
        "charset": "utf-8",
        "biz_content": '{"out_trade_no":"x"}',
    }
    sign = sign_params(params, private_pem)
    assert verify_signature(params, sign, public_pem) is True


def test_verify_rejects_tampered(rsa_keys):
    private_pem, public_pem = rsa_keys
    params = {"a": "1", "b": "2"}
    sign = sign_params(params, private_pem)
    # 篡改一个值
    tampered = dict(params)
    tampered["b"] = "3"
    assert verify_signature(tampered, sign, public_pem) is False


def test_verify_rejects_empty_sign(rsa_keys):
    _, public_pem = rsa_keys
    assert verify_signature({"a": "1"}, "", public_pem) is False


def test_parse_notify_params_separates_sign():
    raw = {"out_trade_no": "o1", "total_amount": "88.00", "sign": "abc=="}
    params, sign = parse_notify_params(raw)
    assert sign == "abc=="
    assert "sign" not in params
    assert params["out_trade_no"] == "o1"


def test_build_signed_query_contains_sign(config):
    q = build_signed_query({"app_id": config.app_id, "biz_content": "{}"}, config.app_private_key)
    assert "sign=" in q
    assert "app_id=2088100000000011" in q


# ---------------- 表单构建 ----------------

def test_build_page_pay_form_contains_autosubmit(config):
    html = build_page_pay_form(config, "gql-1", "88.00", "会员")
    assert 'id="alipay_submit"' in html
    assert "document.getElementById('alipay_submit').submit()" in html
    assert "method=\"post\"" in html
    # action 指向网关 gateway.do（幂等，不出现 /gateway.do/gateway.do）
    assert "gateway.do\"" in html
    assert "/gateway.do/gateway.do" not in html
    # 官方 page_execute 契约：每个参数一个 hidden input，含签名字段
    assert 'name="sign"' in html
    assert 'name="biz_content"' in html
    assert 'name="app_id"' in html
    # 产品码必须出现
    assert "FAST_INSTANT_TRADE_PAY" in html


# ---------------- 异步通知状态机（模拟支付宝回调） ----------------

def _sign_notify(config, payload: dict[str, str]) -> dict[str, str]:
    """用配置私钥对通知参数签名，返回完整通知体（含 sign）。"""
    from gqlsite.payments.sign import sign_params
    from collections import OrderedDict

    ordered = OrderedDict(sorted(payload.items(), key=lambda kv: kv[0]))
    signed = sign_params(ordered, config.app_private_key)
    return {**payload, "sign": signed}


def test_handle_notify_marks_paid(config):
    init_db()
    create_order("gql-notify-1", product_code="gql-guide-pdf", amount="29.90", subject="指南")
    notify = _sign_notify(
        config,
        {
            "app_id": config.app_id,
            "out_trade_no": "gql-notify-1",
            "total_amount": "29.90",
            "trade_status": "TRADE_SUCCESS",
            "trade_no": "alipay-1001",
            "buyer_email": "buyer@example.com",
        },
    )
    ok, msg = handle_notify(config, notify)
    assert ok is True
    order = get_order("gql-notify-1")
    assert order.status == PAY_STATUS_PAID
    assert order.trade_no == "alipay-1001"


def test_handle_notify_idempotent(config):
    """重复成功通知不重复副作用，保持 PAID。"""
    init_db()
    create_order("gql-notify-2", product_code="gql-guide-pdf", amount="29.90", subject="指南")
    notify = _sign_notify(
        config,
        {
            "app_id": config.app_id,
            "out_trade_no": "gql-notify-2",
            "total_amount": "29.90",
            "trade_status": "TRADE_SUCCESS",
        },
    )
    ok1, _ = handle_notify(config, notify)
    ok2, msg2 = handle_notify(config, notify)
    assert ok1 is True and ok2 is True
    assert get_order("gql-notify-2").status == PAY_STATUS_PAID


def test_handle_notify_rejects_bad_signature(config):
    init_db()
    create_order("gql-notify-3", product_code="x", amount="1.00", subject="x")
    bad = {
        "app_id": config.app_id,
        "out_trade_no": "gql-notify-3",
        "total_amount": "1.00",
        "trade_status": "TRADE_SUCCESS",
        "sign": "AAAA-bogus==",
    }
    ok, msg = handle_notify(config, bad)
    assert ok is False
    assert "签名" in msg
    assert get_order("gql-notify-3").status == PAY_STATUS_PENDING


def test_handle_notify_rejects_wrong_app_id(config):
    init_db()
    create_order("gql-notify-4", product_code="x", amount="1.00", subject="x")
    notify = _sign_notify(
        config,
        {
            "app_id": "2088000000000000",  # 不同 app_id
            "out_trade_no": "gql-notify-4",
            "total_amount": "1.00",
            "trade_status": "TRADE_SUCCESS",
        },
    )
    ok, msg = handle_notify(config, notify)
    assert ok is False
    assert "app_id" in msg


def test_handle_notify_rejects_wrong_amount(config):
    """金额不一致必须拒绝，防止篡改。"""
    init_db()
    create_order("gql-notify-5", product_code="x", amount="88.00", subject="会员")
    notify = _sign_notify(
        config,
        {
            "app_id": config.app_id,
            "out_trade_no": "gql-notify-5",
            "total_amount": "1.00",  # 篡改金额
            "trade_status": "TRADE_SUCCESS",
        },
    )
    ok, msg = handle_notify(config, notify)
    assert ok is False
    assert "金额" in msg


def test_handle_notify_ignores_pending_status(config):
    init_db()
    create_order("gql-notify-6", product_code="x", amount="1.00", subject="x")
    notify = _sign_notify(
        config,
        {
            "app_id": config.app_id,
            "out_trade_no": "gql-notify-6",
            "total_amount": "1.00",
            "trade_status": "WAIT_BUYER_PAY",
        },
    )
    ok, _ = handle_notify(config, notify)
    assert ok is False
    assert get_order("gql-notify-6").status == PAY_STATUS_PENDING


# ---------------- Web 路由 ----------------

def test_checkout_unknown_product_404():
    client = TestClient(app)
    r = client.get("/checkout/nope")
    assert r.status_code == 404


def test_checkout_get_when_not_ready(monkeypatch):
    monkeypatch.delenv("GQLSITE_PAY_APP_ID", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", raising=False)
    client = TestClient(app)
    r = client.get("/checkout/gql-weekly")
    assert r.status_code == 200
    assert "支付通道尚未配置" in r.text


def test_checkout_post_not_ready_shows_error(monkeypatch):
    monkeypatch.delenv("GQLSITE_PAY_APP_ID", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", raising=False)
    client = TestClient(app)
    r = client.post("/checkout/gql-weekly")
    assert r.status_code == 200
    assert "暂无法发起交易" in r.text


def test_notify_when_not_ready_returns_failure(monkeypatch):
    monkeypatch.delenv("GQLSITE_PAY_APP_ID", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_APP_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", raising=False)
    client = TestClient(app)
    r = client.post("/pay/notify", data={"out_trade_no": "x"})
    assert r.status_code == 200
    assert r.text == "failure"


def test_order_page_unknown_404():
    client = TestClient(app)
    r = client.get("/order/no-such-order")
    assert r.status_code == 404