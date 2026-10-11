# 守护品质生活 · 动态 Web 服务 MVP

一个按「生活域」浏览的品质生活知识树动态站点。把值得坚持的日常，整理成 11 个可浏览、
可搜索的生活域，每条都是一份"五要素"可执行建议（目的 / 步骤 / 成本收益 / 证据等级 / 禁忌边界）。

基于 **FastAPI + Jinja2 + SQLite（标准库）** 构建，Python 3.14+，纯本地、零外部重型服务。

## 定位

- `src/gqlsite/` 为可安装包（scikit-build-core + src 布局），`wheel.packages = ["src/gqlsite"]`。
- 数据层（`knowledge.py`）+ 应用层（`main.py`）+ 信号持久化（`signals/`）三层解耦，便于后续替换数据来源或展示层。
- 视觉偏好：**阅读优先、暖灰纸感**（暖灰底 `#F5F3EF`、米白卡片 `#FFFDF9`、深灰褐文字 `#3D3833`，无纯黑/高对比深色模式）。

## 目录结构

```
apps/guard-quality-life-site/
├── pyproject.toml              # scikit-build-core + src 布局 + ruff banned-api
├── tasks.py                    # invoke: run / test / check
├── README.md
├── src/gqlsite/
│   ├── __init__.py             # 版本号
│   ├── __main__.py             # python -m gqlsite 启动
│   ├── main.py                 # FastAPI 应用（路由 + 埋点中间件）
│   ├── knowledge.py            # 知识树数据层（Domain → Entry，11 域）
│   ├── signals/
│   │   ├── __init__.py
│   │   └── track.py            # 三验证信号持久化（SQLite）
│   ├── templates/              # Jinja2 模板（暖灰纸感 UI）
│   └── static/styles.css       # 全套样式变量与组件
└── tests/                      # 知识层 / 信号层 / Web 层 / __future__ 门禁
```

## 启动

先去应用目录安装依赖（一次性）：

```bash
cd apps/guard-quality-life-site
pip install -e . --no-build-isolation   # 安装运行时依赖
pip install -e ".[dev]" --no-build-isolation  # 含测试/ruff
```

方式一（invoke）：

```bash
invoke run     # uvicorn 127.0.0.1:8000，reload
```

方式二（`python -m`）：

```bash
python -m gqlsite
```

方式三（uvicorn 命令行）：

```bash
python -m uvicorn gqlsite.main:app --host 127.0.0.1 --port 8000 --reload
```

浏览器访问 <http://127.0.0.1:8000>。

## 路由一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 首页：按域知识树总览卡片网格 |
| GET | `/domain/{domain_id}` | 某域详情 + 条目列表 |
| GET | `/entry/{domain_id}/{entry_id}` | 某条目详情（渲染五要素） |
| GET | `/search?q=` | 搜索 |
| GET | `/subscribe` | 订阅/兴趣登记表单 |
| POST | `/subscribe` | 接收姓名/邮箱/兴趣域，写入 SQLite，返回成功页 |
| GET | `/ping` | 健康检查，返回 `{"status":"ok"}` |

## 测试

```bash
invoke test     # pytest
invoke check    # ruff + pytest
```

必测项：

- `test_knowledge.py`：域数 ≥10、`get_domain`/`get_entry`/`search` 正确。
- `test_signals.py`：订阅写入、访问埋点、推荐位占位。
- `test_web.py`：TestClient 覆盖首页 / 域 / 条目 / 搜索 / 订阅 POST / 404 / ping / 静态 CSS。
- `test_no_future_annotations.py`：AST 断言 `src` 与 `tests` 下无 `from __future__`。

覆盖率目标：整体 ≥80%，`signals/` 与 `knowledge.py` ≥90%。

## 三验证信号（signals/）

访问埋点中间件与订阅登记合并为三路信号，统一走 SQLite（标准库 `sqlite3`）：

1. **订阅登记** — `record_subscription(name, email, interests)` 写入 `subscriptions` 表。
2. **访问埋点** — `record_visit(path, referer, ip)` 写入 `visits` 表；`/static` 与 `/ping` 豁免不计数。
3. **推荐位占位** — `recommended_slot()` 返回 `RECOMMENDED_SLOT`（{"title": "推荐位", "note": "占位，后续接入真实商务"}），以模板全局注入，所有页面渲染该占位。

数据库路径由环境变量 `GQLSITE_DB` 指定；未设置默认 `src 同级的仓库根/.data/gqlsite.db`；不可写时回退内存库保证测试可跑。`init_db()` 幂等建表。

## 与知识包同源说明

内置 11 个生活域的域名与知识包 `concepts` 一致：`home 家居 / health 健康 / diet 饮食 / sleep 睡眠 / efficiency 效率 / finance 财务 / relation 关系 / mind 心理 / travel 出行 / digital 数字生活 / safety 安全`。每条条目的 `evidence_level` 采用 A（强证据） / B（中等和观察证据） / C（经验级）三级并标注来源，`caveat` 记录禁忌/边界。

## 已知限制

- MVP 阶段为单机、无认证；会话级内容不涉及私密数据，仅在 127.0.0.1 监听。
- 订阅表单仅写入本地 SQLite，未接真实邮件发送。
- 埋点为每次请求同步写库；流量大时应改为后台队列/批量落盘（MVP 不做）。