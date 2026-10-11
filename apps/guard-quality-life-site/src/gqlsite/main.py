"""FastAPI 应用入口：知识树站点路由 + 访问埋点中间件 + 订阅表单。"""

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __version__
from .knowledge import all_domains, get_domain, get_entry, search
from .signals.track import (
    recommended_slot,
    record_subscription,
    record_visit,
)

PKG_DIR = Path(__file__).parent
TEMPLATES_DIR = PKG_DIR / "templates"
STATIC_DIR = PKG_DIR / "static"

# 访问埋点豁免的路径（静态资源 / 健康检查不计数）
_TRACK_SKIP = {"/static", "/ping"}


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

    # ---------------- 健康检查 ----------------

    @app.get("/ping", response_class=JSONResponse)
    def ping():
        return {"status": "ok"}

    return app


app = create_app()