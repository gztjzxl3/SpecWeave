# 守护品质生活（guard-quality-life-site）

> 按「生活域」浏览的品质生活知识树动态网站。把值得坚持的日常，整理成 11 个可浏览、可搜索的生活域，
> 每条都是一份"五要素"可执行建议（目的 / 步骤 / 成本收益 / 证据等级 / 禁忌边界）。
> 现已在原 MVP 基础上升级为**可真实交易的付费会员/内容体系**。

## 技术定位

- **FastAPI + Jinja2 + SQLite（标准库）** 构建，Python **3.14+**，纯本地、零外部重型服务。
- `src/gqlsite/` 为可安装包（scikit-build-core + src 布局），`wheel.packages = ["src/gqlsite"]`。
- 数据层（`knowledge.py`）+ 应用层（`main.py`）+ 信号持久化（`signals/`）三层解耦，便于替换数据来源或展示层。
- 支付：标准库 `cryptography` 实现支付宝 RSA2 签名/验签（不依赖 `alipay-sdk-python`）。
- 视觉偏好：**阅读优先、暖灰纸感**（暖灰底 `#F5F3EF`、米白卡片 `#FFFDF9`、深灰褐文字 `#3D3833`，无纯黑/高对比深色模式）。

## 目录结构

```
apps/guard-quality-life-site/
├── pyproject.toml              # scikit-build-core + src 布局 + ruff banned-api
├── tasks.py                    # invoke 任务：run / test / check / tunnel
├── .env.example                # 支付宝沙箱凭据填写模板（复制为 .env 使用）
├── README.md
├── src/gqlsite/
│   ├── __init__.py             # 版本号
│   ├── __main__.py             # python -m gqlsite 启动
│   ├── main.py                 # FastAPI 应用（路由 + 埋点中间件 + 支付路由）
│   ├── knowledge.py            # 知识树数据层（Domain → Entry，11 域）
│   ├── signals/
│   │   ├── __init__.py
│   │   └── track.py            # 三验证信号持久化（SQLite）
│   ├── payments/               # 支付子包
│   │   ├── __init__.py
│   │   ├── config.py           # 环境变量注入 + 占位符检测 + is_ready()
│   │   ├── sign.py             # RSA2 签名/验签（PKCS#1 + SHA256WithRSA）
│   │   ├── store.py            # 订单表 + 幂等状态机（PENDING→PAID）
│   │   └── gateway.py          # 下单表单 + 异步通知入账
│   ├── templates/              # Jinja2 模板（暖灰纸感 UI）
│   └── static/styles.css       # 全套样式变量与组件
└── tests/                      # 知识层 / 信号层 / Web 层 / 支付层 / __future__ 门禁
```

## 快速开始

