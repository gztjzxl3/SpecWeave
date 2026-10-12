"""发行版生命周期命令：list / status / import / export / unregister / exec。

函数体自原 okw.cli 逐字迁入，输出文案与退出码保持不变。
"""

import argparse
import sys

from okw import distro


def cmd_list(_args: argparse.Namespace) -> int:
    distros = distro.list_distros()
    if not distros:
        print("未发现任何 WSL 发行版（wsl --import 导入 openKylin 后重试）")
        return 0
    print(f"共 {len(distros)} 个 WSL 发行版：")
    for d in distros:
        star = "*" if d.is_default else " "
        print(f"  {star} {d.name:<24} WSL{d.version:<3} {d.state}")
    default = distro.default_distro_name()
    if default:
        print(f"默认发行版（星标保护）：{default}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    d = distro.get_distro(args.name)
    if d is None:
        print(f"发行版 {args.name} 不存在（wsl -l -v 查看在列发行版）", file=sys.stderr)
        return 1
    star = "（默认）" if d.is_default else ""
    print(f"{d.name}: WSL{d.version} / {d.state} {star}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    res = distro.import_distro(args.image, args.name, args.location, args.version)
    if not res.ok:
        print("导入失败，按知识库 §4 排障三问排查：", file=sys.stderr)
        print("  1) 失败位置是否漂移（镜像位置/导入目录发生变化）→ 固定位置重试", file=sys.stderr)
        print("  2) 空闲内存是否不足（0.8GB 失败 / 4.5GB 成功）→ wsl --shutdown 后重试", file=sys.stderr)
        print("  3) 仍失败：把 .wsl 解压为纯 tar 再 import", file=sys.stderr)
        if res.stderr.strip():
            print(f"  原始错误：{res.stderr.strip()[:300]}", file=sys.stderr)
        return res.exit_code or 1
    print(f"导入成功：{args.name}（{args.location}）")
    print("提示：默认账号 openkylin/openkylin 为弱口令，首次进入请立即 passwd；", file=sys.stderr)
    print("      桌面版镜像请用 xrdp 连接 3390 端口（知识库 wsl-dual-image-selection）。")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    res = distro.export_distro(args.name, args.output)
    if not res.ok:
        print(f"导出失败：{res.stderr.strip() or f'exit={res.exit_code}'}", file=sys.stderr)
        return res.exit_code or 1
    print(f"已导出：{args.output}")
    return 0


def cmd_unregister(args: argparse.Namespace) -> int:
    res = distro.unregister_distro(args.name, yes=args.yes)
    if not res.ok:
        print(f"已拒绝：{res.stderr.strip()}", file=sys.stderr)
        return res.exit_code or 1
    print(f"已注销：{args.name}")
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    cmd = list(args.cmd)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("exec 需要命令：okw exec <name> -- <cmd>", file=sys.stderr)
        return 2
    res = distro.exec_distro(args.name, cmd)
    if not res.ok:
        print(f"执行失败：{res.stderr.strip() or f'exit={res.exit_code}'}", file=sys.stderr)
        return res.exit_code or 1
    if res.stdout:
        print(res.stdout.rstrip("\n"))
    if res.stderr:
        print(res.stderr.rstrip("\n"), file=sys.stderr)
    return 0
