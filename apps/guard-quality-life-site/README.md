# 守护品质生活（guard-quality-life-site）

> 按域浏览的「品质生活知识树」动态站点：FastAPI + Jinja2 + SQLite，三验证信号（知识/传播/内容校验），暖灰纸感 UI。现已升级为可真实交易的付费会员/内容体系。

## 技术栈

- Python **3.14+**（`requires-python = ">=3.14"`）
- FastAPI + Uvicorn + Jinja2 + SQLite（`sqlite3` 标准库）
- 支付：标准库 `cryptography` 实现支付宝 RSA2 签名/验签（不依赖 `alipay-sdk-python`）
- 构建：scikit-build-core（src 布局），任务管理：invoke

## 目录结构

```
apps/guard-quality-life-site/
├── pyproject.toml          # scikit-build-core 构建、依赖、ruff banned-api
├── tasks.py                # invoke 任务：run / test / check / tunnel
├── .env.example            # 支付宝沙箱凭据填写模板（复制为 .env 使用）
├── src/gqlsite/
│   ├── main.py             # FastAPI 路由（内容浏览 + 订阅 + 支付）
│   ├── knowledge.py        # 11 域知识树数据
│   ├── signals/track.py    # 订阅/访问信号落库
│   ├── payments/           # 支付子包
│   │   ├── config.py       # 环境变量注入 + 占位符检测 + is_ready()
│   │   ├── sign.py         # RSA2 签名/验签（PKCS#1 + SHA256WithRSA）
│   │   ├── store.py        # 订单表 + 幂等状态机（PENDING→PAID）
│   │   └── gateway.py      # 下单表单 + 异步通知入账
│   └── templates/          # Jinja2 模板（含 base/checkout/order/subscribe）
└── tests/                  # pytest 套件
```

## 快速开始

```powershell
# 1) 安装依赖（py314 环境）
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m pip install -e ".[dev]"

# 2) 启动开发服务器（127.0.0.1:8000，reload）
$env:PYTHONPATH = "src"
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m invoke run
# 或直接：python -m uvicorn gqlsite.main:app --host 127.0.0.1 --port 8000 --reload
```

## 测试

```powershell
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m invoke check   # ruff + pytest
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m invoke test    # 仅 pytest
```

## 开通真实支付

接入的是**支付宝电脑网站支付**（`alipay.trade.page.pay`，产品码 `FAST_INSTANT_TRADE_PAY`）。

### ① 申领凭据

1. 前往 [支付宝开放平台](https://open.alipay.com) → 控制台 → 沙箱应用。
2. 获取：应用 `AppId`、应用公私钥（**私钥选 PKCS#1 格式**，非 JAVA）、支付宝公钥、沙箱买家/商家测试账号。
3. 复制 `.env.example` 为 `.env`，逐项如实填写（**禁止编造任何值**）。

### ② 加载配置

```powershell
$env:PYTHONPATH = "src"
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m uvicorn gqlsite.main:app --port 8000 --env-file .env
```

> 凭据未配置时，站点会自动降级为「支付待配置」，不产生任何真实扣款。

### ③ 提供公网回调（沙箱异步通知必需）

```powershell
D:\Users\xinzo\anaconda3\envs\py314\python.exe -m invoke tunnel
```

将终端打印的 `https://<随机>.trycloudflare.com` 填入：

```
GQLSITE_PAY_NOTIFY_URL=https://<随机>.trycloudflare.com/pay/notify
GQLSITE_PAY_RETURN_URL=https://<随机>.trycloudflare.com/checkout/gql-weekly
```

若 `cloudflared` 未安装，`invoke tunnel` 会给出 winget 安装指引。

### ④ 验证闭环

- 访问 `http://127.0.0.1:8000/checkout/gql-weekly` 选择权益 → 跳转支付宝收银台。
- 用沙箱买家账号付款 → 页面回跳 `/order/{id}` 展示订单状态。
- 支付宝异步通知经 `/pay/notify` 验签入账（幂等），订单由 `PENDING` → `PAID`。

## 安全红线（务必遵守）

- 应用私钥（PKCS#1）与 `.env` **禁止**提交进 Git、写入日志或暴露在前端。
- `.env` 已被 `.gitignore` 忽略；`.env.example` 仅作模板可入库。
- 异步通知 `/pay/notify` **必须先验签**再入账；重复成功通知不重复发放（幂等）。
- 正式上线前将 `GQLSITE_PAY_PROD=1` 并换用正式网关与正式凭据。