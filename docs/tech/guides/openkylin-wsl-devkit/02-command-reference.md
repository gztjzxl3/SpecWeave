---
type: "Reference"
title: "okw WSL 与开发命令参考"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#用法"
---

# okw WSL 与开发命令参考

`okw` 封装 WSL 发行版操作、环境验收、deb/dput 脚手架和 openKylin 知识参考。`unregister` 会注销发行版，必须显式提供 `--yes`。

## 发行版生命周期

| 命令 | 用途 |
|---|---|
| `okw list` | 列出 WSL 发行版并标出默认项 |
| `okw status <name>` | 查看单个发行版状态 |
| `okw import <image> --name <name> --location <path> [--version 2]` | 导入镜像 |
| `okw export <name> --output <tar>` | 导出发行版 |
| `okw unregister <name> --yes` | 确认并注销发行版 |
| `okw exec <name> -- <cmd...>` | 在目标发行版内执行命令 |
| `okw verify <name>` | 执行 openKylin 环境五步验收 |

示例：

```powershell
okw import .\openKylin-3.0-wsl-amd64.wsl --name openKylin-3.0 --location D:\wsl\ok30 --version 2
okw exec openKylin-3.0 -- uname -a
okw export openKylin-3.0 --output .\openKylin-3.0.tar
```

发行版名称可用 `okw list` 或 Windows 侧 `wsl -l -v` 查询。导入时若失败，工具会提示按知识库中的排障三问检查镜像/导入位置、空闲内存和纯 tar 导入路径；详见 [WSL 安装与稀疏 VHD 实操指南](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md)。

## 开发脚手架

生成 deb 打包骨架：

```text
okw scaffold deb --project demo --series huanghe --version 0.1.0
```

支持 `yangtze`、`nile`、`huanghe` 系列代号，也可按工具说明使用 `1.0`、`2.0`、`3.0`。生成后编辑 `control`/`changelog`、将源码放入项目根目录，再按提示运行 `dpkg-buildpackage -us -uc`。

生成 OKBS dput 配置片段：

```text
okw scaffold dput --openkylin-id <你的ID> [--output ~/.dput.cf]
```

默认只打印配置；指定 `--output` 才写入文件。上传由开发者自行执行，命令会提示 `dput okbs:~<你的ID>/ppa <source.changes>`；上传需要自行安装 `paramiko` 或 `dput-ng`。

## 开发容器镜像

`okw image` 接管 openKylin 开发容器镜像（`openkylin-dev-container`）的构建与验收，在发行版内以 root 身份执行：

```text
okw image build <name> [--tag <tag>] [--base-image <镜像>] [--pull-base] [--no-cache] [--context <路径>]
okw image verify <name> [--image <镜像>] [--no-boot]
```

`build`：默认基镜像 `localhost/openkylin:3.0` 仅接受本地 exists（禁隐式拉取，`--pull-base` 显式放行）；构建上下文自动同步 Windows 路径→发行版内 `/tmp/okw-build-*/ctx`；`--format docker` 必须（OCI 格式会静默丢弃 `SHELL`/`HEALTHCHECK`）。

`verify`：镜像 exists 禁拉 → 静态探针 P1-P8（sshd/jupyter/supervisord/locale/时区/devuser/subuid/podman 二进制）→ 全量启动等 HEALTHCHECK → 服务探针（SSH/Jupyter 进程、22/8888 端口、Jupyter HTTP 200）→ 清理；`--no-boot` 只做静态。退出码 0 成功 / 1 失败 / 2 前置条件不满足，对齐 podman 组纪律。

示例：

```powershell
okw image build openKylin-3.0-desktop --tag my-dev
okw image verify openKylin-3.0-desktop
```

容器运行契约与镜像详情见 [openKylin 开发容器指南](05-openkylin-dev-container.md)。

## xuan-compose（xc）下游引导

`okw compose` 在 rootless Podman 就绪后，以默认普通用户身份经用户级 uv 引导 xuan-compose（`xc`），并生成 `xuan-compose`/`xc` 双 shim：

```text
okw compose preflight <name> [--source <来源>]
okw compose install  <name> --source <来源> --yes [--editable]
okw compose verify   <name> [--smoke]
```

- `--source` **必填**且无内置默认值，自动归类为本地目录（Windows 路径转 `/mnt/<drive>/...`，校验 `pyproject.toml`，默认拷贝安装）、`git+https` 等 URL/VCS（原样交 uv，不触网预检），或 PEP 503 包名；畸形来源以退出码 2 拒绝且零 WSL 调用。`--editable` 仅限本地源。
- `install` 必须 `--yes`：缺省时只打印四步副作用清单与 GPL 声明（退出码 2，零写入）。安装把 uv 置于 `~/.local/bin`、把 CPython 3.14 交 uv 托管（不改系统 Python），再 `uv tool install --python 3.14`；已登记则 `--force` 幂等重装。
- `verify` 全路径比对双 shim 的 `version --short`；`--smoke` 在 `/tmp/okw-smoke-*` 隔离目录写最小 `compose.yaml` 跑 `xc config --quiet` 做端到端探活，不起容器、不拉镜像，前置有 FAIL 则跳过。
- 退出码 `0` 全通过 / `1` 有 FAIL / `2` 用法错误、仅 UNKNOWN 或缺 `--yes`。

> 许可证边界：xuan-compose 为 **GPL-2.0-only** 第三方软件，okw（MIT）不 import、不复制、不分发，仅在你显式授权后按你指定来源在本机引导安装。完整机制、镜像环境变量与常见问题见 [xuan-compose（xc）引导指南](06-xuan-compose.md)。

## 知识库参考

```text
okw ref
okw ref series
okw ref wsl-troubleshoot
okw ref okbs
okw ref verify
```

`okw ref` 不修改知识库。openKylin 版本代号和开发流程见[知识库对应页面](../../../knowledge/tech/openkylin-docs-wiki/concepts/02-release-lifecycle.md)与[开发者基础设施](../../../knowledge/tech/openkylin-docs-wiki/concepts/06-developer-infrastructure.md)。
