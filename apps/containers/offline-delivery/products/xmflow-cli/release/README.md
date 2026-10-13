# xmflow-cli 离线交付包（XMNN 模型工具链客户运行时）

面向客户的**完全独立**运行环境：解压即用，**无需联网、无需 Python、
不依赖任何其他软件包**。内含 XMNN NPU 模型工具链的客户运行时（`xmflow`
命令行，六个子命令：compile / accuracy / infer / performance / excelreport /
pipeline），在容器内即可完成模型**编译、精度验证、真机/仿真推理、性能与
带宽分析、Excel 报告**全流程；不含任何源码，无需挂载开发目录。

> 👉 **第一次接触、完全不懂技术？** 先花 30 秒建立一个印象：
>
> - 这个交付包可以理解成**一台封装好的"软件电脑"**：里面已经装好 Python
>   3.14 运行时与 XMNN 工具链，你无需自己安装配置任何软件依赖。
> - "Podman"或"Docker"是运行这台"软件电脑"的**播放器**（二者装一个即可），
>   就像视频文件需要播放器才能打开。
> - 你要做的只有一件事：把命令**逐条复制粘贴**到一个叫"终端"的窗口里按回车。
>   下文会讲终端怎么打开、每条命令成功时长什么样。
> - 本产品**没有网页服务、没有端口、没有账号密码**——一切交互都是通过终端
>   执行 `xmflow` 命令。**红字不一定是报错**（黄字是提醒；只有 `[ERR ]`
>   红字且命令提前结束才是失败），拿不准就截图问对接人员。

## 1. 系统要求

| 项 | 要求 |
|---|---|
| 容器运行时（二者任选其一） | **Podman** 5.0+（推荐 Linux 客户）或 **Docker** 24.0+（含 Compose v2 插件） |
| 磁盘空间 | ≥ 5 GB 可用空间 |
| 内存 | ≥ 4 GB |
| 主机架构 | 仅支持 x86_64（amd64） |
| Windows 客户 | Windows 10/11 + **PowerShell 7.0+**（运行 `xmnnctl.ps1`），使用 Podman Machine 或 Docker Desktop |
| Linux / macOS 客户 | bash 4.0+（运行 `xmnnctl`） |

> 交付过程**不需要安装 Python**；Windows 上的 PowerShell 仅用于随包脚本。

> **关于"派生构建"**：`load` 会在你的电脑上把随包载荷（XMNN 工具链本体，
> 一个 wheel 文件）装进底座镜像，因此容器运行时需要具备 **build（构建镜像）
> 能力**——Podman 与 Docker 默认自带，无需额外安装；这一步额外占用约
> **1-3 分钟**与约 **0.2 GB** 磁盘（底座归档与 wheel 文件本身另占空间）。
> 整个过程仍然**完全离线**。

### 开始前，你需要准备三样东西

