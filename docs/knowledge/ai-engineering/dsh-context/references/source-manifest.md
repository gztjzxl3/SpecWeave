# dsh-context 信源清单（Source Manifest）

> 采集协议：wechat-public-okf（公开文章 → OKF）。本页登记可访问来源、所有权信号与采集边界。

## 采集信息

| 项 | 值 |
|----|----|
| 采集会话 | `sc-20261010-dsh-context` |
| 采集方式 | 公开 URL 读取（defuddle 提取）；GitHub 仓库只读核验 |
| 采集时间 | 2026-10-10 |
| 内容敏感度 | 公开（Public）→ 根 `docs/knowledge/` |

## 来源登记表

| source_id | URL | 标题/身份 | 账号/归属 | 所有权信号 | 可达性 | status |
|-----------|-----|-----------|-----------|-----------|--------|--------|
| `wechat-article` | https://mp.weixin.qq.com/s/e_eUY2RkT0QbZy4oCvL6UQ | dsh-context：让 DeepSeek Harness 上下文生命周期可视化 | 微信公众号「AI开源无界」 | 文末公众号名片、推广口径 | 经 defuddle 公开读取；WebFetch 首访遇"环境异常"弹窗，二次路径成功 | collected |
| `github-repo` | https://github.com/bowenliang123/dsh-context | dsh-context 开源仓库 | bowenliang123（作者） | Apache-2.0、约 2.0k star、59 fork、902 commits | 公开读取 | collected |
| `npm-package` | https://www.npmjs.com/package/dsh-context | dsh-context npm 包 | bowenliang123 | 包名与仓库同名 | 公开（未单独抓取版本明细） | referenced |

## 所有权与公信信号

- **作者**：bowenliang123，dsh-context 仓库 owner，Apache-2.0 重新授权（2026-08-14 提交"relicense the project under Apache-2.0"）。
- **官方背书信号**：README 标注被 DeepSeek Harness 团队成员 @tianyicui、@turtle1999 推荐并 star；并附 X 帖子链接。属第三方观察，非官方保证。
- **发布账号**：公众号「AI开源无界」，以推广实用开源项目为定位；文中"我感觉可以让我使用 DSH 的体验上升一个档次"等为**作者/发布者观点**，非事实。

## 采集边界与停步规则

1. 公众号文章正文完整提取（defuddle，无正文镜像入库，仅作分析信源）。
2. 不绕过登录、验证码、邀请码或访问控制；WebFetch 首访弹"环境异常"即记录并切换合法路径，未做任何绕过。
3. 未保存文章全文/反爬 HTML dump 入 bundle；只做事实登记与原创改写。
4. P0 声明（安装命令、版本兼容、Node 要求）以 GitHub README 为准核验；公众号文内版本断言存在时效漂移，见 [verification.md](verification.md)。