"""rootless Podman 子组命令：preflight / install / verify。

三个 CLI 包装函数自原 okw.podman 逐字迁入；判定矩阵、报告类型与格式化
函数仍留在领域模块 okw.podman，本模块只做参数解包与调用编排。
"""

from okw import podman


def cmd_preflight(args) -> int:
    """CLI 入口：okw podman preflight <发行版>。"""
    name = args.name
    report = podman.preflight_check(name)
    print(podman.format_preflight(report))
    return report.exit_code()


def cmd_install(args) -> int:
    """CLI 入口：okw podman install <发行版> [--yes]。"""
    name = args.name
    yes = getattr(args, "yes", False)
    if not yes:
        report = podman.InstallReport(distro_name=name, missing_yes=True)
        print(podman.format_install(report))
        return report.exit_code()
    report = podman.install_run(name, yes=True)
    print(podman.format_install(report))
    return report.exit_code()


def cmd_verify(args) -> int:
    """CLI 入口：okw podman verify <发行版> [--smoke-image LOCAL_IMAGE]。"""
    smoke_image = getattr(args, "smoke_image", None)
    report = podman.verify_run(args.name, smoke_image=smoke_image)
    print(podman.format_verify(report))
    return report.exit_code()