1. **播放器（Podman 或 Docker，二选一）**
   - Windows：推荐安装 [Podman Desktop](https://podman.io/docs/installation)（自带 Podman Machine）或 [Docker Desktop](https://www.docker.com/products/docker-desktop/)；安装后**先启动一次**，等后台图标显示为运行状态。
   - Linux：按 [Podman 官方指引](https://podman.io/docs/installation)用系统包管理器安装。
   - 不确定装没装？在终端执行 `podman --version`，能显示版本号即可；提示找不到命令就先安装。
2. **PowerShell 7（仅 Windows 需要）**：Windows 自带的旧版 PowerShell 5.1 不能用。安装 [PowerShell 7](https://github.com/PowerShell/PowerShell#get-powershell) 后，开始菜单里会出现 **PowerShell 7**。自检：在终端执行 `$PSVersionTable.PSVersion`，主版本号显示 **7** 即正确。
3. **解压后的交付包**：用系统"全部解压缩"或 7-Zip 解压到一个**路径不含空格和中文**的文件夹（例如 `D:\xmflow-cli\`）。⚠️ 不要直接在压缩包窗口里双击运行；解压后若出现两层同名文件夹（`xmflow-cli\xmflow-cli\`），请进入最内层。

## 2. 五分钟上手

> **执行位置**：以下命令均在**交付包根目录**（本 README 所在目录）执行；
> 判别标志——该目录含 `xmnnctl.ps1`、`artifacts/` 与 `payload/`（`workspace/`
> 首次 `up` 时自动创建，刚解压时可能还没有）。
> **SpecWeave 开发仓库**内厂商侧入口是 `apps/containers/offline-delivery` 的
> `bin/relpack`（负责暂存 wheel、构建镜像、打包与冒烟）；
> 在 `release/` 目录内仍按客户方式执行 `./xmnnctl <命令>`。

### 第 0 步：在正确的文件夹里打开终端（最容易出错）

1. 进入解压后的交付包，找到**能直接看到 `xmnnctl.ps1`（Windows）或 `xmnnctl`（Linux/macOS）文件**的那一层，这就是"交付包根目录"；它旁边应有 `artifacts` 文件夹（`workspace` 首次执行命令时自动创建）。
2. Windows：在文件夹空白处 **按住 Shift 点右键** → 选"在终端中打开"（Win11）或"在此处打开 PowerShell 窗口"；也可点击文件夹地址栏，清空后输入 `pwsh` 回车。macOS：可在"系统设置 → 键盘 → 键盘快捷键 → 服务"中开启"新建位于文件夹位置的终端窗口"，然后在文件夹右键→服务中打开。
3. 核对位置：在终端执行 `dir`（Linux/macOS 为 `ls`），输出列表中能看到 `xmnnctl.ps1` 即正确；看不到说明目录不对，回到第 1 步。
4. Windows 还需确认 **Podman Machine 或 Docker Desktop 已经启动**（任务栏托盘图标处于运行状态）。

> 📋 **终端操作小常识**：粘贴命令通常用**鼠标右键**或 `Ctrl+Shift+V`——注意终端里 `Ctrl+C` 的含义是"终止当前命令"，不是复制。每次只粘贴**一条**命令，按回车，等它执行完再粘贴下一条。

### Windows（PowerShell 7）

```powershell
# 如提示执行策略被拦截：
# pwsh -ExecutionPolicy Bypass -File .\xmnnctl.ps1 <命令>
.\xmnnctl.ps1 init      # 生成 .env（本产品无私有凭证：仅复制配置模板，含交付版本号）
.\xmnnctl.ps1 load      # 导入底座镜像并把随包载荷装进去（约 1-6 分钟），构建内自动跑 10 项守卫
```

### Linux / macOS

```bash
chmod +x xmnnctl        # 仅首次需要：赋予脚本可执行权限（执行一次即可）
./xmnnctl init          # 生成 .env（复制配置模板，含交付版本号）
./xmnnctl load          # 导入底座镜像并装入随包载荷，构建内自动跑 10 项守卫
```

**每条命令执行后，正常情况下你会看到：**

| 命令 | 预期输出与耗时（看到这些就是成功） |
|---|---|
| `init` | 绿字 `[ OK ] 初始化完成`，紧接着打印**交付版本**与**容器名**——请按交付通知核对版本号。重复执行只提示"已存在，跳过初始化"，不会覆盖 |
| `load` | 分两段，都会逐条打印进度：① 绿字"完整性校验通过：底座归档"→ 底座导入进度条（约 **1-5 分钟**，硬盘持续读写是正常现象）；② 绿字"完整性校验通过：载荷 wheel"→"派生构建载荷镜像"（约 **1-3 分钟**，日志末尾逐项列出 **10 项守卫结果**）。最后绿字"载荷已装入 localhost/xmflow-cli:<版本>"即成功。**任一步失败都会红字中止且不产出镜像，可直接重跑**（已导入的部分会自动跳过） |
| `smoke` | 逐项打印守卫检查结果并以"通过 N / 失败 0"收尾，即代表载荷镜像随时可复核 |

`load` 成功后即可开始跑模型任务。**推荐用法是下面的一次性 run**
（跑完即退、无需常驻服务）；`up` 常驻模式见 §2.1。

### 跑第一个编译任务（一次性 run，主推用法）

```bash
# 版本占位 <交付版本> 用 init/load 打印的交付版本号替换（与 .env 中 XMNN_VERSION 一致）
docker run --rm \
  -v "$PWD/workspace/models:/workspace/models:ro" \
  -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> compile -n demo.caffe.resnet50
```

Podman 用户将 `docker` 替换为 `podman` 即可；rootless Podman 若因 SELinux
拦截挂载报权限错误，在 `run` 后追加 `--security-opt label=disable`。
模型文件请先按 §4.2 的目录契约放进 `workspace/models/`（详见下文）。

### 2.1 常驻容器模式（可选）

需要反复交互（先编译、再精度、再推理）时，可以让容器常驻：

```bash
./xmnnctl up                                      # 启动常驻容器（保活等待）
docker exec -it xmflow-cli xmflow compile -n demo.caffe.resnet50   # 在容器内跑任务
./xmnnctl down                                    # 停止（workspace 数据保留）
```

## 3. 常用命令

| 操作 | Windows | Linux / macOS |
|---|---|---|
| 初始化配置（复制模板） | `.\xmnnctl.ps1 init` | `./xmnnctl init` |
| 导入底座并装入载荷 | `.\xmnnctl.ps1 load` | `./xmnnctl load` |
| 启动常驻容器 | `.\xmnnctl.ps1 up` | `./xmnnctl up` |
| 停止（保留 workspace 数据） | `.\xmnnctl.ps1 down` | `./xmnnctl down` |
| 查看状态 | `.\xmnnctl.ps1 ps` | `./xmnnctl ps` |
| 查看日志 | `.\xmnnctl.ps1 logs` | `./xmnnctl logs` |
| 运行 10 项载荷守卫 | `.\xmnnctl.ps1 smoke` | `./xmnnctl smoke` |
| 查看交付版本与底座/载荷摘要 | `.\xmnnctl.ps1 version` | `./xmnnctl version` |

### `load` 到底做了什么（一个命令，四步，可反复执行）

1. **预检**：确认容器运行时后台（Podman Machine / Docker Desktop）已启动；
2. **读清单**：核对 `artifacts/release.json` 与 `.env` 的 `XMNN_VERSION`，两者
   不一致会直接拒绝执行并告诉你该填哪个版本；
3. **底座镜像**：本机若已有与清单完全一致（镜像 Id 相同）的底座，**跳过导入**；
   否则先校验归档 sha256 再导入，导入后再次比对 Id（防止归档与清单不配套）；
4. **载荷**：校验 `payload/` 内 wheel 的 sha256 → 离线派生构建，把载荷装进底座，
   **构建过程内跑 10 项守卫与依赖校验**——任一不过即中止且不产出镜像。

派生出的镜像 tag 就是 `.env` 里的版本号（`localhost/xmflow-cli:<版本>`），
一次性 run、`up` 启动与 `smoke` 体检用的都是它。整个流程**幂等**：中断或失败
后重新执行 `load` 即可，已经完成的步骤会自动跳过，不会重复解压底座归档。
客户**不需要**手工执行 `docker load`——脚本已包含导入与双重校验。

### 更新交付（只换载荷 wheel）

交付方只升级 XMNN 工具链载荷（底座镜像不变）时，**不需要重新传底座归档**：

1. 用新 wheel 替换 `payload\` 目录内的旧文件——目录内**同时只应有一个**
   `xmnn-<版本>-cp314-cp314-linux_x86_64.whl`（旧的要删掉，避免误装）；
2. 记事本打开 `.env`，把 `XMNN_VERSION=` 改成交付方给的新版本号
   （`load` 会与交付清单核对，不一致直接报错并提示正确值）；
3. 执行 `.\xmnnctl.ps1 load`（Linux/macOS：`./xmnnctl load`）——脚本发现本机
   底座与清单 Id 一致，**跳过归档导入**，只做载荷校验与派生构建（约 1-3 分钟）；
4. 之后的一次性 run / `up` 即以新载荷的镜像工作；`workspace\` 内文件不受影响。

> 若交付方同时更新了底座（`artifacts\` 内的归档也会换成新版），把新版
> `artifacts\` 与 `payload\` 一起替换后再执行 `load` 即可——脚本检测到底座
> Id 变化时会自动导入新归档。

### 选择容器运行时（Podman / Docker）

默认 `auto`：自动探测，优先 Podman、其次 Docker。需要强制指定时，用
`--runtime`（Windows：`-Runtime`，均可用简写 `-r`）参数，取值
`podman|docker|auto`，参数可放在命令前后：

```bash
./xmnnctl --runtime docker load     # 强制 Docker
./xmnnctl -r podman load            # 强制 Podman（等价写法）
```

```powershell
.\xmnnctl.ps1 -Runtime docker load
```

也可设置环境变量 `XMNN_RUNTIME=podman|docker|auto`。优先级：命令行参数
> 环境变量 > `auto` 自动探测。显式指定了未安装的运行时时脚本会直接报错，
不会静默回退到另一个运行时。

> 本产品**不绑定任何宿主端口**，因此不存在跨运行时的端口冲突预检；但两个
> 运行时各自维护容器与镜像（互不可见）。从 A 运行时换到 B 之前，建议先在
> A 侧执行 `down`；若确需两套实例长期并存，请把交付包整个解压/复制到另一个
> 目录并更换其 `.env` 中的 `XMNN_CONTAINER_NAME`，同时避免两个实例写同一个
> `workspace/temp` 目录。

## 4. 跑模型任务（客户契约）

### 4.1 挂载点约定

镜像内工作目录为 `/workspace`，约定两个挂载点（一次性 run 与常驻模式一致）：

| 容器路径 | 用途 | 客户提供 |
|---|---|---|
| `/workspace/models` | 模型组根目录（只读使用即可） | 必需 |
| `/workspace/temp` | 编译/推理产物输出目录 | 必需（需可写） |

交付包内的对应宿主目录是 `workspace/models` 与 `workspace/temp`（首次 `up`
自动创建；一次性 run 前可 `mkdir -p workspace/models workspace/temp`）。

### 4.2 模型组目录契约

```
workspace/models/
└── demo/
    └── caffe/
        └── resnet50/
            ├── config.toml      # 模型配置（编译 target、量化、数据集、设备 IP）
            ├── *.prototxt       # 网络结构（Caffe）
            ├── *.caffemodel     # 权重（Caffe）/ *.onnx / *.pth
            └── dataset.txt      # 校准数据清单（路径相对模型目录）
```

- **模型名即目录层级**：`-n a.b.c` 对应 `models/a/b/c/`；
- 每个模型目录必须含 `config.toml`，关键字段：
  - `[compile] target`：`SIM_VTA2.0` / `SIM_VTA2.0_PRO` / `SIM_VTA4.0`（仿真），
    `XM210V300` / `XM650V300` / `XM_V500`（真机）；
  - `[compile] quantized_dtype`：`a8w8` / `a16w8` 等；
  - `[compile] tune = true`：自动调优（耗时长）；`false` 时使用随镜像内置的
    预置调优库（autolibs）；
  - `[inference] device_ip` / `device_mount_dir`：真机 telnet 地址与板端目录；
- 产物输出至 `temp/<模型名>/compile/`（`network.xmnn`、`vta_config.bin`、
  `vta_data.bin`、`cpp_deploy_static`、调优日志等）。

### 4.3 常用任务命令

以一次性 run 为例（`<交付版本>` 替换为实际版本号；挂载两行在每条命令中都需
带上；常驻模式改用 `docker exec -it xmflow-cli xmflow ...`）：

```bash
# 编译：模型名 demo.caffe.resnet50 对应 models/demo/caffe/resnet50/
docker run --rm -v "$PWD/workspace/models:/workspace/models:ro" -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> compile -n demo.caffe.resnet50

# 精度验证（SIM 或真机，输出 result.csv：余弦相似度/MSE/MAE 等）
docker run --rm -v "$PWD/workspace/models:/workspace/models:ro" -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> accuracy -n hub.caffe.fp_queena

# 真机推理（需 --network host 使容器可达板卡 telnet 端口，见 §4.4）
docker run --rm --network host \
  -v "$PWD/workspace/models:/workspace/models:ro" -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> infer -n hub.caffe.fp_queena

# 性能分析 / Excel 汇总报告
docker run --rm -v "$PWD/workspace/models:/workspace/models:ro" -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> performance -n hub.caffe.fp_queena
docker run --rm -v "$PWD/workspace/models:/workspace/models:ro" -v "$PWD/workspace/temp:/workspace/temp" \
  localhost/xmflow-cli:<交付版本> excelreport -n hub.caffe.fp_queena

# 流水线：串联多任务
docker run --rm localhost/xmflow-cli:<交付版本> pipeline --help

# 查看任意命令的参数
docker run --rm localhost/xmflow-cli:<交付版本> --help
docker run --rm localhost/xmflow-cli:<交付版本> compile --help
```

### 4.4 真机推理网络说明

主机到板卡（默认 telnet 23 端口）必须网络可达：

- Linux 主机推荐 `--network host`；Docker Desktop（macOS/Windows）需在其
  网络设置中放通到板卡网段的路由；
- 板端 `device_mount_dir`（默认 `/home`）指向的共享存储（NFS/CIFS）由现场
  IT 预先挂载并保证与主机产物目录互通；镜像只负责经 telnet 下发部署与推理
  命令；
- 仿真（`SIM_*` target）不依赖任何外部设备。

## 5. 镜像形态与内容边界

### 5.1 底座形态标签

底座镜像按 torch 前端支持分两种形态（交付包内 `artifacts/` 的归档名与
`release.json` 的镜像 ref 会写明形态，形如 `localhost/xmflow-cli:base-none`
或 `localhost/xmflow-cli:base-cpu`）：

| 形态 | 支持前端 | 体积参考 |
|---|---|---|
| `base-none` | Caffe、ONNX | 镜像约 1.2 GB（压缩归档以实物为准） |
| `base-cpu` | Caffe、ONNX、**PyTorch（CPU 前端）** | 镜像约 2.1 GB（压缩归档以实物为准） |

- PyTorch 模型（`.pth/.pt`）编译必须使用 **cpu 形态**交付包；torch 仅用于
  主机端模型前端加载（CPU 版），不影响板端运行。
- 工具链版本以交付清单为准：`./xmnnctl version` 可查（Python 3.14 ABI）。
- 容器内以非 root 用户 `xmnn` 运行。

### 5.2 镜像内容边界

**包含**：可重定位的 Python 3.14 运行时（隔离 venv）、编译后的
tvm/vta/xmnn 及全部 Python 依赖、内置 LLVM（约 186 MB）与 libtvm（编译需要，
不依赖系统 LLVM）、六个 target 的预编译 `cpp_deploy`/`xm_autotools` 工具、
预置调优库、报告字体；`base-cpu` 形态另含 CPU 版 torch/torchvision。

**不包含**：任何工具链与模型源码、Nuitka 打包器、CUDA/GPU 栈、jupyter/SSH
服务、示例模型与校准数据。

## 6. 数据与目录

| 目录 / 文件 | 说明 |
|---|---|
| `workspace/models/` | 模型组根目录，映射到容器内 `/workspace/models`（只读）；`down` 不删除 |
| `workspace/temp/` | 产物与临时区，映射到容器内 `/workspace/temp`（需可写）；`down` 不删除 |
| `.env` | 配置文件（仅版本与容器名两键，**本产品无私有凭证与端口配置**）；记事本即可打开 |
| `artifacts/` | 底座镜像归档 `xmflow-cli-base-<形态>.tar.gz` 与交付清单 `release.json` |
| `payload/` | 载荷 wheel（XMNN 本体，`xmnn-<版本>-cp314-cp314-linux_x86_64.whl`）与派生构建用的 `Dockerfile`；**请勿改动或删除 Dockerfile** |

> **temp 目录写权限**：容器以非 root 用户 `xmnn` 运行（uid 由镜像构建时
> 分配，不固定）。若宿主 `temp` 目录对该 uid 不可写（新建文件被拒），
> 简易方式是放开目录权限：`mkdir -p workspace/temp && chmod 0777 workspace/temp`；
> 或先查询容器 uid：
>
> ```bash
> docker run --rm --entrypoint id localhost/xmflow-cli:<交付版本> -u
> ```
>
> 再对 `workspace/temp` 执行 `chown`；也可以在 `docker run` 追加
> `--user "$(id -u):$(id -g)"` 以当前宿主用户身份运行。

## 7. 完整性校验

`load` 在导入与构建前会分别比对两份大制品的 **SHA256** 与
`artifacts/release.json` 中记录的摘要：底座归档（`archive.sha256`）与载荷
wheel（`payload.sha256`）。任一不一致即拒绝继续（文件可能在拷贝中损坏，请
重新获取交付包）。

如需手工校验：

```powershell
# Windows（底座归档；载荷 wheel 同理，替换文件名即可）
(Get-FileHash .\artifacts\xmflow-cli-base-*.tar.gz -Algorithm SHA256).Hash.ToLower()
```

```bash
# Linux / macOS
sha256sum artifacts/xmflow-cli-base-*.tar.gz   # 或 shasum -a 256
```

## 8. 交付守卫（自动体检清单）

`load` 的派生构建过程会**逐项自动执行**下列守卫，任一失败即中止且不产出
镜像；日常可用 `./xmnnctl smoke` 随时对派生镜像复核第 2 张清单。

**底座守卫（构建底座镜像时以 root 与 xmnn 双身份各跑一遍，6 项）：**

1. 可重定位解释器与 venv ABI：/opt/conda = cp314 GIL（relocated，prefix 正确、
   报告 GIL enabled）；/opt/xmflow = 由其派生的 venv（pyvenv.cfg 在、prefix
   正确）；venv 可导入 stdlib 关键扩展（ssl/ctypes/sqlite3/lzma/bz2/zlib/
   decimal/pyexpat/venv）
2. deps.txt 每条 Requirement 的发行版已在 venv 安装
3. /opt/xmflow/bin/python -m pip check 无冲突（venv 依赖面全由 deps.txt 铺成，
   无基镜像元数据债务）
4. torch 形态与实物一致（marker ∈ none|cpu vs import 与 version.cuda；
   本产品无 CUDA 形态）
5. 非 root（xmnn）身份可用：venv 可执行、deps.txt 可读、/workspace/temp 可写
6. 反断言：载荷未安装——两个解释器的 site-packages 无 xmnn* 残留、venv bin 无
   xmnn*/xmflow 脚本、`import xmnn` 必须失败且为 ModuleNotFoundError

**交付镜像守卫（载荷装入后的派生镜像，10 项 + pip check）：**

1. 解释器 ABI：/opt/xmflow/bin/python + cp314 GIL enabled
2. import tvm / vta / xmnn，且 `__file__` 落在 site-packages
3. _libs 目录含 libtvm.so 与 libLLVM*
4. 干净环境 ctypes RTLD_GLOBAL 加载 libtvm.so
5. tvm.build('llvm') 向量乘 2 数值断言（合成计算，零模型依赖）
6. relay/std/prelude.rly 数据存在
7. 载荷数据文件：xmnn_bootstrap.pth 在 site-packages + xmnn 数据三目录
   （autolibs/tools_cpp/fonts）
8. deps.txt 闭包关键模块逐一可导入（如 Pillow→PIL、protobuf→google.protobuf）
9. xmflow console script 存在、`--help` 退出码 0、输出含六个子命令名
   （compile/accuracy/infer/performance/excelreport/pipeline）
10. torch 形态与实物一致（marker vs import/version.cuda；none|cpu 双态，无 CUDA 栈）
+ pip check：判据**收窄到载荷相关冲突**（以 `xmnn` 开头的冲突行判失败）；
  其余冲突行属底座层职责（已在底座守卫第 3 项全量把关），此处仅提示放行。

守卫**不含**真实模型的编译冒烟（不引入模型进构建上下文）；真机/仿真模型组
的冒烟请以 §4.3 第一条命令形式执行：
`docker run --rm ... localhost/xmflow-cli:<交付版本> compile -n demo.caffe.resnet50`。

## 9. 排障

| 现象 | 处理 |
|---|---|
| 报"术语 'xmnnctl' 不会被识别为 cmdlet" | 当前目录不对：先确认当前目录是否含 `xmnnctl.ps1`，没有就进入含本 README 的交付包根目录再执行；SpecWeave 开发仓库内如需在交付目录外操作，改用 `offline-delivery/bin/relpack`（见 §2 执行位置） |
| 报 `Cannot connect to Podman` / `unable to connect to Podman socket` | Podman 后台虚拟机未启动：执行 `podman machine start`（或打开 Podman Desktop 等待托盘就绪）后重试原命令；Docker 则启动 Docker Desktop。新版脚本会在导入前直接拦截并给出同样提示 |
| `load` 提示 sha256 不符（底座归档或载荷 wheel） | 文件在拷贝中损坏：重新拷贝/获取交付包后再试；若 `payload/` 内 wheel 是手工替换的，请向交付方索取完整文件 |
| 连接失败后又提示"导入的镜像中没有/版本不符" | 这是旧版脚本的**误导性次生报错**，真因是后台没连上；先按上面一行启动机器并重试，不要改版本号 |
| `load` 报"版本不一致：.env 的 XMNN_VERSION=… 交付清单 version=…" | 这是**保护性拦截**：交付清单才是权威版本。按报错中的"修法"把 `.env` 的 `XMNN_VERSION` 改成清单里的版本后重试 |
| `load` 报"派生构建失败" | 构建全程离线，与网络无关。① 先看报错上方是否磁盘空间不足（派生镜像另需约 0.2 GB），清理后重跑 `load`（幂等）；② "载荷声明的依赖未在底座满足"＝构建日志里出现了以 `xmnn` 开头的 `pip check` 冲突行（载荷声明的依赖在底座缺失或版本不符），属**底座与载荷不匹配**（交付方制品问题），把报错原文反馈给对接人员。注：不以 `xmnn` 开头的冲突行（如底座自身依赖面的元数据冲突）与本次交付无关，构建会照常继续 |
| `load` 报"交付包与镜像不匹配…Id 不一致" | `artifacts/` 内的归档与 `release.json` 不是同一批：重新完整获取交付包（两者必须成套） |
| `load` 后 run/up 仍起不来，报找不到镜像 | 核对 `.env` 的 `XMNN_VERSION` 与 `./xmnnctl version` 打印的"交付版本"是否一致；不一致时先改 `.env` 再 `load` |
| 报 `No module named 'torch'` | 该模型是 PyTorch 前端，需要 **cpu 形态**（`base-cpu`）的交付包：向交付方索取 base-cpu 版归档（见 §5.1），none 形态不含 torch |
| temp 目录权限报错（新建文件被拒） | 容器以非 root 用户 `xmnn` 运行（uid 由镜像构建时分配）：按 §6 的三种方式之一处理（`chmod 0777` 最简易；或查 uid 后 `chown`；或 `run` 加 `--user "$(id -u):$(id -g)"`） |
| `PermissionError: … temp/<模型名>/compile/0-compile.log`（重跑编译时） | 目录本身可写，但其中存在**其他身份（uid）上次运行留下的旧产物文件**（权限通常为 644/555），追加写被拒：删除 `temp/<模型名>` 整个目录后重跑，或固定用同一身份方式运行（见上一行） |
| **推理输出全为 0x7F7F** | 属板端运行毒值，通常为编译 `target` 与实际板卡不匹配（例如用了仿真 target 或错误的真机型号）——**不是镜像问题**：核对 `config.toml` 的 `[compile] target` 与板卡型号一致后重新编译 |
| 真机 `infer` 连不上板卡 | 容器默认网络到不了板卡 telnet 端口：按 §4.3/§4.4 加 `--network host`（Docker Desktop 需放通路由）；仿真 target 无此要求 |
| Podman 提示找不到 compose | 脚本会自动尝试 `~/.local/bin`（pipx/pip --user 安装位置）；仍失败时按报错提示安装 `podman-compose`（推荐 `pipx install podman-compose`）。WSL 非登录 shell 可先执行 `export PATH="$HOME/.local/bin:$PATH"` |
| Linux/macOS 执行报 `'bash\r': No such file or directory` | 脚本在拷贝中被改成了 Windows 行尾：Linux/WSL 执行 `sed -i 's/\r$//' xmnnctl`（macOS 用 `sed -i '' 's/\r$//' xmnnctl`），重新 `chmod +x xmnnctl` 后再试；或重新获取交付包 |
| 报 `network.xmnn` 等产物文件名想确认含义 | 见 §4.2 产物清单：`network.xmnn` 为编译后的模型网络描述，配合 `vta_config.bin`/`vta_data.bin` 下发板端 |

## 10. Windows 使用注意

- 请始终使用 `xmnnctl.ps1`；**不要**在 Git Bash 中运行同名 bash 脚本
  （路径转换会导致容器参数错误）。
- 建议交付包放置在**不含空格与中文**的路径下。
- 使用 Docker Desktop 或 Podman Machine 时，请确保对应后台程序已启动。
- 提示"执行策略"被拦截时，用一次性放行命令：
  `pwsh -ExecutionPolicy Bypass -File .\xmnnctl.ps1 <命令>`（不修改系统设置）。

## 11. 小白词典与常见问题

### 11.1 名词小词典

| 你看到的词 | 人话解释 |
|---|---|
| 终端 / PowerShell | 输入文字命令的窗口；PowerShell 是 Windows 上的终端程序，本包要求 7.0 以上 |
| 命令 | 粘贴进终端、按回车执行的一句话，例如 `.\xmnnctl.ps1 load` |
| 容器 | "软件电脑"运行起来后的实例；可以启动（up）、停止（down），停止不影响你的文件 |
| 镜像 | "软件电脑"的模板；`load` 先把**底座模板**（不含工具链本体的空壳）导入 Podman/Docker，再把**载荷**装进去 |
| 底座 / 载荷 | 底座＝只有 Python 运行时与依赖的"空壳模板"（约 1-2 GB 归档）；载荷＝XMNN 工具链本体（一个 wheel 文件）。两者合成后才是能用的"软件电脑" |
| 派生镜像 | 底座装好载荷后生成的镜像，名字就是 `.env` 里的版本号（`localhost/xmflow-cli:<版本>`）；run、`up` 与 `smoke` 用的都是它 |
| `.env` | 一个普通文本配置文件，存着交付版本号与容器名（本产品无私有凭证），记事本即可打开 |
| `workspace` 文件夹 | 交付包里的普通文件夹：`workspace/models` 等同容器内 `/workspace/models`（放模型组），`workspace/temp` 等同 `/workspace/temp`（放产物），`down` 不删除 |
| 模型组 / `-n 名称` | 你要处理的模型及其配置目录；`-n demo.caffe.resnet50` 就是告诉工具链去 `models/demo/caffe/resnet50/` 找模型（见 §4.2） |
| 交付守卫（smoke） | 10 项自动体检，逐项确认镜像内各组件工作正常 |

### 11.2 高频问题

- **出现红字/黄字是不是失败了？** 黄字 `[WARN]` 是提醒，可继续；只有红字
  `[ERR ]` 且命令提前结束才是失败，对照 §9 排障表处理。
- **`load` 卡住、进度条几分钟不动？** 分两段：底座导入约 1-2 GB，1-5 分钟
  正常；随后"派生构建载荷镜像"约 1-3 分钟（这一步没有进度条，只在结束时
  出现构建日志）。期间勿关终端；超过 10 分钟毫无变化再截图询问对接人员。
- **命令跑完后能关终端窗口吗？** 一次性 run 跑完即退，无影响；`up` 常驻的
  容器在后台运行，关窗口不受影响；下次操作时重新在该文件夹打开终端即可。
- **电脑关机/重启后还要重做哪几步？** 先启动 Podman Machine 或 Docker
  Desktop；一次性 run 可直接执行，常驻模式执行 `up` 一条命令即可；
  **不需要**重新 `init` 或 `load`（除非你删掉了导入的镜像）。
- **Linux 提示 Permission denied？** 先执行一次 `chmod +x xmnnctl`（仅需
  一次），再重新执行原命令。
- **为什么这个包没有网址/密码？** 本产品是命令行工具交付，不运行任何网络
  服务（无 Jupyter/SSH，不占用任何端口），所有功能都在终端里完成。
