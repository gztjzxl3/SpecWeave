"""invoke 任务入口：run / test / check。

用法（在 apps/guard-quality-life-site/ 下）：
    invoke run    # 启动 uvicorn 开发服务器（127.0.0.1:8000，reload）
    invoke test   # 跑 pytest
    invoke check  # ruff 检查 + pytest
"""

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