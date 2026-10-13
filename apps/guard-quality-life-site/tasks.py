"""invoke 任务入口：run / test / check / tunnel。

用法（在 apps/guard-quality-life-site/ 下）：
    invoke run       # 启动 uvicorn 开发服务器（127.0.0.1:8000，reload）
    invoke test      # 跑 pytest
    invoke check     # ruff 检查 + pytest
    invoke tunnel    # 启动 cloudflared quick tunnel 转发到本机 8000（沙箱回调用）
"""

import shutil

from invoke import task


@task
def run(ctx):
    """启动 uvicorn 开发服务器（127.0.0.1:8000，reload）。"""
    ctx.run(
        "python -m uvicorn gqlsite.main:app --host 127.0.0.1 --port 8000 --reload",
        pty=False,
    )


@task
def test(ctx):
    """运行完整测试套件（pytest）。"""
    ctx.run("python -m pytest tests/ -q", pty=False)


@task
def check(ctx):
    """ruff 检查 + pytest。"""
    ctx.run("python -m ruff check src tests", pty=False)
    ctx.run("python -m pytest tests/ -q", pty=False)


@task
def tunnel(ctx, port: int = 8000):
    """为支付宝沙箱异步通知提供公网可达回调：cloudflared quick tunnel。

    零配置、免注册 token：将 https://<随机>.trycloudflare.com 转发到本机
    ``http://127.0.0.1:<port>``。启动后把终端打印的 HTTPS 地址填入
    ``GQLSITE_PAY_NOTIFY_URL``（拼接 ``/pay/notify``）与
    ``GQLSITE_PAY_RETURN_URL``（拼接 ``/checkout/{product}`` 或一个落地页）。

    cloudflared 未安装时本任务会给出安装指引后退出，不会静默安装。
    """
    if shutil.which("cloudflared") is None:
        ctx.run("winget search Cloudflare.Cloudflared", pty=False)
        ctx.run(
            "winget install --id Cloudflare.Cloudflared -e "
            "--scope user --accept-package-agreements --accept-source-agreements",
            pty=False,
        )
        print(
            "\n[提示] 已安装 cloudflared，请重新执行 `invoke tunnel` 启动隧道。"
        )
        return
    ctx.run(
        f"cloudflared tunnel --url http://127.0.0.1:{port} --no-autoupdate",
        pty=False,
    )