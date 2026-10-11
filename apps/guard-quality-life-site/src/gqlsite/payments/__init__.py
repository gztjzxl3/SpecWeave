"""支付子包：支付宝电脑网站支付（真实交易闭环）。

模块划分：
- :mod:`config`：凭据配置（环境变量注入，含占位符检测）
- :mod:`sign`：RSA2 签名与验签（标准库 cryptography）
- :mod:`store`：订单持久化与幂等状态机
- :mod:`gateway`：下单表单构建 + 异步通知验签入账编排
"""

from .config import (
    PaymentConfig,
    PaymentNotConfigured,
    is_placeholder,
    load_payment_config,
)
from .gateway import build_page_pay_form, handle_notify, notify_result
from .store import (
    PAY_STATUS_CLOSED,
    PAY_STATUS_PAID,
    PAY_STATUS_PENDING,
    OrderRecord,
    close_order,
    create_order,
    get_order,
    mark_order_paid,
)

__all__ = [
    "PaymentConfig",
    "PaymentNotConfigured",
    "is_placeholder",
    "load_payment_config",
    "build_page_pay_form",
    "handle_notify",
    "notify_result",
    "PAY_STATUS_PENDING",
    "PAY_STATUS_PAID",
    "PAY_STATUS_CLOSED",
    "OrderRecord",
    "create_order",
    "get_order",
    "mark_order_paid",
    "close_order",
]