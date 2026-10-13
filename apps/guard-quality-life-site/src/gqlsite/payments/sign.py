"""支付宝 RSA2 签名与验签（基于 ``cryptography`` 标准库，不依赖官方 SDK）。

实现支付宝「RSA2」（SHA256WithRSA + PKCS#1 v1.5）签名与异步通知验签。
签名规则与支付宝开放平台一致：

1. 请求/通知参数去掉 ``sign``、``sign_type`` 两个键；值为空串的键也剔除。
2. 剩余键按 ASCII 码升序排列。
3. 以 ``key=value`` 形式用 ``&`` 连接成待签名字符串。
4. 对待签名字符串做 SHA256WithRSA 签名（PKCS#1 v1.5），Base64 编码。

私钥（Python 非 JAVA 场景）使用 **PKCS#1** 格式应用私钥；验签使用支付宝公钥。
两种密钥均为 PEM 文本。本模块不做任何格式转换或前后缀拼接——密钥原样传入。
"""

import base64
from typing import Mapping

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

__all__ = [
    "sign_params",
    "verify_signature",
    "build_signed_query",
    "build_signed_params",
    "parse_notify_params",
]

# 参与签名时需剔除的键
_SIGN_EXCLUDE = {"sign", "sign_type"}


def _build_sign_string(params: Mapping[str, str]) -> str:
    """将参数集按支付宝规则拼接成待签名字符串（剔除 sign/sign_type/空值）。"""
    items = sorted(
        (k, v) for k, v in params.items() if k not in _SIGN_EXCLUDE and v != ""
    )
    return "&".join(f"{k}={v}" for k, v in items)


def _load_private_key(pem: str) -> rsa.RSAPrivateKey:
    key = serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise ValueError("支付宝应用私钥必须是 RSA 私钥")
    return key


def _load_public_key(pem: str):
    key = serialization.load_pem_public_key(pem.encode("utf-8"))
    if not isinstance(key, rsa.RSAPublicKey):
        raise ValueError("支付宝公钥必须是 RSA 公钥")
    return key


def sign_params(params: Mapping[str, str], app_private_key: str) -> str:
    """对参数集按 RSA2 规则生成 Base64 签名。"""
    sign_str = _build_sign_string(params)
    private_key = _load_private_key(app_private_key)
    signature = private_key.sign(
        sign_str.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(
    params: Mapping[str, str],
    sign: str,
    alipay_public_key: str,
) -> bool:
    """校验支付宝异步通知签名。

    - ``params``：收到的通知参数（需已排除 ``sign_type``，本函数会忽略 ``sign``）
    - ``sign``：通知里携带的 Base64 签名
    - ``alipay_public_key``：支付宝公钥 PEM
    """
    if not sign:
        return False
    sign_str = _build_sign_string(params)
    try:
        public_key = _load_public_key(alipay_public_key)
        public_key.verify(
            base64.b64decode(sign.encode("utf-8")),
            sign_str.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def build_signed_params(
    params: Mapping[str, str],
    app_private_key: str,
) -> dict[str, str]:
    """按支付宝规则生成「已签名参数集」：有序参数 + 追加 ``sign``。

    页面跳转类接口（如 ``alipay.trade.page.pay``）的官方 ``page_execute``
    返回一个 HTML 表单，**每个参数都是一个 hidden input**（action 不拼 query）。
    本函数返回的字典即表单 hidden inputs 的数据源，保证渲染内容与签名参数集
    一一对应，避免参数重复或顺序歧义。
    """
    ordered: dict[str, str] = {
        k: v for k, v in params.items() if k not in _SIGN_EXCLUDE and v != ""
    }
    sign = sign_params(ordered, app_private_key)
    ordered["sign"] = sign
    return ordered


def build_signed_query(
    params: Mapping[str, str],
    app_private_key: str,
) -> str:
    """生成为网关请求的最终查询串（含 sign）。"""
    signed = build_signed_params(params, app_private_key)
    import urllib.parse

    return "&".join(
        f"{k}={urllib.parse.quote(v, safe='')}" for k, v in signed.items()
    )


def parse_notify_params(raw: Mapping[str, str]) -> tuple[dict[str, str], str]:
    """从异步通知原始参数分离出「验签参数集」与「sign」。

    返回 ``(params_including_sign_excluded, sign)``。
    注意支付宝异步通知参数集**不含** ``sign_type``（那是请求侧的键，
    通知体只回传 ``sign``）。
    """
    params = {k: v for k, v in raw.items() if k != "sign"}
    sign = raw.get("sign", "")
    return params, sign