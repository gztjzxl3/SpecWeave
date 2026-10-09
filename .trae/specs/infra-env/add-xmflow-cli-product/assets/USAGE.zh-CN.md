# xmflow 客户发布镜像使用说明

本镜像为 XMNN NPU 模型工具链的**客户运行时**：仅含编译后的 wheel 闭包，
不含任何源码，无需挂载开发目录。在容器内即可完成模型**编译、精度验证、
真机/仿真推理、性能与带宽分析、Excel 报告**全流程。

## 1. 镜像标签

| 标签 | 支持前端 | 近似体积 |
|---|---|---|
| `xmflow-release:1.2.1` | Caffe、ONNX | 约 1.2 GB |
| `xmflow-release:1.2.1-torch` | Caffe、ONNX、**PyTorch（CPU 前端）** | 约 1.7 GB |

- 工具链版本：xmnn 1.2.1.dev0（Nuitka 4.2.2 编译，Python 3.14 ABI）
- PyTorch 模型（`.pth/.pt`）编译必须使用 `-torch` 标签；torch 仅用于主机端
  模型前端加载（CPU 版），不影响板端运行。
- 仅支持 x86_64（amd64）主机；容器运行时为容器内非 root 用户 `xmnn`。

加载离线 tar（如通过压缩包交付）：

```bash
# zstd 压缩包
zstd -dc xmflow-release-1.2.1.tar.zst | docker load
# 或 podman
zstd -dc xmflow-release-1.2.1.tar.zst | podman load
```

## 2. 快速开始

镜像内工作目录为 `/workspace`，约定两个挂载点：

| 容器路径 | 用途 | 客户提供 |
|---|---|---|
| `/workspace/models` | 模型组根目录（只读使用即可） | 必需 |
| `/workspace/temp` | 编译/推理产物输出目录 | 必需（需可写） |

```bash
# 编译：模型名 demo.caffe.resnet50 对应 models/demo/caffe/resnet50/
docker run --rm \
  -v "$PWD/models:/workspace/models:ro" \
  -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 compile -n demo.caffe.resnet50

# 查看任意命令的参数
docker run --rm xmflow-release:1.2.1 compile --help
docker run --rm xmflow-release:1.2.1 --help
```

Podman 用户将 `docker` 替换为 `podman` 即可。

## 3. 模型组目录契约

```
models/
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

## 4. 常用命令

```bash
# 精度验证（SIM 或真机，输出 result.csv：余弦相似度/MSE/MAE 等）
docker run --rm -v "$PWD/models:/workspace/models:ro" -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 accuracy -n hub.caffe.fp_queena

# 真机推理（需 --network host 使容器可达板卡 telnet 端口）
docker run --rm --network host \
  -v "$PWD/models:/workspace/models:ro" -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 infer -n hub.caffe.fp_queena

# 性能分析 / 带宽分析 / Excel 汇总报告
docker run --rm -v "$PWD/models:/workspace/models:ro" -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 performance -n hub.caffe.fp_queena
docker run --rm -v "$PWD/models:/workspace/models:ro" -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 excelreport -n hub.caffe.fp_queena

# 流水线：串联多任务
docker run --rm -v "$PWD/models:/workspace/models:ro" -v "$PWD/temp:/workspace/temp" \
  xmflow-release:1.2.1 pipeline --help
```

## 5. 真机推理网络说明

主机到板卡（默认 telnet 23 端口）必须网络可达：

- Linux 主机推荐 `--network host`；Docker Desktop（macOS/Windows）需在其
  网络设置中放通到板卡网段的路由；
- 板端 `device_mount_dir`（默认 `/home`）指向的共享存储（NFS/CIFS）由现场
  IT 预先挂载并保证与主机产物目录互通；镜像只负责经 telnet 下发部署与推理命令；
- 仿真（`SIM_*` target）不依赖任何外部设备。

## 6. 镜像内容边界

**包含**：Python 3.14 运行时（隔离 venv）、编译后的 tvm/vta/xmnn 及全部
Python 依赖、内置 LLVM 186MB 与 libtvm（编译需要，不依赖系统 LLVM）、
六个 target 的预编译 `cpp_deploy`/`xm_autotools` 工具、预置调优库、
报告字体；`-torch` 标签另含 CPU 版 torch/torchvision。

**不包含**：任何工具链与模型源码、Nuitka 打包器、CUDA/GPU 栈、
jupyter/SSH 服务、示例模型与校准数据。

## 7. 常见问题

- **`No module named 'torch'`**：该模型是 PyTorch 前端，请改用
  `xmflow-release:1.2.1-torch` 标签。
- **temp 目录权限报错**：容器以非 root 用户 `xmnn` 运行（uid 由镜像构建时
  分配），请令宿主 `temp` 目录对该 uid 可写：简易方式
  `mkdir -p temp && chmod 0777 temp`；或查询 uid
  （`docker run --rm --entrypoint id xmflow-release:1.2.1 -u`）后 `chown`；
  也可在 `docker run` 加 `--user "$(id -u):$(id -g)"` 以当前宿主用户运行。
- **推理输出全为 0x7F7F**：属板端运行毒值，通常为编译 `target` 与实际板卡
  硬件不匹配或板端共享存储异常，并非镜像问题。
