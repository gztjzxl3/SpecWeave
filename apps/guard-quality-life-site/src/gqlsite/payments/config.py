"""支付宝电脑网站支付配置（环境变量注入，含显式占位符检测）。

真实交易所需的应用凭据（appId / 应用私钥 / 支付宝公钥）必须来自你的
实际申领，本模块**不编造**任何字段。所有配置均通过环境变量读取，
缺省使用**明确标注的占位符**，并在未配置时由上层优雅降级为「支付待配置」
提示，不影响知识树浏览。

约定（与支付宝开放平台语义对齐）：
- 私钥格式：非 JAVA（Python）使用 PKCS#1 应用私钥
- 签名算法：RSA2（SHA256WithRSA）
- 网关默认沙箱地址；上线前切换正式网关
"""

import os
from dataclasses import dataclass

__all__ = [
    "PaymentConfig",
    "PaymentNotConfigured",
    "load_payment_config",
    "is_placeholder",
]

# 显式占位符：值完全等于这些串即视为「尚未配置真实凭据」。
# 注意集合**不含空串**——空值判定已由 is_placeholder 的 stripped 分支承担，
# 否则 ``"" in value`` 恒为 True 会把任何真实值误判为占位符。
_PLACEHOLDER_MARKERS = {"your-app-id-here", "<-- 请填写您的AppId -->"}


def is_placeholder(value: str) -> bool:
    """判定一个配置值是否为占位符（未填写真实凭据）。"""
    stripped = value.strip()
    if not stripped:
        return True
    return any(marker in stripped for marker in _PLACEHOLDER_MARKERS)


class PaymentNotConfigured(RuntimeError):
    """支付宝支付未配置（凭据缺失或仍是占位符）。"""


@dataclass(frozen=True)
class PaymentConfig:
    """支付宝电脑网站支付所需最小配置集合。

    全部来自环境变量（生产建议经 ``.env`` 或部署平台注入），本模块不落盘密钥。
    """

    app_id: str
    app_private_key: str  # PKCS#1 格式，Python 非 JAVA 使用
    alipay_public_key: str
    server_url: str
    sign_type: str = "RSA2"
    charset: str = "utf-8"
    # 异步通知与页面跳转回跳地址（需为公网可达 / 内网穿透，沙箱无法触发真实回调）
    notify_url: str = ""
    return_url: str = ""

    def is_ready(self) -> bool:
        """凭据是否就绪（app_id / 私钥 / 公钥均非空非占位）。"""
        return not (
            is_placeholder(self.app_id)
            or is_placeholder(self.app_private_key)
            or is_placeholder(self.alipay_public_key)
        )


# 网关缺省地址：沙箱环境（快速沙箱仅 Unix 支持；Windows 需自行申领）
_DEFAULT_SERVER_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
_PROD_SERVER_URL = "https://openapi.alipay.com/gateway.do"


def load_payment_config() -> PaymentConfig:
    """从环境变量读取支付配置；凭据缺失/占位时构造出未就绪的配置对象。

    - ``GQLSITE_PAY_APP_ID``：应用 appId（未填=占位）
    - ``GQLSITE_PAY_APP_PRIVATE_KEY``：应用私钥（PKCS#1）
    - ``GQLSITE_PAY_ALIPAY_PUBLIC_KEY``：支付宝公钥
    - ``GQLSITE_PAY_SERVER_URL``：网关，缺省沙箱
    - ``GQLSITE_PAY_PROD``：=1 使用正式网关
    - ``GQLSITE_PAY_NOTIFY_URL`` / ``GQLSITE_PAY_RETURN_URL``：回调地址

    只读配置，不含任何密钥落盘。调用方用 :meth:`PaymentConfig.is_ready`
    判断能否发起真实支付。
    """
    env = os.environ
    server_url = env.get("GQLSITE_PAY_SERVER_URL", "")
    if not server_url:
        server_url = _PROD_SERVER_URL if env.get("GQLSITE_PAY_PROD") == "1" else _DEFAULT_SERVER_URL
    return PaymentConfig(
        app_id=env.get("GQLSITE_PAY_APP_ID", "").strip(),
        app_private_key=env.get("GQLSITE_PAY_APP_PRIVATE_KEY", ""),
        alipay_public_key=env.get("GQLSITE_PAY_ALIPAY_PUBLIC_KEY", ""),
        server_url=server_url,
        notify_url=env.get("GQLSITE_PAY_NOTIFY_URL", ""),
        return_url=env.get("GQLSITE_PAY_RETURN_URL", ""),
    )