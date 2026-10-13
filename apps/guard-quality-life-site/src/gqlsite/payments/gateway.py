"""支付宝电脑网站支付业务编排：下单、生成支付表单、异步通知验签入账。

流程（对应 ``alipay.trade.page.pay`` 电脑网站支付）：

1. :func:`build_page_pay_form` —— 构建网关支付 HTML 表单。
   支付宝页面跳转类接口返回的是 **含自动提交脚本的 HTML form**，
   前端**必须渲染并自动提交此表单**，绝不能用 URL 直接跳转。

2. :func:`handle_notify` —— 处理异步通知：验签 → 校验业务字段 →
   幂等标记 PAID 入账。

配置未就绪或未配置时，本模块抛 :class:`PaymentNotConfigured`，
由路由层捕获并渲染「支付待配置」提示。
"""

from datetime import datetime
from typing import Mapping

from .config import PaymentConfig, PaymentNotConfigured
from .sign import build_signed_params, parse_notify_params, verify_signature
from .store import (
    OrderRecord,
    get_order,
    mark_order_paid,
)

__all__ = [
    "build_page_pay_form",
    "handle_notify",
    "notify_result",
]

# 电脑网站支付产品码固定值
_PRODUCT_CODE = "FAST_INSTANT_TRADE_PAY"


def _alipay_timestamp(dt: datetime) -> str:
    """支付宝要求时间戳格式为 ``yyyy-MM-dd HH:mm:ss``（空格分隔，非 ISO）。"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _ensure_ready(config: PaymentConfig) -> None:
    if not config.is_ready():
        raise PaymentNotConfigured(
            "支付宝支付尚未配置真实凭据（appId/应用私钥/支付宝公钥），"
            "无法发起真实支付。请填写环境变量后重试。"
        )


def _gateway_url(server_url: str) -> str:
    """规范化网关地址为「含 ``/gateway.do``」的形式（幂等）。

    ``server_url`` 可用两种写法表示网关：不带 path 的根地址（如
    ``https://openapi-sandbox.dl.alipaydev.com``）或完整接口地址（如
    ``https://openapi-sandbox.dl.alipaydev.com/gateway.do``）。本函数统一。
    """
    base = server_url.rstrip("/")
    if base.endswith("/gateway.do"):
        return base
    return base + "/gateway.do"


def _build_biz_content(
    out_trade_no: str,
    amount: str,
    subject: str,
) -> str:
    """构造支付宝 ``alipay.trade.page.pay`` 的 ``biz_content`` JSON 字符串。

    注意：``notify_url`` / ``return_url`` 是**顶层公共参数**（参与网关请求签名），
    不放入 ``biz_content``，否则与支付宝签名规则不一致。
    """
    import json

    biz = {
        "out_trade_no": out_trade_no,
        "total_amount": amount,
        "subject": subject,
        "product_code": _PRODUCT_CODE,
        # 超时关单（分钟）
        "timeout_express": "30m",
    }
    return json.dumps(biz, ensure_ascii=False)


def build_page_pay_form(
    config: PaymentConfig,
    out_trade_no: str,
    amount: str,
    subject: str,
) -> str:
    """构建支付宝电脑网站支付 HTML 表单（含自动提交脚本）。

    参数：
    - ``out_trade_no``：商户订单号（唯一）
    - ``amount``：金额，如 ``88.88``
    - ``subject``：商品标题

    返回可直接注入页面的 HTML 字符串。前端必须插入 DOM 并自动提交此 form，
    而非用 URL 跳转。
    """
    _ensure_ready(config)
    params: dict[str, str] = {
        "method": "alipay.trade.page.pay",
        "app_id": config.app_id,
        "sign_type": config.sign_type,
        "charset": config.charset,
        "version": "1.0",
        "timestamp": _alipay_timestamp(datetime.now()),
        "notify_url": config.notify_url,
        "return_url": config.return_url,
        "biz_content": _build_biz_content(out_trade_no, amount, subject),
    }
    # 官方 page_execute 契约：每个参数一个 hidden input，action 不携带 query。
    signed = build_signed_params(params, config.app_private_key)
    action_url = _gateway_url(config.server_url)
    hidden_inputs = "".join(
        f'<input type="hidden" name="{_html_escape(k)}" '
        f'value="{_html_escape(v)}">'
        for k, v in signed.items()
    )
    return (
        f'<form id="alipay_submit" name="alipay_submit" method="post" '
        f'action="{action_url}">'
        f'{hidden_inputs}'
        '<input type="submit" value="立即支付" style="display:none">'
        "</form>"
        "<script>document.getElementById('alipay_submit').submit();</script>"
    )


def _html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def notify_result(ok: bool, message: str) -> str:
    """构造异步通知应答体。支付宝要求：验签/处理成功返回文本 ``success``。

    - 处理成功：返回 ``success``（支付宝停止重发）
    - 处理失败/验签不过：返回 ``failure``（支付宝稍后重发）
    """
    return "success" if ok else "failure"


def handle_notify(
    config: PaymentConfig,
    raw_params: Mapping[str, str],
) -> tuple[bool, str]:
    """处理支付宝异步通知（电脑网站支付）。

    安全顺序（严格）：
    1. **先验签**：使用支付宝公钥校验通知签名，失败即拒绝。
    2. **校验 app_id** 是否与配置一致，防止跨应用伪造。
    3. **幂等入账**：仅当订单处于 PENDING 时才标记 PAID；重复成功通知不重复发放。

    :returns: ``(ok, message)``；``ok`` 由路由层翻转成 ``success``/``failure``
    """
    _ensure_ready(config)
    params, sign = parse_notify_params(raw_params)
    if not verify_signature(params, sign, config.alipay_public_key):
        return False, "签名校验失败"

    notified_app_id = params.get("app_id", "")
    if notified_app_id != config.app_id:
        return False, f"app_id 不匹配（期望 {config.app_id}，收到 {notified_app_id}）"

    out_trade_no = params.get("out_trade_no", "")
    if not out_trade_no:
        return False, "缺少 out_trade_no"

    order = get_order(out_trade_no)
    if order is None:
        return False, f"订单不存在：{out_trade_no}"

    trade_status = params.get("trade_status", "")
    if trade_status == "TRADE_SUCCESS":
        # 幂等：无论当前状态，宿主侧以 mark_order_paid 的 WHERE status=PENDING 保证
        # 不重复发放；若已是 PAID 则返回当前记录，不再重复副作用。
        notified_amount = params.get("total_amount", "")
        if notified_amount and notified_amount != order.amount:
            return False, (
                f"金额不匹配（订单 {order.amount}，通知 {notified_amount}）"
            )
        paid = mark_order_paid(
            out_trade_no,
            params.get("trade_no", ""),
            params.get("buyer_email", ""),
        )
        if paid is None:
            return False, "订单状态异常"
        return True, f"已入账（{paid.status}）"
    elif trade_status == "TRADE_CLOSED":
        return True, "交易关闭，无需入账"
    else:
        # 其他中间态（WAIT_BUYER_PAY 等）不视为支付成功，也不随便失败
        return False, f"未支付状态：{trade_status}"