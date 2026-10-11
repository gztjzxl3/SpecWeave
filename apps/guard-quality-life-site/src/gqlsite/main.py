"""FastAPI 应用入口：知识树站点路由 + 访问埋点中间件 + 订阅表单 + 支付权益。

支付闭环（支付宝电脑网站支付）：
- ``/checkout/{product}``：下单页 + 创建订单并渲染支付宝支付表单
- ``/pay/notify``：异步通知验签入账（返回 ``success``/``failure``）
- ``/order/{out_trade_no}``：订单状态页

凭据未配置时优雅降级为「支付待配置」，不影响知识树浏览与登记。
"""

from datetime import datetime
from pathlib import Path
from secrets import token_hex
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __version__
from .knowledge import all_domains, get_domain, get_entry, search
from .payments import (
    PaymentNotConfigured,
    build_page_pay_form,
    create_order,
    get_order,
    handle_notify,
    load_payment_config,
    notify_result,
)
from .signals.track import (
    recommended_slot,
    record_subscription,
    record_visit,
)

PKG_DIR = Path(__file__).parent
TEMPLATES_DIR = PKG_DIR / "templates"
STATIC_DIR = PKG_DIR / "static"

# 访问埋点豁免的路径（静态资源 / 健康检查 / 支付回调不计数）
_TRACK_SKIP = {"/static", "/ping", "/pay/notify"}

# 付费权益商品目录（唯一 key → 展示信息）。把站点从「兴趣登记」升级为
# 「付费内容/会员」：购买任一商品即解锁对应权益（权益发放逻辑见 order 页）。
PRODUCTS: dict[str, dict[str, str]] = {
    "gql-weekly": {
        "name": "「守护品质生活」年度会员",
        "price": "88.00",
        "desc": "解锁全部 11 域知识树的完整条目与后续每周更新。",
    },
    "gql-guide-pdf": {
        "name": "《品质生活行动指南》电子版",
        "price": "29.90",
        "desc": "精选 30 条高证据等级建议，整理为可打印的 PDF 行动清单。",
    },
}


def _new_out_trade_no(prefix: str) -> str:
    """生成唯一商户订单号：``<prefix>-<时间戳秒>-<6位随机16进制>``。"""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{ts}-{token_hex(3)}"


def _product_or_none(product_id: str) -> Optional[dict[str, str]]:
    return PRODUCTS.get(product_id)


