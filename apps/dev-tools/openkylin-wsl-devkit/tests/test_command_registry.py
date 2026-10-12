"""显式命令注册表 L0 断言：键集、可调用性、旧路径别名、零副作用导入。"""

import subprocess
import sys
from pathlib import Path

import pytest

from okw import image, podman
from okw.commands import COMMAND_HANDLERS
from okw.commands import image_cmds, podman_cmds

EXPECTED_KEYS = sorted(
    [
        "list",
        "status",
        "import",
        "export",
        "unregister",
        "exec",
        "verify",
        "scaffold",
        "ref",
        "podman preflight",
        "podman install",
        "podman verify",
        "image build",
        "image verify",
    ]
)

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_registry_has_exactly_fourteen_leaves():
    assert sorted(COMMAND_HANDLERS) == EXPECTED_KEYS
    assert len(COMMAND_HANDLERS) == 14


def test_every_registry_value_is_callable():
    for key, handler in COMMAND_HANDLERS.items():
        assert callable(handler), key


def test_registry_is_plain_dict():
    assert type(COMMAND_HANDLERS) is dict


@pytest.mark.parametrize(
    "module, attr_name, registry_key",
    [
        (podman, "cmd_preflight", "podman preflight"),
        (podman, "cmd_install", "podman install"),
        (podman, "cmd_verify", "podman verify"),
        (image, "cmd_build", "image build"),
        (image, "cmd_verify", "image verify"),
    ],
)
def test_legacy_module_aliases_resolve_to_registry_handlers(
    module, attr_name, registry_key
):
    assert getattr(module, attr_name) is COMMAND_HANDLERS[registry_key]


def test_legacy_aliases_are_same_objects_as_command_modules():
    assert podman.cmd_preflight is podman_cmds.cmd_preflight
    assert podman.cmd_install is podman_cmds.cmd_install
    assert podman.cmd_verify is podman_cmds.cmd_verify
    assert image.cmd_build is image_cmds.cmd_build
    assert image.cmd_verify is image_cmds.cmd_verify


@pytest.mark.parametrize("module", [podman, image])
def test_unknown_attribute_still_raises_attribute_error(module):
    with pytest.raises(AttributeError):
        getattr(module, "cmd_does_not_exist")


def test_import_commands_has_no_subprocess_side_effects():
    # 干净子进程：把 distro 的 WSL 执行入口替换为探针后导入 commands 包，
    # 任何导入期子进程调用都会令探针失败。
    script = (
        "import sys\n"
        f"sys.path.insert(0, r'{SRC_ROOT}')\n"
        "import okw.distro as d\n"
        "def _boom(*a, **k):\n"
        "    raise AssertionError('import 期发生子进程副作用')\n"
        "d.run_wsl = _boom\n"
        "import okw.commands\n"
        "from okw.commands import COMMAND_HANDLERS\n"
        "assert len(COMMAND_HANDLERS) == 14\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