```powershell
# 0) 进入 py314 环境（本机 conda 环境名为 py314，Python 3.14+）
conda activate py314

# 1) 安装依赖（一次即可）
cd apps/guard-quality-life-site
python -m pip install -e ".[dev]" --no-build-isolation

# 2) 启动（三种方式任选，均需在应用目录下）
$env:PYTHONPATH = "src"
python -m invoke run       # invoke
python -m gqlsite          # python -m
python -m uvicorn gqlsite.main:app --host 127.0.0.1 --port 8000 --reload  # uvicorn
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
| POST | `/subscribe` | 接收姓名/邮箱/兴趣域，写入 SQLite |
| GET | `/checkout/{product}` | 下单页：渲染支付宝电脑网站支付表单 |
| POST | `/pay/notify` | 支付宝异步通知（验签入账，返回 `success`/`failure`） |
| GET | `/order/{id}` | 订单状态展示页 |
| GET | `/ping` | 健康检查，返回 `{"status":"ok"}` |

## 测试

```powershell
python -m invoke test    # pytest
python -m invoke check   # ruff + pytest
```

必测项：

- `test_knowledge.py`：域数 ≥10、`get_domain`/`get_entry`/`search` 正确。
- `test_signals.py`：订阅写入、访问埋点、推荐位占位。
- `test_web.py`：TestClient 覆盖首页 / 域 / 条目 / 搜索 / 订阅 POST / 404 / ping / 静态 CSS。
- `test_payments.py`：RSA2 验签往返、下单表单契约、异步通知状态机（幂等入账 / 坏签名拒绝 / app_id 校验 / 金额校验）、凭据缺失降级路由。
- `test_no_future_annotations.py`：AST 断言 `src` 与 `tests` 下无 `from __future__`。

覆盖率目标：整体 ≥80%，`signals/`、`knowledge.py` 与 `payments/` ≥90%。

## 三验证信号（signals/）

访问埋点中间件与订阅登记合并为三路信号，统一走 SQLite（标准库 `sqlite3`）：

1. **订阅登记** — `record_subscription(name, email, interests)` 写入 `subscriptions` 表。
2. **访问埋点** — `record_visit(path, referer, ip)` 写入 `visits` 表；`/static` 与 `/ping` 豁免不计数。
3. **推荐位占位** — `recommended_slot()` 返回 `RECOMMENDED_SLOT`（{"title": "推荐位", "note": "占位，后续接入真实商务"}），以模板全局注入。

数据库路径由环境变量 `GQLSITE_DB` 指定；未设置默认 `src` 同级的仓库根 `.data/gqlsite.db`；不可写时回退内存库。`init_db()` 幂等建表。

## 与知识包同源说明

内置 11 个生活域与知识包 `concepts` 一致：`home 家居 / health 健康 / diet 饮食 / sleep 睡眠 / efficiency 效率 / finance 财务 / relation 关系 / mind 心理 / travel 出行 / digital 数字生活 / safety 安全`。每条条目的 `evidence_level` 采用 A（强证据）/ B（中等和观察证据）/ C（经验级）三级并标注来源，`caveat` 记录禁忌/边界。

## 开通真实支付

接入的是**支付宝电脑网站支付**（`alipay.trade.page.pay`，产品码 `FAST_INSTANT_TRADE_PAY`）。

### ① 申领凭据

1. 前往 [支付宝开放平台](https://open.alipay.com) → 控制台 → 沙箱应用。
2. 获取：应用 `AppId`、应用公私钥（**私钥选 PKCS#1 格式**，非 JAVA）、支付宝公钥、沙箱买家/商家测试账号。
3. 复制 `.env.example` 为 `.env`，逐项如实填写（**禁止编造任何值**）。

### ② 加载配置

```powershell
$env:PYTHONPATH = "src"
python -m uvicorn gqlsite.main:app --port 8000 --env-file .env
```

> 凭据未配置时，站点自动降级为「支付待配置」，不产生任何真实扣款。

### ③ 提供公网回调（沙箱异步通知必需）

```powershell
python -m invoke tunnel
```

将终端打印的 `https://<随机>.trycloudflare.com` 填入：

```
GQLSITE_PAY_NOTIFY_URL=https://<随机>.trycloudflare.com/pay/notify
GQLSITE_PAY_RETURN_URL=https://<随机>.trycloudflare.com/checkout/gql-weekly
```

`cloudflared` 未安装时，`invoke tunnel` 会给出 winget 安装指引。

### ④ 验证闭环

- 访问 `http://127.0.0.1:8000/checkout/gql-weekly` 选择权益 → 跳转支付宝收银台。
- 用沙箱买家账号付款 → 页面回跳 `/order/{id}` 展示订单状态。
- 支付宝异步通知经 `/pay/notify` 验签入账（幂等），订单由 `PENDING` → `PAID`。

## 安全红线（务必遵守）

- 应用私钥（PKCS#1）与 `.env` **禁止**提交进 Git、写入日志或暴露在前端。
- `.env` 已被 `.gitignore` 忽略；`.env.example` 仅作模板可入库。
- 异步通知 `/pay/notify` **必须先验签**再入账；重复成功通知不重复发放（幂等）。
- 正式上线前将 `GQLSITE_PAY_PROD=1` 并换用正式网关与正式凭据。

## 已知限制

- MVP 阶段为单机、无认证；会话级内容不涉及私密数据，仅在 127.0.0.1 监听。
- 订阅表单仅写入本地 SQLite，未接真实邮件发送。
- 埋点为每次请求同步写库；流量大时应改为后台队列/批量落盘（MVP 不做）。
- 支付异步通知需公网可达 URL，沙箱环境依赖内网穿透工具；正式环境须换成正式凭据与回填公网域名。