def create_app() -> FastAPI:
    app = FastAPI(
        title="守护品质生活",
        version=__version__,
        description="按域浏览的品质生活知识树动态站点",
    )
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    # 推荐位占位注入为模板全局，所有页面（含 notfound）均可引用
    templates.env.globals["slot"] = recommended_slot()
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    def render(request: Request, name: str, **context: object) -> HTMLResponse:
        ctx: dict[str, object] = {"request": request, "version": __version__}
        ctx.update(context)
        return templates.TemplateResponse(request, name, ctx)

    @app.middleware("http")
    async def track_visits(request: Request, call_next):
        response = await call_next(request)
        try:
            path = request.url.path
            if path.startswith("/static") or path in _TRACK_SKIP:
                return response
            referer = request.headers.get("referer", "")
            ip = request.client.host if request.client is not None else ""
            record_visit(path, referer=referer, ip=ip)
        except Exception:
            # 埋点失败绝不影响页面本身
            pass
        return response

    # ---------------- 页面 ----------------

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        domains = all_domains()
        total_entries = sum(len(d.entries) for d in domains)
        return render(
            request,
            "index.html",
            domains=domains,
            total_domains=len(domains),
            total_entries=total_entries,
        )

    def not_found(request: Request, kind: str, key: str) -> HTMLResponse:
        # TemplateResponse 的 status_code 通过 context 透传给响应
        return templates.TemplateResponse(
            request, "notfound.html", {"request": request, "kind": kind, "key": key}, status_code=404
        )

    @app.get("/domain/{domain_id}", response_class=HTMLResponse)
    def domain_page(request: Request, domain_id: str):
        domain = get_domain(domain_id)
        if domain is None:
            return not_found(request, "域", domain_id)
        return render(
            request,
            "domain.html",
            domain=domain,
        )

    @app.get("/entry/{domain_id}/{entry_id}", response_class=HTMLResponse)
    def entry_page(request: Request, domain_id: str, entry_id: str):
        found = get_entry(domain_id, entry_id)
        if found is None:
            return not_found(request, "条目", f"{domain_id}/{entry_id}")
        domain, entry = found
        return render(
            request,
            "entry.html",
            domain=domain,
            entry=entry,
        )

    @app.get("/search", response_class=HTMLResponse)
    def search_page(request: Request, q: str = ""):
        results = search(q)
        return render(
            request,
            "search.html",
            query=q,
            results=results,
            result_count=len(results),
        )

    @app.get("/subscribe", response_class=HTMLResponse)
    def subscribe_form(request: Request):
        return render(
            request,
            "subscribe.html",
            domains=all_domains(),
            submitted=False,
        )

    @app.post("/subscribe", response_class=HTMLResponse)
    def subscribe_submit(
        request: Request,
        name: str = Form(""),
        email: str = Form(""),
        interests: list[str] = Form(default=[]),
    ):
        row_id = record_subscription(name.strip(), email.strip(), ",".join(interests))
        return render(
            request,
            "subscribe.html",
            domains=all_domains(),
            submitted=True,
            sub_id=row_id,
        )

    # ---------------- 支付（付费权益） ----------------

    @app.get("/checkout/{product}", response_class=HTMLResponse)
    def checkout_form(request: Request, product: str):
        item = _product_or_none(product)
        if item is None:
            return not_found(request, "商品", product)
        pay_ready = load_payment_config().is_ready()
        return render(
            request,
            "checkout.html",
            item=item,
            product_id=product,
            pay_ready=pay_ready,
            # 未配置真实凭据时由模板渲染「支付待配置」说明
            placeholder=not pay_ready,
        )

    @app.post("/checkout/{product}", response_class=HTMLResponse)
    def checkout_submit(request: Request, product: str):
        from .payments import PaymentConfig

        item = _product_or_none(product)
        if item is None:
            return not_found(request, "商品", product)
        config: PaymentConfig = load_payment_config()
        if not config.is_ready():
            return render(
                request,
                "checkout.html",
                item=item,
                product_id=product,
                pay_ready=False,
                placeholder=True,
                error="支付通道尚未配置真实凭据，暂无法发起交易。",
            )
        out_trade_no = _new_out_trade_no("gql")
        try:
            create_order(
                out_trade_no,
                product_code=product,
                amount=item["price"],
                subject=item["name"],
            )
            pay_form = build_page_pay_form(
                config,
                out_trade_no,
                item["price"],
                item["name"],
            )
        except PaymentNotConfigured:
            # 理论上已在上面拦截，防御性兜底
            return render(
                request,
                "checkout.html",
                item=item,
                product_id=product,
                pay_ready=False,
                placeholder=True,
                error="支付通道未配置，无法发起交易。",
            )
        return render(
            request,
            "checkout.html",
            item=item,
            product_id=product,
            pay_ready=True,
            placeholder=False,
            out_trade_no=out_trade_no,
            pay_form=pay_form,
        )

    @app.post("/pay/notify", response_class=PlainTextResponse)
    async def alipay_notify(request: Request):
        """支付宝异步通知：验签 → 校验业务字段 → 幂等入账。

        应答必须为纯文本 ``success``（成功，支付宝停止重发）或
        ``failure``（失败，支付宝稍后重发）。**前台不能信任，必须以本通知为准。**
        """
        raw = {k: v for k, v in (await request.form()).items()}
        config = load_payment_config()
        try:
            ok, msg = handle_notify(config, raw)
        except PaymentNotConfigured:
            return PlainTextResponse("failure")
        return PlainTextResponse(notify_result(ok, msg))

    @app.get("/order/{out_trade_no}", response_class=HTMLResponse)
    def order_page(request: Request, out_trade_no: str):
        order = get_order(out_trade_no)
        if order is None:
            return not_found(request, "订单", out_trade_no)
        return render(
            request,
            "order.html",
            order=order,
            item_name=order.subject,
        )

    # ---------------- 健康检查 ----------------

    @app.get("/ping", response_class=JSONResponse)
    def ping():
        return {"status": "ok"}

    return app


app = create_app()