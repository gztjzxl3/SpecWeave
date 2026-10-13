"""offline-delivery 测试夹具（daemon-free，不触 podman / 容器守护进程）。

本目录**不建 Python 包**（无 `__init__.py`、无 `pyproject.toml`），pytest 以 rootdir
方式直接收集；夹具只做路径定位与 product.env 解析，供
`test_release_skeleton.py`（客户交付骨架静态守卫）与
`test_relpack_cli.py`（`bin/relpack*` 静态守卫）共用。

多产品支持（第二交付产品 xmflow-cli 引入，FR-10）：
  - `PRODUCT_NAME` 及其定位的单产品夹具链（`product_dir` / `release_dir` /
    `product_env`）保持原语义不动——它们是 `test_relpack_cli.py` 等厂商侧
    守卫的兼容锚点；
  - `discover_products()` 扫描 `products/*/`（须含 `product.env` 且其声明的
    `RELEASE_DIR` 目录存在），`any_product` 夹具据此对全部已就绪产品自动
    参数化：新增/删除产品无需改动任何测试代码。
"""

from pathlib import Path
from typing import NamedTuple

import pytest

# 应用根：tests/ 的上一级（apps/containers/offline-delivery/）
APP_ROOT = Path(__file__).resolve().parents[1]

# 首个产品；CLI 的产品差异（镜像名/Containerfile/wheel glob/骨架目录名）全部来自
# products/<产品>/product.env，测试据此定位而非复制常量。
PRODUCT_NAME = "xmnn-runtime"


def load_product_env(env_path: Path) -> dict:
    """解析 `product.env`（`KEY=VALUE` 逐行，值不加引号、不写空格）→ dict。"""
    env = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def discover_products(app_root: Path = APP_ROOT) -> list:
    """发现 `products/*/` 下已就绪交付骨架的产品名（字典序）。

    入选条件：目录含 `product.env`，且其 `RELEASE_DIR`（缺省 `release`）目录
    已存在——只有交付骨架就绪的产品才应进入客户侧骨架守卫的参数化集合。
    """
    names = []
    products_root = app_root / "products"
    if products_root.is_dir():
        for d in sorted(products_root.iterdir()):
            env_file = d / "product.env"
            if not d.is_dir() or not env_file.is_file():
                continue
            env = load_product_env(env_file)
            if (d / env.get("RELEASE_DIR", "release")).is_dir():
                names.append(d.name)
    return names


PRODUCT_NAMES = discover_products()


class Product(NamedTuple):
    """一个交付产品的定位结果与参数（通用不变量层的参数化载体）。"""

    name: str
    dir: Path
    release_dir: Path
    env: dict


@pytest.fixture(scope="session")
def app_root() -> Path:
    """应用根目录（`bin/` 与 `products/` 的父目录）。"""
    return APP_ROOT


@pytest.fixture(scope="session")
def bin_dir(app_root: Path) -> Path:
    """厂商侧 CLI 目录（`bin/relpack` + `bin/lib/*.sh` + `bin/relpack.ps1`）。"""
    return app_root / "bin"


@pytest.fixture(scope="session")
def product_dir(app_root: Path) -> Path:
    """单产品锚点：`products/xmnn-runtime/`（`test_relpack_cli.py` 兼容语义，勿改）。"""
    return app_root / "products" / PRODUCT_NAME


@pytest.fixture(scope="session")
def release_dir(product_dir: Path) -> Path:
    """单产品锚点：`products/xmnn-runtime/release/`（客户可见契约，勿改语义）。"""
    return product_dir / "release"


@pytest.fixture(scope="session")
def product_env(product_dir: Path) -> dict:
    """单产品锚点：解析 `products/xmnn-runtime/product.env`。"""
    return load_product_env(product_dir / "product.env")


@pytest.fixture(scope="session", params=PRODUCT_NAMES)
def any_product(request) -> Product:
    """逐个参数化已发现的产品（通用不变量层的入口；产品增删自动生效）。"""
    name = request.param
    pdir = APP_ROOT / "products" / name
    env = load_product_env(pdir / "product.env")
    return Product(name=name, dir=pdir,
                   release_dir=pdir / env.get("RELEASE_DIR", "release"), env=env)
